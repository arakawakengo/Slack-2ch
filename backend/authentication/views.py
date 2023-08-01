from django.shortcuts import render

import logging

from .models import CustomUser, Workspace
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

import secrets


class RegisterWorkshopView(APIView):
    
    def post(self, request):
        
        token = request.data.get('token', None)
        if not token:
            return Response({"error": "Token not provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        client = WebClient(token=token)
        logger = logging.getLogger(__name__)
        
        def save_users(users_array):
            for user in users_array:
                # Key user info on their unique user ID
                user_id = user["id"]
                workshop_id = user["team_id"]
                username = user["real_name"]
                
                channel_id = self.client.conversations_open(users=user_id)["channel"]["id"]
                
                # Store the entire user object (you may not need all of the info)
                new_user = CustomUser(user_id=user_id, workspace_id=workshop_id, username=username, channel_id=channel_id)
                
                password = secrets.token_hex(16)  # 自動生成のパスワード
                new_user.set_password(password)
                
                new_user.save()
                
                self.client.chat_postMessage(channel=channel_id, text="ワークショップID："+ workshop_id + "\nユーザID："+ user_id  +  "\nパスワード："+ password)

                
        workspace_info = self.client.team_info()
        
        new_workspace = Workspace(workspace_id=workspace_info["team"]["id"], workspace_name=workspace_info["team"]["name"])
        
        new_workspace.save()

        # Put users into the dict       
        try:
            # Call the users.list method using the WebClient
            # users.list requires the users:read scope
            result = self.client.users_list()
            save_users(result["members"])
            
            return Response({"message": "Users saved successfully"}, status=status.HTTP_200_OK)


        except SlackApiError as e:
            self.logger.error("Error creating conversation: {}".format(e))
            
            return Response({"error": "Error creating conversation: {}".format(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


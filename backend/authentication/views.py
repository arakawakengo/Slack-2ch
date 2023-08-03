from django.shortcuts import render

import logging

from .models import CustomUser, Workspace
from posts.models import Categories
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework_simplejwt.tokens import RefreshToken

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

import secrets


class RegisterWorkshopView(APIView):
    
    def post(self, request):
        
        token = request.data.get('token', None)
        if not token:
            return Response({"error": "Token not provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        self.client = WebClient(token=token)
        self.logger = logging.getLogger(__name__)
        
        def save_users(users_array):
            for user in users_array:

                if user["is_bot"] == True:
                    continue
                if user["real_name"] == "Slackbot":
                    continue
                
                user_id = user["id"]
                workspace_id = user["team_id"]
                username = user["real_name"]
                email = user["profile"]["email"]
                image_url = user["profile"]["image_192"]
                is_owner = user["is_owner"]
                
                channel_id = self.client.conversations_open(users=user_id)["channel"]["id"]
                
                workspace = Workspace.objects.filter(workspace_id=workspace_id).first()
                
                new_user, created = CustomUser.objects.update_or_create(
                    user_id=user_id,
                    workspace=workspace,
                    defaults={
                        "username":username,
                        "channel_id":channel_id,
                        "email": email,
                        "image_url": image_url,
                        "is_owner": is_owner
                    }
                )
                
                if not created:
                    continue
                 
                password = secrets.token_hex(16)  # 自動生成のパスワード
                new_user.set_password(password)
                new_user.save()
                
                self.client.chat_postMessage(channel=channel_id, text="ワークショップID："+ workspace_id + "\nユーザID："+ user_id  +  "\nパスワード："+ password)

                
        workspace_info = self.client.team_info()
        
        new_workspace, created = Workspace.objects.update_or_create(
                    workspace_id=workspace_info["team"]["id"],
                    defaults={
                        "workspace_name":workspace_info["team"]["name"],
                        "workspace_token":token,
                    }
                )
        
        categories = ["食べ物", "テック","サウナ","その他"]

        if created:
            for category in categories:
                Categories.objects.create(
                    category_name=category,
                    workspace=new_workspace
                )
        

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


class ObtainTokenView(generics.GenericAPIView):
    def post(self, request, *args, **kwargs):
        workspace_id = request.data['workspace_id']
        workspace = Workspace.objects.filter(workspace_id=workspace_id).first()
        user_id = request.data['user_id']
        password = request.data['password']
        user = CustomUser.objects.filter(workspace=workspace, user_id=user_id).first()
        if user and user.check_password(password):
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user_id': user_id,
                'user_name': user.username,
                'email': user.email,
                'image_url': user.image_url,
                'is_owner': user.is_owner,
                'workspace_id': workspace_id,
                'workspace_name': workspace.workspace_name,
            }, status=status.HTTP_200_OK)
        elif not user:
            return Response({"error": "Invalid account"}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({"error": "Incorrect password"}, status=status.HTTP_401_UNAUTHORIZED)

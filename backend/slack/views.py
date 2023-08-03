from rest_framework.views import APIView
from django.http import HttpResponse
import json

from posts.models import Posts, Categories
from authentication.models import CustomUser

from django.http import JsonResponse

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from rest_framework import status

import logging

logger = logging.getLogger(__name__)


def get_client(user):
    Workspace_token = user.workspace.workspace_token
    client = WebClient(token=Workspace_token)
    return client    
   

class CATCH_SLACK_COMMAND(APIView):
    
    def post(self, request):
        
        trigger_id = request.data.get("trigger_id", None)
        channel_id = request.data.get("channel_id", None)
        user_id = request.data.get("user_id", None)
        team_id = request.data.get("team_id", None)
        
        if not (trigger_id and channel_id and user_id and team_id):
            return HttpResponse("Invalid request", status=status.HTTP_400_BAD_REQUEST)
        
        user = CustomUser.objects.filter(user_id=user_id, workspace__workspace_id=team_id).first()
        
        client = get_client(user)
        
        def make_category_options(category_dict):
            options = []
            for key, category in category_dict.items():
                option = {
                    "text": {
                        "type": "plain_text",
                        "text": category,
                        "emoji": True
                    },
                    "value": str(key)
                }
                options.append(option)
            return options
            
            
        
        try:
            category_list = Categories.objects.filter(workspace=user.workspace).values("id", "category_name")
            category_dict = {c["id"]: c["category_name"] for c in category_list}
            
            view = {
                "type": "modal",
                "callback_id": "view_identifier",
                "title": {
                    "type": "plain_text",
                    "text": "2ch 新規投稿",
                },
                "blocks": [
                    {
                        "type": "input",
                        "element": {
                            "type": "static_select",
                            "placeholder": {
                                "type": "plain_text",
                                "text": "カテゴリ選択",
                                "emoji": True
                            },
                            "options": make_category_options(category_dict),
                            "action_id": "category_select-action",
                        },
                        "label": {
                            "type": "plain_text",
                            "text": "カテゴリ",
                            "emoji": True
                        },
                        "block_id": "category_select-block"
                    },
                    {
                        "type": "input",
                        "element": {
                            "type": "plain_text_input",
                            "multiline": True,
                            "action_id": "main_text_input-action",
                        },
                        "label": {
                            "type": "plain_text",
                            "text": "投稿内容",
                            "emoji": True
                        },
                        "block_id": "main_text_input-block",
                    },
                    {
                        "type": "input",
                        "element": {
                            "type": "url_text_input",
                            "action_id": "url_input-action",
                        },
                        "label": {
                            "type": "plain_text",
                            "text": "参考URL",
                            "emoji": True
                        },
                        "optional": True,
                        "hint": {
                            "type": "plain_text",
                            "text": "参考URLがあれば入力してください。",
                            "emoji": True,
                        },
                        "block_id": "url_input-block"
                    }
                ],
                "submit": {
                    "type": "plain_text",
                    "text": "投稿"
                },
            }
            
            result = client.views_open(
                trigger_id=trigger_id,
                view=view
            )
            logger.info(result)

        except SlackApiError as e:
            logger.error("Error creating conversation: {}".format(e))
            
        
        return HttpResponse({}, status=status.HTTP_201_CREATED)

class POST_VIA_SLACK(APIView):
    def post(self, request):
        
        payload_str = request.data.get("payload")
        
        payload = json.loads(payload_str)
        
        category =  payload['view']['state']['values']['category_select-block']['category_select-action']['selected_option']['value']
        category = int(category)
        text = payload['view']['state']['values']['main_text_input-block']['main_text_input-action']['value']
        url_check = payload['view']['state']['values']['url_input-block']['url_input-action']
        url = url_check["value"] if "value" in url_check else None
        
        if url:
            text = text + "\n参考URL:" + url
        
        user_id = payload['user']['id']
        team_id = payload['team']['id']
        
        user = CustomUser.objects.filter(user_id=user_id, workspace__workspace_id=team_id).first()
        if user is None:
            return HttpResponse("User not found", status=status.HTTP_404_NOT_FOUND)

        try:
            category_name = Categories.objects.get(id=category).category_name
            
            Posts.objects.create(user=user, category=category_name, text=text)
        
            client = get_client(user)
            client.chat_postMessage(channel=user.channel_id, text="投稿が完了しました。")
            
            return JsonResponse({}, status=status.HTTP_201_CREATED)
        
        except:
            return JsonResponse({
                "response_action": "errors",
                "errors": {
                    "block_id_of_input_field": "Error message here."}
            })
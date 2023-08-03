from rest_framework.views import APIView
from django.http import HttpResponse
from rest_framework.response import Response
from datetime import datetime
import json
import pytz

from posts.models import Posts, Questions, Replies, Categories
from authentication.models import CustomUser, Workspace

from slack_sdk import WebClient

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import AccessToken

import logging


def json_serial(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError ("Type %s not serializable" % type(obj))

def get_user_id(request):
    auth_header = request.META.get('HTTP_AUTHORIZATION')
    if auth_header is not None and 'Bearer' in auth_header:
        token = auth_header.split('Bearer ')[1]
    else:
        return False, "Invalid authorization header"
    
    try:
        token_decoded = AccessToken(token)
    except:
        return False, "Invalid token"
    
    id = token_decoded['user_id']
    
    return True, id

def get_client(user):
    Workspace_token = user.workspace.workspace_token
    client = WebClient(token=Workspace_token)
    return client    

def get_thread_user(question, reply_user):
    unique_user_list = set()
    thread_user_list = []
    question_user = question.user

    in_thread_reply = Replies.objects.filter(question=question).all()
    for reply in in_thread_reply:
        if reply.user.user_id in unique_user_list or \
            reply.user == reply_user or \
            reply.user == question_user:
            continue
        unique_user_list.add(reply.user.user_id)
        thread_user_list.append(reply.user)

    return thread_user_list

class POSTS(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        
        category = request.GET.get('category', None)

        is_valid, result = get_user_id(request)
        if not is_valid:
            return HttpResponse(result, status=status.HTTP_401_UNAUTHORIZED)
        user = CustomUser.objects.filter(id=result).first()

        Category = Categories.objects.filter(workspace=user.workspace).values_list('category_name')
        category_list = [x[0] for x in list(Category)]

        if category and category not in category_list:
            return HttpResponse("Invalid category", status=status.HTTP_400_BAD_REQUEST)

        if category:
            post_list = Posts.objects.filter(category=category)
            question_list = Questions.objects.filter(post__category=category)
            reply_list = Replies.objects.filter(question__post__category=category)
        else:
            post_list = Posts.objects.all()
            question_list = Questions.objects.all()
            reply_list = Replies.objects.all()
        params = {
            "post_list": [],
            "category": category_list
        }

        for p in post_list:
            post_info = {
                "post_id": p.id,
                "user_id": p.user.user_id,
                "user_name": p.user.username,
                "user_image_url": p.user.image_url,
                "post_text": p.text,
                "category": p.category,
                "comment_cnt": p.comment_cnt,
                "created_at": p.created_at,
            }
            params["post_list"].append(post_info)

        params["post_list"] = sorted(params["post_list"], key=lambda x:x["created_at"], reverse=True)

        question_dict = {}
        for q in question_list:
            question_info = {
                "question_id": q.id,
                "post_id": q.post.id,
                "user_id": q.user.user_id,
                "user_name": q.user.username,
                "user_image_url": q.user.image_url,
                "text": q.text,
                "created_at": q.created_at
            }
            post_id = q.post.id
            if post_id not in question_dict.keys():
                question_dict[post_id] = [question_info]
            else:
                question_dict[post_id].append(question_info)

        reply_dict = {}
        for r in reply_list:
            reply_info = {
                "reply_id": r.id,
                "question_id": r.question.id,
                "user_id": r.user.user_id,
                "user_name": r.user.username,
                "user_image_url": r.user.image_url,
                "text": r.text,
                "created_at": r.created_at
            }
            question_id = r.question.id
            if question_id not in reply_dict.keys():
                reply_dict[question_id] = [reply_info]
            else:
                reply_dict[question_id].append(reply_info)

        for i in range(len(params["post_list"])):
            if (post_id := params["post_list"][i]["post_id"]) not in question_dict.keys():
                q_list = []
            else:
                q_list = question_dict[post_id]
                q_list = sorted(q_list, key=lambda x:x["created_at"])
            params["post_list"][i]["question_list"] = q_list

            for j in range(len(q_list)):
                if (question_id := q_list[j]["question_id"]) not in reply_dict.keys():
                    r_list = []
                else:
                    r_list = reply_dict[question_id]
                    r_list = sorted(r_list, key=lambda x:x["created_at"])
                params["post_list"][i]["question_list"][j]["reply_list"] = r_list

        json_str = json.dumps(params, default=json_serial, ensure_ascii=False, indent=2) 
        return HttpResponse(json_str, content_type="application/json", status=status.HTTP_200_OK)

    
    def post(self, request):
        
        text = request.data.get("text", None)
        category = request.GET.get('category', "その他")
        
        is_valid, result = get_user_id(request)
        if not is_valid:
            return HttpResponse(result, status=status.HTTP_401_UNAUTHORIZED)
        user = CustomUser.objects.filter(id=result).first()
        
        if user is None:
            return HttpResponse("User not found", status=status.HTTP_404_NOT_FOUND)

        if text is None:
            return HttpResponse("Invalid parameters", status=status.HTTP_400_BAD_REQUEST)
        
        Category = Categories.objects.filter(workspace=user.workspace).values_list('category_name')
        category_list = [x[0] for x in list(Category)]
        if category not in category_list:
            return HttpResponse("Invalid category", status=status.HTTP_400_BAD_REQUEST)
        

        Posts.objects.create(user=user, category=category, text=text)

        return HttpResponse("Post created", status=status.HTTP_201_CREATED)

class QUESTIONS(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request, post_id):
        question_list = Questions.objects.all()
        for q in question_list:
            print(f"id:{q.id}, post_id:{q.post.id}, text:{q.text}, crested_at:{q.created_at}")

        return HttpResponse("got it!!!")

    def post(self, request, post_id):
        
        question_text = request.data.get("text", None)

        if question_text is None:
            return HttpResponse("Invalid parameters", status=status.HTTP_400_BAD_REQUEST)

        is_valid, result = get_user_id(request)
        
        if not is_valid:
            return HttpResponse(result, status=status.HTTP_401_UNAUTHORIZED)
        
        user = CustomUser.objects.filter(id=result).first()
        post = Posts.objects.filter(id=post_id).first()
        
        if not user or not post:
            return HttpResponse("User or Post not found", status=status.HTTP_404_NOT_FOUND)


        Questions.objects.create(
            post=post,
            user=user,
            text=question_text
        )
        
        channel_id = post.user.channel_id
        text_shorten = post.text[:20] + "..." if len(post.text) > 20 else post.text

        client = get_client(post.user)
        

        client.chat_postMessage(
            channel=channel_id,
            blocks= [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"<@{user.user_id}> さんから質問が来ました。 \nあなたの投稿：\n{text_shorten}\n返信：\n{question_text}"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "GMO 2ch はこちらから:point_right:"
                    },
                    "accessory": {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "サイトへ",
                            "emoji": True
                        },
                        "value": "click_me",
                        "url": "http://118.27.24.255/",
                        "action_id": "button-action"
                    }
                }
            ],
        )
            
        return HttpResponse("got it!!!")

class REPLIES(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request, post_id, question_id):
        relies_list = Replies.objects.all()
        for r in relies_list:
            print(f"id:{r.id}, question_id:{r.question.id}, text:{r.text}, created_at:{r.created_at}")

        return HttpResponse("got it!!!")


    def post(self, request, post_id, question_id):
        
        request_data = request.data
        reply_text = request_data.get("text", None)
        
        is_valid, result = get_user_id(request)
        
        if not is_valid:
            return HttpResponse(result, status=status.HTTP_401_UNAUTHORIZED)
        

        user = CustomUser.objects.filter(id=result).first()
        
        question = Questions.objects.filter(id=question_id).first()

        Replies.objects.create(
            question=question,
            user=user, 
            text=reply_text)
        
        channel_id = question.user.channel_id
        text_shorten = question.text[:20] + "..." if len(question.text) > 20 else question.text

        client = get_client(question.user)

        if user != question.user:
            client.chat_postMessage(
                channel=channel_id,
                blocks= [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"<@{user.user_id}> さんから返信が来ました。\nあなたの投稿：\n{text_shorten}\n返信：\n{reply_text}"
                        }
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "GMO 2ch はこちらから:point_right:"
                        },
                        "accessory": {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "サイトへ",
                                "emoji": True
                            },
                            "value": "click_me",
                            "url": "http://118.27.24.255/",
                            "action_id": "button-action"
                        }
                    }
                ]
            )
            
        thread_users = get_thread_user(question, user)
        for r_user in thread_users:
            channel_id = r_user.channel_id
            client.chat_postMessage(
                channel=channel_id,
                blocks= [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"<@{user.user_id}> さんから返信が来ました。\nあなたが参加した会話：\n{text_shorten}"
                        }
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "GMO 2ch はこちらから:point_right:"
                        },
                        "accessory": {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "サイトへ",
                                "emoji": True
                            },
                            "value": "click_me",
                            "url": "http://118.27.24.255/",
                            "action_id": "button-action"
                        }
                    }
                ],
            )
        
        return HttpResponse("got it!!!!!")
    
class CATERGOORIES(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request_data = request.data
        category_name = request_data.get("text", None)
        
        is_valid, result = get_user_id(request)
        if not is_valid:
            return HttpResponse(result, status=status.HTTP_401_UNAUTHORIZED)
        user = CustomUser.objects.filter(id=result).first()

        if user.is_owner == False:
            return HttpResponse("Insufficient User Permissions", status=status.HTTP_401_UNAUTHORIZED)
        
        workspace = user.workspace

        try:
            Categories.objects.create(
                category_name=category_name,
                workspace=workspace
            )
            return Response({"message": "category saved successfully"}, status=status.HTTP_200_OK)

        except Exception as e:
            self.logger.error("Error creating conversation: {}".format(e))
            
            return Response({"error": "Error creating conversation: {}".format(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
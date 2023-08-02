from rest_framework.views import APIView
from django.http import HttpResponse
from datetime import datetime
import json
import pytz

from posts.models import dbposts, dbquestions, dbreplies
from authentication.models import CustomUser, Workspace

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

import logging

class POSTS(APIView):
    #authentication_classes = [JWTAuthentication]
    #permission_classes = [IsAuthenticated]
    
    def get(self, rquest):
        print("実行！！")

        post_list = dbposts.objects.all()
        # question_list = dbquestions.objects.all()
        # reply_list = dbreplies.objects.all()

        return HttpResponse("got it!!")

    def post(self, request):
        request_data = request.data
        user_id = request_data.get("user_id", None)
        text = request_data.get("text", None)
        
        dbposts.objects.create(user_id=user_id, text=text, comment_cnt=0, created_at=datetime.now(pytz.timezone('Asia/Tokyo')))
        
        return HttpResponse("got it!!")


class QUESTIONS(APIView):
    #authentication_classes = [JWTAuthentication]
    #permission_classes = [IsAuthenticated]
    
    def get(self, request, post_id):
        question_list = dbquestions.objects.all()
        for q in question_list:
            print(f"id:{q.id}, post_id:{q.post_id}, text:{q.text}, crested_at:{q.created_at}")

        return HttpResponse("got it!!!")

    def post(self, request, post_id):
        print(post_id)
        body = json.loads(request.body)
        question_text = body["text"]
        print(question_text)

        dbquestions.objects.create(post_id=post_id, text=question_text, created_at=datetime.now(pytz.timezone('Asia/Tokyo')))
        
        post = dbposts.objects.filter(id=post_id).first()
        
        user_post = CustomUser.objects.filter(user_id=post.user_id).first()
        channel_id = user_post.channel_id
        text_shorten = post.text[:20] + "..." if len(post.text) > 20 else post.text
        
        Workspace_id = user_post.workspace_id
        Workspace_token = Workspace.objects.filter(workspace_id=Workspace_id)[0].workspace_token
        
        self.client = WebClient(token=Workspace_token)
        self.logger = logging.getLogger(__name__)
        
        self.client.chat_postMessage(channel=channel_id, text="xxxさんから質問が来ました！\nあなたの投稿：" + text_shorten + "\n質問：" + question_text)
        
        return HttpResponse("got it!!!")

class REPLIES(APIView):
    #authentication_classes = [JWTAuthentication]
    #permission_classes = [IsAuthenticated]
    
    def post(self, request, post_id, question_id):
        reply_text = request.text

        dbreplies.objects.create(question_id=question_id, text=reply_text,
                                 created_at=datetime.now())

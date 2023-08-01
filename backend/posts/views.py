from rest_framework.views import APIView
from django.http import HttpResponse
from datetime import datetime
import json
import pytz

from posts.models import dbposts, dbquestions, dbreplies

class POSTS(APIView):
    def get(self, rquest):
        print("実行！！")

        post_list = dbposts.objects.all()
        # question_list = dbquestions.objects.all()
        # reply_list = dbreplies.objects.all()

        return HttpResponse("got it!!")

    def post(self, request):
        print("頑張って")
        dbposts.objects.create(user_id="hogehoge", text="今日も楽しかった", comment_cnt=0, created_at=datetime.now(pytz.timezone('Asia/Tokyo')))
        print("できたよ")
        return HttpResponse("got it!!")


class QUESTIONS(APIView):
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
        return HttpResponse("got it!!!")

class REPLIES(APIView):
    def post(self, request, post_id, question_id):
        reply_text = request.text

        dbreplies.objects.create(question_id=question_id, text=reply_text,
                                 created_at=datetime.now())


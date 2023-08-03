from django.contrib import admin

# モデルをインポート
from .models import Posts, Questions, Replies

class PostsAdmin(admin.ModelAdmin):
    list_display = ('id', "user_id", 'text', "comment_cnt", "created_at")

class QuestionsAdmin(admin.ModelAdmin):
    list_display = ('id', "post", 'user', "text", "created_at")

class RepliesAdmin(admin.ModelAdmin):
    list_display = ('id', "user", "question", 'text', "created_at")

# 管理ツールに登録
admin.site.register(Posts, PostsAdmin)
admin.site.register(Questions, QuestionsAdmin)
admin.site.register(Replies, RepliesAdmin)
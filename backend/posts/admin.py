from django.contrib import admin

# モデルをインポート
from .models import dbposts, dbquestions, dbreplies

class PostsAdmin(admin.ModelAdmin):
    list_display = ('id', "user_id", 'text', "comment_cnt", "created_at")

# 管理ツールに登録
admin.site.register(dbposts, PostsAdmin)
admin.site.register(dbquestions)
admin.site.register(dbreplies)
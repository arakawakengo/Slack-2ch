from django.contrib import admin

# モデルをインポート
from .models import CustomUser, Workspace

# 管理ツールに登録
admin.site.register(CustomUser)
admin.site.register(Workspace)
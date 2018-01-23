from django.contrib import admin
from django.db import models as django_models

from . import models


class PostAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}
    list_display = ('title', 'post_date', 'posted_by',
                    'comment_count', 'allow_comments')
    readonly_fields = ('comment_count',)


class CommentAdmin(admin.ModelAdmin):
    list_display = ('user_name', 'user_email', 'ip_address', 'post_date')

admin.site.register(models.Post, PostAdmin)
admin.site.register(models.Comment, CommentAdmin)

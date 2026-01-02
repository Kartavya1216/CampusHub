from django.contrib import admin
from .models import Notice

@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'posted_by',
        'created_at',
        'is_active'
    )

    list_filter = (
        'is_active',
        'created_at'
    )

    search_fields = (
        'title',
        'content'
    )

    ordering = ('-created_at',)

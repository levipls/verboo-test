from django.contrib import admin
from django.utils.html import format_html
from django.utils.text import Truncator
from .models import Feedback

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "email", "franchise", "feedback_type", "message_preview", "created_at")
    list_filter  = ("feedback_type", "franchise", "created_at")
    search_fields = ("name", "email", "franchise", "message")
    fields = ("name", "email", "franchise", "message", "feedback_type", "created_at")
    readonly_fields = ("created_at",)
    list_per_page = 50
    ordering = ("-created_at",)

    @admin.display(description="Message")
    def message_preview(self, obj):
        full = (obj.message or "").strip()
        short = Truncator(full).chars(80)
        return format_html('<span title="{}">{}</span>', full, short)

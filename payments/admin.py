from django.contrib import admin, messages
from django.db.models import Sum
from .models import Payment
from django.contrib.admin.models import LogEntry
from django.urls import path
from django.shortcuts import redirect
from django.utils.html import format_html

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("student_name", "student_class", "session", "term", "parent_email", "amount", "status", "date")
    list_filter = ("student_class", "term", "session", "status")  # ✅ added class & status
    search_fields = ("student_name", "parent_email", "payment_reference")
    ordering = ("-date",)
    list_per_page = 25

    # ✅ Disable admin history logging of deletions (optional)
    def log_deletion(self, request, object, object_repr):
        pass

    # ✅ Show total of successful payments only
    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context=extra_context)
        try:
            qs = response.context_data["cl"].queryset
            # ✅ Filter only successful payments
            total = qs.filter(status="successful").aggregate(total_amount=Sum("amount"))["total_amount"] or 0
            response.context_data["total_amount"] = total
        except (AttributeError, KeyError):
            pass
        return response

# ✅ Custom admin view to clear recent actions
@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    list_display = ("user", "content_type", "object_repr", "action_flag", "action_time")
    readonly_fields = [f.name for f in LogEntry._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return True  # allow deletion if needed


# ✅ Add custom URL to clear logs
def clear_recent_actions(request):
    LogEntry.objects.all().delete()
    messages.success(request, "✅ All recent admin actions have been cleared.")
    return redirect("/admin/")


# ✅ Extend the admin site URLs
admin.site.get_urls = (lambda get_urls: 
    lambda: [path("clear-recent-actions/", clear_recent_actions, name="clear_recent_actions")] + get_urls()
)(admin.site.get_urls)

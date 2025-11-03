from django.contrib import admin
from django.db.models import Sum
from .models import Payment

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

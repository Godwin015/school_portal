from django.contrib import admin
from .models import Payment
from django.db.models import Sum

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("student_name", "student_class", "session", "term", "parent_email", "amount", "status", "date")
    list_filter = ("student_class", "term", "session", "status")  # ✅ added class here
    search_fields = ("student_name", "parent_email", "payment_reference")
    ordering = ("-date",)
    list_per_page = 25

    # ✅ Disable log deletion if you don’t want deleted ones to appear in "Recent actions"
    def log_deletion(self, request, object, object_repr):
        pass  # Removes record from admin history log

    # ✅ Add total sum of amounts at the bottom
    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context=extra_context)
        try:
            qs = response.context_data["cl"].queryset
            total = qs.aggregate(total_amount=Sum("amount"))["total_amount"] or 0
            response.context_data["total_amount"] = total
        except (AttributeError, KeyError):
            pass
        return response

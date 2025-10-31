from django.contrib import admin
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('student_name', 'parent_email', 'amount', 'status', 'payment_reference', 'session', 'term', 'date_created')
    search_fields = ('student_name', 'parent_email', 'payment_reference')
    list_filter = ('status', 'term', 'session')
    ordering = ('-date_created',)

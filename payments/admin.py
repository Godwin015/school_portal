from django.contrib import admin
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        'student_name',
        'parent_email',
        'amount',
        'payment_reference',
        'session',
        'term',
        'date',
    )
    search_fields = ('student_name', 'parent_email', 'payment_reference')
    list_filter = ('term', 'session')
    ordering = ('-date',)

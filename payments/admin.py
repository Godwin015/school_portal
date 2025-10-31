from django.contrib import admin
from django.contrib.admin import AdminSite
from .models import Payment

# 🎓 Custom Admin Branding
class SunshineAdminSite(AdminSite):
    site_header = "Sunshine Academy Administration"
    site_title = "Sunshine Academy Admin Portal"
    index_title = "Welcome to Sunshine Academy Admin Dashboard"

# Create a custom admin site instance
admin_site = SunshineAdminSite(name='sunshine_admin')

# ✅ Register your models here
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('student_name', 'parent_email', 'amount', 'status', 'payment_reference', 'session', 'term', 'date_created')
    search_fields = ('student_name', 'parent_email', 'payment_reference')
    list_filter = ('status', 'term', 'session')
    ordering = ('-date_created',)

# Register model with default admin too
admin.site.register(Payment, PaymentAdmin)

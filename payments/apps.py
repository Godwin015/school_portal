from django.apps import AppConfig

class PaymentsConfig(AppConfig):
    name = 'payments'

    def ready(self):
        from django.contrib import admin
        admin.site.site_header = "Sunshine Academy Administration"
        admin.site.site_title = "Sunshine Admin Portal"
        admin.site.index_title = "Manage School Payments and Records"

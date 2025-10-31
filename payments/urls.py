from django.urls import path
from . import views

urlpatterns = [
    path("pay/", views.pay_fees, name="pay_fees"),  # Show payment form
    path("confirm/", views.payment_confirm, name="payment_confirm"),  # Confirm details
    path("initialize/", views.initialize_payment, name="initialize_payment"),  # Flutterwave init
    path("verify/", views.verify_payment, name="verify_payment"),
    path("receipt/<str:reference>/", views.download_receipt, name="download_receipt"),
    path("about/", views.about, name="about"),
]

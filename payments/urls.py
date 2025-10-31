from django.urls import path
from . import views

urlpatterns = [
    path("pay/", views.pay_fees, name="pay_fees"),  # Step 1: Show and confirm payment
    path("initialize/", views.initialize_payment, name="initialize_payment"),  # Step 2: Process payment
    path("verify/", views.verify_payment, name="verify_payment"),  # Step 3: Verify payment
    path("receipt/<str:reference>/", views.download_receipt, name="download_receipt"),
    path("about/", views.about, name="about"),
]

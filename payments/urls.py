from django.urls import path
from . import views

urlpatterns = [
    path("pay/", views.initialize_payment, name="initialize_payment"),  # start payment via Flutterwave
    path("verify/", views.verify_payment, name="verify_payment"),       # verify callback
    path("receipt/<str:reference>/", views.download_receipt, name="download_receipt"),
    path("about/", views.about, name="about"),
]

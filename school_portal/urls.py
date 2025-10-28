from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),  # ✅ Use your own home view
    path('payments/', include('payments.urls')),  # ✅ Keep this
    path('about/', views.about, name='about'),  # ✅ Works fine now
    path('contact/', views.contact, name='contact'),
]


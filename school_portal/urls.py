from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('payments/', include('payments.urls')),
    path('', include('payments.urls')),
    path('about/', views.about, name='about'),
]




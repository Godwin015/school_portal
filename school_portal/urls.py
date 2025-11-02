from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    path('admin/logout/', auth_views.LogoutView.as_view(template_name='registration/logged_out.html'), name='logout'),
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('payments/', include('payments.urls')),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
]

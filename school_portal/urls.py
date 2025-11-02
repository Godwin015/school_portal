from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    # ✅ Add Jet Dashboard before the admin path
    path('jet/', include('jet.urls', 'jet')),  
    path('jet/dashboard/', include('jet.dashboard.urls', 'jet-dashboard')),

    # ✅ Django Admin (now powered by Jet)
    path('admin/', admin.site.urls),

    # ✅ Your main app routes
    path('', views.home, name='home'),
    path('payments/', include('payments.urls')),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
]





from django.contrib import admin
from django.urls import path
from . import views  # Import your views here

# Here, you define all your URLs
urlpatterns = [
    path('admin/', admin.site.urls),  # Admin URL
    path('simple_optimization/', views.SimpleOptimization.as_view(), name='simple_optimization'),
    path('bi_objective_optimization/', views.BiObjectiveOptimization.as_view(), name='bi_objective_optimization'),
    path('dynamic_optimization/', views.DynamicOptimization.as_view(), name='dynamic_optimization'),
    
    # Add more URL patterns here as needed for your project.
]

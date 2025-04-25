# urls.py

from django.urls import path
from .views import (
    SimpleOptimization,
    BiObjectiveOptimization,
    DynamicOptimization,
    TransformXLSX
)

urlpatterns = [
    path('simple-optimization/', SimpleOptimization.as_view(), name='simple_optimization'),
    path('bi-objective-optimization/', BiObjectiveOptimization.as_view(), name='bi_objective_optimization'),
    path('dynamic-optimization/', DynamicOptimization.as_view(), name='dynamic_optimization'),
    path('transform-xlsx/', TransformXLSX.as_view(), name='transform_xlsx'),
]

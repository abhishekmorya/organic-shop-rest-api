from django.urls import path, include
from rest_framework import routers
from rest_framework.routers import DefaultRouter
from product import views

app_name = 'product'

router = DefaultRouter()
router.register('category', views.CategoryView)
router.register('product', views.ProductView)

urlpatterns = [
    path('greet', views.greet),
    path('', include(router.urls)),
]
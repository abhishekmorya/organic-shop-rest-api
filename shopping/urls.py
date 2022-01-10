from rest_framework.routers import DefaultRouter
from django.urls import path, include

from shopping import views

app_name = 'shopping'

router = DefaultRouter()
router.register('shopping', views.ShoppingView, base_name=app_name)

urlpatterns = [
    path('', include(router.urls)),
]
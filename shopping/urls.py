from rest_framework.routers import DefaultRouter
from django.urls import path, include

from shopping import views

app_name = 'shopping'

router = DefaultRouter()
router.register('shopping', viewset = views.ShoppingView, base_name=app_name)
router.register('aUser', viewset=views.SessionShoppingView, base_name='aUser')

urlpatterns = [
    path('', include(router.urls)),
]
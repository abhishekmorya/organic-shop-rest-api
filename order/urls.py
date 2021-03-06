from rest_framework.routers import DefaultRouter
from django.urls import path, include

from order import views

app_name = 'order'

router = DefaultRouter()

router.register('paymentmode', views.PaymentModeView)
router.register('order', views.OrderView)

urlpatterns = [
    path('', include(router.urls)),
]
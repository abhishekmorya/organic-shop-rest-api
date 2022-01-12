from django.urls import include, path
from rest_framework.routers import DefaultRouter

from offers import views

app_name = 'offers'
router = DefaultRouter()

router.register('offers', views.OfferView, base_name=app_name)

urlpatterns = [
    path('', include(router.urls))
]

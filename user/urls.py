from django.urls import path, include
from rest_framework.routers import DefaultRouter

from user import views
app_name = 'user'

router = DefaultRouter()
router.register('address', views.UserAddressView, base_name='address')
router.register('user-details', views.UserDetailsView, base_name='user-details')

urlpatterns = [
    path('create/', views.CreateUserView.as_view(), name = 'create'),
    path('token/', views.UserTokenView.as_view(), name = 'token'),
    path('me/', views.RetrieveUpdateUserView().as_view(), name = 'me'),
    path('', include(router.urls), name = 'address'),
]
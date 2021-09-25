from django.urls import path

from user import views
app_name = 'user'

urlpatterns = [
    path('create/', views.CreateUserView.as_view(), name = 'create'),
    path('token/', views.UserTokenView.as_view(), name = 'token'),
    path('me/', views.RetrieveUpdateUserView().as_view(), name = 'me')
]
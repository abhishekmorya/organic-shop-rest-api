from django.urls import path
from product import views

urlpatterns = [
    path('greet', views.greet),
    path('category', views.CategoryView.as_view()),
]
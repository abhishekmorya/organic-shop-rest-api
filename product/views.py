from django.http import HttpResponse, JsonResponse

from rest_framework import views, viewsets
from core import models


# Create your views here.

def greet(request):
    """Greet message"""
    return HttpResponse("Hello!")


class CategoryView(views.View):
    """Category by View"""
    model = models.Category
    def get(self, request):
        """Get method"""
        queryset = self.model.objects.all()
        # return JsonResponse({'greet': 'hello!'})
        return queryset
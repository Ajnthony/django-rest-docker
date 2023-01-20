"""
url mappings for recipe app
"""

from django.urls import (
    path,
    include,
)
from rest_framework.routers import DefaultRouter
from recipe import views

router = DefaultRouter()

# create routes for default http requests
router.register('recipes', views.RecipeViewSet)
router.register('tags', views.TagViewSet)
router.register('ingredients', views.IngredientViewSet)

app_name = 'recipe'

urlpatterns = [
    path('', include(router.urls))
]

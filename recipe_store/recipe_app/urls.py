from django.urls import path, include
from rest_framework.routers import DefaultRouter

from recipe_app import views

# create a DefaultRouter - automatically generates multiple urls for ViewSets

router = DefaultRouter()
router.register('tags', views.TagViewSet)  # Register TagViewSetas tags with router
router.register('ingredients', views.IngredientViewSet)

app_name = 'recipe_app'

urlpatterns = [
    path('', include(router.urls))
]

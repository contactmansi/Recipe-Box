from rest_framework import serializers
from core.models import Tag, Ingredient, Recipe

# Create a ModelSerializer link this to our model Tag


class TagSerializer(serializers.ModelSerializer):
    """Serializer for Tag objects"""
    class Meta:
        model = Tag
        fields = ('id', 'name')
        read_only_fields = ('id',)


class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for Ingredient Objects"""
    class Meta:
        model = Ingredient
        fields = ('id', 'name',)
        read_only_fields = ('id',)


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for Recipe objects"""
    # Define the PK related fields within our fields for recipe
    # Lists the ingreditents with PK ID and not all details only id
    ingredients = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Ingredient.objects.all()
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all()
    )

    class Meta:
        model = Recipe
        fields = ('id', 'title', 'ingredients', 'tags', 'time_minutes', 'price', 'link',)
        read_only_fields = ('id',)

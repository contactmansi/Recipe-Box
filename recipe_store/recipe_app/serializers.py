from rest_framework import serializers
from core.models import Tag

# Create a ModelSerializer link this to our model Tag


class TagSerializer(serializers.ModelSerializer):
    """Serializer for Tag objects"""
    class Meta:
        model = Tag
        fields = ('id', 'name')
        read_only_fields = ('id',)

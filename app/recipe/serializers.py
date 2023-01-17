"""
serializers for recipe apis
"""

from rest_framework import serializers
from core.models import Recipe


class RecipeSerializer(serializers.ModelSerializer):
    # serializer for recipes

    class Meta:
        model = Recipe
        fields = ['id', 'title', 'time_minutes', 'price', 'link']
        read_only_fields = ['id']


# it seems that
# this class is simply the extend of RecipeSerializer above
# hence basing off RecipeSerializer.
# Meta here as well
class RecipeDetailSerializer(RecipeSerializer):
    # serializer for recipe detail view

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description']

"""
serializers for recipe apis
"""

from rest_framework import serializers
from core.models import (
    Recipe,
    Tag,
    Ingredient
)


class IngredientSerializer(serializers.ModelSerializer):
    # serializer for ingredients

    class Meta:
        model = Ingredient
        fields = ['id', 'name']
        read_only_fields = ['id']


class TagSerializer(serializers.ModelSerializer):
    # serializer for tags

    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']


class RecipeSerializer(serializers.ModelSerializer):
    # serializer for recipes

    # nesting TagSerializer iside RecipeSerializer
    # 'tags' will be a list field under recipe object
    # nested serializers are read-only by default
    # but it's possible to override it
    tags = TagSerializer(many=True, required=False)
    ingredients = IngredientSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        fields = ['id', 'title', 'time_minutes',
                  'price', 'link', 'tags', 'ingredients']
        read_only_fields = ['id']

    # starting a method name with underscore
    # seems to be indicating that
    # this is a private method
    # so it shouldn't be called (used)
    # anywhere outside this class
    # it's possible anyway, technically,
    # but not recommended
    def _get_or_create_tags(self, tags, recipe):
        # handle getting or creating tags as needed

        auth_user = self.context['request'].user
        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(
                user=auth_user,
                **tag,
            )
            recipe.tags.add(tag_obj)

    def _get_or_create_ingredients(self, ingredients, recipe):
        # handle getting or creating ingredients as needed

        auth_user = self.context['request'].user
        for ing in ingredients:
            ing_obj, created = Ingredient.objects.get_or_create(
                user=auth_user,
                **ing
            )
            recipe.ingredients.add(ing_obj)

    def create(self, validated_data):
        # create a recipe

        # remove the tags list from recipe object
        # and assigning it to a variable called 'tags'
        # the 2nd arg [] is a default value
        # if len(recipe.tags) == 0
        # if I do the following instead:
        #   tags = validated_data.get('tags', [])
        # it would still do the same job
        # except the tags list will still be inside recipe obj
        tags = validated_data.pop('tags', [])
        ingredients = validated_data.pop('ingredients', [])
        recipe = Recipe.objects.create(**validated_data)
        self._get_or_create_tags(tags, recipe)
        self._get_or_create_ingredients(ingredients, recipe)

        return recipe

    # instance means which one I'm updating
    def update(self, instance, validated_data):
        # update recipe

        tags = validated_data.pop('tags', None)
        ingredients = validated_data.pop('ingredients', None)

        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags, instance)

        if ingredients is not None:
            instance.ingredients.clear()
            self._get_or_create_ingredients(ingredients, instance)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


# it seems that
# this class is simply the extend of RecipeSerializer above
# hence basing off RecipeSerializer.
# Meta here as well
class RecipeDetailSerializer(RecipeSerializer):
    # serializer for recipe detail view

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description', 'image']


class RecipeImageSerializer(serializers.ModelSerializer):
    # serializer for uploading images for recipes.

    class Meta:
        model = Recipe
        fields = ['id', 'image']
        read_only_fields = ['id']
        extra_kwargs = {'image': {'required': 'True'}}

"""
views for recipe api
"""

from rest_framework import (
    viewsets,
    mixins,
    status,
)
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from core.models import (
    Recipe,
    Tag,
    Ingredient,
)
from recipe import serializers


class RecipeViewSet(viewsets.ModelViewSet):
    # view for managing recipe api

    serializer_class = serializers.RecipeDetailSerializer
    queryset = Recipe.objects.all()

    # the following two lines
    # will require the user to be authenticated
    # in order to interact with recipe api
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # override get_queryset
        # retrieve recipes for authenticated user

        return self.queryset.filter(user=self.request.user).order_by('-id')

    def get_serializer_class(self):
        # return the serializer class for request

        if self.action == 'list':
            # notice there's no () at the end
            # ...RecipeSerializer()
            return serializers.RecipeSerializer
        elif self.action == 'upload_image':
            return serializers.RecipeImageSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        # create a new recipe

        serializer.save(user=self.request.user)

    # detail would be equal to recipe id
    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        # upload an image to recipe

        recipe = self.get_object()
        serializer = self.get_serializer(recipe, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BaseRecipeAttrViewSet(mixins.DestroyModelMixin,
                            mixins.UpdateModelMixin,
                            mixins.ListModelMixin,
                            viewsets.GenericViewSet):
    # base viewset for recipe attributes

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # filter queryset to authenticated user

        return self.queryset.filter(user=self.request.user).order_by('-name')


# DestroyModelMixin handles deletion of tags
# UpdateModelMixin handls update of tags
class TagViewSet(BaseRecipeAttrViewSet):
    # manage tags in the db

    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()


class IngredientViewSet(BaseRecipeAttrViewSet):
    # manage ingredients in the database

    serializer_class = serializers.IngredientSerializer
    queryset = Ingredient.objects.all()

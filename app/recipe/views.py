from django.shortcuts import render
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets,mixins,status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
# Create your views here.
from core.models import Tag,Ingredient,Recipe

from . import serializers

class BaseRecipeAttrViewSet(viewsets.GenericViewSet,
                            mixins.ListModelMixin,
                            mixins.CreateModelMixin):
    """Base viewset for user owned recipe attributes"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Return objects for the current authenticated user only"""
        assigned_only = bool(
            int(self.request.query_params.get('assigned_only', 0))
        )
        queryset = self.queryset
        if assigned_only:
            queryset = queryset.filter(recipe__isnull=False)

        return queryset.filter(
            user=self.request.user
        ).order_by('-name').distinct()

    def perform_create(self, serializer):
        """Create a new object"""
        serializer.save(user=self.request.user)


class TagViewSet(viewsets.GenericViewSet,mixins.ListModelMixin,mixins.CreateModelMixin):
    """Manage tags in the database"""
    authentication_classes = TokenAuthentication,
    permission_classes = IsAuthenticated,
    queryset = Tag.objects.all()
    serializer_class = serializers.SerializerTag

    def get_queryset(self):
        """Return objects for the current aUthenticated users only!"""
        return self.queryset.filter(user=self.request.user).order_by('-name')

    def perform_create(self, serializer):
        """Create a new tag"""
        serializer.save(user=self.request.user)

class IngredientViewset(viewsets.GenericViewSet,mixins.ListModelMixin,mixins.CreateModelMixin):
    """Manage ingredient in the database"""
    authentication_classes = TokenAuthentication,
    permission_classes = IsAuthenticated,
    queryset = Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer

    def get_queryset(self):
        """Return objects for the current authenticated users"""
        return self.queryset.filter(user=self.request.user).order_by('-name')

    def perform_create(self, serializer):
        """Create a new ingredient"""
        serializer.save(user=self.request.user)



class RecipeViewSet(viewsets.ModelViewSet):
    """Manage recipes in the database"""
    serializer_class = serializers.RecipeSerializer
    queryset = Recipe.objects.all()
    authentication_classes = TokenAuthentication,
    permission_classes = IsAuthenticated,
    def _params_to_int(self,qs):

        return [int(str_id) for str_id in qs.split(',')]


    def get_queryset(self):
        """Retrieve the recipe for the authenticated user"""
        tags = self.request.query_params.get('tags')
        ingredients = self.request.query_params.get('ingredients')
        queryset = self.queryset
        if tags:
            tags_ids = self._params_to_int(tags)
            queryset = queryset.filter(tags__id__in=tag_ids)
        if ingredients:
            ingredients_ids = self._params_to_int(ingredients)
            queryset = queryset.filter(tags__id__in=ingredients_ids)
        return self.queryset.filter(user = self.request.user)

    def get_serializer_class(self):
        """Return appropriate serializer class"""
        if self.action =='retrieve':
            return serializers.RecipeDetailSerializer
        elif self.action=='upload_image':
            return serializers.RecipeImageSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        """ Create a new recipe"""
        serializer.save(user=self.request.user)


    @action(methods=['POST'],detail=True,url_path='upload_image')
    def upload_image(self,request,pk=None):
        """Upload an image to a recipe"""
        recipe = self.get_object()
        serializer = self.get_serializer(
            recipe,
            data=request.data
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_200_OK

            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

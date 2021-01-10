from django.shortcuts import render
from rest_framework import viewsets,mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
# Create your views here.
from core.models import Tag,Ingredient,Recipe

from . import serializers

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

    def get_queryset(self):
        """Retrieve the recipe for the authenticated user"""
        return self.queryset.filter(user = self.request.user)

    def get_serializer_class(self):
        """Return appropriate serializer class"""
        if self.action =='retrieve':
            return serializers.RecipeDetailSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """ Create a new recipe"""
        serializer.save(user=self.request.user)

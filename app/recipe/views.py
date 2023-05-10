"""
Views for Recipe APIs.
"""
from rest_framework import (
    viewsets,
    mixins,
    status,
)
from rest_framework.decorators import action
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import HttpRequest
from rest_framework.response import Response

from core.models import (
    Recipe,
    Tag,
    Ingredient,
)
from recipe import serializers


class RecipeViewSet(viewsets.ModelViewSet):
    """ViewSet for Recipe app."""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Recipe.objects.all()
    serializer_class = serializers.RecipeDetailSerializer

    def get_queryset(self):
        """Return objects for the current authenticated user only."""
        return self.queryset.filter(user=self.request.user).order_by('-id')

    def get_serializer_class(self):
        """Return appropriate serializer class."""
        if self.action == 'list':
            return serializers.RecipeSerializer
        elif self.action == 'upload_image':
            return serializers.RecipeImageSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new recipe."""
        serializer.save(user=self.request.user)

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request: HttpRequest, pk=None):
        """Upload an image to a recipe."""
        recipe = self.get_object()
        serializer = self.get_serializer(recipe, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BaseRecipeAttrViewSet(
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    """Base ViewSet for recipe attributes."""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user).order_by('-name')


class TagViewSet(BaseRecipeAttrViewSet):
    """ViewSet for tags."""
    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()

    def _instance_exists(
        self,
        request: HttpRequest,
        serializer: serializers.TagSerializer
    ) -> bool:
        """Check if the instance exists."""
        serializer.is_valid(raise_exception=True)
        tag = serializer.validated_data
        return Tag.objects.filter(
            user=request.user,
            name__iexact=tag['name']
        ).exists()

    def create(self, request: HttpRequest, *args, **kwargs):
        """Create a new tag."""
        serializer = self.get_serializer(data=request.data)
        tag_exists = self._instance_exists(request, serializer)
        if not tag_exists:
            serializer.save(user=self.request.user)
            return Response(
                {'message': 'Tag created successfully'},
                status=status.HTTP_201_CREATED
            )

        return Response(
            {'message': 'Tag already exists'},
            status=status.HTTP_400_BAD_REQUEST
        )

    def update(self, request: HttpRequest, *args, **kwargs):
        """Update a new tag."""
        instance = self.get_object()
        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=True
        )
        tag_exists = self._instance_exists(request, serializer)
        if not tag_exists:
            serializer.save()
            return Response(
                {'message': 'Tag updated successfully'},
                status=status.HTTP_200_OK
            )

        return Response(
            {'message': 'Tag with the same name already exists'},
            status=status.HTTP_400_BAD_REQUEST
        )

    def destroy(self, request, *args, **kwargs):
        """Delete a tag."""
        instance: Tag = self.get_object()
        instance.delete()
        return Response(
            {'message': 'Tag deleted successfully'},
            status=status.HTTP_204_NO_CONTENT
        )


class IngredientViewSet(BaseRecipeAttrViewSet):
    """ViewSet for ingredients"""
    serializer_class = serializers.IngredientSerializer
    queryset = Ingredient.objects.all()

    def _instance_exists(
        self,
        request: HttpRequest,
        serializer: serializers.IngredientSerializer
    ) -> bool:
        """Check if the instance exists."""
        serializer.is_valid(raise_exception=True)
        tag = serializer.validated_data
        return Ingredient.objects.filter(
            user=request.user,
            name__iexact=tag['name']
        ).exists()

    def create(self, request: HttpRequest, *args, **kwargs):
        """Create a new ingredient."""
        serializer = self.get_serializer(data=request.data)
        ingredient_exists = self._instance_exists(request, serializer)
        if not ingredient_exists:
            serializer.save(user=self.request.user)
            return Response(
                {'message': 'Ingredient created successfully'},
                status=status.HTTP_201_CREATED
            )

        return Response(
            {'message': 'Ingredient already exists'},
            status=status.HTTP_400_BAD_REQUEST
        )

    def update(self, request: HttpRequest, *args, **kwargs):
        """Update a new ingredient."""
        instance = self.get_object()
        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=True
        )
        ingredient_exists = self._instance_exists(request, serializer)
        if not ingredient_exists:
            serializer.save()
            return Response(
                {'message': 'Ingredient updated successfully'},
                status=status.HTTP_200_OK
            )

        return Response(
            {'message': 'Ingredient with the same name already exists'},
            status=status.HTTP_400_BAD_REQUEST
        )

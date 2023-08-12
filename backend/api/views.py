from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet

from api.filters import IngredientFilter, RecipeFilter
from api.pagination import LimitPageNumberPagination
from api.permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly
from api.serializers import (IngredientSerializer,
                             FavoriteOrSubscribeSerializer,
                             RecipeSerializer, SubscribeSerializer,
                             TagSerializer, UserSerializer,
                             UserPasswordSerializer)
from core import constants
from recipes.models import (FavoriteRecipe, Ingredient, RecipeList,
                            ShoppingCart, Tag)
from users.models import Subscribe


User = get_user_model()


class SetPasswordView(APIView):
    def post(self, request):
        """ Изменить пароль. """
        serializer = UserPasswordSerializer(
            data=request.data,
            context={'request': request},
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {'message': 'Пароль изменен!'},
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {'error': 'Введите верные данные!'},
            status=status.HTTP_400_BAD_REQUEST,
        )


class UserViewSet(DjoserUserViewSet):
    """ Класс Пользователи и подписки. """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter,)
    search_fields = ('username', 'email')
    permission_classes = (AllowAny,)

    @action(methods=['POST', 'DELETE'], detail=True,)
    def subscribe(self, request, id):
        """ функция подписки и отписки. """
        author = get_object_or_404(User, id=id)
        if request.method == 'POST':
            if request.user.id == author.id:
                raise ValueError('Нельзя подписаться на себя самого')
            serializer = SubscribeSerializer(
                Subscribe.objects.create(user=request.user,
                                         author=author),
                context={'request': request})
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            if Subscribe.objects.filter(user=request.user,
                                        author=author
                                        ).exists():
                Subscribe.objects.filter(user=request.user,
                                         author=author
                                         ).delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'errors': 'Нельзя отписаться от автора, '
                 'на которго вы не подписаны!'},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(methods=['GET'],
            detail=False,
            permission_classes=(IsAuthenticated, )
            )
    def subscriptions(self, request):
        """ Получить на кого пользователь подписан. """
        serializer = SubscribeSerializer(
            self.paginate_queryset(Subscribe.objects.filter(
                                   user=request.user)),
            many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)


class IngredientsViewSet(ReadOnlyModelViewSet):
    """ Список ингридиентов. """
    queryset = Ingredient.objects.all()
    permission_classes = (IsAdminOrReadOnly,)
    serializer_class = IngredientSerializer
    filter_backends = (IngredientFilter,)
    search_fields = ('^name',)
    pagination_class = None


class TagsViewSet(ReadOnlyModelViewSet):
    """ Список тэгов. """
    queryset = Tag.objects.all()
    permission_classes = (IsAdminOrReadOnly,)
    serializer_class = TagSerializer
    pagination_class = None


class RecipesViewSet(viewsets.ModelViewSet):
    """ Список рецептов. """
    queryset = RecipeList.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = LimitPageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_classes = (IsAuthorOrReadOnly, )

    def perform_create(self, serializer):
        serializer.save(author=self.request.user,)

    def new_favorite_or_cart(self, model, user, pk):
        recipe = get_object_or_404(RecipeList, id=pk)
        model.objects.create(user=user, recipe=recipe)
        serializer = FavoriteOrSubscribeSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def remove_favorite_or_cart(self, model, user, pk):
        obj = model.objects.filter(user=user, recipe__id=pk)
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'errors': 'Рецепт уже удален!'},
                        status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['POST', 'DELETE'],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        """ Добавить рецепт в избранное или удалить из него. """
        if request.method == 'POST':
            return self.new_favorite_or_cart(FavoriteRecipe,
                                             request.user, pk)
        return self.remove_favorite_or_cart(FavoriteRecipe,
                                            request.user, pk)

    @action(detail=True, methods=['POST', 'DELETE'],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        """ Добавить рецепт в список покупок или удалить из него. """
        if request.method == 'POST':
            return self.new_favorite_or_cart(ShoppingCart, request.user, pk)
        return self.remove_favorite_or_cart(ShoppingCart, request.user, pk)

    @action(detail=False, methods=['GET'],
            permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        """ Скачать корзину (список) покупок. """
        shopping_cart = ShoppingCart.objects.filter(user=request.user).all()
        shopping_list = {}
        for item in shopping_cart:
            for recipe_ingredient in item.recipe.recipe_ingredients.all():
                name = recipe_ingredient.ingredient.name
                measuring_unit = recipe_ingredient.ingredient.measurement_unit
                amount = recipe_ingredient.amount
                if name not in shopping_list:
                    shopping_list[name] = {
                        'name': name,
                        'measurement_unit': measuring_unit,
                        'amount': amount
                    }
                else:
                    shopping_list[name]['amount'] += amount
        content = (
            [f'{item["name"]} ({item["measurement_unit"]}) '
             f'- {item["amount"]}\n'
             for item in shopping_list.values()]
        )
        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = (
            f'attachment; filename={0}'.format(constants.OUTPUT_FILENAME)
        )
        return response

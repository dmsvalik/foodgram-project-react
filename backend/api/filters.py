# backend/api/filters.py
from django_filters import rest_framework as filters
from recipes.models import RecipeList
from rest_framework.filters import SearchFilter


class IngredientFilter(SearchFilter):
    """ Поиск по имени Ингредиента. """
    search_param = 'name'


class RecipeFilter(filters.FilterSet):
    """ Фильтр для рецепта. """
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')
    is_favorited = filters.BooleanFilter(
        field_name='is_favorited',
        method='filter_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        field_name='is_in_shopping_cart',
        method='filter_in_shopping_cart')

    class Meta:
        model = RecipeList
        fields = ('author',)

    def filter_favorited(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(favorites__user=self.request.user)
        return queryset

    def filter_in_shopping_cart(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(shopping_cart__user=self.request.user)
        return queryset

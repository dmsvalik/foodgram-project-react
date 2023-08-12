import base64

from django.core.files.base import ContentFile
from django.http import HttpResponse
from rest_framework import serializers

from core import constants
from recipes.models import ShoppingCart


class Base64ImageField(serializers.ImageField):
    """ Декодируем изображение. """
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


def collect_shopping_cart(request):
    """ Формирование корзины (списка) покупок. """
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

import base64

from core import constants
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.hashers import make_password
from django.core.files.base import ContentFile
from djoser.serializers import UserSerializer as UserHandleSerializer
from recipes.models import Ingredient, IngredientInRecipe, RecipeList, Tag
from rest_framework import serializers, validators
from rest_framework.generics import get_object_or_404
from users.models import Subscribe

User = get_user_model()


class Base64ImageField(serializers.ImageField):
    """ Сериализатор для кодирования и декодирования изображения. """
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class UserSerializer(UserHandleSerializer):
    """ Сериализатор обработки пользователей. """
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'email', 'username',
                  'first_name', 'last_name',
                  'is_subscribed')

    def get_is_subscribed(self, obj):
        """ Проверка подписки. """
        user = self.context.get('request').user
        return not user.is_anonymous and obj.subscribing.filter(
            user=user).exists()


class UserPasswordSerializer(serializers.Serializer):
    """ Сериализатор изменения пароля. """
    new_password = serializers.CharField(
        label='Новый пароль')
    current_password = serializers.CharField(
        label='Текущий пароль')

    def validate_current_password(self, current_password):
        user = self.context['request'].user
        if not authenticate(
                username=user.email,
                password=current_password):
            raise serializers.ValidationError(
                'Не удается войти в систему с '
                'предоставленными учетными данными.',
                code='authorization')
        return current_password

    def validate_new_password(self, new_password):
        validators.validate_password(new_password)
        return new_password

    def create(self, validated_data):
        user = self.context['request'].user
        password = make_password(
            validated_data.get('new_password'))
        user.password = password
        user.save()
        return validated_data


class TagSerializer(serializers.ModelSerializer):
    """ Сериализатор для тега. """
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    """  Сериализатор для ингредиента. """
    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    """ Сериализатор модели IngredientInRecipe. """
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class FavoriteOrSubscribeSerializer(serializers.ModelSerializer):
    """ Сериализатор для избранного или подписок.  """
    image = Base64ImageField()

    class Meta:
        model = RecipeList
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')


class SubscribeSerializer(serializers.ModelSerializer):
    """ Сериализатор для подписчика. """
    id = serializers.IntegerField(source='author.id')
    email = serializers.EmailField(source='author.email')
    username = serializers.CharField(source='author.username')
    first_name = serializers.CharField(source='author.first_name')
    last_name = serializers.CharField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Subscribe
        fields = ('id', 'email', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count',)
        read_only_fields = ('is_subscribed', 'recipes_count',)

    def validate(self, data):
        """ Проверка данных на уровне сериализатора. """
        user_id = data['user_id']
        author_id = data['author_id']
        if user_id == author_id:
            raise serializers.ValidationError({
                'errors': 'Ошибка подписки! Нельзя подписаться на самого себя.'
            })
        if user_id.subscribing.filter(author_id=author_id).exists():
            raise serializers.ValidationError({
                'errors': 'Ошибка подписки! Нельзя подписаться повторно.'
            })
        data['user'] = get_object_or_404(User, id=user_id)
        data['author'] = get_object_or_404(User, id=author_id)
        return data

    def get_is_subscribed(self, obj):
        """ Проверка подписки. """
        return Subscribe.objects.filter(
            user=obj.user, author=obj.author).exists()

    def get_recipes(self, obj):
        """ Получение рецептов автора. """
        request = self.context.get('request')
        recipes_limit = request.GET.get('recipes_limit')
        recipes = RecipeList.objects.filter(author=obj.author)
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]
        serializer = FavoriteOrSubscribeSerializer(recipes, many=True)
        return serializer.data

    def get_recipes_count(self, obj):
        """ Подсчет рецептов автора. """
        return obj.author.recipes.count()


class RecipeSerializer(serializers.ModelSerializer):
    """ Сериализатор рецепта. """
    tags = TagSerializer(
        read_only=True,
        many=True
    )
    image = Base64ImageField()
    author = UserSerializer(
        read_only=True
    )
    cooking_time = serializers.IntegerField()
    ingredients = IngredientInRecipeSerializer(
        many=True, read_only=True,
        source='recipe_ingredients'
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = RecipeList
        fields = ('id', 'tags', 'author', 'ingredients',
                  'name', 'image', 'text', 'cooking_time',
                  'is_favorited', 'is_in_shopping_cart')

    @staticmethod
    def __create_ingredients(recipe, ingredients):
        """ Создание ингредиентов в промежуточной таблице. """
        IngredientInRecipe.objects.bulk_create(
            [IngredientInRecipe(recipe=recipe,
             ingredient_id=ingredient.get('id'),
             amount=ingredient.get('amount'))
             for ingredient in ingredients])

    def create(self, validated_data):
        """ Создание рецепта. """
        image = validated_data.pop('image')
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = RecipeList.objects.create(image=image, **validated_data)
        recipe.tags.set(tags)
        self.__create_ingredients(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        """ Обновление рецепта. """
        instance.tags.clear()
        instance.tags.set(validated_data.pop('tags'))
        IngredientInRecipe.objects.filter(recipe=instance).delete()
        self.__create_ingredients(
            recipe=instance,
            ingredients=validated_data.pop('ingredients')
        )
        super().update(instance, validated_data)
        return instance

    def to_internal_value(self, data):
        ingredients = data.pop('ingredients')
        tags = data.pop('tags')
        data = super().to_internal_value(data)
        data['tags'] = tags
        data['ingredients'] = ingredients
        return data

    def get_is_favorited(self, obj):
        """ Проверка рецепта в списке избранного. """
        user = self.context.get('request').user
        return not user.is_anonymous and obj.favorites.filter(
            user=user).exists()

    def get_is_in_shopping_cart(self, obj):
        """ Проверка рецепта в корзине покупок. """
        user = self.context.get('request').user
        if not user or user.is_anonymous:
            return False
        return obj.shopping_cart.filter(user=user).exists()

    def validate(self, data):
        """ Валидация различных данных на уровне сериализатора. """
        ingredients = data.get('ingredients')
        errors = []
        if not ingredients:
            errors.append('Добавьте минимум один ингредиент для рецепта.')
        added_ingredients = []
        for ingredient in ingredients:
            if int(ingredient['amount']) < constants.MIN_INGREDIENT_AMOUNT:
                errors.append(
                    f'Количество ингредиента с id {ingredient["id"]} должно '
                    f'быть целым и не меньше '
                    f'{constants.MIN_INGREDIENT_AMOUNT}.'
                )
            if ingredient['id'] in added_ingredients:
                errors.append(
                    'Дважды один тот же ингредиент в рецепт поместить нельзя.'
                )
            added_ingredients.append(ingredient['id'])
        cooking_time = data.get('cooking_time')
        if cooking_time < constants.MIN_COOKING_TIME:
            errors.append(
                f'Время приготовления должно быть не меньше '
                f'{constants.MIN_COOKING_TIME} минут(ы).'
            )
        if cooking_time > constants.MAX_COOKING_TIME:
            errors.append(
                f'Время приготовления должно быть не больше '
                f'{constants.MAX_COOKING_TIME} минут(ы).'
            )
        if errors:
            raise serializers.ValidationError({'errors': errors})
        data['ingredients'] = ingredients
        return data

from django.contrib.auth import get_user_model
from django.core import validators
from django.db import models

from core import constants


User = get_user_model()


class Ingredient(models.Model):
    """ Модель Ингредиент. """
    name = models.CharField(
        'Название ингредиента',
        max_length=200,
    )
    measurement_unit = models.CharField(
        'Единица измерения ингредиента',
        max_length=20,
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}.'


class Tag(models.Model):
    """ Модель Тэг. """
    name = models.CharField(
        'Название',
        max_length=60,
        unique=True,
    )
    color = models.CharField(
        'Цвет в HEX',
        max_length=7,
        unique=True,
    )
    slug = models.SlugField(
        'Уникальный слаг',
        max_length=80,
        unique=True,
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'
        ordering = ('-id',)

    def __str__(self):
        return self.name


class RecipeList(models.Model):
    """ Модель Рецепт. """
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта',
        help_text='Выберите автора рецепта'
    )
    name = models.CharField(
        max_length=255,
        verbose_name='Название рецепта',
        help_text='Введите название рецепта',
    )
    image = models.ImageField(
        'Ссылка на картинку на сайте',
        upload_to='static/recipe/',
        blank=True,
        null=True,
    )
    text = models.TextField(
        verbose_name='Описание рецепта',
        help_text='Введите описания рецепта'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientInRecipe',
        related_name='recipe',
        verbose_name='Ингредиенты в рецепте',
        help_text='Выберите ингредиенты рецепта'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тег рецепта',
        help_text='Выберите тег рецепта'
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления в минутах',
        validators=[
            validators.MinValueValidator(
                constants.MIN_COOKING_TIME,
                message=f'Минимальное время приготовления: '
                        f'{constants.MIN_COOKING_TIME} минута!',
            ),
            validators.MaxValueValidator(
                constants.MAX_COOKING_TIME,
                message=f'Максимальное время приготовления: '
                        f'{constants.MAX_COOKING_TIME} минут!',
            )
        ],
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания рецепта',
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name


class IngredientInRecipe(models.Model):
    """ Модель количества ингридиентов в рецепте. """
    recipe = models.ForeignKey(
        RecipeList,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='recipe_ingredients',
    )
    ingredient = models.ForeignKey(
        'Ingredient',
        null=True,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
        related_name='ingredient',
    )
    amount = models.PositiveIntegerField(
        default=constants.MIN_INGREDIENT_AMOUNT,
        validators=(
            validators.MinValueValidator(
                constants.MIN_INGREDIENT_AMOUNT,
                message=(f'Минимальное количество ингредиентов'
                         f'`{constants.MIN_INGREDIENT_AMOUNT}` !')
            ),
        ),
        verbose_name='Количество ингредиентов',
    )

    class Meta:
        verbose_name = 'Количество ингредиентов'
        verbose_name_plural = 'Количество ингредиента'
        ordering = ('-id',)
        constraints = (
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_and_ingredient'),
        )


class RecipeUserList(models.Model):
    """Абстрактная модель между пользователем и рецептом
    для моделей Избранное и Карзина покупок."""
    recipe = models.ForeignKey(
        RecipeList,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )

    class Meta:
        abstract = True
        ordering = ('user', 'recipe')


class FavoriteRecipe(RecipeUserList):
    """ Модель Избранное. """
    class Meta(RecipeUserList.Meta):
        default_related_name = 'favorites'
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
        ordering = ('-id',)
        constraints = (
            models.UniqueConstraint(
                fields=['recipe', 'user'],
                name='unique_favorite_list_user',
            ),
        )

    def __str__(self):
        return (f'Пользователь @{self.user.username} '
                f'добавил {self.recipe} в избранное.')


class ShoppingCart(RecipeUserList):
    """ Модель Карзина покупок. """
    class Meta(RecipeUserList.Meta):
        default_related_name = 'shopping_cart'
        verbose_name = 'Покупка'
        verbose_name_plural = 'Покупки'
        constraints = (
            models.UniqueConstraint(
                fields=['recipe', 'user'],
                name='unique_cart_list_user'
            ),
        )

    def __str__(self):
        return (f'Пользователь {self.user} '
                f'добавил {self.recipe.name} в покупки.')

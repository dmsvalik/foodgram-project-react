# Generated by Django 3.2.19 on 2023-08-17 10:37

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('recipes', '0003_auto_20230808_1705'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='favoriterecipe',
            options={'default_related_name': 'favorites', 'ordering': ('-id',), 'verbose_name': 'избранное', 'verbose_name_plural': 'избранные'},
        ),
        migrations.AlterModelOptions(
            name='ingredient',
            options={'ordering': ('name',), 'verbose_name': 'ингредиент', 'verbose_name_plural': 'Ингредиенты'},
        ),
        migrations.AlterModelOptions(
            name='ingredientinrecipe',
            options={'ordering': ('-id',), 'verbose_name': 'количество ингредиентов', 'verbose_name_plural': 'количество ингредиента'},
        ),
        migrations.AlterModelOptions(
            name='recipelist',
            options={'ordering': ('-pub_date',), 'verbose_name': 'рецепт', 'verbose_name_plural': 'рецепты'},
        ),
        migrations.AlterModelOptions(
            name='shoppingcart',
            options={'default_related_name': 'shopping_cart', 'ordering': ('user', 'recipe'), 'verbose_name': 'покупка', 'verbose_name_plural': 'покупки'},
        ),
        migrations.AlterModelOptions(
            name='tag',
            options={'ordering': ('-id',), 'verbose_name': 'тэг', 'verbose_name_plural': 'тэги'},
        ),
        migrations.AlterField(
            model_name='favoriterecipe',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorites', to=settings.AUTH_USER_MODEL, verbose_name='пользователь'),
        ),
        migrations.AlterField(
            model_name='ingredient',
            name='name',
            field=models.CharField(db_index=True, max_length=200, verbose_name='Название ингредиента'),
        ),
        migrations.AlterField(
            model_name='ingredientinrecipe',
            name='amount',
            field=models.PositiveSmallIntegerField(default=1, validators=[django.core.validators.MinValueValidator(1, message='Минимальное количество ингредиентов`1` !')], verbose_name='Количество ингредиентов'),
        ),
        migrations.AlterField(
            model_name='ingredientinrecipe',
            name='ingredient',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='ingredient', to='recipes.ingredient', verbose_name='ингредиент'),
        ),
        migrations.AlterField(
            model_name='ingredientinrecipe',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipe_ingredients', to='recipes.recipelist', verbose_name='рецепт'),
        ),
        migrations.AlterField(
            model_name='recipelist',
            name='author',
            field=models.ForeignKey(help_text='Выберите автора рецепта', on_delete=django.db.models.deletion.CASCADE, related_name='recipes', to=settings.AUTH_USER_MODEL, verbose_name='автор рецепта'),
        ),
        migrations.AlterField(
            model_name='recipelist',
            name='cooking_time',
            field=models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1, message='Минимальное время приготовления: 1 минута!'), django.core.validators.MaxValueValidator(1000, message='Максимальное время приготовления: 1000 минут!')], verbose_name='время приготовления в минутах'),
        ),
        migrations.AlterField(
            model_name='recipelist',
            name='ingredients',
            field=models.ManyToManyField(help_text='Выберите ингредиенты рецепта', related_name='recipe', through='recipes.IngredientInRecipe', to='recipes.Ingredient', verbose_name='ингредиенты в рецепте'),
        ),
        migrations.AlterField(
            model_name='recipelist',
            name='name',
            field=models.CharField(help_text='Введите название рецепта', max_length=255, verbose_name='название рецепта'),
        ),
        migrations.AlterField(
            model_name='recipelist',
            name='pub_date',
            field=models.DateTimeField(auto_now_add=True, verbose_name='дата создания рецепта'),
        ),
        migrations.AlterField(
            model_name='recipelist',
            name='tags',
            field=models.ManyToManyField(help_text='Выберите тег рецепта', to='recipes.Tag', verbose_name='тег рецепта'),
        ),
        migrations.AlterField(
            model_name='recipelist',
            name='text',
            field=models.TextField(help_text='Введите описания рецепта', verbose_name='описание рецепта'),
        ),
        migrations.AlterField(
            model_name='shoppingcart',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shopping_cart', to=settings.AUTH_USER_MODEL, verbose_name='пользователь'),
        ),
    ]

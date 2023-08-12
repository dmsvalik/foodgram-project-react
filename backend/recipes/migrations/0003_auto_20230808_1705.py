# Generated by Django 3.2.19 on 2023-08-08 14:05

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('recipes', '0002_alter_recipelist_cooking_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredientinrecipe',
            name='amount',
            field=models.PositiveIntegerField(default=1, validators=[django.core.validators.MinValueValidator(1, message='Минимальное количество ингредиентов`1` !')], verbose_name='Количество ингредиентов'),
        ),
        migrations.AlterField(
            model_name='recipelist',
            name='author',
            field=models.ForeignKey(help_text='Выберите автора рецепта', on_delete=django.db.models.deletion.CASCADE, related_name='recipes', to=settings.AUTH_USER_MODEL, verbose_name='Автор рецепта'),
        ),
        migrations.AlterField(
            model_name='recipelist',
            name='ingredients',
            field=models.ManyToManyField(help_text='Выберите ингредиенты рецепта', related_name='recipe', through='recipes.IngredientInRecipe', to='recipes.Ingredient', verbose_name='Ингредиенты в рецепте'),
        ),
        migrations.AlterField(
            model_name='recipelist',
            name='name',
            field=models.CharField(help_text='Введите название рецепта', max_length=255, verbose_name='Название рецепта'),
        ),
        migrations.AlterField(
            model_name='recipelist',
            name='pub_date',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Дата создания рецепта'),
        ),
        migrations.AlterField(
            model_name='recipelist',
            name='tags',
            field=models.ManyToManyField(help_text='Выберите тег рецепта', to='recipes.Tag', verbose_name='Тег рецепта'),
        ),
        migrations.AlterField(
            model_name='recipelist',
            name='text',
            field=models.TextField(help_text='Введите описания рецепта', verbose_name='Описание рецепта'),
        ),
    ]

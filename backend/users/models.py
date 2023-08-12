from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


class User(AbstractUser):

    class Roles(models.TextChoices):
        USER = 'user'
        ADMIN = 'admin'

    username = models.CharField(
        verbose_name='Ник пользователя',
        max_length=150,
        unique=True,
        validators=(RegexValidator(
            regex=r'^[\w.@+-]+\Z', message=(
                'Введено некорректное значение '
                'поля "username"')
        ),)
    )
    email = models.EmailField(
        verbose_name='Электронная почта',
        max_length=254,
        db_index=True,
        unique=True,
        help_text='Введите адрес электронной почты',
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=150,
        help_text='Введите имя',
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=150,
        help_text='Введите фамилию',
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('id',)

    @property
    def is_admin(self):
        return (self.is_staff or self.is_superuser
                or self.role == User.Roles.ADMIN)

    @property
    def is_user(self):
        return self.is_user or self.role == User.Roles.USER

    def __str__(self):
        return f'@{self.username}: {self.email}.'


class Subscribe(models.Model):
    """ Модель Подписчик. """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriber',
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribing',
        verbose_name='Автор',
    )
    created = models.DateTimeField(
        'Дата подписки',
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'Подписчик'
        verbose_name_plural = 'Подписчики'
        ordering = ('-id',)
        constraints = (
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_subscribing',
            ),
        )

    def __str__(self):
        return (f'Пользователь {self.user.username} '
                f'подписан на {self.author.username}')

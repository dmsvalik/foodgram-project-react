import datetime
import json

from django.conf import settings
from django.core.management import BaseCommand
from recipes.models import Ingredient

FILE: str = f'{settings.BASE_DIR}/data/ingredients.json'


def import_json_data() -> None:
    """ Обработка файла json. """
    with open(FILE, 'r', encoding='utf-8') as file:
        data = json.load(file)
        for note in data:
            Ingredient.objects.get_or_create(**note)


class Command(BaseCommand):
    """ Загрузка данных из json-файла. """
    help = ('Загрузка данных из /data/ingredients.json.'
            'Запуск: python manage.py load_data.')

    def handle(self, *args, **options) -> None:
        start_time = datetime.datetime.now()
        try:
            import_json_data()
        except Exception as error:
            self.stdout.write(
                self.style.WARNING(f'Сбой в работе импорта: {error}.')
            )
        else:
            self.stdout.write(self.style.SUCCESS(
                f'Загрузка данных завершена за '
                f' {(datetime.datetime.now() - start_time).total_seconds()} '
                f'сек.')
            )

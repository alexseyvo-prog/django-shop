# Django Shop

Учебный Django-проект интернет-магазина.

## Возможности

- Django Admin
- Модели товаров, заказов и пользователей
- REST-сериализация заказов
- Кэширование JSON-экспорта заказов
- Docker Compose и Gunicorn

## Запуск

```bash
docker compose up -d --build
```

## Миграции

```bash
docker compose run --rm web python manage.py migrate
```

## Статические файлы

```bash
docker compose run --rm web python manage.py collectstatic --noinput
```

## Экспорт заказов

```text
/shop/users/<user_id>/orders/export/
```
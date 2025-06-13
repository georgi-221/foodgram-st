# Foodgram — Продуктовый помощник
**Foodgram** — это веб-приложение для публикации рецептов, добавления их в избранное и список покупок, а также подписки на авторов.
## Автор
**Павлов Георгий**
[GitHub: georgi-221](https://github.com/georgi-221)

##  Стек технологий

* Python 3.13
* Django 5.2
* Django REST Framework
* PostgreSQL
* Docker
* Docker Compose
* Nginx
* Gunicorn
* GitHub Actions

## Локальный запуск с Docker

### 1. Клонирование репозитория

```bash
git clone https://github.com/georgi-221/foodgram-st.git
cd foodgram-st
```

### 2. Создание и настройка `.env` файла

В корне проекта создайте файл `.env` со следующим содержимым:

```env
POSTGRES_DB=foodgram
POSTGRES_USER=foodgram_user
POSTGRES_PASSWORD=foodgram_password
DB_HOST=db
DB_PORT=5432
SECRET_KEY=your_django_secret_key
DEBUG=False
ALLOWED_HOSTS=127.0.0.1,localhost
```

### 3. Запустить docker compose:

Перейдите в директорию infra/ и выполните:

```bash

docker compose up --build
```

### 4. Применение миграций и сбор статики

```bash

docker compose exec backend python manage.py migrate

docker-compose exec backend python manage.py collectstatic --noinput
```

### 5. Создание суперпользователя

```bash
docker-compose exec backend python manage.py createsuperuser
```

### 6. Загрузка данных

Загрузите ингредиенты

```bash
docker-compose exec backend python manage.py load_ingredients

```

### 7. Доступ к приложению

* Frontend: [http://localhost/](http://localhost/)
* Админка: [http://localhost/admin/](http://localhost/admin/)
* API: [http://localhost/api/](http://localhost/api/)

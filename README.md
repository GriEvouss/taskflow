# Project Management Backend

## Установка

```bash
cd project-management-backend
pip install -r requirements.txt
```

## Настройка

1. Скопируйте `.env.example` в `.env`
2. Отредактируйте `.env` с вашими настройками БД

## Запуск

```bash
python run.py
```

## API Endpoints

- `POST /api/v1/auth/register` - Регистрация
- `POST /api/v1/auth/login` - Вход
- `GET /api/v1/projects` - Список проектов
- `POST /api/v1/projects` - Создать проект
- `GET /api/v1/projects/<id>` - Получить проект
- `PUT /api/v1/projects/<id>` - Обновить проект
- `DELETE /api/v1/projects/<id>` - Удалить проект
TOOLS: list = [
    {
        "name": "get_user_tasks",
        "description": "Викликай цей tool, коли юзер хоче побачити список своїх задач, "
        "дізнатися що в нього заплановане, або отримати інформацію про існуючі задачі",  # <- твій опис
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "create_task",
        "description": "Викликай цей tool, коли юзер хоче створити нову задачу",  # ← напиши коли модель має це викликати
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Назва задачі"},
                "description": {
                    "type": "string",
                    "description": "Опис задачі, може бути пустим, якщо текст для назви завеликий, "
                    "то частину інформації можна помістити сюди ",
                },
                "priority": {
                    "type": "integer",
                    "description": "Пріоритет задачі від 0 (низький) до 5 (найвищий). За замовчуванням 0.",
                },
                "due_date": {
                    "type": "string",
                    "description": "Дата завершення задачі у форматі YYYY-MM-DD. "
                    "Інтерпретуй відносні дати ('завтра', 'наступний понеділок') відносно поточної дати.",
                },
            },
            "required": ["title"],
        },
    },
    {
        "name": "delete_task",
        "description": "Викликай для видалення задачі по id. Якщо id невідомий, спочатку викликай get_user_tasks"
        " щоб знайти id потрібної задачі по назві або іншим критеріям.",
        "input_schema": {
            "type": "object",
            "properties": {
                "id": {
                    "type": "integer",
                    "description": "ID задачі, яку потрібно видалити",
                }
            },
            "required": ["id"],
        },
    },
    {
        "name": "update_task",
        "description": "Викликай для оновлення задачі по id. Якщо id невідомий, спочатку викликай get_user_tasks",
        "input_schema": {
            "type": "object",
            "properties": {
                "id": {
                    "type": "integer",
                    "description": "ID задачі, яку потрібно оновити",
                },
                "title": {"type": "string", "description": "Нова назва задачі"},
                "description": {"type": "string", "description": "Новий опис задачі"},
                "priority": {
                    "type": "integer",
                    "description": "Новий пріоритет задачі від 0 (низький) до 5 (найвищий).",
                },
                "due_date": {
                    "type": "string",
                    "description": "Нова дата завершення задачі у форматі YYYY-MM-DD. "
                    "Інтерпретуй відносні дати ('завтра', 'наступний понеділок') відносно поточної дати.",
                },
                "is_done": {
                    "type": "boolean",
                    "description": "Статус задачі: true якщо виконано, false якщо ні.",
                },
            },
            "required": ["id"],
        },
    },
]

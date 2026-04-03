# knowledge-base

Заметки, которые ищутся не только по целому слову. Когда сохраняешь новую, в ответе приходит список похожих, если такие уже лежат в базе.

Сходство — TF-IDF по кускам слова, 3–5 символов (`char_wb` в scikit-learn). Иначе «борщ» и «борща» для индекса разные токены, и русский текст почти не ищется. Синонимы так не находятся: «машина» и «автомобиль» останутся двумя заметками.

Порог, после которого заметка помечается дублем, один на всех. Это `DUPLICATE_THRESHOLD` в `.env`, сейчас 0.6.

Индекс каждый раз считается заново по всем заметкам. На несколько сотен записей укладывается в миллисекунды. Файлы и вложения не индексируются, только `title` и `content`.

## Запуск

```bash
docker compose up --build
```

Swagger: http://localhost:8002/docs

Без Docker используется SQLite, Postgres не нужен:

```bash
python -m venv .venv
.venv/Scripts/activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

На Linux и macOS окружение включается через `source .venv/bin/activate`.

```bash
curl -X POST localhost:8002/notes -H "Content-Type: application/json" \
  -d '{"title": "Рецепт борща", "content": "свекла, капуста, картофель, варить бульон"}'

curl -X POST localhost:8002/notes -H "Content-Type: application/json" \
  -d '{"title": "Ещё рецепт борща", "content": "свёкла и капуста, варим бульон почти так же"}'

curl "localhost:8002/search?q=борщ+со+свеклой"
```

У второго `POST` в поле `possible_duplicates` должна быть первая заметка. Поиск по «борщ со свеклой» ставит рецепт выше посторонней заметки.

```bash
pytest -v
```

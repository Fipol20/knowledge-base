# knowledge-base

Заметки с поиском по кускам слов. При сохранении в ответе есть `possible_duplicates`, если похожая заметка уже была.

```bash
docker compose up --build
```

http://localhost:8000/docs

Без Docker поднимается SQLite:

```bash
python -m venv .venv
.venv/Scripts/activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

Linux и macOS: `source .venv/bin/activate`.

```bash
curl -X POST localhost:8000/notes -H "Content-Type: application/json" \
  -d '{"title": "Рецепт борща", "content": "свекла, капуста, картофель, варить бульон"}'

curl -X POST localhost:8000/notes -H "Content-Type: application/json" \
  -d '{"title": "Ещё рецепт борща", "content": "свёкла и капуста, варим бульон почти так же"}'

curl "localhost:8000/search?q=борщ+со+свеклой"
```

Второе сохранение должно вернуть первую заметку в `possible_duplicates`. Поиск по «борщ со свеклой» ставит рецепт первым.

Считается косинусное сходство TF-IDF по n-граммам 3–5 символов, не по целым словам. Поэтому «свекла» и «свеклой» ещё совпадают. «Машина» и «автомобиль» нет.

Порог дубля один, `DUPLICATE_THRESHOLD`. Индекс пересобирается на каждый запрос. Пока заметок сотни, отдельное хранилище индекса не нужно.

```bash
pytest -v
```

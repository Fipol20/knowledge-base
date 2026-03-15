from app.models import Note
from app.search_service import SearchIndex


def _note(note_id: int, title: str, content: str) -> Note:
    # не кладём в БД - для юнит-теста самого индекса это не нужно
    note = Note(title=title, content=content, url=None)
    note.id = note_id
    return note


def test_search_ranks_relevant_note_first():
    notes = [
        _note(1, "Рецепт борща", "свекла, капуста, картофель, варить бульон"),
        _note(2, "Настройка FastAPI", "uvicorn, роутеры, pydantic схемы"),
        _note(3, "Ещё один суп", "борщ со свеклой и капустой, немного другой рецепт"),
    ]
    index = SearchIndex(notes)

    results = index.search("рецепт борща со свеклой")

    assert results[0].note.id in (1, 3)
    # заметка про FastAPI по этому запросу не должна оказаться в топе
    top_ids = [r.note.id for r in results[:2]]
    assert 2 not in top_ids


def test_search_on_empty_index_returns_empty():
    index = SearchIndex([])
    assert index.search("что угодно") == []


def test_find_duplicates_detects_near_identical_text():
    notes = [_note(1, "Заметка про FastAPI", "FastAPI роутеры и pydantic схемы для валидации")]
    index = SearchIndex(notes)

    duplicates = index.find_duplicates(
        "Заметка про FastAPI: роутеры и pydantic схемы для валидации", threshold=0.5
    )

    assert len(duplicates) == 1
    assert duplicates[0].note.id == 1
    assert duplicates[0].score >= 0.5


def test_find_duplicates_ignores_unrelated_text():
    notes = [_note(1, "Рецепт борща", "свекла, капуста, картофель")]
    index = SearchIndex(notes)

    duplicates = index.find_duplicates("настройка Kubernetes кластера", threshold=0.5)

    assert duplicates == []


def test_find_duplicates_excludes_given_id():
    notes = [_note(1, "Одно и то же", "текст один в один")]
    index = SearchIndex(notes)

    duplicates = index.find_duplicates("Одно и то же текст один в один", threshold=0.1, exclude_id=1)

    assert duplicates == []

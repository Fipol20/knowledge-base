from app.note_service import create_note, search_notes


def test_create_note_without_duplicates(db_session):
    note, duplicates = create_note(db_session, "Первая заметка", "какой-то уникальный текст про космос", None)
    assert note.id is not None
    assert duplicates == []


def test_create_note_flags_duplicate(db_session):
    create_note(db_session, "Про FastAPI", "FastAPI роутеры, pydantic схемы, dependency injection", None)

    _, duplicates = create_note(
        db_session,
        "Про FastAPI (2)",
        "FastAPI роутеры, pydantic схемы и dependency injection",
        None,
    )

    assert len(duplicates) == 1
    assert duplicates[0].score >= 0.6


def test_search_notes_finds_relevant(db_session):
    create_note(db_session, "Рецепт борща", "свекла капуста картофель бульон", None)
    create_note(db_session, "Настройка CI", "github actions pytest pipeline", None)

    results = search_notes(db_session, "борщ со свеклой")

    assert results
    assert results[0].note.title == "Рецепт борща"

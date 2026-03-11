from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.models import Note
from app.search_service import ScoredNote, SearchIndex


def _all_notes(db: Session) -> list[Note]:
    return list(db.execute(select(Note)).scalars())


def create_note(db: Session, title: str, content: str, url: str | None) -> tuple[Note, list[ScoredNote]]:
    """Создаёт заметку и сразу возвращает список похожих существующих
    заметок (не блокирует создание - решение "это дубль или нет" за
    пользователем, автоматически удалять/мерджить не пытаемся)."""
    existing = _all_notes(db)
    index = SearchIndex(existing)
    duplicates = index.find_duplicates(f"{title}\n{content}", threshold=settings.duplicate_threshold)

    note = Note(title=title, content=content, url=url)
    db.add(note)
    db.commit()
    db.refresh(note)
    return note, duplicates


def search_notes(db: Session, query: str, top_k: int | None = None) -> list[ScoredNote]:
    notes = _all_notes(db)
    index = SearchIndex(notes)
    return index.search(query, top_k=top_k or settings.default_search_top_k)


def delete_note(db: Session, note: Note) -> None:
    db.delete(note)
    db.commit()

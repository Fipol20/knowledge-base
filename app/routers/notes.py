from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Note
from app.note_service import create_note, delete_note, search_notes
from app.schemas import NoteCreate, NoteCreateResponse, NoteOut, PossibleDuplicate, SearchResult

router = APIRouter(tags=["notes"])


@router.post("/notes", response_model=NoteCreateResponse, status_code=201)
def add_note(payload: NoteCreate, db: Session = Depends(get_db)):
    note, duplicates = create_note(db, payload.title, payload.content, payload.url)
    return NoteCreateResponse(
        note=NoteOut.model_validate(note),
        possible_duplicates=[
            PossibleDuplicate(note_id=d.note.id, title=d.note.title, similarity=d.score) for d in duplicates
        ],
    )


@router.get("/notes", response_model=list[NoteOut])
def list_notes(db: Session = Depends(get_db)):
    return list(db.execute(select(Note).order_by(Note.id.desc())).scalars())


@router.get("/notes/{note_id}", response_model=NoteOut)
def get_note(note_id: int, db: Session = Depends(get_db)):
    note = db.get(Note, note_id)
    if note is None:
        raise HTTPException(404, "заметка не найдена")
    return note


@router.delete("/notes/{note_id}", status_code=204)
def remove_note(note_id: int, db: Session = Depends(get_db)):
    note = db.get(Note, note_id)
    if note is None:
        raise HTTPException(404, "заметка не найдена")
    delete_note(db, note)


@router.get("/search", response_model=list[SearchResult])
def search(q: str = Query(..., min_length=1), top_k: int = 10, db: Session = Depends(get_db)):
    results = search_notes(db, q, top_k=top_k)
    return [SearchResult(note=NoteOut.model_validate(r.note), score=r.score) for r in results]

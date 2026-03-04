import datetime as dt

from pydantic import BaseModel, ConfigDict


class NoteCreate(BaseModel):
    title: str
    content: str
    url: str | None = None


class NoteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    content: str
    url: str | None
    created_at: dt.datetime


class PossibleDuplicate(BaseModel):
    note_id: int
    title: str
    similarity: float


class NoteCreateResponse(BaseModel):
    note: NoteOut
    possible_duplicates: list[PossibleDuplicate]


class SearchResult(BaseModel):
    note: NoteOut
    score: float

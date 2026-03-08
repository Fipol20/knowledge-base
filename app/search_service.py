"""
Поиск и детект дублей на TF-IDF + косинусном сходстве.

Это лексическое сходство, не семантическое - "машина" и "автомобиль"
для TF-IDF два разных слова, реальные синонимы/парафразы он не поймает.
Для честного семантического поиска нужны embeddings (sentence-transformers)
и векторный индекс (pgvector/faiss). Осознанно начал с TF-IDF: он не тянет
никаких весов моделей, работает мгновенно и уже закрывает практичный
кейс "нашёл почти такую же заметку" - а интерфейс SearchIndex сделан так,
чтобы позже подменить векторизатор на embeddings без переписывания
остального сервиса.
"""

from dataclasses import dataclass

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.models import Note


def _note_text(note: Note) -> str:
    return f"{note.title}\n{note.content}"


@dataclass
class ScoredNote:
    note: Note
    score: float


class SearchIndex:
    """Строится по снапшоту заметок на момент запроса. Для пары сотен
    заметок пересчёт TF-IDF на каждый запрос занимает миллисекунды - для
    большего масштаба индекс стоило бы кэшировать и инвалидировать по
    изменению данных, а не пересобирать с нуля."""

    def __init__(self, notes: list[Note]):
        self.notes = notes
        self._vectorizer: TfidfVectorizer | None = None
        self._matrix = None
        if notes:
            # analyzer='char_wb' + n-граммы 3-5 символов вместо целых слов -
            # осознанный выбор под русскую морфологию. Без стеммера/лемматизатора
            # обычный word-level TF-IDF не увидит связь "борщ" и "борща",
            # "свекла" и "свеклой" - разные словоформы для него разные токены.
            # Символьные n-граммы ловят общий корень слова само собой, без
            # подключения pymorphy2/spacy. Платим за это чуть более шумным
            # сходством на коротких словах - для заметок это приемлемо.
            self._vectorizer = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), min_df=1)
            self._matrix = self._vectorizer.fit_transform([_note_text(n) for n in notes])

    def search(self, query: str, top_k: int = 10) -> list[ScoredNote]:
        if not self.notes or self._vectorizer is None or not query.strip():
            return []

        query_vec = self._vectorizer.transform([query])
        scores = cosine_similarity(query_vec, self._matrix)[0]
        ranked = sorted(zip(self.notes, scores), key=lambda pair: pair[1], reverse=True)
        return [ScoredNote(note, float(score)) for note, score in ranked[:top_k] if score > 0]

    def find_duplicates(
        self, candidate_text: str, threshold: float, exclude_id: int | None = None
    ) -> list[ScoredNote]:
        if not self.notes or self._vectorizer is None:
            return []

        candidate_vec = self._vectorizer.transform([candidate_text])
        scores = cosine_similarity(candidate_vec, self._matrix)[0]

        result = [
            ScoredNote(note, float(score))
            for note, score in zip(self.notes, scores)
            if score >= threshold and note.id != exclude_id
        ]
        return sorted(result, key=lambda item: item.score, reverse=True)

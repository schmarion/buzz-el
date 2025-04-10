import random
from typing import Iterable

from litellm import embedding
from sentence_transformers.util import semantic_search
from spacy.tokens import Span


class Disambiguator:
    def __init__(self, disambiguator_type: str = "random", embedding_model: str = None) -> None:
        if disambiguator_type == "random":
            self._disambiguator_type = "random"
        elif disambiguator_type == "similarity":
            self._disambiguator_type = "similarity"
            self._embedding_model = embedding_model
        else :
            raise ValueError(
                "The 'disambiguator_type' can only takes as value 'random' or 'similarity'."
                )

    def _extract_more_similar_entities(self, overlapping_spans: Iterable[Span]) -> Iterable[Span]:
        doc_embed = embedding(
            model=self._embedding_model, 
            input=[overlapping_spans[0].doc.text]
        )
        spans_embed = embedding(
            model=self._embedding_model, 
            input=[span.text for span in overlapping_spans]
        )
        selected_span = semantic_search(
            doc_embed,
            spans_embed,
            top_k=1
        )
        return selected_span

    def __call__(self, overlapping_spans: Iterable[Span]) -> Iterable[Span]:
        if self._disambiguator_type == "similarity":
            selected_span = self._extract_more_similar_entities(overlapping_spans)
        else :
            selected_span = [random.choice(overlapping_spans)]
        return selected_span

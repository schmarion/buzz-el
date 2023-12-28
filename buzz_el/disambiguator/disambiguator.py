import random
from typing import Iterable

from spacy.tokens import Span


class Disambiguator:
    def __init__(self) -> None:
        pass

    def __call__(self, overlapping_spans: Iterable[Span]) -> Iterable[Span]:
        return [random.choice(overlapping_spans)]

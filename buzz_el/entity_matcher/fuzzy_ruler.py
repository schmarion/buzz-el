from typing import Dict, List, Optional, Tuple

from spacy.language import Language
from spacy.tokens import Doc, Span
from spaczz.matcher import FuzzyMatcher


class FuzzyRuler:
    def __init__(
        self,
        spacy_model: Language,
        ignore_case: Optional[bool] = True,
        spans_key: Optional[str] = None,
        config: Optional[Dict] = None
        # spans_key: str,
        # min_r: Optional[int] = None,
        # fuzzy_func: Optional[str] = None,
    ) -> None:
        self.spacy_model = spacy_model
        self.ignore_case = ignore_case
        if spans_key is None:
            spans_key = "fuzzy"
        self.spans_key = spans_key

        # self.min_r = min_r
        # if (fuzzy_func is not None) and (fuzzy_func in EXISTING_FUZZY_FUNC):
        #     self.fuzzy_func = fuzzy_func
        # else:
        #     self.fuzzy_func = "simple"

        if config is not None:
            self.matcher = FuzzyMatcher(
                self.spacy_model.vocab, ignore_case=self.ignore_case, **config
            )
        else:
            self.matcher = FuzzyMatcher(
                self.spacy_model.vocab, ignore_case=self.ignore_case
            )

    def add_patterns(self, patterns: List[Dict[str, str]]) -> None:
        for pattern in patterns:
            label_with_id = f"{pattern['label']}#{pattern['id']}"
            self.matcher.add(label_with_id, [self.spacy_model(pattern["pattern"])])

    def __call__(self, doc: Doc) -> Doc:
        matches = self.matcher(doc)
        self.set_annotations(doc, matches)
        return doc

    def set_annotations(self, doc: Doc, matches: List[Tuple]):
        deduplicated_matches = set(
            Span(
                doc,
                start,
                end,
                label=label_with_id[: label_with_id.find("#")],
                span_id=label_with_id[label_with_id.find("#") + 1 :],
            )
            for label_with_id, start, end, ratio, pattern in matches
            if start != end
        )
        formatted_matches = sorted(list(deduplicated_matches))
        doc.spans[self.spans_key] = formatted_matches
        return

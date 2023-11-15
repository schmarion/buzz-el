from typing import Callable, Dict, List, Optional, Union

import spacy.tokens.Doc
from spacy.language import Language
from spacy.pipeline import SpanRuler

from ..graph_loader import GraphLoader

SPACY_TOK_ATTR_TO_FUNCT = {"LOWER": lambda s: s.lower(), "UPPER": lambda s: s.upper()}


class EntityMatcher:
    def __init__(
        self,
        graph_loader: GraphLoader,
        matching_attribute: Optional[str] | None,
        fuzzy_matcher: Callable[[str, str, int], bool],
    ) -> None:
        self.graph_loader = graph_loader
        self.fuzzy_matcher = fuzzy_matcher
        self._spacy_component = None

    def _construct_phrase_patterns(
        self,
        entity_label: Optional[str] = "KG_ENT",
        ent_str_preprocessing: Callable[[str], str] = lambda s: s,
    ) -> List[Dict]:
        phrase_patterns = []

        for ent_id, match_phrases in self.graph_loader.entity_str_idx.items():
            for match_ph in match_phrases:
                phrase_patterns.append(
                    {
                        "label": entity_label,
                        "pattern": ent_str_preprocessing(match_ph),
                        "id": ent_id,
                    }
                )

        return phrase_patterns

    def build_entity_ruler(
        self, nlp: Language, config: Dict, entity_label: Optional[str] = "KG_ENT"
    ) -> SpanRuler:
        ruler = SpanRuler(nlp, **config)

        preprocessing_func = lambda s: s
        span_attr_to_match = config.get("phrase_matcher_attr")
        if span_attr_to_match is not None:
            preprocessing_func = SPACY_TOK_ATTR_TO_FUNCT.get(
                span_attr_to_match, lambda s: s
            )

        ph_patterns = self._construct_phrase_patterns(
            entity_label=entity_label,
            ent_str_preprocessing=preprocessing_func,
        )

        ruler.add_patterns(ph_patterns)

        return ruler

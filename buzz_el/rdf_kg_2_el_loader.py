from collections import defaultdict
from typing import Any, Callable, Dict, List, Optional, Set

import numpy as np
import rdflib
from rdflib import Graph
from spacy.language import Language
from spacy.pipeline import SpanRuler
from spacy.util import ensure_path

SPACY_TOK_ATTR_TO_FUNCT = {"LOWER": lambda s: s.lower(), "UPPER": lambda s: s.upper()}


class RDF_KG_2_EL:
    def __init__(
        self,
        kg_file_path: Any,
        annotation_properties: Optional[Set[str]] = None,
        text_vectoriser: Optional[Callable[[str], np.ndarray]] = None,
        lang_filter_tag: Optional[str] = None,
    ) -> None:
        self._kg_file_path = ensure_path(kg_file_path)
        self._rdf_annotation_properties = (
            annotation_properties if annotation_properties else {"rdfs:label"}
        )
        self._text_vectoriser = text_vectoriser
        self._lang_filter = lang_filter_tag

        self._kg = Graph()
        self._entity_ruler = None
        self._entity_linker = None
        self._kb = None
        self._entity_str_idx = defaultdict(set)

    def load_kg_from_file(self) -> None:
        self._kg = self._kg.parse(self._kg_file_path)

    def build_entity_strings_index(self) -> None:
        sparql_alternative_path_str = "|".join(self._rdf_annotation_properties)
        sparql_lang_filter_str = (
            f'FILTER ( lang(?label) = "{self._lang_filter}" )'
            if self._lang_filter
            else ""
        )
        sparql_q_ent_labels = f"""
            SELECT DISTINCT ?ent_uri ?label WHERE {{
                ?ent_uri {sparql_alternative_path_str} ?label .
                {sparql_lang_filter_str}
            }}
        """
        for r in self._kg.query(sparql_q_ent_labels):
            self._entity_str_idx[str(r["ent_uri"])].add(str(r["label"]))

    def _construct_phrase_patterns(
        self,
        entity_label: Optional[str] = "KG_ENT",
        ent_str_preprocessing: Callable[[str], str] = lambda s: s,
    ) -> List[Dict]:
        phrase_patterns = list()

        for ent_id, match_phrases in self._entity_str_idx.items():
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

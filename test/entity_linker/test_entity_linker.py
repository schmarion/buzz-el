from typing import List

import pytest
from spacy.tokens import Doc

from buzz_el.entity_linker import EntityLinker
from buzz_el.entity_matcher import EntityMatcher


@pytest.fixture(scope="session")
def corpus(en_sm_spacy_model, pizza_bisou_en_reviews) -> List[Doc]:
    docs = [doc for doc in en_sm_spacy_model.pipe(pizza_bisou_en_reviews)]
    return docs


class TestEntityLinker:
    @pytest.fixture(scope="class")
    def entity_linker(self, pizza_bisou_kg, en_sm_spacy_model) -> EntityLinker:
        entity_matcher = EntityMatcher(
            pizza_bisou_kg, en_sm_spacy_model, use_fuzzy=True
        )
        entity_linker = EntityLinker(pizza_bisou_kg, en_sm_spacy_model, entity_matcher)
        return entity_linker

    def test_extract_overlapping_spans(self, entity_linker, corpus) -> None:
        doc = entity_linker.entity_matcher(corpus[0])
        overlapping_spans = entity_linker._extract_overlapping_spans(doc)
        assert len(overlapping_spans) == 10
        for span_group in overlapping_spans:
            if len(span_group) > 1:
                for entity in span_group:
                    assert (
                        ("pepper" in entity.text)
                        or ("Castafiore" in entity.text)
                        or ("cheese" in entity.text)
                    )

    def test_remove_ambiguities(self, entity_linker, corpus) -> None:
        doc = entity_linker.entity_matcher(corpus[0])
        assert len(doc.spans[entity_linker.entity_matcher.spans_key]) == 14
        assert not (doc.ents)
        doc = entity_linker._remove_ambiguities(doc)
        assert len(doc.ents) == 10

    def test_entity_linker_call(self, entity_linker, corpus) -> None:
        doc = corpus[0]
        assert not (doc.ents)
        doc = entity_linker(doc)
        assert len(doc.ents) == 10

    def test_entity_linker_call(self, entity_linker, corpus) -> None:
        for doc in corpus[1:]:
            assert not (doc.ents)
        corpus = entity_linker.pipe(corpus[1:])
        for doc in corpus:
            assert len(doc.ents) > 0

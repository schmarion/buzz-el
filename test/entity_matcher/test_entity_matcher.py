from typing import List

import pytest
import spacy

from buzz_el.entity_matcher import EntityMatcher


@pytest.fixture(scope="session")
def corpus(en_sm_spacy_model, pizza_bisou_en_reviews) -> List[spacy.tokens.Doc]:
    docs = [doc for doc in en_sm_spacy_model.pipe(pizza_bisou_en_reviews)]
    return docs


class TestEntityMatcherString:
    @pytest.fixture(scope="class")
    def string_matcher(self, en_sm_spacy_model, pizza_bisou_kg) -> EntityMatcher:
        entity_matcher = EntityMatcher(
            knowledge_graph=pizza_bisou_kg, spacy_model=en_sm_spacy_model
        )
        return entity_matcher

    @pytest.fixture(scope="class")
    def processed_docs(self, string_matcher, corpus) -> List[spacy.tokens.Doc]:
        docs = [doc for doc in string_matcher.pipe(corpus)]

        return docs

    def test_string_matcher_init(self, string_matcher) -> None:
        assert string_matcher._string_matcher is not None
        assert string_matcher._fuzzy_matcher is None

    def test_string_matcher_call(self, corpus, string_matcher) -> None:
        doc = corpus[0]

        string_matcher(doc)

        assert len(doc.spans["string"]) > 0

    def test_string_matcher_pipe(self, processed_docs) -> None:
        assert len(processed_docs[0].spans["string"]) > 0
        assert len(processed_docs[1].spans["string"]) > 0
        assert len(processed_docs[2].spans["string"]) > 0

    def test_matched_entities(self, processed_docs) -> None:
        god_save_the_king_review = processed_docs[2]

        matched_ents = {span.id_ for span in god_save_the_king_review.spans["string"]}

        assert (
            "http://www.msesboue.org/o/pizza-data-demo/bisou#_godSaveTheKing"
            in matched_ents
        )
        assert (
            "http://www.msesboue.org/o/pizza-data-demo/bisou#_tomatoBase"
            in matched_ents
        )
        assert (
            "http://www.msesboue.org/o/pizza-data-demo/bisou#_mozzaFiorDiLatte"
            in matched_ents
        )


class TestEntityMatcherFuzzy:
    @pytest.fixture(scope="class")
    def fuzzy_matcher(self, en_sm_spacy_model, pizza_bisou_kg) -> EntityMatcher:
        entity_matcher = EntityMatcher(
            knowledge_graph=pizza_bisou_kg,
            spacy_model=en_sm_spacy_model,
            use_fuzzy=True,
        )
        return entity_matcher

    @pytest.fixture(scope="session")
    def misspelling_corpus(
        self, en_sm_spacy_model, pizza_bisou_en_misspelling_reviews
    ) -> List[spacy.tokens.Doc]:
        docs = [
            doc for doc in en_sm_spacy_model.pipe(pizza_bisou_en_misspelling_reviews)
        ]
        return docs

    @pytest.fixture(scope="class")
    def processed_misspelling_docs(
        self, fuzzy_matcher, misspelling_corpus
    ) -> List[spacy.tokens.Doc]:
        docs = [doc for doc in fuzzy_matcher.pipe(misspelling_corpus)]

        return docs

    def test_fuzzy_matcher_init(self, fuzzy_matcher) -> None:
        assert fuzzy_matcher._string_matcher is None
        assert fuzzy_matcher._fuzzy_matcher is not None

    def test_fuzzy_matcher_call(self, misspelling_corpus, fuzzy_matcher) -> None:
        doc = misspelling_corpus[0]

        fuzzy_matcher(doc)
        assert len(doc.spans["fuzzy"]) > 0

    def test_fuzzy_matcher_pipe(self, processed_misspelling_docs) -> None:
        assert len(processed_misspelling_docs[0].spans["fuzzy"]) > 0
        assert len(processed_misspelling_docs[1].spans["fuzzy"]) > 0
        assert len(processed_misspelling_docs[2].spans["fuzzy"]) > 0

    def test_matched_entities(self, processed_misspelling_docs) -> None:
        god_save_the_king_review = processed_misspelling_docs[2]

        matched_ents_fuzzy = {
            span.id_ for span in god_save_the_king_review.spans["fuzzy"]
        }

        assert (
            "http://www.msesboue.org/o/pizza-data-demo/bisou#_godSaveTheKing"
            in matched_ents_fuzzy
        )
        assert (
            "http://www.msesboue.org/o/pizza-data-demo/bisou#_tomatoBase"
            in matched_ents_fuzzy
        )
        assert (
            "http://www.msesboue.org/o/pizza-data-demo/bisou#_mozzaFiorDiLatte"
            in matched_ents_fuzzy
        )

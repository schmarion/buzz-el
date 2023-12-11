from typing import List

import pytest
import spacy

from buzz_el.entity_matcher import EntityMatcher


@pytest.fixture(scope="session")
def corpus(en_sm_spacy_model, pizza_bisou_en_reviews) -> List[spacy.tokens.Doc]:
    docs = [doc for doc in en_sm_spacy_model.pipe(pizza_bisou_en_reviews)]
    return docs


@pytest.fixture(scope="session")
def default_matcher(en_sm_spacy_model, pizza_bisou_kg) -> EntityMatcher:
    entity_matcher = EntityMatcher(
        knowledge_graph=pizza_bisou_kg, spacy_model=en_sm_spacy_model
    )
    return entity_matcher


class TestEntityMatcherString:
    @pytest.fixture(scope="class")
    def processed_docs(self, default_matcher, corpus) -> List[spacy.tokens.Doc]:
        docs = [doc for doc in default_matcher.pipe(corpus)]

        return docs

    def test_default_matcher_init(self, default_matcher) -> None:
        assert default_matcher._string_matcher is not None
        assert (
            default_matcher._string_matcher_config.get("phrase_matcher_attr") == "LOWER"
        )

    def test_default_matcher_call(self, corpus, default_matcher) -> None:
        doc = corpus[0]

        default_matcher(doc)

        assert len(doc.spans["string"]) > 0

    def test_default_matcher_pipe(self, processed_docs) -> None:
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

import os.path
from typing import List

import pytest
import spacy

from buzz_el.entity_matcher import EntityMatcher
from buzz_el.graph_loader import GraphLoader


@pytest.fixture(scope="session")
def example_texts() -> List[str]:
    docs = [
        "Margherita Pizza: The classic Italian pizza, topped with tomato sauce, fresh mozzarella cheese, fresh basil leaves, and a drizzle of olive oil.",
        "Pepperoni Pizza: A beloved American favorite, topped with tomato sauce, mozzarella cheese, and slices of pepperoni, which are a type of spicy salami.",
        "Hawaiian Pizza: A controversial choice, featuring tomato sauce, mozzarella cheese, ham, and pineapple. The sweet and salty combination is either loved or loathed by pizza enthusiasts.",
    ]
    return docs

@pytest.fixture(scope="session")
def spacy_nlp():
    spacy_model = spacy.load(
        "en_core_web_sm",
        exclude=["tok2vec", "tagger", "parser", "attribute_ruler", "lemmatizer", "ner"],
    )
    return spacy_model

@pytest.fixture(scope="session")
def corpus(spacy_nlp, example_texts) -> List[spacy.tokens.Doc]:
    docs = [doc for doc in spacy_nlp.pipe(example_texts)]
    return docs

@pytest.fixture(scope="session")
def graph_file_path() -> str:
    ex_data_path = os.path.join(
        os.path.dirname(__file__), "..", "..", "examples", "data"
    )
    file_path = os.path.join(ex_data_path, "pizza.ttl")

    return file_path

@pytest.fixture(scope="session")
def graph_loader(graph_file_path) -> GraphLoader:
    loader = GraphLoader(
        kg_file_path=graph_file_path,
        annotation_properties={"skos:altLabel", "rdfs:label", "skos:prefLabel"},
        lang_filter_tag="en"
    )
    return loader

@pytest.fixture(scope="session")
def default_matcher(spacy_nlp, graph_loader) -> EntityMatcher:
    matcher = EntityMatcher(
        graph_loader=graph_loader,
        nlp=spacy_nlp
    )
    return matcher

@pytest.fixture(scope="session")
def custom_config_matcher(spacy_nlp, graph_loader) -> EntityMatcher:
    matcher = EntityMatcher(
        graph_loader=graph_loader,
        nlp=spacy_nlp,
        span_ruler_config = {
            "phrase_matcher_attr": "LOWER",
            "spans_key": "kg_ents"
        }
    )

    return matcher

class TestEntityRulerInit:
    
    def test_default_matcher_init(self, default_matcher) -> None:
        assert default_matcher.spacy_component is not None
        assert default_matcher._span_ruler_config.get("phrase_matcher_attr") == "LOWER"

    def test_custom_config_matcher_init(self, custom_config_matcher) -> None:
        assert custom_config_matcher.spacy_component is not None
        assert custom_config_matcher._span_ruler_config.get("spans_key") is not None

class TestBuildEntityRuler:

    @pytest.fixture(scope="class")
    def matcher(self, spacy_nlp, graph_loader) -> EntityMatcher:
        matcher = EntityMatcher(
            graph_loader=graph_loader,
            nlp=spacy_nlp
        )
        return matcher
    def test_default_build(self, matcher) -> None:
        # test with custom entity_label
        # test with custom config
        matcher.spacy_component = None
        matcher.build_entity_ruler()

        assert isinstance(matcher.spacy_component, spacy.pipeline.SpanRuler)
        assert matcher.spacy_component.key == "ruler"

    def test_custom_config_build(self, matcher) -> None:
        matcher.build_entity_ruler(config={
            "phrase_matcher_attr": "LOWER",
            "spans_key": "kg_ents"
        })

        assert isinstance(matcher.spacy_component, spacy.pipeline.SpanRuler)
        assert matcher.spacy_component.key == "kg_ents"


class TestConstructPhrasePatterns:

    def test_default_construct_phrase_patterns(self, default_matcher) -> None:
        
        patterns = default_matcher._construct_phrase_patterns()
        ent_labels = {pat["label"] for pat in patterns}

        assert ent_labels == {"KG_ENT"}

    def test_custom_construct_phrase_patterns(self, default_matcher) -> None:
        
        patterns = default_matcher._construct_phrase_patterns(entity_label="CUSTOM_LABEL")
        ent_labels = {pat["label"] for pat in patterns}

        assert ent_labels == {"CUSTOM_LABEL"}

class TestEntityMatcherCall:

    def test_default_matcher_call(self, corpus, default_matcher) -> None:
        doc = corpus[0]

        default_matcher(doc)

        assert len(doc.spans["ruler"]) > 0

    def test_custom_config_matcher_call(self, corpus, custom_config_matcher) -> None:
        doc = corpus[0]

        custom_config_matcher(doc)

        assert len(doc.spans["kg_ents"]) > 0

class TestEntityMatcherPipe:

    def test_default_matcher_pipe(self, corpus, default_matcher) -> None:

        docs = [doc for doc in default_matcher.pipe(corpus)]

        assert len(docs[0].spans["ruler"]) > 0
        assert len(docs[1].spans["ruler"]) > 0
        assert len(docs[2].spans["ruler"]) > 0

    def test_custom_config_matcher_pipe(self, corpus, custom_config_matcher) -> None:
        docs = [doc for doc in custom_config_matcher.pipe(corpus)]

        assert len(docs[0].spans["ruler"]) > 0
        assert len(docs[1].spans["ruler"]) > 0
        assert len(docs[2].spans["ruler"]) > 0

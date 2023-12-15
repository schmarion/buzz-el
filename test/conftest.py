import os.path
from os import PathLike
from typing import List

import pytest
import spacy

from buzz_el.graph import KnowledgeGraph, RDFGraphLoader


@pytest.fixture(scope="session")
def en_sm_spacy_model() -> spacy.language.Language:
    nlp = spacy.load(  # we make the pipeline as small as possible
        "en_core_web_sm",
        exclude=["tok2vec", "tagger", "parser", "attribute_ruler", "lemmatizer", "ner"],
    )
    return nlp


@pytest.fixture(scope="session")
def pizza_bisou_kg_file_path() -> PathLike:
    ex_data_path = os.path.join(os.path.dirname(__file__), "..", "examples", "data")
    file_path = os.path.join(ex_data_path, "pizzas_bisou_sample.ttl")

    return file_path


@pytest.fixture(scope="session")
def pizza_bisou_rdf_graph_loader(pizza_bisou_kg_file_path) -> RDFGraphLoader:
    graph_loader = RDFGraphLoader(
        kg_file_path=pizza_bisou_kg_file_path,
        label_properties={"rdfs:label", "skos:altLabel"},
        context_properties={"rdfs:comment"},
        lang_filter_tag="en",
    )

    return graph_loader


@pytest.fixture(scope="session")
def pizza_bisou_kg(pizza_bisou_rdf_graph_loader) -> KnowledgeGraph:
    kg = pizza_bisou_rdf_graph_loader()

    return kg


@pytest.fixture(scope="session")
def pizza_bisou_en_reviews() -> List[str]:
    reviews = [
        """Absolutely delightful! The Bianca Castafiore pizza with its ricotta cream base offers a perfect blend of flavors. 
        I love the options of goat cheese and vegetarian toppings—especially the combination of black pepper, goat cheese, 
        honey, fior di latte mozzarella, spinach, and walnuts. A true treat for the taste buds!""",
        """A flavor explosion! The BurraTadah pizza, with its tomato base and pork pizza category, is a must-try. 
        The combination of black pepper, cherry tomatoes, mozzarella di burrata, fior di latte mozzarella, olive oil, 
        Parma ham, Parmesan cheese, and rocket creates a symphony of deliciousness. Simply irresistible!""",
        """Fit for royalty! The God Save The King pizza, featuring a tomato base and exquisite pork toppings, is a culinary masterpiece. 
        The Parisian mushroom carpaccio, ham from Paris with herbs, fior di latte mozzarella, and olives create a regal flavor profile. 
        A royal feast for the senses!""",
    ]
    return reviews


@pytest.fixture(scope="session")
def pizza_bisou_en_misspelling_reviews() -> List[str]:
    reviews = [
        """Absolutely delightful! The Bianca Castafiore pizza with its ricota cream base offers a perfect blend of flavors. 
        I love the options of goat chese and vegetarian toppings—especially the combination of black peper, goat cheese, 
        honey, fior di latte mozzarella, spinach, and walnuts. A true treat for the taste buds!""",
        """A flavor explosion! The BurraTadah pizza, with its tomato base and pork pizza category, is a must-try. 
        The combination of black pepper, cherry tomatoes, mozzarella di burrata, fior di late mozarela, olive oil, 
        Parma ham, Parmesan cheese, and rocket creates a symphony of deliciousness. Simply irresistible!""",
        """Fit for royalty! The God Save The King pizza, featuring a tomato base and exquisite pork toppings, is a culinary masterpiece. 
        The Parisian mushrooms carpaccio, ham from Paris with herbs, fior di late mozarela, and olives create a regal flavor profile. 
        A royal feast for the senses!""",
    ]
    return reviews

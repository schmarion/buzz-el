import os.path
from os import PathLike

import pytest

from buzz_el.knowledge_graph import KnowledgeGraph


@pytest.fixture(scope="session")
def pizza_bisou_kg_file_path() -> PathLike:
    ex_data_path = os.path.join(os.path.dirname(__file__), "..", "examples", "data")
    file_path = os.path.join(ex_data_path, "pizzas_bisou_sample.ttl")

    return file_path


@pytest.fixture(scope="session")
def pizza_bisou_kg(pizza_bisou_kg_file_path) -> KnowledgeGraph:
    kg = KnowledgeGraph(
        kg_file_path=pizza_bisou_kg_file_path,
        annotation_properties={"rdfs:label", "skos:altLabel"},
        lang_filter_tag="en",
        interpretation_type="RDF",
    )

    return kg

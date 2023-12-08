import os.path
from os import PathLike

import pytest

from buzz_el.graph import KnowledgeGraph, RDFGraphLoader


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
        lang_filter_tag="en"
    )

    return graph_loader

@pytest.fixture(scope="session")
def pizza_bisou_kg(pizza_bisou_rdf_graph_loader) -> KnowledgeGraph:
    kg = pizza_bisou_rdf_graph_loader()

    return kg

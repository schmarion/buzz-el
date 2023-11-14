import os.path

import pytest

from buzz_el.graph_loader import GraphLoader


@pytest.fixture(scope="session")
def graph_file_path() -> str:
    ex_data_path = os.path.join(
        os.path.dirname(__file__), "..", "..", "examples", "data"
    )
    file_path = os.path.join(ex_data_path, "pizza.ttl")

    return file_path


@pytest.fixture(scope="session")
def base_graph_loader(graph_file_path):
    annotation_properties = {"rdfs:label", "skos:prefLabel"}
    lang_filter_tag = "en"
    return GraphLoader(graph_file_path, annotation_properties, lang_filter_tag)


def test_graph_loader_init(graph_file_path):
    # Test initializing the GraphLoader object with valid parameters
    annotation_properties = {"rdfs:label", "custom:property"}
    lang_filter_tag = "en"
    graph_loader = GraphLoader(graph_file_path, annotation_properties, lang_filter_tag)

    assert graph_loader._rdf_annotation_properties == annotation_properties
    assert graph_loader._lang_filter == lang_filter_tag
    assert graph_loader.ent_str_sparql_q is not None


class TestSparqlQuery:
    def test_build_ent_str_sparql_q_base(self, base_graph_loader):
        expected_prop_path = "|".join(base_graph_loader._rdf_annotation_properties)

        assert expected_prop_path in base_graph_loader.ent_str_sparql_q

    def test_build_ent_str_sparql_q_base_full_uri(self, graph_file_path):
        full_uri_graph_loader = GraphLoader(
            graph_file_path,
            annotation_properties={
                "http://www.w3.org/2000/01/rdf-schema#label",
                "skos:prefLabel",
            },
        )
        expected_prop_path = "<http://www.w3.org/2000/01/rdf-schema#label>"

        full_uri_graph_loader.build_entity_strings_index()

        assert expected_prop_path in full_uri_graph_loader.ent_str_sparql_q
        assert "|" in full_uri_graph_loader.ent_str_sparql_q
        assert len(full_uri_graph_loader.entity_str_idx) > 0


def test_build_ent_str_sparql_q(base_graph_loader):
    expected_prop_path = "|".join(base_graph_loader._rdf_annotation_properties)

    assert expected_prop_path in base_graph_loader.ent_str_sparql_q


def test_load_kg_from_file(base_graph_loader):
    base_graph_loader.load_kg_from_file()

    assert len(base_graph_loader.kg) > 0


def test_build_entity_strings_index(base_graph_loader):
    base_graph_loader.load_kg_from_file()

    base_graph_loader.build_entity_strings_index()

    label_values = set()
    for val in base_graph_loader.entity_str_idx.values():
        label_values.update(val)

    assert len(base_graph_loader.entity_str_idx) > 0
    assert "PizzaComQueijo" not in label_values
    assert "CheesyPizza" in label_values
    assert "PizzaDecarne" not in label_values

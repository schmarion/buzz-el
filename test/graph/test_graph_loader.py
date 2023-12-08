from typing import Callable

import pytest

from buzz_el.graph import KnowledgeGraph, RDFGraphLoader


@pytest.fixture(scope="module")
def default_rdf_graph_loader(pizza_bisou_kg_file_path) -> RDFGraphLoader:
    graph_loader = RDFGraphLoader(kg_file_path=pizza_bisou_kg_file_path)

    return graph_loader


@pytest.fixture(scope="module")
def custom_rdf_graph_loader(pizza_bisou_kg_file_path) -> RDFGraphLoader:
    graph_loader = RDFGraphLoader(
        kg_file_path=pizza_bisou_kg_file_path,
        label_properties={"rdfs:label", "http://www.w3.org/2004/02/skos/core#altLabel"},
        context_properties={
            "rdfs:comment",
            "http://www.msesboue.org/o/pizza-data-demo/bisou#context_prop",
        },
        lang_filter_tag="en",
    )

    return graph_loader


class TestDefaultRDFGraphLoaderInit:
    def test_attributes(
        self, default_rdf_graph_loader, pizza_bisou_kg_file_path
    ) -> None:
        assert default_rdf_graph_loader.label_properties == {"rdfs:label"}
        assert default_rdf_graph_loader.context_properties is None
        assert str(default_rdf_graph_loader._kg_file_path) == str(
            pizza_bisou_kg_file_path
        )
        assert default_rdf_graph_loader._label_sparql_alt_path_str == "rdfs:label"
        assert default_rdf_graph_loader._context_sparql_alt_path_str is None
        assert default_rdf_graph_loader._sparql_lang_filter_str == ""
        assert default_rdf_graph_loader._lang_filter is None

    def test_load_kg_from_file(self, default_rdf_graph_loader) -> None:
        assert len(default_rdf_graph_loader.kg) > 0


class TestCustomRDFGraphLoaderInit:
    def test_attributes(
        self, custom_rdf_graph_loader, pizza_bisou_kg_file_path
    ) -> None:
        assert custom_rdf_graph_loader.label_properties == {
            "rdfs:label",
            "<http://www.w3.org/2004/02/skos/core#altLabel>",
        }
        assert custom_rdf_graph_loader.context_properties == {
            "rdfs:comment",
            "<http://www.msesboue.org/o/pizza-data-demo/bisou#context_prop>",
        }
        assert str(custom_rdf_graph_loader._kg_file_path) == str(
            pizza_bisou_kg_file_path
        )

        splitted_label_sparql_alt_path_str = (
            custom_rdf_graph_loader._label_sparql_alt_path_str.split("|")
        )
        assert "rdfs:label" in splitted_label_sparql_alt_path_str
        assert (
            "<http://www.w3.org/2004/02/skos/core#altLabel>"
            in splitted_label_sparql_alt_path_str
        )

        splitted_context_sparql_alt_path_str = (
            custom_rdf_graph_loader._context_sparql_alt_path_str.split("|")
        )
        assert "rdfs:comment" in splitted_context_sparql_alt_path_str
        assert (
            "<http://www.msesboue.org/o/pizza-data-demo/bisou#context_prop>"
            in splitted_context_sparql_alt_path_str
        )

        assert (
            custom_rdf_graph_loader._sparql_lang_filter_str
            == f'FILTER ( lang(?{custom_rdf_graph_loader._sparql_var}) = "en" )'
        )
        assert custom_rdf_graph_loader._lang_filter == "en"

    def test_load_kg_from_file(self, custom_rdf_graph_loader) -> None:
        assert len(custom_rdf_graph_loader.kg) > 0


class TestSPARQLqueries:
    def test_build_ent_labels_sparql_query(
        self, default_rdf_graph_loader, custom_rdf_graph_loader
    ) -> None:
        default_loader_query = default_rdf_graph_loader._build_ent_labels_sparql_query()
        custom_loader_query = custom_rdf_graph_loader._build_ent_labels_sparql_query()

        sparql_var = "?" + default_rdf_graph_loader._sparql_var
        assert sparql_var in default_loader_query
        assert sparql_var in custom_loader_query

        assert "FILTER" not in default_loader_query
        assert 'FILTER ( lang(?sparql_key) = "en" )' in custom_loader_query

        # test for the alternative paths
        assert "|" not in default_loader_query
        assert "|" in custom_loader_query

    def test_build_ent_context_from_labels_query(
        self, default_rdf_graph_loader, custom_rdf_graph_loader
    ) -> None:
        ent_uri = "http://www.msesboue.org/o/pizza-data-demo/bisou#_godSaveTheKing"

        default_loader_query = (
            default_rdf_graph_loader._build_ent_context_from_labels_query(ent_uri)
        )
        custom_loader_query = (
            custom_rdf_graph_loader._build_ent_context_from_labels_query(ent_uri)
        )

        sparql_var = "?" + default_rdf_graph_loader._sparql_var
        assert sparql_var in default_loader_query
        assert sparql_var in custom_loader_query

        assert "?context_ent" in default_loader_query
        assert "?context_ent" in custom_loader_query

        assert "FILTER" not in default_loader_query
        assert 'FILTER ( lang(?sparql_key) = "en" )' in custom_loader_query

        # test for the alternative paths
        assert "|" not in default_loader_query
        assert "|" in custom_loader_query

        assert ent_uri in default_loader_query
        assert ent_uri in custom_loader_query

    def test_build_ent_context_from_props_query(
        self, default_rdf_graph_loader, custom_rdf_graph_loader
    ) -> None:
        ent_uri = "http://www.msesboue.org/o/pizza-data-demo/bisou#_godSaveTheKing"

        default_loader_query = (
            default_rdf_graph_loader._build_ent_context_from_props_query(ent_uri)
        )
        custom_loader_query = (
            custom_rdf_graph_loader._build_ent_context_from_props_query(ent_uri)
        )

        sparql_var = "?" + default_rdf_graph_loader._sparql_var
        assert sparql_var in default_loader_query
        assert sparql_var in custom_loader_query

        assert "?context_ent" not in default_loader_query
        assert "?context_ent" not in custom_loader_query

        assert "FILTER" not in default_loader_query
        assert 'FILTER ( lang(?sparql_key) = "en" )' in custom_loader_query

        # test for the alternative paths
        assert "|" not in default_loader_query
        assert "|" in custom_loader_query

        assert ent_uri in default_loader_query
        assert ent_uri in custom_loader_query


class TestDefaultRDFGraphLoader:
    def test_build_patterns_default_loader(self, default_rdf_graph_loader) -> None:
        patterns = default_rdf_graph_loader.build_patterns()

        assert {
            "label": "KG_ENT",
            "pattern": "honey",
            "id": "http://www.msesboue.org/o/pizza-data-demo/bisou#_honey",
        } in patterns
        assert {
            "label": "KG_ENT",
            "pattern": "miel",
            "id": "http://www.msesboue.org/o/pizza-data-demo/bisou#_honey",
        } in patterns
        assert {
            "label": "KG_ENT",
            "pattern": "God save the king",
            "id": "http://www.msesboue.org/o/pizza-data-demo/bisou#_godSaveTheKing",
        } in patterns
        assert {
            "label": "KG_ENT",
            "pattern": "dieu sauve le roi",
            "id": "http://www.msesboue.org/o/pizza-data-demo/bisou#_godSaveTheKing",
        } not in patterns

    def test_build_patterns_custom_loader(self, custom_rdf_graph_loader) -> None:
        patterns = custom_rdf_graph_loader.build_patterns()

        assert {
            "label": "KG_ENT",
            "pattern": "honey",
            "id": "http://www.msesboue.org/o/pizza-data-demo/bisou#_honey",
        } in patterns
        assert {
            "label": "KG_ENT",
            "pattern": "miel",
            "id": "http://www.msesboue.org/o/pizza-data-demo/bisou#_honey",
        } not in patterns
        assert {
            "label": "KG_ENT",
            "pattern": "God save the king",
            "id": "http://www.msesboue.org/o/pizza-data-demo/bisou#_godSaveTheKing",
        } in patterns
        assert {
            "label": "KG_ENT",
            "pattern": "dieu sauve le roi",
            "id": "http://www.msesboue.org/o/pizza-data-demo/bisou#_godSaveTheKing",
        } not in patterns

        assert {
            "label": "KG_ENT",
            "pattern": "pepper",
            "id": "http://www.msesboue.org/o/pizza-data-demo/bisou#_blackPepper",
        } in patterns


class TestGetContext:
    def test_kg_get_context_default_loader(self, default_rdf_graph_loader) -> None:
        get_context = default_rdf_graph_loader.kg_get_context()

        context_string = get_context(
            "http://www.msesboue.org/o/pizza-data-demo/bisou#_burraTadah"
        )

        assert "pizza au porc" in context_string
        assert "pork pizza" in context_string
        assert "black pepper" in context_string
        assert "poivre" in context_string
        assert "pepper" in context_string
        assert "Burra'tadah!" not in context_string

    def test_kg_get_context_custom_loader(self, custom_rdf_graph_loader) -> None:
        get_context = custom_rdf_graph_loader.kg_get_context()

        context_string = get_context(
            "http://www.msesboue.org/o/pizza-data-demo/bisou#_burraTadah"
        )

        assert (
            context_string
            == "The 'BurraTadah' pizza features a tomato base and falls under the"
            " category of 'pork pizzas.' Its delectable toppings include black"
            " pepper, cherry tomatoes, mozzarella di burrata, fior di latte"
            " mozzarella, olive oil, Parma ham, Parmesan cheese, and rocket."
        )
        assert (
            "La pizza 'BurraTadah' présente une base de tomate et appartient à la"
            " catégorie des pizzas au porc. Ses garnitures délicieuses comprennent du"
            " poivre noir, des tomates cerises, de la mozzarella di burrata, de la"
            " mozzarella fior di latte, de l'huile d'olive, du jambon de Parme, du"
            " fromage Parmesan et de la roquette."
            not in context_string
        )


class TestBuildKG:
    def test_build_knowledge_graph_default_loader(
        self, default_rdf_graph_loader
    ) -> None:
        kg_instance = default_rdf_graph_loader.build_knowledge_graph()

        test_endpoint_q = """
            SELECT ?sparql_key WHERE {
                <http://www.msesboue.org/o/pizza-data-demo/bisou#_blackPepper> rdfs:label ?sparql_key .
            }
        """
        test_q_res = [
            str(r["sparql_key"]) for r in kg_instance.sparql_endpoint(test_endpoint_q)
        ]

        assert isinstance(kg_instance, KnowledgeGraph)
        assert "black pepper" in test_q_res
        assert "poivre noir" in test_q_res
        assert len(kg_instance.kg) > 0
        assert len(kg_instance.entity_patterns) > 0
        assert isinstance(kg_instance.get_context, Callable) > 0

    def test_build_knowledge_graph_custom_loader(self, custom_rdf_graph_loader) -> None:
        kg_instance = custom_rdf_graph_loader.build_knowledge_graph()

        test_endpoint_q = """
            SELECT ?sparql_key WHERE {
                <http://www.msesboue.org/o/pizza-data-demo/bisou#_blackPepper> rdfs:label ?sparql_key .
            }
        """
        test_q_res = [
            str(r["sparql_key"]) for r in kg_instance.sparql_endpoint(test_endpoint_q)
        ]

        assert isinstance(kg_instance, KnowledgeGraph)
        assert "black pepper" in test_q_res
        assert "poivre noir" in test_q_res
        assert len(kg_instance.kg) > 0
        assert len(kg_instance.entity_patterns) > 0
        assert isinstance(kg_instance.get_context, Callable) > 0

    def test_call_graph_default_loader(self, default_rdf_graph_loader) -> None:
        kg_instance = default_rdf_graph_loader()

        test_endpoint_q = """
            SELECT ?sparql_key WHERE {
                <http://www.msesboue.org/o/pizza-data-demo/bisou#_blackPepper> rdfs:label ?sparql_key .
            }
        """
        test_q_res = [
            str(r["sparql_key"]) for r in kg_instance.sparql_endpoint(test_endpoint_q)
        ]

        assert isinstance(kg_instance, KnowledgeGraph)
        assert "black pepper" in test_q_res
        assert "poivre noir" in test_q_res
        assert len(kg_instance.kg) > 0
        assert len(kg_instance.entity_patterns) > 0
        assert isinstance(kg_instance.get_context, Callable) > 0

    def test_call_graph_custom_loader(self, custom_rdf_graph_loader) -> None:
        kg_instance = custom_rdf_graph_loader()

        test_endpoint_q = """
            SELECT ?sparql_key WHERE {
                <http://www.msesboue.org/o/pizza-data-demo/bisou#_blackPepper> rdfs:label ?sparql_key .
            }
        """
        test_q_res = [
            str(r["sparql_key"]) for r in kg_instance.sparql_endpoint(test_endpoint_q)
        ]

        assert isinstance(kg_instance, KnowledgeGraph)
        assert "black pepper" in test_q_res
        assert "poivre noir" in test_q_res
        assert len(kg_instance.kg) > 0
        assert len(kg_instance.entity_patterns) > 0
        assert isinstance(kg_instance.get_context, Callable) > 0

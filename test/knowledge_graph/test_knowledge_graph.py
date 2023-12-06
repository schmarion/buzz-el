import pytest

from buzz_el.knowledge_graph import KnowledgeGraph


@pytest.fixture(scope="module")
def default_kg(pizza_bisou_kg_file_path) -> KnowledgeGraph:
    kg = KnowledgeGraph(kg_file_path=pizza_bisou_kg_file_path)
    return kg


class TestKGinit:
    def test_default_init(self, default_kg) -> None:
        assert default_kg.annotation_properties == {"rdfs:label"}
        assert default_kg._sparql_alternative_path_str == "rdfs:label"
        assert default_kg._lang_filter is None
        assert default_kg._sparql_lang_filter_str == ""
        assert default_kg.interpretation_type == "RDF"
        assert len(default_kg.kg) > 0

        pattern = default_kg.entity_patterns[0]
        assert pattern.get("label") == "KG_ENT"
        assert isinstance(pattern.get("pattern"), str)
        assert isinstance(pattern.get("id"), str)

    def test_extracted_ent_labels(self, default_kg) -> None:
        labels = {pattern["pattern"] for pattern in default_kg.entity_patterns}

        assert "miel" in labels
        assert "Burrata" not in labels


def test_build_patterns_from_rdf(pizza_bisou_kg) -> None:
    patterns = pizza_bisou_kg.build_patterns_from_rdf()

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


def test_build_patterns(pizza_bisou_kg) -> None:
    assert pizza_bisou_kg.entity_patterns == pizza_bisou_kg.build_patterns()


def test_get_context(pizza_bisou_kg) -> None:
    context_labels = set(
        pizza_bisou_kg.get_context(
            entity_uri="http://www.msesboue.org/o/pizza-data-demo/bisou#_godSaveTheKing"
        )
    )

    assert context_labels == {
        "tomato base",
        "pork pizza",
        "carpaccio de champignons de Paris",
        "jambon de Paris with herbs",
        "Mozzarella Fior Di Latte",
        "Mozzarella",
        "olive",
    }


class TestSPARQLqueries:
    def test_build_ent_str_sparql_query(self, default_kg, pizza_bisou_kg) -> None:
        default_kg_query = default_kg._build_ent_str_sparql_query()
        pizza_bisou_kg_query = pizza_bisou_kg._build_ent_str_sparql_query()

        assert "FILTER" not in default_kg_query
        assert 'FILTER ( lang(?label) = "en" )' in pizza_bisou_kg_query

        # test for the alternative paths
        assert "|" not in default_kg_query
        assert "|" in pizza_bisou_kg_query

    def test_build_ent_context_sparql_query(self, default_kg, pizza_bisou_kg) -> None:
        ent_uri = "http://www.msesboue.org/o/pizza-data-demo/bisou#_godSaveTheKing"

        default_kg_query = default_kg._build_ent_context_sparql_query(ent_uri)
        pizza_bisou_kg_query = pizza_bisou_kg._build_ent_context_sparql_query(ent_uri)

        assert "FILTER" not in default_kg_query
        assert 'FILTER ( lang(?label) = "en" )' in pizza_bisou_kg_query

        # test for the alternative paths
        assert "|" not in default_kg_query
        assert "|" in pizza_bisou_kg_query

        assert ent_uri in default_kg_query
        assert ent_uri in pizza_bisou_kg_query

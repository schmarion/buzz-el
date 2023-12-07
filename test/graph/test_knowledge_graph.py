import pytest
from rdflib import Graph, URIRef

from buzz_el.graph import KnowledgeGraph


@pytest.fixture(scope="module")
def my_graph() -> Graph:
    g = Graph()
    g.add((URIRef("subject"), URIRef("predicate"), URIRef("object")))
    g.add((URIRef("sujet"), URIRef("predicat"), URIRef("objet")))

    return g

@pytest.fixture(scope="module")
def knowledge_graph(my_graph) -> KnowledgeGraph:

    knowledge_graph = KnowledgeGraph(
        kg=my_graph,
        entity_patterns=[
            {
                "label": "KG_ENT", 
                "pattern": "entity phrase pattern",
                "id": "entity uri"
            }
        ],
        get_entity_context= lambda ent_uri: "entity context",
    )

    return knowledge_graph

def test_knowledge_graph(knowledge_graph) -> None:

    assert isinstance(knowledge_graph.kg, Graph)
    assert len(knowledge_graph.kg) == 2

    assert len(knowledge_graph.entity_patterns) == 1
    assert knowledge_graph.entity_patterns[0] == {
                "label": "KG_ENT", 
                "pattern": "entity phrase pattern",
                "id": "entity uri"
            }
    assert knowledge_graph.get_context("my_entity") == "entity context"

    test_endpoint_q = """
            SELECT ?s ?p ?o WHERE {
                ?s ?p ?o .
            }
        """
    test_q_res = [(str(r["s"]), str(r["p"]), str(r["o"])) for r in knowledge_graph.sparql_endpoint(test_endpoint_q)]

    assert ("subject", "predicate", "object") in test_q_res
    assert ("sujet", "predicat", "objet") in test_q_res
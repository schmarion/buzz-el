from typing import Any, Callable, Dict, Iterable, List


class KnowledgeGraph:
    """
    A class to interact with a knowledge graph.

    Instances of this class are typically built by a graph loader.

    Attributes
    ----------
    kg: Any
        The KG object.
    entity_patterns: List[Dict[str, str]]
        The entity patterns.
    get_context : Callable[[str], str]
        Callable to fetch the context string of an entity.
    """

    def __init__(
        self,
        kg: Any,
        entity_patterns: List[Dict[str, str]],
        get_entity_context: Callable[[str], str],
    ) -> None:
        """Initialise the knowledge graph object.

        Parameters
        ----------
        kg: Any
            The KG object.
        entity_patterns: List[Dict[str, str]]
            The entity patterns.
        get_entity_context : Callable[[str], str]
            Callable to fetch the context string of an entity.
        """

        self.kg = kg
        self.entity_patterns = entity_patterns
        self.get_context = get_entity_context

    def sparql_endpoint(self, sparql_query: str) -> Iterable:
        """SPARQL endpoint to query the knowledge graph.

        Parameters
        ----------
        sparql_query : str
            The SPARQL query to run.

        Returns
        -------
        Iterable
            Iterable over the query results.
        """
        res_iter = self.kg.query(sparql_query)
        return res_iter

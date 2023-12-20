from os import PathLike
from typing import Callable, Dict, List, Optional, Set

from rdflib import Graph

from ..commons.utils import is_valid_url
from .graph_loader import GraphLoader
from .knowledge_graph import KnowledgeGraph


class RDFGraphLoader(GraphLoader):
    """
    A class to build a knowledge graph instance.

    Attributes
    ----------
    kg_file_path : PathLike
        The path to the knowledge graph file.
    kg: rdflib.Graph
        The knowledge graph object.
    label_properties : Set[str]
        Set of relations used to link entities to their labels, by default {"rdfs:label"}.
    _label_properties : Set[str]
        Same relations as label_properties but processed to be used in a SPARQL query.
    context_properties : Set[str]
        Set of relations used to link entities to their context strings, by default None.
    _context_properties : Set[str]
        Same relations as context_properties but processed to be used in a SPARQL query.
    _label_sparql_alt_path_str: str
        Constructed alternative entity labels paths for use in SPARQL queries.
    _context_sparql_alt_path_str: str
        Constructed alternative entity context strings paths for use in SPARQL queries,
        by default None.
    _sparql_var: str
        Name of the SPARQL variable to use when processing SPARQL results.
        It is an attribute to make sure all SPARQL queries use the same variable name.
    _lang_filter : str
        Language filter tag to filter entity labels and context strings based on language,
        by default None.
    _sparql_lang_filter_str: str
        The portion of the SPARQL query constituting the language filter.
    """

    def __init__(
        self,
        kg_file_path: PathLike,
        label_properties: Optional[Set[str]] = None,
        context_properties: Optional[Set[str]] = None,
        lang_filter_tag: Optional[str] = None,
    ) -> None:
        """Initialise the RDF graph loader object.

        Parameters
        ----------
        kg_file_path : PathLike
            The path to the knowledge graph file.
        label_properties : Optional[Set[str]], optional
            Set of relations used to link entities to their labels, by default {"rdfs:label"}.
        context_properties : Optional[Set[str]], optional
            Set of relations used to link entities to their context strings, by default None.
        lang_filter_tag : Optional[str], optional
            Language filter tag to filter entity labels and context strings based on language,
            by default None.
        """

        super().__init__(kg_file_path)

        self._label_properties = {"rdfs:label"}
        self.label_properties = label_properties

        self._context_properties = None
        self.context_properties = context_properties

        self._label_sparql_alt_path_str = "|".join(self._label_properties)

        if self._context_properties is None:
            self._context_sparql_alt_path_str = None
        else:
            self._context_sparql_alt_path_str = "|".join(self._context_properties)

        self._sparql_var = "sparql_key"

        self._lang_filter = lang_filter_tag
        self._sparql_lang_filter_str = (
            f'FILTER ( lang(?{self._sparql_var}) = "{self._lang_filter}" )'
            if self._lang_filter
            else ""
        )

        self.entity_patterns = self.build_patterns()

    @property
    def label_properties(self) -> Set[str]:
        """Getter for the label properties attribute.

        Returns
        -------
        Set[str]
            The set of label properties.
        """
        return self._label_properties

    @label_properties.setter
    def label_properties(self, props: Set[str]) -> None:
        """Setter for the label properties attribute.

        Ensure properties'strings are ready to be used in a SPARQL query.

        Parameters
        ----------
        props : Set[str]
            The label properties.
        """
        if props is not None:
            label_properties = set()
            # we need to add <uri> if a full URI is provided
            for prop in props:
                if is_valid_url(prop):
                    label_properties.add(f"<{prop}>")
                else:
                    label_properties.add(prop)

            self._label_properties = label_properties

    @property
    def context_properties(self) -> Set[str]:
        """Getter for the context properties attribute.

        Returns
        -------
        Set[str]
            The set of context properties.
        """
        return self._context_properties

    @context_properties.setter
    def context_properties(self, props: Set[str]) -> None:
        """Setter for the context properties attribute.

        Ensure properties'strings are ready to be used in a SPARQL query.

        Parameters
        ----------
        props : Set[str]
            The context properties.
        """
        if props is not None:
            context_properties = set()
            # we need to add <uri> if a full URI is provided
            for prop in props:
                if is_valid_url(prop):
                    context_properties.add(f"<{prop}>")
                else:
                    context_properties.add(prop)

            self._context_properties = context_properties

    def __call__(self) -> KnowledgeGraph:
        """Builds and return the knowledge graph instance.

        Returns
        -------
        KnowledgeGraph
            The knowledge graph instance.
        """
        kg_instance = self.build_knowledge_graph()

        return kg_instance

    def load_kg_from_file(self) -> Graph:
        """Load the knowledge graph from the specified file."""

        kg = Graph()
        kg.parse(self._kg_file_path)

        return kg

    def build_patterns(self) -> List[Dict[str, str]]:
        """Build the entity patterns.

        Returns
        -------
        List[Dict[str, str]]
            The entity patterns.
        """
        query = self._build_ent_labels_sparql_query()

        sparql_res = self.kg.query(query)

        patterns = []
        for res in sparql_res:
            patterns.append(
                {
                    "label": "KG_ENT",
                    "pattern": str(res[self._sparql_var]),
                    "id": str(res["ent_uri"]),
                }
            )

        return patterns

    def _build_ent_labels_sparql_query(self) -> str:
        """
        Build the SPARQL query for extracting distinct entity URIs and labels.

        The query is based on the specified label properties and language filter.
        """
        sparql_q_ent_labels = f"""
            SELECT DISTINCT ?ent_uri ?{self._sparql_var} WHERE {{
                ?ent_uri {self._label_sparql_alt_path_str} ?{self._sparql_var} .
                {self._sparql_lang_filter_str}
            }}
        """
        return sparql_q_ent_labels

    def _build_ent_context_from_labels_query(self, entity_uri: str) -> str:
        """
        Build the SPARQL query for extracting an entity context string from the surrounding
        entities.

        The query is based on the specified label properties and language filter.
        """
        ent_context_query = f"""
            SELECT DISTINCT ?{self._sparql_var} WHERE {{
                <{entity_uri}>  ?p  ?context_ent .
                ?context_ent {self._label_sparql_alt_path_str} ?{self._sparql_var} .
                {self._sparql_lang_filter_str}
            }}
        """

        return ent_context_query

    def _build_ent_context_from_props_query(self, entity_uri: str) -> str:
        """
        Build the SPARQL query for extracting an entity context string from the specified context properties.

        The query is based on the specified context properties and language filter.
        """
        ent_context_query = f"""
            SELECT DISTINCT ?{self._sparql_var} WHERE {{
                <{entity_uri}> {self._context_sparql_alt_path_str} ?{self._sparql_var} .
                {self._sparql_lang_filter_str}
            }}
        """

        return ent_context_query

    def kg_get_context(self) -> Callable[[str], str]:
        """Build and return the knowledge graph instance get_context method.

        Returns
        -------
        Callable[[str], str]
            The get_context method.
        """

        if self.context_properties is not None:
            get_sparql_query = self._build_ent_context_from_props_query
        else:
            get_sparql_query = self._build_ent_context_from_labels_query

        def get_context(entity_uri: str) -> str:
            sparql_query = get_sparql_query(entity_uri)

            sparql_res = self.kg.query(sparql_query)

            ent_context_strings = []
            for res in sparql_res:
                ent_context_strings.append(res[self._sparql_var])

            context_string = " ".join(ent_context_strings)

            return context_string

        return get_context

    def build_knowledge_graph(self) -> KnowledgeGraph:
        """Builds and return the knowledge graph instance.

        Returns
        -------
        KnowledgeGraph
            The knowledge graph instance.
        """

        entity_patterns = self.build_patterns()
        get_context = self.kg_get_context()

        kg_instance = KnowledgeGraph(
            kg=self.kg, entity_patterns=entity_patterns, get_entity_context=get_context
        )

        return kg_instance

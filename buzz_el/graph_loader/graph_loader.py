from collections import defaultdict
from typing import Any, Dict, Optional, Set

from rdflib import Graph
from spacy.util import ensure_path

from buzz_el.commons.utils import is_valid_url


class GraphLoader:
    """
    A class for loading a knowledge graph, extracting entity labels, and building an index.

    Parameters
    ----------
    kg_file_path : Any
        The path to the knowledge graph file.
    annotation_properties : Optional[Set[str]], optional
        Set of RDF annotation properties used to extract entity labels, by default {"rdfs:label"}.
    lang_filter_tag : Optional[str], optional
        Language filter tag to filter entity labels based on language, by default None.

    Attributes
    ----------
    kg : rdflib.graph.Graph
        The knowledge graph.
    entity_str_idx : defaultdict
        A dictionary mapping entity URIs to sets of associated labels.
    ent_str_sparql_q : str or None
        The SPARQL query for extracting distinct entity URIs and labels.

    Methods
    -------
    build_ent_str_sparql_q()
        Build the SPARQL query for extracting entity labels based on annotation properties and language filter.
    load_kg_from_file()
        Load the knowledge graph from the specified file.
    build_entity_strings_index()
        Build the index of entity strings by querying the knowledge graph.
    """

    def __init__(
        self,
        kg_file_path: Any,
        annotation_properties: Optional[Set[str]] = None,
        lang_filter_tag: Optional[str] = None,
    ) -> None:
        """Initialiser for the graph loader.

        Parameters
        ----------
        kg_file_path : Any
            The path to the knowledge graph file.
        annotation_properties : Optional[Set[str]], optional
            Set of RDF annotation properties used to extract entity labels, by default {"rdfs:label"}.
        lang_filter_tag : Optional[str], optional
            Language filter tag to filter entity labels based on language, by default None.
        """
        self._kg_file_path = ensure_path(kg_file_path)
        self._rdf_annotation_properties = (
            annotation_properties if annotation_properties else {"rdfs:label"}
        )
        self._lang_filter = lang_filter_tag

        self.kg = Graph()
        self.load_kg_from_file()
        self._entity_str_idx = None

        self.ent_str_sparql_q = None
        self.build_ent_str_sparql_q()

    @property
    def entity_str_idx(self) -> Dict[str, Set[str]]:
        """Getter for the entity strings index.

        Returns
        -------
        Dict[str, Set[str]]
            The built self._entity_str_idx attribute.
        """
        if self._entity_str_idx is None:
            self.build_entity_strings_index()

        return self._entity_str_idx

    def build_ent_str_sparql_q(self) -> None:
        """
        Build the SPARQL query for extracting distinct entity URIs and labels.

        The query is based on the specified RDF annotation properties and language filter.
        """
        annotation_properties = []
        # we need to add <uri> if a full URI is provided
        for prop in self._rdf_annotation_properties:
            if is_valid_url(prop):
                annotation_properties.append(f"<{prop}>")
            else:
                annotation_properties.append(prop)

        sparql_alternative_path_str = "|".join(annotation_properties)
        sparql_lang_filter_str = (
            f'FILTER ( lang(?label) = "{self._lang_filter}" )'
            if self._lang_filter
            else ""
        )
        sparql_q_ent_labels = f"""
            SELECT DISTINCT ?ent_uri ?label WHERE {{
                ?ent_uri {sparql_alternative_path_str} ?label .
                {sparql_lang_filter_str}
            }}
        """
        self.ent_str_sparql_q = sparql_q_ent_labels

    def load_kg_from_file(self) -> None:
        """Load the knowledge graph from the specified file."""
        self.kg = self.kg.parse(self._kg_file_path)

    def build_entity_strings_index(self) -> None:
        """Build the index of entity strings by querying the knowledge graph."""
        self._entity_str_idx = defaultdict(set)
        for r in self.kg.query(self.ent_str_sparql_q):
            self._entity_str_idx[str(r["ent_uri"])].add(str(r["label"]))

from os import PathLike
from typing import Dict, Iterable, List, Optional, Set

from rdflib import Graph
from spacy.util import ensure_path

from ..commons.utils import is_valid_url


class KnowledgeGraph:
    """
    A class for loading a knowledge graph and interacting with it.

    Parameters
    ----------
    kg_file_path : PathLike
        The path to the knowledge graph file.
    annotation_properties : Optional[Set[str]], optional
        Set of RDF annotation properties used to extract entity labels, by default {"rdfs:label"}.
    lang_filter : Optional[str], optional
        Language filter tag to filter entity labels based on language, by default None.
    interpretation_type: Enum["RDF", "RDFS", "OWL"], optional
        Tag specifying how to interpret the KG file, by default "RDF".

    Attributes
    ----------
    _kg_file_path : PathLike
        The path to the knowledge graph file.
    annotation_properties : Optional[Set[str]], optional
        Set of RDF annotation properties used to extract entity labels, by default {"rdfs:label"}.
    _annotation_properties: Set[str]
        Annotation properties processed to be used directly in a SPARQL query.
    _lang_filter : Optional[str], optional
        Language filter tag to filter entity labels based on language, by default None.
    _sparql_alternative_path_str: str
        The portion of the SPARQL query constituting the alternative paths. 
    _sparql_lang_filter_str: str
        The portion of the SPARQL query constituting the language filter.
    _interpretation_type: Enum["RDF", "RDFS", "OWL"], optional
        Tag specifying how to interpret the KG file, by default "RDF".
    kg: Graph
        The KG object.
    entity_patterns: List[Dict[str, str]]
        The entity patterns.
    """
    def __init__(
        self,
        kg_file_path: PathLike,
        annotation_properties: Optional[Set[str]] = None,
        lang_filter_tag: Optional[str] = None,
        interpretation_type: Optional[str] = None
    ) -> None:
        """Initialise the knowledge graph object.

        Parameters
        ----------
        kg_file_path : PathLike
            The path to the knowledge graph file.
        annotation_properties : Optional[Set[str]], optional
            Set of RDF annotation properties used to extract entity labels, by default {"rdfs:label"}.
        lang_filter_tag : Optional[str], optional
            Language filter tag to filter entity labels based on language, by default None.
        interpretation_type : Optional[str], optional
           Tag specifying how to interpret the KG file, by default "RDF".
        """
        self._kg_file_path = ensure_path(kg_file_path)

        self._annotation_properties = {"rdfs:label"}
        self.annotation_properties = annotation_properties

        self._sparql_alternative_path_str = "|".join(self.annotation_properties)

        self._lang_filter = lang_filter_tag
        self._sparql_lang_filter_str = (
            f'FILTER ( lang(?label) = "{self._lang_filter}" )'
            if self._lang_filter
            else ""
        )

        self._interpretation_type = None
        self.interpretation_type = interpretation_type

        self.kg = Graph()
        self.load_kg_from_file()

        self.entity_patterns = self.build_patterns()

    @property
    def interpretation_type(self) -> str:
        """Getter for the interpretation type attribute.

        Returns
        -------
        str
            The interpretation type attribute.
        """
        return self._interpretation_type
    
    @interpretation_type.setter
    def interpretation_type(self, interpretation: str) -> None:
        """Getter for the interpretation type attribute.

        Parameters
        ----------
        interpretation : str
            The interpretation type. Must be one of ["RDF", "RDFS", "OWL"].
            Default to "RDF".
        """
        if interpretation in ["RDF", "RDFS", "OWL"]:
            self._interpretation_type = interpretation
        else:
            self._interpretation_type = "RDF"

    @property
    def annotation_properties(self) -> Set[str]:
        """Getter for the annotation properties attribute.

        Returns
        -------
        Set[str]
            The annotation properties attribute.
        """
        return self._annotation_properties

    @annotation_properties.setter
    def annotation_properties(self, props: Set[str]) -> None:
        """Setter for the annotation properties attribute.

        Makes sure the annotation properties are ready to be used in a 
        SPARQL query.

        Parameters
        ----------
        props : Set[str]
            The annotation properties.    
        """
        if props is not None:
            annotation_properties = set()
            # we need to add <uri> if a full URI is provided
            for prop in props:
                if is_valid_url(prop):
                    annotation_properties.add(f"<{prop}>")
                else:
                    annotation_properties.add(prop)

            self._annotation_properties = annotation_properties

    def load_kg_from_file(self) -> None:
        """Load the knowledge graph from the specified file."""
        self.kg.parse(self._kg_file_path)

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

    def build_patterns(self) -> List[Dict[str, str]]:
        """Build the entity patterns based on the interpretation type.

        Returns
        -------
        List[Dict[str, str]]
            The entity patterns.

        Raises
        ------
        NotImplementedError
            Error for the interpretation types not yet implemented.
        """
        patterns = []

        if self.interpretation_type == "RDFS":
            raise NotImplementedError
        elif self.interpretation_type == "OWL":
            raise NotImplementedError
        else: # default to RDF (even if wrong value for interpretation type)
            patterns = self.build_patterns_from_rdf()

        return patterns

    def build_patterns_from_rdf(self) -> List[Dict[str, str]]:
        """Build the entity patterns specifically for the interpretation type "RDF".

        Returns
        -------
        List[Dict[str, str]]
            The entity patterns.
        """
        query = self._build_ent_str_sparql_query()

        sparql_res = self.sparql_endpoint(sparql_query=query)

        patterns = []
        for res in sparql_res:
            patterns.append({
                "label": "KG_ENT", 
                "pattern": str(res["label"]),
                "id": str(res["ent_uri"])
            })

        return patterns

    def get_context(self, entity_uri: str) -> List[str]:
        """Fetch an entity context.

        Parameters
        ----------
        entity_uri : str
            The URI of the entity to fetch the context from.

        Returns
        -------
        List[str]
            The list of labels from the context entities.
        """
        query = self._build_ent_context_sparql_query(entity_uri)

        sparql_res = self.sparql_endpoint(sparql_query=query)

        context_texts = []
        for res in sparql_res:
            context_texts.append(str(res["label"]))

        return context_texts

    def _build_ent_str_sparql_query(self) -> str:
        """
        Build the SPARQL query for extracting distinct entity URIs and labels.

        The query is based on the specified RDF annotation properties and language filter.
        """
        sparql_q_ent_labels = f"""
            SELECT DISTINCT ?ent_uri ?label WHERE {{
                ?ent_uri {self._sparql_alternative_path_str} ?label .
                {self._sparql_lang_filter_str}
            }}
        """
        return sparql_q_ent_labels

    def _build_ent_context_sparql_query(self, entity_uri: str) -> str:
        """
        Build the SPARQL query for extracting an entity context.

        The query is based on the specified RDF annotation properties and language filter.
        """
        ent_context_query = f"""
            SELECT DISTINCT ?label WHERE {{
                <{entity_uri}>  ?p  ?context_ent .
                ?context_ent {self._sparql_alternative_path_str} ?label .
                {self._sparql_lang_filter_str}
            }}
        """

        return ent_context_query

from abc import ABC, abstractmethod
from os import PathLike
from typing import Callable, Dict, List

from spacy.util import ensure_path

from .knowledge_graph import KnowledgeGraph


class GraphLoader(ABC):
    """Abstract class for the graph loaders.

    Parameters
    ----------
    kg_file_path : PathLike
        The path to the knowledge graph file.
    kg: Any
        The knowledge graph object.
    """
    def __init__(self, kg_file_path: PathLike) -> None:
        """Initialise the RDF graph loader object.

        Parameters
        ----------
        kg_file_path : PathLike
            The path to the knowledge graph file.
        """
        self._kg_file_path = ensure_path(kg_file_path)

        self.kg = self.load_kg_from_file()

    @abstractmethod
    def load_kg_from_file(self) -> None:
        """Load the knowledge graph from the specified file."""

    @abstractmethod
    def build_patterns(self) -> List[Dict[str, str]]:
        """Build the entity patterns.

        Returns
        -------
        List[Dict[str, str]]
            The entity patterns.
        """

    @abstractmethod
    def kg_get_context(self) -> Callable[[str], str]:
        """Build and return the knowledge graph instance get context method.

        Returns
        -------
        Callable[[str], str]
            The get context method.
        """

    @abstractmethod
    def build_knowledge_graph(self) -> KnowledgeGraph:
        """Builds and return the knowledge graph instance.

        Returns
        -------
        KnowledgeGraph
            The knowledge graph instance.
        """
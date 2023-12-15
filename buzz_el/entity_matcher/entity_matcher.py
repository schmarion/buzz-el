from typing import Dict, Iterable, Optional

from spacy.language import Language
from spacy.pipeline import SpanRuler
from spacy.tokens import Doc

from ..graph import KnowledgeGraph
from .fuzzy_ruler import FuzzyRuler


class EntityMatcher:
    """
    A class to construct an entity matcher from a knowledge graph.

    Parameters
    ----------
    knowledge_graph : KnowledgeGraph
        The knowledge graph to match the entities.
    spacy_model : Language
        The spaCy model to use in internal spaCy components.
    ignore_case : Optional[bool], optional
        Whether to ignore case, by default True.
    min_r : Optional[int], optional
        TODO, by default None
    fuzzy_func : Optional[str], optional
        The fuzzy matching function to use, by default None.

    Attributes
    ----------
    kg : KnowledgeGraph
        The knowledge graph to match the entities.
    spacy_model : Language
        The spaCy model to use in internal spaCy components.
    ignore_case : bool
        Whether to ignore case.
    _string_matcher: Callable[spacy.tokens.Doc, spacy.tokens.Doc]
        The string matcher component matching entities through string alignment.
    _fuzzy_matcher: Callable[spacy.tokens.Doc, spacy.tokens.Doc]
        The fuzzy matcher component matching entities through string fuzzy alignment.
    _string_matcher_config : Dict
        Configuration for the spaCy span ruler used for string matching,
        by default {"spans_key": "string"}.
        See: <https://spacy.io/api/spanruler#config>
    _fuzzy_matcher_config : Dict
        Configuration for the custom fuzzy ruler used for fuzzy matching,
        by default {"spans_key": "fuzzy"}.
    """

    def __init__(
        self,
        knowledge_graph: KnowledgeGraph,
        spacy_model: Language,
        ignore_case: Optional[bool] = True,
        use_fuzzy: Optional[bool] = False,
        # min_r: Optional[int] = None,
        # fuzzy_func: Optional[str] = None,
    ) -> None:
        """Initialiser for the entity matcher.

        Parameters
        ----------
        knowledge_graph : KnowledgeGraph
            The knowledge graph to match the entities.
        spacy_model : Language
            The spaCy model to use in internal spaCy components.
        ignore_case : Optional[bool], optional
            Whether to ignore case, by default True.
        min_r : Optional[int], optional
            TODO, by default None
        fuzzy_func : Optional[str], optional
            The fuzzy matching function to use, by default None.
        """
        self.spacy_model = spacy_model
        self.kg = knowledge_graph
        self.ignore_case = ignore_case
        # self.min_r = min_r
        # self.fuzzy_func = fuzzy_func

        # self._string_matcher_config = {"spans_key": "string"}

        # if self.ignore_case:
        # self._string_matcher_config["phrase_matcher_attr"] = "LOWER"

        self._string_matcher = None
        self.build_string_matcher()

        # self._fuzzy_matcher_config = {"spans_key": "fuzzy"}
        self._fuzzy_matcher = None
        if use_fuzzy:
            self.build_fuzzy_matcher()

    def __call__(self, doc: Doc) -> Doc:
        """
        Apply the entity matching to a spaCy doc.

        Parameters
        ----------
        doc : Doc
            The spaCy doc to process.
        """
        if self._string_matcher is None:
            self.build_string_matcher()
        else:
            doc = self._string_matcher(doc)

        if self._fuzzy_matcher is not None:
            doc = self._fuzzy_matcher(doc)

        return doc

    def pipe(self, docs: Iterable[Doc]) -> Iterable[Doc]:
        """
        Apply the entity matching component to an iterable of spaCy docs.

        Parameters
        ----------
        docs : Iterable[Doc]
            An iterable of spaCy docs to process.

        Returns
        -------
        Iterable
            An iterable of processed spaCy docs.
        """
        for doc in docs:
            processed_doc = self(doc)
            yield processed_doc

    def build_string_matcher(self, config: Optional[Dict] = None) -> None:
        """
        Build the entity string matcher.

        This method updates the self._string_matcher attribute.

        Parameters
        ----------
        config : Optional[Dict], optional
            Configuration for the spaCy span ruler, by default None.
        """
        if config is None:
            string_matcher_config = {"spans_key": "string"}
            if self.ignore_case:
                string_matcher_config["phrase_matcher_attr"] = "LOWER"
            ruler = SpanRuler(self.spacy_model, **string_matcher_config)
        else:
            ruler = SpanRuler(self.spacy_model, **config)

        ruler.add_patterns(self.kg.entity_patterns)

        self._string_matcher = ruler

    def build_fuzzy_matcher(self, config: Optional[Dict] = None) -> None:
        """
        Build the entity fuzzy matcher.

        This method updates the self._fuzzy_matcher attribute.

        Parameters
        ----------
        config : Optional[Dict], optional
            Configuration for the custom fuzzy ruler, by default None.
        """
        spans_key = "fuzzy"
        if config is not None:
            ruler = FuzzyRuler(
                self.spacy_model,
                self.ignore_case,
                spans_key,
                **config,
                # self.min_r,
                # self.fuzzy_func,
            )
        else:
            ruler = FuzzyRuler(
                self.spacy_model,
                self.ignore_case,
                spans_key,
                # self.min_r,
                # self.fuzzy_func,
            )

        ruler.add_patterns(self.kg.entity_patterns)
        self._fuzzy_matcher = ruler

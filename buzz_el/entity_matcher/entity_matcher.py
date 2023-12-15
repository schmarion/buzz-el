from typing import Dict, Iterable, Optional

from spacy.language import Language
from spacy.pipeline import SpanRuler
from spacy.tokens import Doc

from ..graph import KnowledgeGraph
from .fuzzy_ruler import FuzzyRuler


class EntityMatcher:
    """
    A class to construct an entity matcher from a knowledge graph.

    Attributes
    ----------
    kg : KnowledgeGraph
        The knowledge graph to match the entities.
    spacy_model : Language
        The spaCy model to use in internal spaCy components.
    ignore_case : bool
        Whether to ignore case.
    use_fuzzy : bool
        Whether to use fuzzy matching.
    fuzzy_threshold : int
        It corresponds to min_r parameter in spaczz FuzzyMatcher.
        Minimum ratio needed to match as a value between 0 and 100.
        Default is 0, which deactivates this behaviour.
    _string_matcher: Callable[spacy.tokens.Doc, spacy.tokens.Doc]
        The string matcher component matching entities through string alignment.
    _fuzzy_matcher: Callable[spacy.tokens.Doc, spacy.tokens.Doc]
        The fuzzy matcher component matching entities through string fuzzy alignment.
    """

    def __init__(
        self,
        knowledge_graph: KnowledgeGraph,
        spacy_model: Language,
        ignore_case: Optional[bool] = True,
        use_fuzzy: Optional[bool] = False,
        fuzzy_threshold: Optional[int] = None,
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
        use_fuzzy : Optional[bool], optional
            Whether to use fuzzy matching, by default False.
        fuzzy_threshold : int
            It corresponds to min_r parameter in spaczz FuzzyMatcher.
            Minimum ratio needed to match as a value between 0 and 100.
            Default is 0, which deactivates this behaviour.
        """
        self.spacy_model = spacy_model
        self.kg = knowledge_graph
        self.ignore_case = ignore_case
        self.use_fuzzy = use_fuzzy
        self.fuzzy_threshold = fuzzy_threshold

        self._string_matcher = None
        self._fuzzy_matcher = None
        if self.use_fuzzy:
            self.build_fuzzy_matcher()
        else:
            self.build_string_matcher()

    def __call__(self, doc: Doc) -> Doc:
        """
        Apply the entity matching to a spaCy doc.

        Parameters
        ----------
        doc : Doc
            The spaCy doc to process.
        """
        if (self._string_matcher is None) and (self._fuzzy_matcher is None):
            self.build_string_matcher()
            doc = self._string_matcher(doc)
        elif self._fuzzy_matcher is not None:
            doc = self._fuzzy_matcher(doc)
        else:
            doc = self._string_matcher(doc)

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
            See: <https://spacy.io/api/spanruler#config>
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
            See: <https://spaczz.readthedocs.io/en/latest/reference.html#spaczz.matcher.FuzzyMatcher.defaults>
        """
        spans_key = "fuzzy"
        if config is not None:
            ruler = FuzzyRuler(
                self.spacy_model,
                self.ignore_case,
                spans_key,
                self.fuzzy_threshold,
                **config,
            )
        else:
            ruler = FuzzyRuler(
                self.spacy_model, self.ignore_case, spans_key, self.fuzzy_threshold
            )

        ruler.add_patterns(self.kg.entity_patterns)
        self._fuzzy_matcher = ruler

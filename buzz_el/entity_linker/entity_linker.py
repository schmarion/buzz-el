from typing import Iterable, Optional

from spacy.language import Language
from spacy.tokens import Doc, Span

from ..disambiguator import Disambiguator
from ..entity_matcher import EntityMatcher
from ..graph import KnowledgeGraph


class EntityLinker:
    """
    A class to construct an entity linker from a knowledge graph.

    First step is to apply entity matcher to extract candidate entities.
    Then, disambiguator is applied when ambiguous candidate entities are found
    for the same tokens.

    Attributes
    ----------
    kg : KnowledgeGraph
        The knowledge graph to link the entities.
    spacy_model : Language
        The spaCy model to use in internal spaCy components.
    entity_matcher : EntityMatcher
        The entity matcher to extract candidate entities.
    disambiguator : Disambiguator
        The disambiguator to filter ambiguous candidate entities.
    """

    def __init__(
        self,
        knowledge_graph: KnowledgeGraph,
        spacy_model: Language,
        entity_matcher: Optional[EntityMatcher] = None,
        disambiguator: Optional[Disambiguator] = None,
    ) -> None:
        """
        Initialiser for the entity linker.

        Parameters
        ----------
        knowledge_graph : KnowledgeGraph
            The knowledge graph to link the entities.
        spacy_model : Language
            The spaCy model to use in internal spaCy components.
        entity_matcher : EntityMatcher
            The entity matcher to extract candidate entities.
        disambiguator : Disambiguator
            The disambiguator to filter ambiguous candidate entities.
        """
        self.kg = knowledge_graph
        self.spacy_model = spacy_model
        if entity_matcher is None:
            self.entity_matcher = EntityMatcher(self.kg, spacy_model)
        else:
            self.entity_matcher = entity_matcher
        if disambiguator is None:
            self.disambiguator = Disambiguator()
        else:
            self.disambiguator = disambiguator

    def __call__(self, doc: Doc) -> Doc:
        """
        Apply the entity linking to a spaCy doc.

        Parameters
        ----------
        doc : Doc
            The spaCy doc to process.

        Returns
        -------
        Doc
            The spaCy doc processed.
        """
        doc = self.entity_matcher(doc)
        doc = self._remove_ambiguities(doc)
        return doc

    def pipe(self, docs: Iterable[Doc]) -> Iterable[Doc]:
        """
        Apply the entity linking component to an iterable of spaCy docs.

        Parameters
        ----------
        docs : Iterable[Doc]
            An iterable of spaCy docs to process.

        Returns
        -------
        Iterable[Doc]
            An iterable of processed spaCy docs.
        """
        for doc in docs:
            processed_doc = self(doc)
            yield processed_doc

    def _remove_ambiguities(self, doc: Doc) -> Doc:
        """
        Check if the doc span group has overlap.
        If it is the case, the disambiguator is used to determine the right candidate.
        Entites found are stored in the doc ents attribute.

        Parameters
        ----------
        doc : Doc
            The spaCy doc to process.

        Returns
        -------
        Doc
            The spaCy doc processed.
        """
        doc_entities = []
        if doc.spans[self.entity_matcher.spans_key].has_overlap:
            overlapping_spans = self._extract_overlapping_spans(doc)
            for spans in overlapping_spans:
                selected_entities = self.disambiguator(spans)
                doc_entities.extend(selected_entities)
        else:
            doc_entities = doc.spans[self.entity_matcher.spans_key]
        doc.set_ents(doc_entities)
        return doc

    def _extract_overlapping_spans(self, doc: Doc) -> Iterable[Iterable[Span]]:
        """
        Group overlapping candidate entities spans together.

        Parameters
        ----------
        doc : Doc
            The spaCy doc to process.

        Returns
        -------
        Iterable[Iterable[Span]]

        """
        overlapping_spans = []
        entity_group = []
        span_end = 0
        for entity in doc.spans[self.entity_matcher.spans_key]:
            if len(entity_group) == 0:
                entity_group.append(entity)
                span_end = entity.end
            elif entity.start < span_end:
                entity_group.append(entity)
                span_end = max(span_end, entity.end)
            else:
                overlapping_spans.append(entity_group)
                entity_group = [entity]
                span_end = entity.end
        overlapping_spans.append(entity_group)
        return overlapping_spans

from typing import Dict, Iterable, List, Optional

from spacy.language import Language
from spacy.pipeline import SpanRuler
from spacy.tokens import Doc

from ..graph_loader import GraphLoader


class EntityMatcher:
    """
    A class to construct a spaCy span ruler from a RDF graph.

    Parameters
    ----------
    graph_loader : GraphLoader
        An instance of the GraphLoader class for loading knowledge graph data.
    spacy_model : Language
        The spaCy language to use when constructing the spaCy span ruler.
    span_ruler_config : Optional[Dict], optional
        Configuration for the spaCy span ruler, by default {"phrase_matcher_attr": "LOWER"}.
        See <https://spacy.io/api/spanruler#config>

    Attributes
    ----------
    spacy_model : Language
        The spaCy language to use when constructing the spaCy span ruler.
    graph_loader : GraphLoader
        An instance of the GraphLoader class for loading knowledge graph data.
    _span_ruler_config : Dict
        Configuration for the spaCy span ruler, by default {"phrase_matcher_attr": "LOWER"}.
        See: <https://spacy.io/api/spanruler#config>
    spacy_component : SpanRuler
        The spaCy span ruler component for the knowledge graph entity matching.
    """

    def __init__(
        self,
        graph_loader: GraphLoader, # KG
        spacy_model: Language,
        ignore_case,
        min_r,
        fuzzy_funct
    ) -> None:
        """
        Initialiser for the entity matcher.

        Parameters
        ----------
        graph_loader : GraphLoader
            An instance of the GraphLoader class for loading knowledge graph data.
        spacy_model : Language
            The spaCy language to use when constructing the spaCy span ruler.
        span_ruler_config : Optional[Dict], optional
            Configuration for the spaCy span ruler, by default {"phrase_matcher_attr": "LOWER"}.
            See: <https://spacy.io/api/spanruler#config>
        """
        self.spacy_model = spacy_model
        self.graph_loader = graph_loader

        if span_ruler_config is None:
            self._span_ruler_config = {"phrase_matcher_attr": "LOWER"}
        else:
            self._span_ruler_config = span_ruler_config

        self.build_entity_ruler()  # set self.spacy_component

    def __call__(self, doc: Doc) -> None:
        """
        Apply the entity matching to a spaCy doc.

        Parameters
        ----------
        doc : Doc
            The spaCy doc to process.
        """
        if self.spacy_component is None:
            self.build_entity_ruler()

        self.spacy_component(doc)

    def pipe(self, docs: Iterable[Doc]) -> Iterable:
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
        if self.spacy_component is None:
            self.build_entity_ruler()

        doc_process_pipe = self.spacy_component.pipe(docs)

        return doc_process_pipe

    def _construct_phrase_patterns(
        self,
        entity_label: Optional[str] = "KG_ENT",
    ) -> List[Dict]:
        """
        Construct phrase patterns for the spaCy span ruler based on the graph loader.

        Parameters
        ----------
        entity_label : Optional[str], optional
            The label for the constructed entity patterns, by default "KG_ENT".

        Returns
        -------
        List[Dict]
            A list of dictionaries representing phrase patterns.
        """
        phrase_patterns = []

        for ent_id, match_phrases in self.graph_loader.entity_str_idx.items():
            for match_ph in match_phrases:
                phrase_patterns.append(
                    {
                        "label": entity_label,
                        "pattern": match_ph,
                        "id": ent_id,
                    }
                )

        return phrase_patterns

    def build_entity_ruler(
        self, config: Optional[Dict] = None, entity_label: Optional[str] = "KG_ENT"
    ) -> None:
        """
        Build the entity matching spaCy span ruler.

        This method updates the self.spacy_component attribute.

        Parameters
        ----------
        config : Optional[Dict], optional
            Configuration for the spaCy span ruler, by default None.
        entity_label : Optional[str], optional
            The label for the constructed entity patterns, by default "KG_ENT".
        """
        if config is None:
            ruler = SpanRuler(self.spacy_model, **self._span_ruler_config)
        else:
            ruler = SpanRuler(self.spacy_model, **config)

        ph_patterns = self._construct_phrase_patterns(
            entity_label=entity_label,
        )

        ruler.add_patterns(ph_patterns)

        self.spacy_component = ruler

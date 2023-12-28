from typing import Dict, List, Optional, Tuple

from spacy.language import Language
from spacy.tokens import Doc, Span
from spaczz.matcher import FuzzyMatcher


class FuzzyRuler:
    """
    A class to construct a Fuzzy Ruler from hr spaczz Fuzzy Matcher.

    Attributes
    ----------
    spacy_model : Language
        The spaCy model to use in internal spaCy components.
    ignore_case : Optional[bool], optional
        Whether to ignore case, by default True.
    spans_key : Optional[str], optional
        The spans key to use to store the matches found in the spaCy doc spans attribute.
    fuzzy_threshold : Optional[int], optional
        It corresponds to min_r parameter in spaczz FuzzyMatcher.
        Minimum ratio needed to match as a value between 0 and 100.
        Default is 0, which deactivates this behaviour.
    matcher : FuzzyMatcher
        The spaczz matcher to use to match entities.
    """

    def __init__(
        self,
        spacy_model: Language,
        ignore_case: Optional[bool] = True,
        spans_key: Optional[str] = None,
        fuzzy_threshold: Optional[int] = None,
        config: Optional[Dict] = None,
    ) -> None:
        """Initialiser for the fuzzy entity matcher.

        Parameters
        ----------
        spacy_model : Language
            The spaCy model to use in internal spaCy components.
        ignore_case : Optional[bool], optional
            Whether to ignore case, by default True.
        spans_key : Optional[str], optional
            The spans key to use to store the matches found in the spaCy doc spans attribute.
        fuzzy_threshold : Optional[int], optional
            Threshold used to validate fuzzy matches.
            It corresponds to min_r parameter in spaczz FuzzyMatcher.
            Minimum ratio needed to match as a value between 0 and 100.
            Default is 0, which deactivates this behaviour.
        config : Optional[Dict], optional
            Configuration for the custom fuzzy ruler, by default None.
            See: <https://spaczz.readthedocs.io/en/latest/reference.html#spaczz.matcher.FuzzyMatcher.defaults>
        """
        self.spacy_model = spacy_model
        self.ignore_case = ignore_case
        if spans_key is None:
            spans_key = "fuzzy"
        self.spans_key = spans_key

        self.fuzzy_threshold = fuzzy_threshold

        if config is None:
            config = {}
        if self.fuzzy_threshold is not None:
            config["min_r"] = self.fuzzy_threshold

        self.matcher = FuzzyMatcher(
            vocab=self.spacy_model.vocab, ignore_case=self.ignore_case, **config
        )

    def add_patterns(self, patterns: List[Dict[str, str]]) -> None:
        """
        Add patterns to the ruler.

        The spaczz pattern adapted to our case is:
        `{label (str), pattern (str), id (str)}`.

        Parameters
        ----------
        patterns: List[Dict[str,str]]
            The patterns to add.
        """
        for pattern in patterns:
            label_with_id = f"{pattern['label']}#{pattern['id']}"
            self.matcher.add(label_with_id, [self.spacy_model(pattern["pattern"])])

    def __call__(self, doc: Doc) -> Doc:
        """
        Apply the fuzzy matcher to a spaCy doc.

        Parameters
        ----------
        doc : Doc
            The spaCy doc to process.

        Returns
        -------
        Doc
            The spaCy doc processed.
        """
        matches = self.matcher(doc)
        self.set_annotations(doc, matches)
        return doc

    def set_annotations(self, doc: Doc, matches: List[Tuple]) -> None:
        """
        Modify the spaCy doc with matches information in the spans attribute.

        Parameters
        ----------
        doc : Doc
            The spaCy doc to modify.
        matches : List[Tuple]
            The matches found by the matcher.
        """
        deduplicated_matches = set(
            Span(
                doc,
                start,
                end,
                label=label_with_id[: label_with_id.find("#")],
                span_id=label_with_id[label_with_id.find("#") + 1 :],
            )
            for label_with_id, start, end, _, _ in matches
            if start != end
        )
        formatted_matches = sorted(list(deduplicated_matches))
        doc.spans[self.spans_key] = formatted_matches

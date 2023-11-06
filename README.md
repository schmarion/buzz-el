# buzz-el

> Towards universal entity linker and beyonds 🚀

## Project description

The aim of this project is to do entity linking from any knowledge graph.
So we try to extract the entities from a graph mentioned in a text.
We base our work on [spaCy](https://spacy.io/) tools.

The entity linker consists of 3 modules :

- the **graph loader** is responsible for loading the graph and extracting entities from the graph
- the **entity matcher** is responsible for extracting candidate entities from the given text
- the **disambiguator** is responsible for is responsible for removing any ambiguities that may exist between the candidate entities.

The steps for using the entity linker are as follows :

- load a graph with the **graph loader**
- load a NLP pipeline from spaCy to process the text
- extract the candidate entities from the text with the **entity matcher**
- apply the **disambiguator** if needed.

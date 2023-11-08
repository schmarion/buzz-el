# buzz-el

> Towards universal entity linker and beyonds 🚀

## Project description

The aim of this project is to do entity linking from any knowledge graph expressed in RDF.
So we try to extract the entities from a graph mentioned in a text.
We base our work on [spaCy](https://spacy.io/) tools.

The entity linker consists of 3 modules :

- the **graph loader** is responsible for loading the knowledge graph and extracting entities from it;
- the **entity matcher** is responsible for extracting candidate entities from the given text;
- the **disambiguator** is responsible for removing any ambiguities that may exist between the candidate entities, i.e., selecting the correct entity among the candidate ones.

The steps for using the entity linker are as follows :

- load a graph with the **graph loader**;
- load a NLP pipeline from spaCy to preprocess the text;
- extract the candidate entities from the text with the **entity matcher**;
- apply the **disambiguator** if needed.

## Usage

The project is not yet pushed on Pypi, but it is already setup to be loaded with `pip install`. To pip install the project as a Python package run the following command in your terminal: `pip install git+https://github.com/schmarion/buzz-el.git`.
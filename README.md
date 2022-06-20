# Similiar_Concepts
 A repo for my bachelor project about creating  Query-specific Similar Concepts with BERT-based retrieval for Commonsense Knowledge


In this repo the following DataSets have been used:
* Repo: [ConceptNet5](https://github.com/commonsense/conceptnet5), Download link: [Version5.7.0](https://s3.amazonaws.com/conceptnet/downloads/2019/edges/conceptnet-assertions-5.7.0.csv.gz)
* Repo: [CommonsenseQA](https://github.com/jonathanherzig/commonsenseqa) in this repo i use a specific selection of questions thats available on the FindItOut repo linked below.

The following models have been used:
* [BERT](https://huggingface.co/docs/transformers/model_doc/bert) a NLP model
* [SimSCE](https://github.com/princeton-nlp/SimCSE) an implementation of BERT

This repo also uses some code from the [FindItOut](https://github.com/delftcrowd/FindItOut) that has been slightly modified
in order to get more repeatable output.


To be honest this repo is quite a mess but the basic run order is:

extract_cpnet.py

hopcreation.py

rating_neighbours.py

scoring_gameboards.py

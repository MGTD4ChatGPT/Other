'''
    author: Bipin
'''

import neuralcoref
import spacy
nlp = spacy.load('en')

# add to spacy's pipeline
neuralcoref.add_to_pipe(nlp)


def resolveCoreference(sentence):
    # doc = nlp(sentence.encode("UTF-8"))
    doc = nlp(sentence)
    return doc._.coref_resolved


if __name__ == "__main__":
    print(resolveCoreference("My sister has a dog. She loves him."))
    # output: My sister has a dog. My sister loves a dog.

    doc = nlp(u"My sister has a dog. She loves him.")

    print(doc._.has_coref)
    print(doc._.coref_clusters)

    print(doc._.coref_resolved)

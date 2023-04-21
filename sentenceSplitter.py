'''
    author: Bipin
'''

from sentenceSimplifier import Simplifier
from conjunctionSentenceSplitter import SplitWithConjuction
from coreferenceResolver import resolveCoreference
import os
import sys
import re
import spacy
import nltk
nltk.download('averaged_perceptron_tagger')

# add root folder into path so that all the folders inside root will by accessible
# from folders inside so that python can be started from within any subfolders instead of runner.py
# this is just for development purpose
# at prod; python should always be initiated from runner.py
if __name__ == "__main__":
    project_root_path = os.path.split(
        os.path.dirname(os.path.realpath(__file__)))[0]
    project_root_path = os.path.split(project_root_path)[0]
    sys.path.insert(0, project_root_path)
    # print(sys.path)


# Load English tokenizer, tagger, parser, NER and word vectors
nlp = spacy.load("en")


# splitting rules
# 1. replacing reference words like he, it, .. by suitable noun from sentence (resolving coreference)
# 2. splitting sentence (full stops)
# 3. splitting sentence with (but, because, ...)
# 4. splitting sentence with (either or, neither nor)
# 4. splitting sentence with (and, ',') into multiple sentences


def sentenceSplitter_(sentence):
    sentence = u"{}".format(sentence)
    doc = nlp(sentence)
    retval = []
    for sent in doc.sents:
        retval.append(sent.text)
    return retval


def butGroupSplitter(sentence):
    but_group = ['but', 'because', 'though', 'however', 'although', 'merely', 'yet', 'nevertheless', 'nonetheless', 'except',
                 'therefore', 'anyway', 'perhaps', 'whereas', 'furthermore', 'besides', 'moreover', 'otherwise', 'furthermore', ]
    regex = r"\s+(?:" + "|".join(but_group) + r")\s+"
    # print(regex)
    return re.split(regex, sentence)


def eitherOrGroupSplitter(sentence):
    # TODO: may be its needed but lets igore this for now
    return [sentence]


def conjunctionSplitter(sentence):
    conjSplitter = SplitWithConjuction()
    return conjSplitter.split(sentence)


def flatList(lst):
    '''
        flattens the nested listed (list of lists) into a single list of elements
    '''
    retval = []
    for i in lst:
        if type(i) == list:
            retList = flatList(i)
            for r in retList:
                retval.append(r)
        else:
            retval.append(i)
    return retval


def listOperation(lst, operation):
    '''
        perform the given operation function for every list item
    '''
    nextLst = []
    for l in lst:
        nextLst.append(operation(l))
    return list(set(flatList(nextLst)))


def splitSentenceVerbose(sentence, resolveCoref=False):
    '''
        Split sentence by the pipeline different kinds of splitters
        And provides debug information in every step
            splitting pipeline:
                1. replacing reference words like he, it, .. by suitable noun from sentence (resolving coreference)
                2. splitting sentence (full stops)
                3. splitting sentence with (but, because, ...)
                4. splitting sentence with (either or, neither nor)
                4. splitting sentence with (and, ',') into multiple sentences
    '''
    print("before: ", sentence)
    if resolveCoref:
        sentence = resolveCoreference(sentence)
        print("\nafter coreference resolution: ", sentence)
    lst = sentenceSplitter_(sentence)
    print("\nafter sentence splitting: ", lst)

    simplifier = Simplifier()
    lst = simplifier.getSplitSentences(lst)
    print("\nafter simplifier: ", lst)

    lst = listOperation(lst, butGroupSplitter)
    print("\nafter butGroup splitting: ", lst)
    lst = listOperation(lst, eitherOrGroupSplitter)
    print("\nafter eitherorGroup splitting: ", lst)
    lst = listOperation(lst, conjunctionSplitter)
    print("\nafter conjunction splitting: ", lst)

    return lst


def splitSentence(sentence, resolveCoref=False):
    '''
        Split sentence by the pipeline different kinds of splitters
            splitting pipeline:
                1. replacing reference words like he, it, .. by suitable noun from sentence (resolving coreference)
                2. splitting sentence (full stops)
                3. splitting sentence with (but, because, ...)
                4. splitting sentence with (either or, neither nor)
                4. splitting sentence with (and, ',') into multiple sentences
    '''
    if resolveCoref:
        sentence = resolveCoreference(sentence)
    lst = sentenceSplitter_(sentence)

    simplifier = Simplifier()
    lst = simplifier.getSplitSentences(lst)

    lst = listOperation(lst, butGroupSplitter)
    lst = listOperation(lst, eitherOrGroupSplitter)
    lst = listOperation(lst, conjunctionSplitter)
    return lst


if __name__ == "__main__":
    test0 = "Ram called his friend Hari. They both liked the place but didn't like the price attached."
    test1 = "The pricing, service and location is just perfect but its too bad we cannot depends on its availability."
    test2 = "Health care and scooling are free in Canada."
    test3 = "Getting a job is a blast here in XYZ due to economic boom however the transportation is just terrible here."
    test4 = "Despite huge criticisms, I must say; his performance in ABC was admirable."
    test5 = "Plot was good, acting was bad."
    test6 = "plot good acting bad"
    test7 = "plot was good but acting was bad"
    test8 = "bad acting but a good movie"
    test9 = "mix of both good and bad"
    test10 = "good movie with bad acting"
    test11 = "good location and plot but bad acting and cinematography"
    test12 = "good on issues like immigration and healthcare but I didn't like her agenda on climate change and economy"
    test13 = "issues like immigration and healthcare are represented properly but her agenda on climate change and economic development doesn't look promising"
    test14 = "Overall amazing phone with killer display and processor with only downside benig its 3000mAh battery"
    test15 = "If i had her number i would have definitely called her"
    test16 = "Lion and tiger are chasing a deer and fox is chasing a rabbit"
    test17 = "My father, who is a President, is an honest man."
    test18 = "My brother and sister, who are the members of the association are working hard."

    tests = [test0, test1, test2, test3, test4, test5, test6, test7,
             test8, test9, test10, test11, test12, test13, test14, test15, test16]
    small_tests = [test0, test1, test2, test3, test16]
    curated_tests = [test0, test1, test7, test11, test17, test18]

    for test in curated_tests:
        print("\n\n splitting : ", test)
        print(splitSentence(test))
        print("-"*100)

    while True:
        print("input: ", end="")
        sent = input()
        print(splitSentence(sent))
        print("-"*100)

#!/usr/bin/env python
# coding: utf-8
import spacy
import nltk


class Simplifier:
    def __init__(self, model_library_name="en_core_web_sm"):
        self.nlp = spacy.load(model_library_name)
        self.relpron = ['whom', 'whose', 'which', 'who']

    def transform(self, parsed):
        d = {}
        for x in parsed:
            rel = x.dep_
            parent = x.head.i + 1
            dependent = x.i + 1
            if parent == dependent and rel == 'ROOT':
                parent = 0
            if parent not in d.keys():
                d[parent] = {}
            if rel not in d[parent].keys():
                d[parent][rel] = []

            d[parent][rel].append(dependent)
        return d

    def analyse_rc(self, sentence):
        # check for markers indicating rel_clause
        if any([s.lower() in self.relpron for s in sentence]):
            mark = []
            for s in sentence:
                if s.lower() in self.relpron:
                    mark.append(s.lower())
            return True, mark
        else:
            return False, None

    def remove_all(self, aux, item):
        for a in aux.keys():
            for d in aux[a].keys():
                if item in aux[a][d]:
                    aux[a][d].remove(item)

    def build(self, root, dep, aux, words, final, yes_root=True, previous=None):
        if previous == None:
            previous = []

        if root in previous:
            return

        previous.append(root)

        if yes_root:
            final[root] = words[root-1]
            previous.append(root)

        for k in dep.keys():
            for i in dep[k]:
                if i in aux.keys():

                    deps = aux[i]
                    self.build(i, deps, aux, words, final, previous=previous)

                final[i] = words[i-1]

    def appositive_phrases(self, dep_dict, words, root, dep_root, ant):

        if 'nsubj' in dep_root:
            subj = dep_root['nsubj'][0]
            subj_word = words[subj-1]

            if subj not in dep_dict:
                return False, ant

            deps_subj = dep_dict[subj]
            v_tense = words[root-1][1]
            n_num = words[subj-1][1]

            if 'amod' in deps_subj:
                mod = deps_subj['amod'][0]
                if mod in dep_dict:
                    deps_mod = dep_dict[mod]
                else:
                    deps_mod = {}
                del dep_dict[subj]['amod']
                deps_subj = dep_dict[subj]

                # Treat simple cases such as 'general rule'
                if 'JJ' in words[mod-1][1] and 'punct' not in deps_subj:
                    return False, ant

            elif 'appos' in deps_subj:
                mod = deps_subj['appos'][0]
                if mod in dep_dict:
                    deps_mod = dep_dict[mod]
                else:
                    deps_mod = {}
                del dep_dict[subj]['appos']
                deps_subj = dep_dict[subj]
            else:
                return False, ant

            if 'punct' in deps_subj.keys():
                del deps_subj['punct']

            final_root = {}
            self.build(root, dep_root, dep_dict, [
                       s[0].lower() for s in words], final_root)
            final_appos = {}
            self.build(mod, deps_mod, dep_dict, [
                       s[0].lower() for s in words], final_appos)
            final_subj = {}
            self.build(subj, deps_subj, dep_dict, [
                       s[0].lower() for s in words], final_subj)

            s1 = []
            for i in sorted(final_root):
                s1.append(final_root[i])
            s1 = ' '.join(s1)

            s2 = []
            for i in sorted(final_appos):
                s2.append(final_appos[i])
            s2 = ' '.join(s2)
            s3 = []
            for i in sorted(final_subj):
                s3.append(final_subj[i])
            s3 = ' '.join(s3)

            if len(final_appos.keys()) < 2:
                return False, ant

            if n_num in ["NN", "NNP"]:
                if v_tense in ["VBP", "VBZ", "VB"]:
                    s3 += " is "
                elif v_tense in ["VBD", "VBG", "VBN"]:
                    s3 += " was "

            elif n_num in ["NNS", "NNPS"]:
                if v_tense in ["VBP", "VBZ", "VB"]:
                    s3 += " are "
                elif v_tense in ("VBD", "VBG", "VBN"):
                    s3 += " were "

            elif n_num in ["PRP"] and subj_word.lower() == "they":

                if v_tense in ["VBP", "VBZ", "VB"]:
                    s3 += " are "
                elif v_tense in ["VBD", "VBG", "VBN"]:
                    s3 += " were "

            elif n_num in ["PRP"]:
                if v_tense in ["VBP", "VBZ", "VB"]:
                    s3 += " is "
                elif v_tense in ["VBD", "VBG", "VBN"]:
                    s3 += " was "

            s2 = s3 + s2
            return True, [s1, s2]
        return False, ant

    def relative_clauses(self, dep_dict, words, root, dep_root, rel, ant):
        subj = dep_root[rel][0]
        if subj in dep_dict:

            dep_subj = dep_dict[subj]

            if 'relcl' in dep_subj or 'rcmod' in dep_subj:
                if 'relcl' in dep_subj:
                    relc = dep_subj['relcl'][0]
                    type_rc = 'relcl'
                else:
                    relc = dep_subj['rcmod'][0]
                    type_rc = 'rcmod'
                deps_relc = dep_dict[relc]

                if 'nsubj' in deps_relc:
                    subj_rel = 'nsubj'
                elif 'nsubjpass' in deps_relc:
                    subj_rel = 'nsubjpass'

                if 'ref' in dep_subj:
                    to_remove = dep_subj['ref'][0]
                    mark = words[dep_subj['ref'][0]-1].lower()
                else:
                    to_remove = deps_relc[subj_rel][0]
                    mark = words[deps_relc[subj_rel][0]-1].lower()


                if mark in self.relpron:
                    deps_relc[subj_rel][0] = subj
                    self.remove_all(dep_dict, to_remove)
                elif 'dobj' in deps_relc:  # needed for cases where the subject of the relative clause is the object
                    obj = deps_relc['dobj'][0]

                    if 'poss' in dep_dict[obj]:
                        mod = dep_dict[obj]['poss'][0]
                        aux_words = words[mod-1]
                        aux_words = words[subj-1] + '\'s'
                        words[mod-1] = aux_words
                        dep_dict[mod] = dep_dict[subj]
                    else:
                        return False, ant
                else:
                    return False, ant  # for borken cases - " There are some situations where it is particularly important that you get financial information and advice that is independent of us."

                del dep_dict[subj][type_rc]

                if 'punct' in dep_subj:
                    del dep_dict[subj]['punct']

                final_root = {}
                self.build(root, dep_root, dep_dict, words, final_root)
                final_relc = {}
                self.build(relc, deps_relc, dep_dict, words, final_relc)


                s1 = []
                for i in sorted(final_root):
                    s1.append(final_root[i])

                s2 = []
                for i in sorted(final_relc):
                    s2.append(final_relc[i])

                return True, [' '.join(s1), ' '.join(s2)]
        return False, ant

    def getSplitSentences(self, sentences):
        '''
        I simplifies the list of sentence received into simpler ones.
        eg:
        input: ["My father, who is a President, is an honest man."]
        output: ['my father , is an honest man .', 'my father is a president']

        eg:
        input: ["My brother and my sister, who are the members of the association are working hard."]
        output: ['my brother and my sister , are working hard .', 'my brother and my sister , are the members of the association']
        '''
        result = []
        for s in sentences:
            output = self.nlp(s)
            dep_dict = self.transform(output)
            tokens = [token.text.lower() for token in output]
            words = nltk.pos_tag(tokens)
            if 0 in dep_dict:
                root = dep_dict[0]['ROOT'][0]
                if root in dep_dict:
                    dep_root = dep_dict[root]
                    # handle appositive_phrases
                    flag_appos, res = self.appositive_phrases(
                        dep_dict, words, root, dep_root, sentences)
                    if flag_appos:
                        result += res
                        continue
                    # check for relative clauses
                    flag_rc, type_rc = self.analyse_rc(s.split())
                    if flag_rc:
                        if 'nsubj' in dep_root:
                            flag, res = self.relative_clauses(
                                dep_dict, tokens, root, dep_root, 'nsubj', sentences)
                            if flag:
                                result += res
                                continue
                        elif 'dobj' in dep_root:
                            flag, res = self.relative_clauses(
                                dep_dict, tokens, root, dep_root, 'dobj', sentences)
                            if flag:
                                result += res
                                continue
            result.append(s)
        return result


if __name__ == "__main__":
    # sentences = ['Sachin Tendulkar, who is a MP of Indian Parliament, played cricket.', "My father, who is a President, is an honest man.", "My brother and my sister, who are the members of the association are working hard."]
    sentences = ["My father, who is a President, is an honest man.",
                 "My brother and my sister, who are the members of the association are working hard."]
    # sentences = ["My name is Bipin Oli.", "My name is bipin oli."]
    simplifier = Simplifier("en_core_web_sm")
    result = simplifier.getSplitSentences([sentences[0]])
    print(result)
    result = simplifier.getSplitSentences([sentences[1]])
    print(result)

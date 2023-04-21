'''
    author: Bipin Oli
'''
import spacy

nlp = spacy.load("en")


class SplitWithConjuction:
    def __init__(self):
        self.track = []
        self.seen = {}

    def findRoot(self, doc):
        '''
        returns root from the Spacy Doc
        '''
        root = 0
        for i in range(len(doc)):
            if doc[i].dep_ == 'ROOT':
                root = i
                break
        return doc[root]

    def bfs(self, root):
        children = list(root.children)
        if len(children) == 0:
            if root not in self.seen:
                self.track.append(root)
            return

        rootGrp = [root]

        for child in children:
            if child.dep_ in ["conj", "npadvmod"]:
                rootGrp.append(child)

        if len(rootGrp) > 1:
            found = -1
            for i in range(len(self.track)):
                v = self.track[i]
                if type(v) == type(list()) and len(set(v).intersection(set(rootGrp))) > 0:
                    found = i
                    break
            if found != -1:
                for r in rootGrp:
                    if r not in self.track[found]:
                        self.track[found].append(r)
            else:
                self.track.append(rootGrp)
        else:
            if root not in self.seen:
                self.track.append(root)

        for r in rootGrp:
            self.seen[r] = True

        for child in children:
            self.bfs(child)

    def getSplitted(self, text):
        '''
        Splits text from conjunction
        eg:
            input: its too bad that timing and something is not per the standard.
            output: ['its','too','bad','that', ['timing','something'], 'is', 'not', 'per', 'the', 'standard', '.']
        '''
        doc = nlp(text)

        self.bfs(self.findRoot(doc))

        # don't take items with 'cc' dependency (conjunction)
        retval = []
        for x in self.track:
            if type(x) != type(list()):
                if x.dep_ == "cc":
                    continue
            retval.append(x)
        self.track = []
        self.seen = {}

        # get position of token
        def getPosition(token):
            if type(token) != type(list()):
                return token.i
            return min(list(map(lambda x: x.i, token)))

        retval.sort(key=lambda x: getPosition(x))
        return retval

    def stitchSentence(self, splittedList, pos):
        if pos == len(splittedList)-1:
            if type(splittedList[pos]) == type(list()):
                return splittedList[pos]
            return [splittedList[pos]]

        rest = self.stitchSentence(splittedList, pos+1)

        if type(splittedList[pos]) != type(list()):
            retval = []
            for x in rest:
                retval.append(str(splittedList[pos]) + " " + str(x))
            return retval

        retval = []
        for x in splittedList[pos]:
            for y in rest:
                retval.append(str(x) + " " + str(y))
        return retval

    def split(self, text):
        '''
        Splits the given text from conjunction and returns sentences.
        '''
        return(self.stitchSentence(self.getSplitted(text), 0))


if __name__ == "__main__":
    s = SplitWithConjuction()
    print(s.split("its too bad that timing and something is not per the standard."))

# Production script for AWS Lambda.
#
# Consider this code as automatically generated and not for humans.
#
# Pavel Bazin 2018

import boto3
import random
import pprint
import sys
import re

# Initialize access to S3 resource
s3 = boto3.resource('s3')
bucket_name = 'trumpket'
file_name = 'data_sample.csv'
data_object = s3.Object(bucket_name, file_name)
data = data_object.get()['Body'].read()
print(data)

stop_words = ['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've", "you'll", "you'd", 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', "she's", 'her', 'hers', 'herself', 'it', "it's", 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', "don't", 'should', "should've", 'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', "aren't", 'couldn', "couldn't", 'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't", 'haven', "haven't", 'isn', "isn't", 'ma', 'mightn', "mightn't", 'mustn', "mustn't", 'needn', "needn't", 'shan', "shan't", 'shouldn', "shouldn't", 'wasn', "wasn't", 'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't"]
punctuation = ['.', ',', '!', '?', ';']
finals = ['.', '!', '?', ';']


class MarkovChain:
    def __init__(self, data):
        self.trigram_chain = {}
        self.twogram_chain = {}
        self.onegram_chain = {}
        self.words = MarkovChain.filter(data)
        self.build_chain(self.words)

    @staticmethod
    def filter(text):
        # Remove urls from text
        text = str(text,'utf-8')
        url_free_text = re.sub(r'http\S+', '', text)
        # Find words where word is a 'aaa', '#aaa' and punctuation goes separately
        # the rest will be ignored.
        return re.findall(r"[\w+#']+|[.,!?;]", url_free_text.lower())

    def build_chain(self, sequence):
        # Todo: refactor ngram generators
        def mc_trigrams():
            if len(sequence) < 4:
                return

            for i in range(len(sequence) - 3):
                yield (sequence[i], sequence[i+1], sequence[i+2], sequence[i+3])
        
        def mc_twograms():
            if len(sequence) < 3:
                return

            for i in range(len(sequence) - 2):
                yield (sequence[i], sequence[i+1], sequence[i+2])

        def mc_onegrams():
            if len(sequence) < 2:
                return

            for i in range(len(sequence) - 1):
                yield (sequence[i], sequence[i+1])
    
        # Trigram is a generator which returns markov chain trigrams
        # + one word after a trigram. For example:
        # (the, weather, is, nasty), where (the, weather, is) is an actual
        # trigram and nasty is a trigram's chain word
        for w1, w2, w3, w4 in mc_trigrams():
            trigram = (w1, w2, w3)
            if trigram in self.trigram_chain:
                self.trigram_chain[trigram].append(w4)
            else:
                self.trigram_chain[trigram] = [w4]

        for w1, w2, w3 in mc_twograms():
            twogram = (w1, w2)
            if twogram in self.twogram_chain:
                self.twogram_chain[twogram].append(w3)
            else:
                self.twogram_chain[twogram] = [w3]

        for w1, w2 in mc_onegrams():
            onegram = (w1)
            if onegram in self.onegram_chain:
                self.onegram_chain[onegram].append(w2)
            else:
                self.onegram_chain[onegram] = [w2]
            
    def write_chain(self, fname):
        # Format chain
        trigram_data = pprint.pformat(self.trigram_chain)
        twogram_data = pprint.pformat(self.twogram_chain)
        onegram_data = pprint.pformat(self.onegram_chain)

        data = trigram_data + '\n' + trigram_data + '\n' + onegram_data

        with open(fname, 'w') as f:
            f.write(data)
    
    def generate(self, tokens=None, wcount=100):
        condition = lambda ngram : ngram[0] not in punctuation
        choose = lambda ngram_set: random.choice(ngram_set)

        # Pick a thrigram to start a generation, shouldn't start with
        # punctuation.
        trigram = ('', '', '')
        twogram = ('', '')
        onegram = ('', )

        if tokens != None:
            if len(tokens) == 3:
                if tokens in self.trigram_chain:
                    trigram = tokens
                else:
                    # Fallback to 2-gram
                    tokens = (tokens[-2], tokens[-1])

            if len(tokens) == 2:
                if tokens in self.twogram_chain:
                    trigram = ('', tokens[-2], tokens[-1])
                    twogram = tokens
                else:
                    # Fallback to 1-gram
                    tokens = (tokens[-1],)
            
            if len(tokens) == 1:
                if tokens[0] in self.onegram_chain:
                    twogram = ('', tokens[-1])
                    onegram = (tokens[-1],)
                else:
                    # Fallback to random 3-gram
                    tokens = None

        # Parametrized input inactive, pick a random trigram
        if tokens == None:
            done = False
            while not done:
                x = choose(list(self.trigram_chain.keys()))
                if condition(x):
                    trigram = x
                    done = True

        sentence = []
        if trigram != ('', '', ''):
            [sentence.append(gram) for gram in trigram if gram != '']
        elif twogram != ('', ''):
            [sentence.append(gram) for gram in twogram if gram != '']
        elif onegram != (''):
            [sentence.append(gram) for gram in onegram if gram != '']

        for i in range(wcount):
            word = ''
            
            # Repeat until we have a new trigram in the chain
            if trigram in self.trigram_chain:
                word = random.choice(self.trigram_chain[trigram])
                trigram = (trigram[1], trigram[2], word)
                sentence.append(word)
                continue
            elif trigram != ('', '', ''):
                # If not - construct a twogram and continue
                twogram = (trigram[1], trigram[2])
                
            if twogram in self.twogram_chain:
                word = random.choice(self.twogram_chain[twogram])
                twogram = (twogram[1], word)
                sentence.append(word)
                trigram = (trigram[1], twogram[0], twogram[1])
                continue
            elif twogram != ('', ''):
                onegram = (twogram[1])

            if onegram in self.onegram_chain:
                word = random.choice(self.onegram_chain[onegram])
                onegram = (word)
                sentence.append(word)
                twogram = (twogram[1], onegram[0])
                continue
            else:
                pass

        return sentence

    @staticmethod
    def englishify(sequence, length):
        def to_sentence(sequence):
            prev_word = sequence[0]
            result = []
            result.append(prev_word)
            result_index = 1
            
            for i in range(1, len(sequence)):
                curr_word = sequence[i]
                if curr_word in punctuation:
                    result[len(result)-1] += curr_word
                else:
                    result.append(curr_word)
                result_index += 1
            
            return result

        def capitalize(sequence):
            sequence[0] = sequence[0].capitalize()
            prev = sequence[0].capitalize()
            
            for i in range(1, len(sequence)):
                if prev in finals:
                    sequence[i] = sequence[i].capitalize()

                prev = sequence[i]
            
            return sequence

        def cut(sequence, min_length):
            for i in range(min_length, len(sequence)):
                if sequence[i][-1] in finals:
                    return sequence[:i+1]
            
            return sequence
        
        return ' '.join(cut(to_sentence(capitalize(sequence)), length))

def parse_user_input(uinput):
    remove_stopwords = lambda x: x not in stop_words
    remove_punctuation = lambda x: x not in punctuation
    decapitalize = lambda x: x.lower()
    split = lambda text: re.findall(r"[\w+#']+|[.,!?;]", text)

    ulist = []
    if type(uinput) == type(''):
        ulist = split(uinput)
    else:
        ulist = uinput

    ulist = list(filter(remove_stopwords, filter(remove_punctuation, map(decapitalize, ulist))))

    if len(ulist) >= 3:
        return (ulist[-3], ulist[-2], ulist[-1])
    elif len(ulist) >= 2:
        return (ulist[-2], ulist[-1])
    elif len(ulist) >= 1:
        return (ulist[0],)
    else:
        return ('fake', 'news')

def chat(mc):
    while True:
        uinput = input('User: ')
        tokens = parse_user_input(uinput)
        raw_text = mc.generate(tokens)
        engl_like = MarkovChain.englishify(raw_text, 25)
        print('Trump: ' + engl_like)
        print()

markov_chain = MarkovChain(data)

def lambda_handler(event, context):
    utokens = parse_user_input('fake news are the best')
    raw_text = markov_chain.generate(utokens)
    res_text = MarkovChain.englishify(raw_text, 20)
    print('done')
    return res_text

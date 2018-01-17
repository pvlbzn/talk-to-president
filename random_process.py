import logging
import random
import pprint
import sys
import re


from utils import stop_words, punctuation, finals

class MarkovChain:
    def __init__(self, fname):
        logging.basicConfig(stream=sys.stdout, level=logging.CRITICAL)
        self.trigram_chain = {}
        self.twogram_chain = {}
        self.onegram_chain = {}
        self.words = MarkovChain.read_file(fname, MarkovChain.filter)
        self.build_chain(self.words)

    @staticmethod
    def read_file(fpath, filter):
        with open(fpath) as txt:
            data = txt.read()

        logging.debug('original data length: ' + str(len(data)))

        if filter:
            data = filter(data)
            logging.debug('filtered data length: ' + str(len(data)))
            return data
        else:
            return data

    @staticmethod
    def filter(text):
        # Remove urls from text
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
        
        logging.info('trigram chain built, #grams: ' + str(len(self.trigram_chain)))


        for w1, w2, w3 in mc_twograms():
            twogram = (w1, w2)
            if twogram in self.twogram_chain:
                self.twogram_chain[twogram].append(w3)
            else:
                self.twogram_chain[twogram] = [w3]
        
        logging.info('twogram chain built, #grams: ' + str(len(self.twogram_chain)))


        for w1, w2 in mc_onegrams():
            onegram = (w1)
            if onegram in self.onegram_chain:
                self.onegram_chain[onegram].append(w2)
            else:
                self.onegram_chain[onegram] = [w2]
        
        logging.info('onegram chain built, #grams: ' + str(len(self.onegram_chain)))
    
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

        logging.debug('tokens: ' + str(tokens))

        if tokens != None:
            if len(tokens) == 3:
                if tokens in self.trigram_chain:
                    trigram = tokens
                else:
                    # Fallback to 2-gram
                    logging.debug('falling back to 2-gram')
                    tokens = (tokens[-2], tokens[-1])

            if len(tokens) == 2:
                if tokens in self.twogram_chain:
                    trigram = ('', tokens[-2], tokens[-1])
                    twogram = tokens
                else:
                    # Fallback to 1-gram
                    logging.debug('falling back to 1-gram')
                    tokens = (tokens[-1],)
            
            if len(tokens) == 1:
                if tokens[0] in self.onegram_chain:
                    twogram = ('', tokens[-1])
                    onegram = (tokens[-1],)
                else:
                    # Fallback to random 3-gram
                    logging.debug('param is none')
                    tokens = None

        # Parametrized input inactive, pick a random trigram
        if tokens == None:
            logging.debug('generating random trigram')
            done = False
            while not done:
                x = choose(list(self.trigram_chain.keys()))
                if condition(x):
                    trigram = x
                    done = True
        
        logging.debug('trigram: ' + str(trigram))
        logging.debug('twogram: ' + str(twogram))
        logging.debug('onegram: ' + str(onegram))

        sentence = []
        if trigram != ('', '', ''):
            [sentence.append(gram) for gram in trigram if gram != '']
        elif twogram != ('', ''):
            [sentence.append(gram) for gram in twogram if gram != '']
        elif onegram != (''):
            [sentence.append(gram) for gram in onegram if gram != '']

        logging.debug('initial sentence is: ' + str(sentence))

        for i in range(wcount):
            word = ''
            
            # Repeat until we have a new trigram in the chain
            if trigram in self.trigram_chain:
                word = random.choice(self.trigram_chain[trigram])
                trigram = (trigram[1], trigram[2], word)
                sentence.append(word)
                logging.debug('trigram build: ' + str(trigram))
                continue
            elif trigram != ('', '', ''):
                # If not - construct a twogram and continue
                twogram = (trigram[1], trigram[2])
                
            logging.debug('fallback to 2-gram')

            if twogram in self.twogram_chain:
                word = random.choice(self.twogram_chain[twogram])
                twogram = (twogram[1], word)
                sentence.append(word)
                trigram = (trigram[1], twogram[0], twogram[1])
                logging.debug('twogram build: ' + str(twogram))
                continue
            elif twogram != ('', ''):
                onegram = (twogram[1])

            logging.debug('fallback to 1-gram')

            if onegram in self.onegram_chain:
                word = random.choice(self.onegram_chain[onegram])
                onegram = (word)
                sentence.append(word)
                twogram = (twogram[1], onegram[0])
                logging.debug('onegram build: ' + str(onegram))
                continue
            else:
                logging.critical('fallback failure')
            
        logging.info('final sentence is: ' + str(sentence))
        logging.info('final sentence len: ' + str(len(sentence)))

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

    logging.debug('user tokens are: ' + str(ulist))

    if len(ulist) >= 3:
        return (ulist[-3], ulist[-2], ulist[-1])
    elif len(ulist) >= 2:
        return (ulist[-2], ulist[-1])
    elif len(ulist) >= 1:
        return (ulist[0],)
    else:
        logging.critical('parsing error, ulist is empty')
        return ('fake', 'news')


def chat(mc):
    while True:
        uinput = input('User: ')
        tokens = parse_user_input(uinput)
        raw_text = mc.generate(tokens)
        engl_like = MarkovChain.englishify(raw_text, 25)
        print('Trump: ' + engl_like)
        print()

if __name__ == '__main__':    
    mc = MarkovChain('data_1515521742.csv')

    # print(MarkovChain.englishify(mc.generate(('income', 'tax')), 25))

    chat(mc)
    # mc.write_chain('chain')

import logging
import random
import pprint
import json
import sys
import re


class MarkovChain:
    def __init__(self, fname):
        logging.basicConfig(stream=sys.stdout, level=logging.CRITICAL)
        self.punctuation = ['.', ',', '!', '?', ';']
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
    
    def generate(self, wcount):
        condition = lambda ngram : ngram[0] not in self.punctuation
        choose = lambda ngram_set: random.choice(ngram_set)

        # Pick a thrigram to start a generation, shouldn't start with
        # punctuation.
        trigram = ''
        twogram = ''
        onegram = ''

        while trigram == '':
            x = choose(list(self.trigram_chain.keys()))
            if condition(x):
                trigram = x
        
        sentence = []
        [sentence.append(gram) for gram in trigram]

        logging.debug('initial sentence is: ' + str(sentence))

        for i in range(wcount):
            word = ''
            
            # Repeat until we have a new trigram in the chain
            if trigram in self.trigram_chain:
                word = random.choice(self.trigram_chain[trigram])
                trigram = (trigram[1], trigram[2], word)
                sentence.append(word)
                continue
            else:
                # If not - construct a twogram and continue
                twogram = (trigram[1], trigram[2])
            
            logging.debug('fallback to 2-gram')

            if twogram in self.twogram_chain:
                word = random.choice(self.twogram_chain[twogram])
                twogram = (twogram[1], word)
                sentence.append(word)
                trigram = (trigram[1], twogram[0], twogram[1])
                continue
            else:
                onegram = (twogram[1])

            logging.debug('fallback to 1-gram')

            if onegram in self.onegram_chain:
                word = random.choice(self.onegram_chain[onegram])
                onegram = (word)
                sentence.append(word)
                twogram = (twogram[1], onegram[0])
                continue
            else:
                logging.critical('fallback failure')
            
        logging.info('final sentence is: ' + str(sentence))
        logging.info('final sentence len: ' + str(len(sentence)))

        return sentence

    @staticmethod
    def englishify(sequence, length):
        punctuation = ['.', ',', '!', '?', ';']
        finals = ['.', '!', '?', ';']

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

if __name__ == '__main__':    
    mc = MarkovChain('data_1515521742.csv')

    for i in range(20):
        print(MarkovChain.englishify(mc.generate(50), 25))
        print()

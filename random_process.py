import random
import pprint


class MarkovChain:
    def __init__(self, fname):
        self.chain = {}
        self.build(MarkovChain.filter(MarkovChain.read_file(fname)))

    @staticmethod
    def read_file(fpath):
        with open(fpath) as txt:
            data = txt.read()
        return data

    @staticmethod
    def to_list(data):
        return data.split()

    @staticmethod
    def filter(text):
        return [word.lower() for word in text.split(' ') if word != '']

    def print_stats(self):
        def get_symmetric_diff():
            values = set()
            for container in self.chain.values():
                for word in container:
                    values.add(word)
            keys = set(self.chain.keys())

            return values.symmetric_difference(keys)

        leafs = get_symmetric_diff()

        print('{number} leaf: {list}'.format(number=len(leafs), list=leafs))

    def build(self, sequence):
        index = 1

        for word in sequence[1:]:
            key = sequence[index-1]
            if key in self.chain:
                self.chain[key].append(word)
            else:
                self.chain[key] = [word]
            index += 1

    def generate(self, length=20):
        # Initialization, firs step
        word = random.choice(list(self.chain.keys()))
        message = word.capitalize()
        count = 0

        # Loop invariant
        while count < length:
            if word in self.chain:
                second_word = random.choice(self.chain[word])
            else:
                return message

            word = second_word
            message += ' ' + second_word
            count += 1

        return message

    def insight_generation(self, insight, length=20):
        '''By keyword'''
        pass


if __name__ == '__main__':
    mc = MarkovChain('txt_data')
    pprint.pprint(mc.chain)
    print(mc.generate())
    mc.print_stats()

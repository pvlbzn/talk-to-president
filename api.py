# REST API for Markov Chain Chat
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# Normaly chats aren't implemented over http/s protocol, however due to the
# fact that markov chain process is context independent it is a good solution.
# In other words while user may maitain some context for markov chain this
# is doesn't matter because each answer is based only on keywords.
#
# API
# ~~~
#
# GET
# /api/v1/trump
#

from random_process import MarkovChain, parse_user_input
from flask import Flask

app = Flask(__name__)
markov_chain = MarkovChain('./data/data_1515521742.csv')


@app.route("/api/v1/trump/<string:umsg>", methods=['GET'])
def build_message(umsg):
    utokens = parse_user_input(umsg)
    raw_text = markov_chain.generate(utokens)
    res_text = MarkovChain.englishify(raw_text, 25)
    return res_text


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=26000)

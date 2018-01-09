import os
import time
import pprint
import collections
from urllib.parse import urlencode

# 3-rd party
import requests
from requests_oauthlib import OAuth1Session


def get_twitter_keys():
    def get_var(name):
        val = None
        if name in os.environ:
            val = os.environ[name]
        else:
            raise Exception('missing {name} environment variable'.format(name=name))
        
        return val
    
    keys = dict(
        CONSUMER_KEY=get_var('TWITTER_CONSUMER_KEY'),
        CONSUMER_SECRET=get_var('TWITTER_CONSUMER_SECRET'),
        ACCESS_TOCKEN=get_var('TWITTER_ACCESS_TOCKEN'),
        ACCESS_TOCKEN_SECRET=get_var('TWITTER_ACCESS_TOCKEN_SECRET'),
    )

    return keys

Twitt = collections.namedtuple('Twitt', 'id text')

class TwittCollector:
    def __init__(self, credentials):
        self.conn = OAuth1Session(
            credentials['CONSUMER_KEY'],
            credentials['CONSUMER_SECRET'],
            credentials['ACCESS_TOCKEN'],
            credentials['ACCESS_TOCKEN_SECRET'],)

        self.urlparams = dict(
            screen_name='',
            tweet_mode='extended',
            include_rts='false',
            count=2,
        )

        self.base_url = 'https://api.twitter.com/1.1/statuses/user_timeline.json?'

        self.storage = open('data_' + str(int(time.time())) + '.csv', 'w')
    
    def __del__(self):
        self.storage.close()
    
    def get_twitts(self, n=3200):
        if n > 200:
            self.urlparams['count'] = 200
        
            while n > 0:
                data = self.conn.get(self.base_url + urlencode(self.urlparams))

                for twitt in data.json():
                    twt = Twitt(id=twitt['id'], text=twitt['full_text'])
                    self.urlparams['max_id'] = twt.id - 1
                    yield twt
                
                n -= 200
        
    def write(self, twitt):
        # Ensure that there are no new line characters in the text
        txt = ' '.join(twitt.text.split())
        self.storage.write(txt + '\n')

    def collect(self, uname, number):
        '''Collect tweets of a given `uname` user name.

        By default tweets are collected in extended mode (no truncation)
        and no retweets. Twitter's max limitation is 3200 tweets by `max_id`,
        and 200 tweets per request.

        Tweets are collected and recorded in a stream pipeline. As soon as
        tweet serialized it will be yielded to writer.
        '''
        self.urlparams['screen_name'] = uname
        getter = self.get_twitts(number)

        for twitt in getter:
            self.write(twitt)
        

if __name__ == '__main__':
    tc = TwittCollector(get_twitter_keys())
    tc.collect('realDonaldTrump', 3200)

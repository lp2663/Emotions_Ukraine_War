#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May  4 18:32:13 2022

@author: khevnaparikh
"""
import datetime
from twarc.client2 import Twarc2
from twarc.expansions import ensure_flattened
import pandas as pd

# Your bearer token here
t = Twarc2(bearer_token="AAAAAAAAAAAAAAAAAAAAAHDfcAEAAAAAsDj9BLeyK5aPY2kl6JOGGiiKfXw%3DkOilWue9skptf2CVyXe55x9mb8yY5KvIjzyDPit1BSaj8r9wWV")

start = datetime.datetime(2022, 2, 17, 0, 0, 0, 0, datetime.timezone.utc)
end = datetime.datetime(2022, 2, 25, 0, 0, 0, 0, datetime.timezone.utc)


# prewar_start = datetime.datetime(2021, 11, 24, 0, 0, 0, 0, datetime.timezone.utc)
# prewar_end = datetime.datetime(2022, 2, 17, 0, 0, 0, 0, datetime.timezone.utc)
# postwar_start = datetime.datetime(2022, 2, 25, 0, 0, 0, 0, datetime.timezone.utc)
# postwar_end = datetime.datetime(2022, 5, 3, 0, 0, 0, 0, datetime.timezone.utc)


cities = {
    'U1': 'Kyiv, Ukraine',
    'U2': 'Kharkiv, Ukraine',
    'U3': 'Odesa, Ukraine',
    'R1': 'Moscow, Russia',
    'R2': 'St. Petersburg, Russia',
    'R3': 'Novosibirsk, Russia'
    }

# ukraine_stops = 'з і до в це ви що він був для на є як з нею вони я на бути це мають від або один мав за словом але не те що всі ми були коли твій можна сказати там використати кожний який вона робити як їх якщо буде до іншого про'
# u = set(ukraine_stops.split(" "))
# u_str = ''
# for i in u:
#     u_str += i + ' OR '
    
    
# russian_stops = 'от и до в это вы что это он был для на такие как с его они я в быть это есть от или кто-то сказал по слову но не то что все мы были когда вы можете сказать там использовать каждый что она делает как их если'
# r = set(russian_stops.split(" "))
# r_str = ''
# for i in r:
#     r_str += i + ' OR '

stopwords = {
    'Ukrainian ': 'але OR нею OR як OR в OR мають OR від OR сказати OR або OR він OR що OR це OR для OR вони OR іншого OR до OR з OR твій OR на OR там OR був OR словом OR ви OR і OR їх OR про OR буде OR кожний OR не OR можна OR ми OR використати OR який OR мав OR один OR всі OR вона OR я OR були OR робити OR коли OR бути OR є OR те OR якщо OR за',
    
    'Russian': 'использовать OR когда OR в OR от OR как OR были OR был OR кто-то OR для OR это OR до OR их OR если OR там OR на OR с OR его OR и OR делает OR или OR они OR не OR сказал OR что OR он OR все OR вы OR то OR она OR по OR слову OR такие OR я OR есть OR быть OR сказать OR но OR каждый OR мы OR можете',
        }


buckets = {
    'during': (start, end)
    }

tweet_list = [] 
for city in cities.keys():
    print("Pulling for city: " + str(cities[city]))
    for bucket in buckets.keys():
        # if bucket == 'prewar' and city == 'U1':
        #     continue
        print("Pulling for bucket: " + str(bucket))
        tweet_timestamp, tweet_text, tweet_location = [], [], []
        t_0 = buckets[bucket][0]
        t_1 = t_0 + datetime.timedelta(hours=1)
        while t_1 <= buckets[bucket][1]:
            print(t_0)
            stopkey = 'uk' if city[0] == 'U' else 'ru'
            qry = stopwords[stopkey] + " lang:" + stopkey + " place:" + cities[city]
            search_results = t.search_all(query=qry, start_time = t_0, end_time = t_1)
            for page in search_results:
                for tweet in ensure_flattened(page):
                    tweet_list.append(tweet)
                    tweet_timestamp.append(tweet['created_at'])
                    tweet_text.append(tweet['text'])
                    tweet_location.append(cities[city])
                break
            t_0 = t_0 + datetime.timedelta(hours=1)
            t_1 = t_1 + datetime.timedelta(hours=1)
        df_out = pd.DataFrame({
            'timestamp': tweet_timestamp,
            'text': tweet_text,
            'location': tweet_location
            })
        directory = "/Users/khevnaparikh/Desktop/Test"
        path = directory + "/" + str(city) + str(bucket) + ".csv"
        df_out.to_csv(path)
            

#,  place_fields=[cities[city]]





# # Start and end times must be in UTC
# start_time = datetime.datetime(2021, 11, 24, 0, 0, 0, 0, datetime.timezone.utc)
# end_time = datetime.datetime(2021, 11, 24, 1, 0, 0, 0, datetime.timezone.utc)

# # search_results is a generator, max_results is max tweets per page, 500 max for full archive search.
# search_results = t.search_all(query=qry, start_time=start_time, end_time=end_time, max_results=100)

# tweet_list = []

# # Get all results page by page:
# for page in search_results:
#     # print(page)
#     # or alternatively, "flatten" results returning 1 tweet at a time, with expansions inline:
#     for tweet in ensure_flattened(page):
#         # Do something with the tweet
#         tweet_list.append(tweet)
#     # Stop iteration prematurely, to only get 1 page of results.
#     break



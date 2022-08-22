#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May  8 21:43:20 2022

@author: levpaciorkowski
"""

import pandas as pd
import re
import matplotlib.pyplot as plt
import pandasql as ps
from datetime import datetime

pysqldf = lambda q: ps.sqldf(q, globals())



#%%
# define functions for loading and cleaning data

def clean_df(df):
    text_list = []
    time_list = list(df['timestamp'])
    loc_list = list(df['location'])
    for i in range(df.shape[0]):
        t = df['text'][i]
        t = t.lower()
        t = re.sub(r'[^\w\s]','',t)
        text_list.append(t)
    df_out = pd.DataFrame({
        'timestamp': time_list,
        'text': text_list,
        'location': loc_list
        })
    return df_out






def certain_russian(text: str):
    russian_only_chars = ['ё', 'ъ', 'ы', 'э']
    for char in russian_only_chars:
        if char in text:
            return True
    return False

def certain_ukrainian(text: str):
    ukrainian_only_chars = ['ґ', 'є', 'і', 'ї']
    for char in ukrainian_only_chars:
        if char in text:
            return True
    return False

def ukrainian_or_russian(text: str):
    ukr_or_russ_chars = ['а', 'б', 'в', 'г', 'д', 'е', 'ж', 'з', 'и', 'й', 'к', 'л', 'м', 'н', 'о', 'п', 'р', 'с', 'т', 'у', 'ф', 'х',
                     'ц', 'ч', 'ш', 'щ', 'ь', 'ю', 'я']
    for char in ukr_or_russ_chars:
        if char in text:
            return True
    return False


def assign_language(df: pd.DataFrame):
    lang = []
    for i in range(df.shape[0]):
        t = df['text'][i]
        if certain_russian(t):
            lang.append('Russian')
        elif certain_ukrainian(t):
            lang.append('Ukrainian')
        elif ukrainian_or_russian(t):
            lang.append('Ukr/Russ')
        else:
            lang.append('Other')
    
    df['language'] = lang
    return df


def parse_date(dtm: str):
    dtm = dtm.split('-')
    yr = dtm[0]
    mon = dtm[1]
    day = dtm[2][:2]
    return (int(yr), int(mon), int(day))

def assign_date(df: pd.DataFrame):
    yr, mon, day = [], [], []
    for i in range(df.shape[0]):
        dt = parse_date(df['timestamp'][i])
        yr.append(dt[0])
        mon.append(dt[1])
        day.append(dt[2])
    df['year'] = yr
    df['month'] = mon
    df['day'] = day
    return df

def assign_word_counts(df: pd.DataFrame):
    num_words = []
    for i in range(df.shape[0]):
        num_words.append(len(df['text'][i].split()))
    df['num_words'] = num_words
    return df



def load_data():
    # return cleaned data all in singular dataframe
    # also assigns language based on characters known to be exclusively in Ukrainian and Russian
    prefixes = ['R2', 'R3', 'U1', 'U2', 'U3']
    suffixes = ['prewar', 'during', 'postwar']
    prewar = clean_df(pd.read_csv("data/R1prewar.csv"))
    during = clean_df(pd.read_csv("data/R1during.csv", lineterminator='\n'))
    postwar = clean_df(pd.read_csv("data/R1postwar.csv"))
    for suffix in suffixes:
        for prefix in prefixes:
            filepath = "data/" + prefix + suffix + ".csv"
            df = pd.read_csv(filepath) if suffix != 'during' else pd.read_csv(filepath, lineterminator='\n')
            df = clean_df(df)
            if suffix == 'prewar':
                prewar = pd.concat([prewar, df])
            elif suffix == 'during':
                during = pd.concat([during, df])
            else:
                postwar = pd.concat([postwar, df])
    prewar = prewar.drop(columns = ['location'])
    during = during.drop(columns = ['location'])
    postwar = postwar.drop(columns = ['location'])
    prewar = prewar.drop_duplicates()
    during = during.drop_duplicates()
    postwar = postwar.drop_duplicates()
    all_data = pd.concat([prewar, during, postwar])
    all_data = all_data.reset_index()
    all_data = all_data.drop(columns = ['index'])
    all_data = assign_language(all_data)
    all_data = assign_date(all_data)
    all_data = assign_word_counts(all_data)
    
    return all_data


def load_dictionaries():
    # Load Russian sentiment dictionary
    russian_dict = pd.read_csv("russian_dictionary.csv")
    russ_dict = dict()
    for i in range(russian_dict.shape[0]):
        russ_dict[russian_dict['word'][i]] = russian_dict['score'][i]
    
    # Load Ukrainian sentiment dictionary
    ukr_words, ukr_sentiment = [], []
    with open("/Users/levpaciorkowski/Documents/Spring_2022/TextAsData/FinalProject/ukrainian_dictionary.txt") as file:
        for line in file:
            t = line.strip().split()
            ukr_words.append(t[0])
            ukr_sentiment.append(t[1])
    ukr_dict = dict()
    for i in range(len(ukr_words)):
        ukr_dict[ukr_words[i]] = int(ukr_sentiment[i])
    
    return ukr_dict, russ_dict



#%%

# Load data

df = load_data()
ukr_dict, russ_dict = load_dictionaries()


# manually define certain topics so that their prevalence can be measured over time

happy = ['рад', 'щаслив', 'щаст', 'счаст', 'весёл', 'весел', 'довол', 'задовол', 'смешн', 'смішн']
war = ['войн','війн']
tanks = ['танк', 'бак']
hlp = ['помощ', 'допомог', 'помог']
ukraine = ['украин', 'україн']
russia = ['росси', 'росі', 'русск', 'російськ']
fear = ['страх', 'боюсь', 'боюся', 'боишься', 'боїшся', 'боится', 'боїться', 'боимся', 'боїмося', 'боитесь', 'боїтеся',
        'боятся', 'бояться', 'боял', 'боявся', 'страшн', 'волн', 'хвилю']

winter = ['снег', 'сніг', 'снежн', 'сніжн', 'холодн', 'зим', 'лёд', 'льд', 'лед', 'лід', 'льод']
freedom = ['свобод', 'демократи', 'независимост', 'незалежніст', 'незалежност']

zelenskyy = ['зеленск', 'зеленськ']
putin = ['путин', 'путін']
mariupol = ['мариупол', 'маріупол']
donbass = ['донбас']
children = ['дети', 'дитя', 'детей', 'детьми', 'дітей', 'діти', 'дітям', 'дітьми', 'дітьом', 
            'ребенок', 'ребёнок', 'дитина']

woman = ['женщин', 'жінк', 'мам', 'бабушк', 'бабус']
love = ['любл', 'любиш', 'люби', 'любя', 'любов', 'любв']
bravery = ['храбр', 'хоробр', 'герой', 'герои', 'герої']

homeland = ['родин', 'батьківщ', 'отечеств', 'вітчизн', 'страны', 'страна', 'странам', 'стране', 'страну',
            'странами', 'страной', 'странах']

liberation = ['освобождени', 'звільнен']
nato = ['нато']

kyiv = ['киев', 'київ', 'києв']
kharkiv = ['харьков', 'харків', 'харков']



c = pysqldf("SELECT * FROM df WHERE text LIKE '%дет%' OR text LIKE '%дит%' OR text LIKE '%ребёнок%' OR text LIKE '%ребенок%'")


topics = {'happy': happy, 'war': war, 'tanks': tanks, 'hlp': hlp, 'ukraine': ukraine, 'russia': russia,
          'fear': fear, 'winter': winter, 'freedom': freedom, 'zelenskyy': zelenskyy, 'putin': putin,
          'mariupol': mariupol, 'donbass': donbass, 'children': children, 'woman': woman, 'love': love,
          'bravery': bravery, 'homeland': homeland, 'liberation': liberation, 'nato': nato, 'kyiv': kyiv,
          'kharkiv': kharkiv}

#%%
# define useful functions for calculating data aggregations

def mentions_topic(text: str, topic: list):
    words = text.split()
    for word in words:
        for conj in topic:
            if conj in word:
                return 1
    return 0




def moving_average(data: pd.DataFrame, col: str, days: int):
    ma = []
    for i in range(data.shape[0]):
        if i < days:
            ma.append(None)
            continue
        vals = data[col][i-days:i]
        ma.append(vals.mean())
    return ma





def graph_prevalence_over_time(topic: list, df: pd.DataFrame):
    occurrences = []
    for i in range(df.shape[0]):
        print(i)
        t = df['text'][i]
        mentions = mentions_topic(t, topic)
        occurrences.append(mentions)
    df['occurrences'] = occurrences
    query = "SELECT year, month, day, COUNT(*) AS n, SUM(occurrences) AS x FROM df GROUP BY year, month, day"
    query_rus = "SELECT year, month, day, COUNT(*) AS n, SUM(occurrences) AS x FROM df WHERE language = 'Russian' GROUP BY year, month, day"
    query_ukr = "SELECT year, month, day, COUNT(*) AS n, SUM(occurrences) AS x FROM df WHERE language = 'Ukrainian' GROUP BY year, month, day"
    print("Calculating for all")
    summary_df = pysqldf(query)
    summary_df['prop'] = summary_df['x']/summary_df['n']
    print("Calculating for Russian only")
    summary_rus = pysqldf(query_rus)
    summary_rus['prop'] = summary_rus['x']/summary_rus['n']
    print("Calculating for Ukrainian only")
    summary_ukr = pysqldf(query_ukr)
    summary_ukr['prop'] = summary_ukr['x']/summary_ukr['n']
    
    

    x_axis, y_axis, rus, ukr = [], [], [], []
    for i in range(summary_df.shape[0]):
        dt = datetime(year=summary_df['year'][i], month=summary_df['month'][i], day=summary_df['day'][i])
        x_axis.append(dt)
        stat = summary_df['x'][i]/summary_df['n'][i]
        y_axis.append(stat)
        stat_rus = summary_rus['x'][i]/summary_rus['n'][i]
        rus.append(stat_rus)
        stat_ukr = summary_ukr['x'][i]/summary_ukr['n'][i]
        ukr.append(stat_ukr)
    three_day_ma = moving_average(summary_df, 'prop', 3)
    three_day_rus = moving_average(summary_rus, 'prop', 3)
    three_day_ukr = moving_average(summary_ukr, 'prop', 3)
    
    return pd.DataFrame({
        'date': x_axis,
        'prevalence': y_axis,
        'MA_3': three_day_ma
        }), pd.DataFrame({
            'date': x_axis,
            'prevalence_russian': rus,
            'MA_3': three_day_rus
            }), pd.DataFrame({
                'date': x_axis,
                'prevalence_ukrainian': ukr,
                'MA_3': three_day_ukr
                })

def graph_language_proportion():
    tweets_per_day = pysqldf("SELECT year, month, day, COUNT(*) as n FROM df GROUP BY year, month, day")
    russian_daily = pysqldf("SELECT year, month, day, COUNT(*) as n FROM df WHERE language = 'Russian' GROUP BY year, month, day")
    ukraine_daily = pysqldf("SELECT year, month, day, COUNT(*) as n FROM df WHERE language = 'Ukrainian' GROUP BY year, month, day")
    russ_ukr_daily = pysqldf("SELECT year, month, day, COUNT(*) as n FROM df WHERE language = 'Ukr/Russ' GROUP BY year, month, day")
    
    x_axis, russ, ukr, either, other = [], [], [], [], []
    for i in range(tweets_per_day.shape[0]):
        dt = datetime(year=tweets_per_day['year'][i], month=tweets_per_day['month'][i], day=tweets_per_day['day'][i])
        x_axis.append(dt)
        n = tweets_per_day['n'][i]
        r = russian_daily['n'][i]
        u = ukraine_daily['n'][i]
        e = russ_ukr_daily['n'][i]
        russ.append(r / n)
        ukr.append(u / n)
        either.append(e / n)
        other.append(1 - (r+u+e)/n)
    summary_df = pd.DataFrame({
        'date': x_axis,
        'russian': russ,
        'ukrainian': ukr,
        'either': either,
        'other': other
        })
    return summary_df

#%%
# Graph proportion of tweet language over time
lang_prop = graph_language_proportion()
ukr_baseline = sum(lang_prop['ukrainian'][:68]) / len(lang_prop['ukrainian'][:68])
ukr_peak = max(lang_prop['ukrainian'][92:100])
ukr_latest = sum(lang_prop['ukrainian'][-7:]) / len(lang_prop['ukrainian'][-7:])

x_axis = lang_prop['date']
russ = lang_prop['russian']
ukr = lang_prop['ukrainian']
either = lang_prop['either']
other = lang_prop['other']

plt.plot(x_axis, russ, label = 'Russian')
plt.plot(x_axis, ukr, label = 'Ukrainian')
plt.plot(x_axis, either, label = 'Russian or Ukrainian')
plt.plot(x_axis, other, label = 'Other Languages')
plt.ylim((0,1))
plt.vlines(x=datetime(year=2022, month=2, day=24), ymin=0, ymax = 0.6,
           colors='red',
           label='Invasion Date (2/24)',
           linestyles='dashed')
plt.xlabel('Date')
plt.ylabel('Proportion')
plt.title('Proportion of Tweets by Language')
plt.legend()
plt.show()

#%%
# define more useful functions
def measure_baseline(df, colname):
    return sum(df[colname][:68]) / len(df[colname][:68])

def measure_extreme(df, colname, kind):
    if kind == 'max':
        arg = df['date'][df[colname][92:100].argmax()+92]
        return max(df[colname][92:100]), arg
    if kind == 'min':
        arg = df['date'][df[colname][92:100].argmin()+92]
        return min(df[colname][92:100]), arg

def measure_latest(df, colname):
    return df[colname][-7:].mean()


# Calculate recovery coefficient by language
def calculate_R(df, colname, kind):
    baseline = measure_baseline(df, colname)
    extreme, t0 = measure_extreme(df, colname, kind)
    latest = measure_latest(df, colname)
    t1 = datetime(year=2022, month=5, day=2)
    delta = t1-t0
    delta = delta.days
    
    shock = 100*(extreme - baseline) / baseline
    
    R = ((extreme - latest) / (extreme - baseline)) * 30/(delta)
    
    results = {
        'baseline': baseline,
        'extreme': extreme,
        'shock': shock,
        'current': latest,
        'R': R
        }
    return results

#%%

# Graph prevalence of tweets mentioning 'war' over time
war_all, war_rus, war_ukr = graph_prevalence_over_time(topics['war'], df)

x_axis = war_all['date']
all_prop = war_all['prevalence']
rus_prop = war_rus['prevalence_russian']
ukr_prop = war_ukr['prevalence_ukrainian']

plt.plot(x_axis, all_prop, label = "Russian and Ukrainian", linewidth=3, color='green')
plt.plot(x_axis, rus_prop, label = "Russian only", linewidth=0.5, color='red')
plt.plot(x_axis, ukr_prop, label = "Ukrainian only", linewidth=0.5, color='blue')
plt.vlines(x=datetime(year=2022, month=2, day=24), ymin=0, ymax=0.025, colors='red',
            label='Invasion Date (2/24)',
            linestyles='dashed')
plt.xlabel('Date')
plt.ylabel('Proportion')
plt.title("Proportion of Tweets Mentioning Declensions of 'war'")
plt.legend()
plt.show()

calculate_R(war_all, 'prevalence', 'max')
calculate_R(war_rus, 'prevalence_russian', 'max')
calculate_R(war_ukr, 'prevalence_ukrainian', 'max')


# %%
# Prevalence of tweets mentioning 'tank' over time
tanks_all, tanks_rus, tanks_ukr = graph_prevalence_over_time(topics['tanks'], df)

x_axis = tanks_all['date']
all_prop = tanks_all['prevalence']
rus_prop = tanks_rus['prevalence_russian']
ukr_prop = tanks_ukr['prevalence_ukrainian']

plt.plot(x_axis, all_prop, label = "Russian and Ukrainian", linewidth=3, color='green')
plt.plot(x_axis, rus_prop, label = "Russian only", linewidth=0.5, color='red')
plt.plot(x_axis, ukr_prop, label = "Ukrainian only", linewidth=0.5, color='blue')
plt.vlines(x=datetime(year=2022, month=2, day=24), ymin=0, ymax=0.007, colors='red',
            label='Invasion Date (2/24)',
            linestyles='dashed')
plt.xlabel('Date')
plt.ylabel('Proportion')
plt.title("Proportion of Tweets Mentioning Declensions of 'tank'")
plt.legend()
plt.show()

calculate_R(tanks_all, 'prevalence', 'max')
calculate_R(tanks_rus, 'prevalence_russian', 'max')
calculate_R(tanks_ukr, 'prevalence_ukrainian', 'max')

# %%
# Prevalence of tweets mentioning 'happy', 'cheerful' or 'laugh' over time
happy_all, happy_rus, happy_ukr = graph_prevalence_over_time(topics['happy'], df)

x_axis = happy_all['date']
all_prop = happy_all['prevalence']
rus_prop = happy_rus['prevalence_russian']
ukr_prop = happy_ukr['prevalence_ukrainian']

plt.plot(x_axis, all_prop, label = "Russian and Ukrainian", linewidth=3, color='green')
plt.plot(x_axis, rus_prop, label = "Russian only", linewidth=0.5, color='red')
plt.plot(x_axis, ukr_prop, label = "Ukrainian only", linewidth=0.5, color='blue')
plt.vlines(x=datetime(year=2022, month=2, day=24), ymin=0, ymax=0.04, colors='red',
            label='Invasion Date (2/24)',
            linestyles='dashed')
plt.vlines(x=datetime(year=2021, month=12, day=31), ymin=0, ymax=0.04, colors='purple',
           label="New Year's Eve",
           linestyles='dashed')
plt.xlabel('Date')
plt.ylabel('Proportion')
plt.title("Proportion of Tweets Mentioning Declensions of 'happy', 'cheerful', 'laugh'")
plt.ylim((0,0.17))
plt.legend(loc = 'upper left')
plt.show()

calculate_R(happy_all, 'prevalence', 'min')
calculate_R(happy_rus, 'prevalence_russian', 'min')
calculate_R(happy_ukr, 'prevalence_ukrainian', 'min')



#%%
# Prevalence of tweets mentioning 'help' over time
help_all, help_rus, help_ukr = graph_prevalence_over_time(topics['hlp'], df)

x_axis = help_all['date']
all_prop = help_all['prevalence']
rus_prop = help_rus['prevalence_russian']
ukr_prop = help_ukr['prevalence_ukrainian']

plt.plot(x_axis, all_prop, label = "Russian and Ukrainian", linewidth=3, color='green')
plt.plot(x_axis, rus_prop, label = "Russian only", linewidth=0.5, color='red')
plt.plot(x_axis, ukr_prop, label = "Ukrainian only", linewidth=0.5, color='blue')
plt.vlines(x=datetime(year=2022, month=2, day=24), ymin=0, ymax=0.01, colors='red',
            label='Invasion Date (2/24)',
            linestyles='dashed')
plt.xlabel('Date')
plt.ylabel('Proportion')
plt.title("Proportion of Tweets Mentioning Declensions of 'help'")
plt.ylim((0,0.05))
plt.legend(loc = 'upper left')
plt.show()

calculate_R(help_all, 'prevalence', 'max')
calculate_R(help_rus, 'prevalence_russian', 'max')
calculate_R(help_ukr, 'prevalence_ukrainian', 'max')

#%%
# Prevalence of tweets mentioning 'Ukraine' over time
ukraine_all, ukraine_rus, ukrain_ukr = graph_prevalence_over_time(topics['ukraine'], df)

x_axis = ukraine_all['date']
all_prop = ukraine_all['prevalence']
rus_prop = ukraine_rus['prevalence_russian']
ukr_prop = ukrain_ukr['prevalence_ukrainian']

plt.plot(x_axis, all_prop, label = "Russian and Ukrainian", linewidth=3, color='green')
plt.plot(x_axis, rus_prop, label = "Russian only", linewidth=0.5, color='red')
plt.plot(x_axis, ukr_prop, label = "Ukrainian only", linewidth=0.5, color='blue')
plt.vlines(x=datetime(year=2022, month=2, day=24), ymin=0, ymax=0.07, colors='red',
            label='Invasion Date (2/24)',
            linestyles='dashed')
plt.xlabel('Date')
plt.ylabel('Proportion')
plt.title("Proportion of Tweets Mentioning Declensions of 'Ukraine'")
plt.ylim((0,0.35))
plt.legend(loc = 'upper left')
plt.show()

calculate_R(ukraine_all, 'prevalence', 'max')
calculate_R(ukraine_rus, 'prevalence_russian', 'max')
calculate_R(ukrain_ukr, 'prevalence_ukrainian', 'max')

#%%
# Prevalence of tweets mentioning 'Russia' over time
russia_all, russia_rus, russia_ukr = graph_prevalence_over_time(topics['russia'], df)

x_axis = russia_all['date']
all_prop = russia_all['prevalence']
rus_prop = russia_rus['prevalence_russian']
ukr_prop = russia_ukr['prevalence_ukrainian']


plt.plot(x_axis, all_prop, label = "Russian and Ukrainian", linewidth=3, color='green')
plt.plot(x_axis, rus_prop, label = "Russian only", linewidth=0.5, color='red')
plt.plot(x_axis, ukr_prop, label = "Ukrainian only", linewidth=0.5, color='blue')
plt.vlines(x=datetime(year=2022, month=2, day=24), ymin=0, ymax=0.1, colors='red',
            label='Invasion Date (2/24)',
            linestyles='dashed')
plt.xlabel('Date')
plt.ylabel('Proportion')
plt.title("Proportion of Tweets Mentioning Declensions of 'Russia', 'Russian'")
plt.legend(loc = 'upper left')
plt.show()

calculate_R(russia_all, 'prevalence', 'max')
calculate_R(russia_rus, 'prevalence_russian', 'max')
calculate_R(russia_ukr, 'prevalence_ukrainian', 'max')

#%%
# Prevalence of tweets mentioning words related to 'fear' over time
fear_all, fear_rus, fear_ukr = graph_prevalence_over_time(topics['fear'], df)

x_axis = fear_all['date']
all_prop = fear_all['prevalence']
rus_prop = fear_rus['prevalence_russian']
ukr_prop = fear_ukr['prevalence_ukrainian']

plt.plot(x_axis, all_prop, label = "Russian and Ukrainian", linewidth=3, color='green')
plt.plot(x_axis, rus_prop, label = "Russian only", linewidth=0.5, color='red')
plt.plot(x_axis, ukr_prop, label = "Ukrainian only", linewidth=0.5, color='blue')
plt.vlines(x=datetime(year=2022, month=2, day=24), ymin=0, ymax=0.01, colors='red',
            label='Invasion Date (2/24)',
            linestyles='dashed')
plt.xlabel('Date')
plt.ylabel('Proportion')
plt.title("Proportion of Tweets Mentioning Declensions of 'fear', 'afraid', 'scary' or 'worry'")
plt.legend(loc = 'upper left')
plt.show()

calculate_R(fear_all, 'prevalence', 'max')
calculate_R(fear_rus, 'prevalence_russian', 'max')
calculate_R(fear_ukr, 'prevalence_ukrainian', 'max')

# %%
# Prevalence of tweets mentioning winter-related words? - seems to decline in prevalence as weather gets warmer
winter_all, winter_rus, winter_ukr = graph_prevalence_over_time(topics['winter'], df)

x_axis = winter_all['date']
all_prop = winter_all['prevalence']
rus_prop = winter_rus['prevalence_russian']
ukr_prop = winter_ukr['prevalence_ukrainian']

plt.plot(x_axis, all_prop, label = "Russian and Ukrainian", linewidth=3, color='green')
plt.plot(x_axis, rus_prop, label = "Russian only", linewidth=0.5, color='red')
plt.plot(x_axis, ukr_prop, label = "Ukrainian only", linewidth=0.5, color='blue')
plt.vlines(x=datetime(year=2022, month=2, day=24), ymin=0, ymax=0.02, colors='red',
            label='Invasion Date (2/24)',
            linestyles='dashed')
plt.ylim((0,0.1))
plt.xlabel('Date')
plt.ylabel('Proportion')
plt.title("Proportion of Tweets Mentioning Declensions of 'snow', 'cold', 'winter' or 'ice'")
plt.legend(loc = 'upper left')
plt.show()

calculate_R(winter_all, 'prevalence', 'min')

#%%
# Prevalence of tweets mentioning 'freedom' or 'democracy' - this does not appear to be significant as the data is too noisy for this term
free_all, free_rus, free_ukr = graph_prevalence_over_time(topics['freedom'], df)

x_axis = free_all['date']
all_prop = free_all['prevalence']
rus_prop = free_rus['prevalence_russian']
ukr_prop = free_ukr['prevalence_ukrainian']

plt.plot(x_axis, all_prop, label = "Russian and Ukrainian", linewidth=3, color='green')
plt.plot(x_axis, rus_prop, label = "Russian only", linewidth=0.5, color='red')
plt.plot(x_axis, ukr_prop, label = "Ukrainian only", linewidth=0.5, color='blue')
plt.vlines(x=datetime(year=2022, month=2, day=24), ymin=0, ymax=0.02, colors='red',
            label='Invasion Date (2/24)',
            linestyles='dashed')
plt.xlabel('Date')
plt.ylabel('Proportion')
plt.title("Proportion of Tweets Mentioning Declensions of 'freedom', 'democracy' or 'independence'")
plt.legend(loc = 'upper left')
plt.show()

calculate_R(free_all, 'prevalence', 'max')
calculate_R(free_rus, 'prevalence_russian', 'max')
calculate_R(free_ukr, 'prevalence_ukrainian', 'max')

# %%
# Prevalence of tweets mentioning 'zelenskyy' - note the drastic difference in trend shock comparing Russian to Ukrainian
zelenskyy_all, zelenskyy_rus, zelenskyy_ukr = graph_prevalence_over_time(topics['zelenskyy'], df)

x_axis = zelenskyy_all['date']
all_prop = zelenskyy_all['prevalence']
rus_prop = zelenskyy_rus['prevalence_russian']
ukr_prop = zelenskyy_ukr['prevalence_ukrainian']

plt.plot(x_axis, all_prop, label = "Russian and Ukrainian", linewidth=3, color='green')
plt.plot(x_axis, rus_prop, label = "Russian only", linewidth=0.5, color='red')
plt.plot(x_axis, ukr_prop, label = "Ukrainian only", linewidth=0.5, color='blue')
plt.vlines(x=datetime(year=2022, month=2, day=24), ymin=0, ymax=0.02, colors='red',
            label='Invasion Date (2/24)',
            linestyles='dashed')
plt.xlabel('Date')
plt.ylabel('Proportion')
plt.title("Proportion of Tweets Mentioning Declensions of 'Zelenskyy'")
plt.legend(loc = 'upper left')
plt.show()

calculate_R(zelenskyy_all, 'prevalence', 'max')
calculate_R(zelenskyy_rus, 'prevalence_russian', 'max')
calculate_R(zelenskyy_ukr, 'prevalence_ukrainian', 'min')

#%%
# Prevalence of tweets mentioning 'putin'
putin_all, putin_rus, putin_ukr = graph_prevalence_over_time(topics['putin'], df)

x_axis = putin_all['date']
all_prop = putin_all['prevalence']
rus_prop = putin_rus['prevalence_russian']
ukr_prop = putin_ukr['prevalence_ukrainian']


plt.plot(x_axis, all_prop, label = "Russian and Ukrainian", linewidth=3, color='green')
plt.plot(x_axis, rus_prop, label = "Russian only", linewidth=0.5, color='red')
plt.plot(x_axis, ukr_prop, label = "Ukrainian only", linewidth=0.5, color='blue')
plt.vlines(x=datetime(year=2022, month=2, day=24), ymin=0, ymax=0.02, colors='red',
            label='Invasion Date (2/24)',
            linestyles='dashed')
plt.xlabel('Date')
plt.ylabel('Proportion')
plt.title("Proportion of Tweets Mentioning Declensions of 'Putin'")
plt.legend(loc = 'upper left')
plt.show()

calculate_R(putin_all, 'prevalence', 'max')
calculate_R(putin_rus, 'prevalence_russian', 'max')
calculate_R(putin_ukr, 'prevalence_ukrainian', 'max')

#%%
# Prevalence of tweets mentioning 'Mariupol' - the most significant jump yet
mariupol_all, mariupol_rus, mariupol_ukr = graph_prevalence_over_time(topics['mariupol'], df)

x_axis = mariupol_all['date']
all_prop = mariupol_all['prevalence']
rus_prop = mariupol_rus['prevalence_russian']
ukr_prop = mariupol_ukr['prevalence_ukrainian']


plt.plot(x_axis, all_prop, label = "Russian and Ukrainian", linewidth=3, color='green')
plt.plot(x_axis, rus_prop, label = "Russian only", linewidth=0.5, color='red')
plt.plot(x_axis, ukr_prop, label = "Ukrainian only", linewidth=0.5, color='blue')
plt.vlines(x=datetime(year=2022, month=2, day=24), ymin=0, ymax=0.02, colors='red',
            label='Invasion Date (2/24)',
            linestyles='dashed')
plt.xlabel('Date')
plt.ylabel('Proportion')
plt.title("Proportion of Tweets Mentioning Declensions of 'Mariupol'")
plt.legend(loc = 'upper left')
plt.show()

calculate_R(mariupol_all, 'prevalence', 'max')
calculate_R(mariupol_rus, 'prevalence_russian', 'max')
calculate_R(mariupol_ukr, 'prevalence_ukrainian', 'max')

#%%
# Prevalence of tweets mentioning 'Donbass' - see how this spikes right before the invasion
donbass_all, donbass_rus, donbass_ukr = graph_prevalence_over_time(topics['donbass'], df)

x_axis = donbass_all['date']
all_prop = donbass_all['prevalence']
rus_prop = donbass_rus['prevalence_russian']
ukr_prop = donbass_ukr['prevalence_ukrainian']

plt.plot(x_axis, all_prop, label = "Russian and Ukrainian", linewidth=3, color='green')
plt.plot(x_axis, rus_prop, label = "Russian only", linewidth=0.5, color='red')
plt.plot(x_axis, ukr_prop, label = "Ukrainian only", linewidth=0.5, color='blue')
plt.vlines(x=datetime(year=2022, month=2, day=24), ymin=0, ymax=0.02, colors='red',
            label='Invasion Date (2/24)',
            linestyles='dashed')
plt.xlabel('Date')
plt.ylabel('Proportion')
plt.title("Proportion of Tweets Mentioning Declensions of 'Donbass'")
plt.legend(loc = 'upper left')
plt.show()

calculate_R(donbass_all, 'prevalence', 'max')
calculate_R(donbass_rus, 'prevalence_russian', 'max')
calculate_R(donbass_ukr, 'prevalence_ukrainian', 'min')

#%%
# Prevalence of tweets mentioning declensions of 'child' - was curious to check if this had a response to the crisis
# have to choose these declensions carefully and fully specify many of them
# Notably, Ukrainian sees a major spike on 03/09 - day the children's hospital was bombed in Mariupol
# Russian language does not see a spike on 03/09
children_all, children_rus, children_ukr = graph_prevalence_over_time(topics['children'], df)

x_axis = children_all['date']
all_prop = children_all['prevalence']
rus_prop = children_rus['prevalence_russian']
ukr_prop = children_ukr['prevalence_ukrainian']

plt.plot(x_axis, all_prop, label = "Russian and Ukrainian", linewidth=3, color='green')
plt.plot(x_axis, rus_prop, label = "Russian only", linewidth=0.5, color='red')
plt.plot(x_axis, ukr_prop, label = "Ukrainian only", linewidth=0.5, color='blue')
plt.vlines(x=datetime(year=2022, month=2, day=24), ymin=0, ymax=0.02, colors='red',
            label='Invasion Date (2/24)',
            linestyles='dashed')
plt.xlabel('Date')
plt.ylabel('Proportion')
plt.title("Proportion of Tweets Mentioning Declensions of 'child'")
plt.legend(loc = 'upper left')
plt.show()

calculate_R(children_all, 'prevalence', 'max')
calculate_R(children_rus, 'prevalence_russian', 'max')
calculate_R(children_ukr, 'prevalence_ukrainian', 'max')

#%%
# Out of similar curiosity, examine prevalence of tweets mentioning declensions of 'woman', 'mother', 'grandmother'
# Nothing significant as a response to the invasion. A noticeable spike occurs on 03/08, international women's day
woman_all, woman_rus, woman_ukr = graph_prevalence_over_time(topics['woman'], df)

x_axis = woman_all['date']
all_prop = woman_all['prevalence']
rus_prop = woman_rus['prevalence_russian']
ukr_prop = woman_ukr['prevalence_ukrainian']


plt.plot(x_axis, all_prop, label = "Russian and Ukrainian", linewidth=3, color='green')
plt.plot(x_axis, rus_prop, label = "Russian only", linewidth=0.5, color='red')
plt.plot(x_axis, ukr_prop, label = "Ukrainian only", linewidth=0.5, color='blue')
plt.vlines(x=datetime(year=2022, month=2, day=24), ymin=0, ymax=0.02, colors='red',
            label='Invasion Date (2/24)',
            linestyles='dashed')
plt.xlabel('Date')
plt.ylabel('Proportion')
plt.title("Proportion of Tweets Mentioning Declensions of 'woman', 'mother', 'grandmother'")
plt.legend(loc = 'upper left')
plt.show()

# %%
# Prevalence of tweets mentioning 'love'
# This seems to be significant for Russian, less so for Ukrainian although that may be because of too few data for just Ukrainian
# Notably in Russian there is a drop that begins before the invasion
# Note the spike on New Year's
# It's interesting that overall, Ukrainians don't seem to tweet as much about love as Russians

love_all, love_rus, love_ukr = graph_prevalence_over_time(topics['love'], df)

x_axis = love_all['date']
all_prop = love_all['prevalence']
rus_prop = love_rus['prevalence_russian']
ukr_prop = love_ukr['prevalence_ukrainian']

plt.plot(x_axis, all_prop, label = "Russian and Ukrainian", linewidth=3, color='green')
plt.plot(x_axis, rus_prop, label = "Russian only", linewidth=0.5, color='red')
plt.plot(x_axis, ukr_prop, label = "Ukrainian only", linewidth=0.5, color='blue')
plt.vlines(x=datetime(year=2022, month=2, day=24), ymin=0, ymax=0.05, colors='red',
            label='Invasion Date (2/24)',
            linestyles='dashed')
plt.ylim((0,0.1))
plt.xlabel('Date')
plt.ylabel('Proportion')
plt.title("Proportion of Tweets Mentioning Declensions of 'love'")
plt.legend(loc = 'upper left')
plt.show()

calculate_R(love_all, 'prevalence', 'min')
calculate_R(love_rus, 'prevalence_russian', 'min')
calculate_R(love_ukr, 'prevalence_ukrainian', 'min')

#%%
# Bravery
bravery_all, bravery_rus, bravery_ukr = graph_prevalence_over_time(topics['bravery'], df)

x_axis = bravery_all['date']
all_prop = bravery_all['prevalence']
rus_prop = bravery_rus['prevalence_russian']
ukr_prop = bravery_ukr['prevalence_ukrainian']

plt.plot(x_axis, all_prop, label = "Russian and Ukrainian", linewidth=3, color='green')
plt.plot(x_axis, rus_prop, label = "Russian only", linewidth=0.5, color='red')
plt.plot(x_axis, ukr_prop, label = "Ukrainian only", linewidth=0.5, color='blue')
plt.vlines(x=datetime(year=2022, month=2, day=24), ymin=0, ymax=0.02, colors='red',
            label='Invasion Date (2/24)',
            linestyles='dashed')
plt.ylim((0,0.04))
plt.xlabel('Date')
plt.ylabel('Proportion')
plt.title("Proportion of Tweets Mentioning Declensions of 'bravery', 'courage', 'hero'")
plt.legend(loc = 'upper left')
plt.show()

calculate_R(bravery_all, 'prevalence', 'max')
calculate_R(bravery_rus, 'prevalence_russian', 'max')
calculate_R(bravery_ukr, 'prevalence_ukrainian', 'max')



#%%
# Homeland
homeland_all, homeland_rus, homeland_ukr = graph_prevalence_over_time(topics['homeland'], df)

x_axis = homeland_all['date']
all_prop = homeland_all['prevalence']
rus_prop = homeland_rus['prevalence_russian']
ukr_prop = homeland_ukr['prevalence_ukrainian']

plt.plot(x_axis, all_prop, label = "Russian and Ukrainian", linewidth=3, color='green')
plt.plot(x_axis, rus_prop, label = "Russian only", linewidth=0.5, color='red')
plt.plot(x_axis, ukr_prop, label = "Ukrainian only", linewidth=0.5, color='blue')
plt.vlines(x=datetime(year=2022, month=2, day=24), ymin=0, ymax=0.02, colors='red',
            label='Invasion Date (2/24)',
            linestyles='dashed')
plt.xlabel('Date')
plt.ylabel('Proportion')
plt.title("Proportion of Tweets Mentioning Declensions of 'homeland', 'fatherland', 'country'")
plt.legend(loc = 'upper left')
plt.show()

calculate_R(homeland_all, 'prevalence', 'max')
calculate_R(homeland_rus, 'prevalence_russian', 'max')
calculate_R(homeland_ukr, 'prevalence_ukrainian', 'max')

#%%
# Liberation
liberation_all, liberation_rus, liberation_ukr = graph_prevalence_over_time(topics['liberation'], df)

x_axis = liberation_all['date']
all_prop = liberation_all['prevalence']
rus_prop = liberation_rus['prevalence_russian']
ukr_prop = liberation_ukr['prevalence_ukrainian']

plt.plot(x_axis, all_prop, label = "Russian and Ukrainian", linewidth=3, color='green')
plt.plot(x_axis, rus_prop, label = "Russian only", linewidth=0.5, color='red')
plt.plot(x_axis, ukr_prop, label = "Ukrainian only", linewidth=0.5, color='blue')
plt.vlines(x=datetime(year=2022, month=2, day=24), ymin=0, ymax=0.02, colors='red',
            label='Invasion Date (2/24)',
            linestyles='dashed')
plt.xlabel('Date')
plt.ylabel('Proportion')
plt.title("Proportion of Tweets Mentioning Declensions of 'liberation'")
plt.legend(loc = 'upper left')
plt.show()

#%%
# Nato
nato_all, nato_rus, nato_ukr = graph_prevalence_over_time(topics['nato'], df)

x_axis = nato_all['date']
all_prop = nato_all['prevalence']
rus_prop = nato_rus['prevalence_russian']
ukr_prop = nato_ukr['prevalence_ukrainian']

plt.plot(x_axis, all_prop, label = "Russian and Ukrainian", linewidth=3, color='green')
plt.plot(x_axis, rus_prop, label = "Russian only", linewidth=0.5, color='red')
plt.plot(x_axis, ukr_prop, label = "Ukrainian only", linewidth=0.5, color='blue')
plt.vlines(x=datetime(year=2022, month=2, day=24), ymin=0, ymax=0.02, colors='red',
            label='Invasion Date (2/24)',
            linestyles='dashed')
plt.xlabel('Date')
plt.ylabel('Proportion')
plt.title("Proportion of Tweets Mentioning Declensions of 'NATO'")
plt.legend(loc = 'upper left')
plt.show()

#%%
# Kyiv
kyiv_all, kyiv_rus, kyiv_ukr = graph_prevalence_over_time(topics['kyiv'], df)

x_axis = kyiv_all['date']
all_prop = kyiv_all['prevalence']
rus_prop = kyiv_rus['prevalence_russian']
ukr_prop = kyiv_ukr['prevalence_ukrainian']

plt.plot(x_axis, all_prop, label = "Russian and Ukrainian", linewidth=3, color='green')
plt.plot(x_axis, rus_prop, label = "Russian only", linewidth=0.5, color='red')
plt.plot(x_axis, ukr_prop, label = "Ukrainian only", linewidth=0.5, color='blue')
plt.vlines(x=datetime(year=2022, month=2, day=24), ymin=0, ymax=0.02, colors='red',
            label='Invasion Date (2/24)',
            linestyles='dashed')
plt.xlabel('Date')
plt.ylabel('Proportion')
plt.title("Proportion of Tweets Mentioning Declensions of 'Kyiv'")
plt.legend(loc = 'upper left')
plt.show()

calculate_R(kyiv_all, 'prevalence', 'max')
calculate_R(kyiv_rus, 'prevalence_russian', 'max')
calculate_R(kyiv_ukr, 'prevalence_ukrainian', 'max')

#%%
# Kharkiv
kharkiv_all, kharkiv_rus, kharkiv_ukr = graph_prevalence_over_time(topics['kharkiv'], df)

x_axis = kharkiv_all['date']
all_prop = kharkiv_all['prevalence']
rus_prop = kharkiv_rus['prevalence_russian']
ukr_prop = kharkiv_ukr['prevalence_ukrainian']

plt.plot(x_axis, all_prop, label = "Russian and Ukrainian", linewidth=3, color='green')
plt.plot(x_axis, rus_prop, label = "Russian only", linewidth=0.5, color='red')
plt.plot(x_axis, ukr_prop, label = "Ukrainian only", linewidth=0.5, color='blue')
plt.vlines(x=datetime(year=2022, month=2, day=24), ymin=0, ymax=0.02, colors='red',
            label='Invasion Date (2/24)',
            linestyles='dashed')
plt.xlabel('Date')
plt.ylabel('Proportion')
plt.title("Proportion of Tweets Mentioning Declensions of 'Kharkiv'")
plt.legend(loc = 'upper left')
plt.show()

calculate_R(kharkiv_all, 'prevalence', 'max')
calculate_R(kharkiv_rus, 'prevalence_russian', 'max')
calculate_R(kharkiv_ukr, 'prevalence_ukrainian', 'max')





































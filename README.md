# Emotions_Ukraine_War
Note that this project is being done as a team of two with team members Lev Paciorkowski and Khevna Parikh, both masters candidates at the New York University Center for Data Science.

Research Topic:
The scope of our research is in detecting emotions from text data, specifically tweets and other social media text. Our overall goal is to analyze two sets of tweets from Ukraine before and after Russia's invasion on February 24, 2022, and see how tweet sentiment and emotion changed. Given that Russia's invasion is of great current relevance, this analysis is important because it allows us to objectively quantify the emotional impact of such an event, and similar automated tweet extraction and analysis procedures could conceivably be done regarding other significant events for comparison.

Research Question:
How have the sentiments and emotions of tweets from Ukraine changed as a result of Russia's invasion in late Feburary 2022?

Independent Variable:
The independent variable is an event: the Russian invasion of Ukraine in February 2022.

Outcome Variable:
Our outcome variable is tweet sentiment, which can be defined and measured in a number of ways. We propose to measure sentiment in two ways: firstly, by classifying certain words as "positive" and "negative", and then defining "sentiment" to be a function of the positive word count, negative word count, and total word count; secondly, by developing a model to classify tweets according to a pre-defined outcome space of emotion labels, and then measuring the prevalence of certain emotions such as "sad" or "happy".

Text Data:
The text data will predominantly come from Twitter, although some data from other social media sites may also be used. We do not already have this data and plan to use Twitter's developer API for automated tweet extraction. After acquiring the data, one obstacle we anticipate is how to tailor our analysis procedures to the nuances of Ukrainian and Russian. We likely will need to treat and use this data differently than we would if everything was in English.

Method/Research Design:
We plan to use a dictionary approach (of Russian and Ukrainian words) to measure sentiment according to positive and negative word counts. Additionally, we plan to use a supervised learning approach to train a model to identify emotions from tweets, and have acquired a training dataset in English for this purpose. These two methods will ideally give us an objective way of measuring tweet sentiment that will enable us to assess the change caused by Russia's invasion in an impartial manner.

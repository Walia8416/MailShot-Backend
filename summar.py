from transformers import pipeline
import textwrap
import numpy as np
import pandas as pd
from pprint import pprint
ts = """ 
Hi all,

I’ve been working on developing models that take historical data and use ML models to predict the future direction (up/down) for these prices. Below is a description of what I did to get 60% accuracy in my predictions for up/down and some of the issues I ran into. Any advice to help me improve the accuracy of my predictions would be greatly appreciated!

Data
I took historical candlesticks (Open, High, Low, Close, Volume) for the EURO/USD pair from the Oanda foreign currency exchange. I then added technical indicators via the TA-Lib library. I split the technical indicators into the feature groups that TA-Lib has in their official documentation 24.

Models
I tested for both classification (just predicting future up or down movements in closing price) and regression (predicting the next price) by iterating over these models:

AdaBoostClassifier
AdaBoostRegressor
CatBoostClassifier
CatBoostRegressor
ElasticNetCV
GradientBoostingClassifier
GradientBoostingRegressor
LassoCV
LGBMClassifier
LGBMRegressor
LinearRegression
LogisticRegression
RandomForestClassifier
RandomForestRegressor
RidgeClassifierCV
RidgeCV
XGBClassifier
Testing Methodology
I split the testing into 3 phases.

Phase I - initial Test (>10K variations) - I first tested over 10K variations of the models with different feature sets and hyperparameters on the first 2 weeks of 2023 to find the most promising models.
Phase II - CrossValidation (500 variations) - I then picked the 500 highest performing model variations from Phase I and tested them on data from mid Jan 2023 till October 1, 2023.
Phase III - Final Test (10 variations) - I then picked the top 10 variations from Phase II and tested them on data from October 1, 2023, till the end of December 2023.
Issues
I’ve been able to get pretty good accuracy of over 60% in my predictions for my test data in Phase I. But when I test some of the models on the cross validation set, some of the models still return around 60% accuracy, but it’s hard to predict a priori which of the model configurations will do well.

Ideally, I’d like to see the best performing models in Phase I do well in subsequent phases. But I’m not seeing that in my results. Rather, I’m seeing some models which didn’t do as well in Phase I rise to the top in Phase II and III."""
summarizer = pipeline('summarization', model="Falconsai/text_summarization")
print(summarizer(ts, max_length=230, min_length=30, do_sample=False))
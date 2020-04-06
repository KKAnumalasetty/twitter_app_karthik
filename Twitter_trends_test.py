# -*- coding: utf-8 -*-
"""
Created on Mon Apr  6 15:37:43 2020

@author: karth
"""
from __future__ import unicode_literals
from tweepy import OAuthHandler
from tweepy import API
import os
import pandas as pd
import numpy as np
import yweather
import re

class Twitter_Authenticator():
    
    def twitter_authenticator(self):
        api_key=os.environ.get('TWITTER_API_KEY')
        api_secret_key=os.environ.get('TWITTER_API_SECRET_KEY')
        access_token=os.environ.get('TWITTER_ACCESS_TOKEN')
        access_token_secret=os.environ.get('TWITTER_ACCESS_TOKEN_SECRET')
        
        auth = OAuthHandler(api_key,api_secret_key)
        auth.set_access_token(access_token,access_token_secret)
        return auth
    
class Country_Mapping():
    
    def __init__(self):
        self.client = yweather.Client()
        self.country_code = 1
    
    def get_country_code_by_name(self,country_name):
        self.country_code = self.client.fetch_woeid(country_name)
        return self.country_code


if __name__ == "__main__":
    # OAuth process, using the keys and tokens
    auth = Twitter_Authenticator().twitter_authenticator()
    api = API(auth,wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
    country_code = Country_Mapping().get_country_code_by_name("World")
    raw_trends = api.trends_place(country_code)
    data = raw_trends[0] 
    # grab the trends
    trends = data['trends']
    # grab the name from each trend
    names = []
    tweet_volumes = []
    for trend in trends:
        if (isinstance(trend['tweet_volume'], int)):
            if (trend['tweet_volume'] >0):
                trend_name = trend['name'].encode("ascii", errors="ignore").decode()
                trend_name = re.sub("#_*","",trend_name)
                names.append(trend_name)
                tweet_volumes.append(trend['tweet_volume'])
    # put all the names together with a ' ' separating them
    trends_DF = pd.DataFrame({
            'Trend_Name':names,
            'Tweet_count':tweet_volumes
                })
    trends_DF['Trend_Name'] = trends_DF['Trend_Name'].str.strip()
    trends_DF['Trend_Name'].replace('', np.nan, inplace=True)
    trends_DF = trends_DF.dropna()
    trends_DF = trends_DF.sort_values(['Tweet_count'],ascending=False)
    trends_DF.reset_index(drop=True,inplace=True)
    trends_DF['Tweet_count']= trends_DF['Tweet_count'].astype(int).apply('{:,}'.format)

#    print(len(trends_list),type(trends_list))
#    for index,each_trend in enumerate(trends_list):
#        print(each_trend)
#        print('********************')
#    print('Trends = ',json.loads(trends_json))
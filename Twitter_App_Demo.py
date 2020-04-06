from __future__ import unicode_literals
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy import Cursor
from tweepy import API


import os
import json
import streamlit as st
import pandas as pd
import re
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

class Twitter_client():
    def __init__(self,twitter_user=None):
        self.auth = Twitter_Authenticator().twitter_authenticator()
        self.api = API(self.auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
        self.twitter_user = twitter_user
        
        
    def get_user_tweets(self, num_tweets):
        tweets =[]
        location = []
#        print('user = ',self.twitter_client)
#        print('timeline = ',self.twitter_client.user_timeline)
               
        for status in Cursor(self.api.user_timeline, screen_name=self.twitter_user, tweet_mode="extended").items(num_tweets):
            tweets.append(status.full_text)
            location.append(status.user.location)
        return tweets

class Twitter_Authenticator():
    
    def twitter_authenticator(self):
        api_key=os.environ.get('TWITTER_API_KEY')
        api_secret_key=os.environ.get('TWITTER_API_SECRET_KEY')
        access_token=os.environ.get('TWITTER_ACCESS_TOKEN')
        access_token_secret=os.environ.get('TWITTER_ACCESS_TOKEN_SECRET')
        
        auth = OAuthHandler(api_key,api_secret_key)
        auth.set_access_token(access_token,access_token_secret)
        return auth
        
class Twitter_Streamer():
    """
    Create a twitter stream class
    """
    def __init__(self):
        self.twitter_authenticator = Twitter_Authenticator()
        self.auth = Twitter_Authenticator().twitter_authenticator()
        self.runanalyzer = Tweet_Sentiment_Analyzer()

    
    
    def stream_tweets(self,fetched_tweets_file,hash_tag_list,num_tweets):
        listener = StdOutListener(fetched_tweets_file)
        auth = self.twitter_authenticator.twitter_authenticator()
        stream = Stream(auth,listener)
        
        ##filter for corona virus, donald trump etc.
        stream.filter(track=hash_tag_list)

    def stream_tweets_new(self,hash_tag_list,num_tweets):
        tweets =[]
        locations = []
        users = []
        api = API(self.auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
        for status in Cursor(api.search, q=hash_tag_list+"&lang=en").items(num_tweets):
            tweets.append(status.text)
            locations.append(status.user.location)
            users.append(status.user.screen_name)
        tweets_DF = pd.DataFrame({
                'user':users,
                'tweet':tweets
                })
#        st.table(tweets_DF)
        sentiment_tweets_DF =  self.runanalyzer.tweet_sentiment_analyzer_DF(tweets_DF)
#        st.table(sentiment_tweets_DF)
        return sentiment_tweets_DF

        


class StdOutListener(StreamListener):
    
    def __init__(self,fetched_tweets_file):
        self.fetched_tweets_file = fetched_tweets_file
    
    def on_data(self,data):
        try:
#            print(data)
            with open(self.fetched_tweets_file,'a') as tf:
                tf.write(str(json.loads(data)['text'].encode('windows-1251'), 'utf-8'))
                st.write(str(json.loads(data)['text'].encode('windows-1251'), 'utf-8'))
            
        except BaseException as e:
            print("Error on data : %s" %str(e))
            
        return True
                         
           
    def on_error(self, status):
        if status==420:
            st.write('Twitter rate limit breached and need to halt application')
            return False
        st.write(status)
        
        
        
class Tweet_Sentiment_Analyzer():
    def __init__(self):
        self.analyzer = SentimentIntensityAnalyzer()
        
        
    # Needs a dataframe with tweet column that has text in english language
    def tweet_sentiment_analyzer_DF(self,dataframe):
        tweet_DF = pd.DataFrame()
        tweet_DF = dataframe.copy()
        def clean_tweet(tweet):
            if (len(tweet) >0):
                tweet = re.sub("\n","",tweet)
                tweet = re.sub(r'^https?:\/\/.*[\r\n]*', '', tweet, flags=re.MULTILINE)
                tweet = re.sub(r'http\S+', '', tweet)
                tweet = re.sub("&amp;","",tweet)
                tweet = re.sub("@[\w]","",tweet)
                tweet = re.sub("RT @[\w]","",tweet)
            else:
                st.write('Tweet has no characters to analyze')
            return tweet
        sentiment_scores = []
        if (tweet_DF.empty == False) & (tweet_DF.shape[0]>0):
            tweet_DF['my_clean_tweet'] = tweet_DF['tweet'].apply(lambda x: clean_tweet(x))
            for index,each_row in enumerate(tweet_DF.values):
                sentiment_score = self.analyzer.polarity_scores(tweet_DF.loc[index]['my_clean_tweet'])['compound']
                sentiment_scores.append(sentiment_score)
            tweet_DF.drop(['my_clean_tweet'], axis=1,inplace=True)
            tweet_DF['Sentiment_Score'] = sentiment_scores
            tweet_DF['Sentiment'] = tweet_DF['Sentiment_Score'].apply(lambda x: 'Positive' if x >0  else 'Negative')
            tweet_DF= tweet_DF[['user','tweet','Sentiment','Sentiment_Score']]
#            tweet_DF['Sentiment_Score'] = tweet_DF['Sentiment_Score'].apply(float)
        else:
            st.write('Sentiment analysis failed due to error, please check')
        return tweet_DF


    def tweet_sentiment_analyzer_list(self,tweet_list):
        def clean_tweet(tweet):
            tweet = re.sub("\n","",tweet)
            tweet = re.sub(r'^https?:\/\/.*[\r\n]*', '', tweet, flags=re.MULTILINE)
            tweet = re.sub("@[\w]","",tweet)
            tweet = re.sub("RT @[\w]","",tweet)
            return tweet
        tweet_DF = pd.DataFrame()
        sentiment_scores = []
        for each_tweet in enumerate(tweet_list):
            my_clean_tweet = clean_tweet(each_tweet)
            sentiment_score = self.analyzer.polarity_scores(my_clean_tweet)
            sentiment_scores.append(sentiment_score)
        tweet_DF['tweet'] =  tweet_list
        tweet_DF['Sentiment_Score'] = sentiment_scores
        return tweet_DF

        
if __name__ =="__main__":
    
    st.subheader(" Twitter real time data analytics and sentiment analysis by Karthik Anumalasetty ")
    
    combo_link = "<a href='https://www.linkedin.com/in/karthikanumalasetty/' target='_blank' ><img src='https://user-images.githubusercontent.com/45413346/78455807-fc9acf80-7665-11ea-810d-fee583f9e0c9.png' width='50' height='50' /> </a><a href='https://github.com/KKAnumalasetty/twitter_app_karthik' target='_blank' ><img src='https://user-images.githubusercontent.com/45413346/78455558-b6913c00-7664-11ea-90f4-744eb2acd6c1.jpg' width='125' height='100' /> </a>"
    st.write(combo_link,unsafe_allow_html=True)
    
    
    twitter_handle = "I'll search by Person/Twitter Handle (@realdonaldtrump)"
    twitter_hashtag = "I'll search by topic/hashtag (#corona virus)"
    search_type = st.radio("Search Category", [twitter_hashtag,twitter_handle])

    num_tweets = st.slider("How many Tweets you want to analyze", 1, 10,1,1)
    
    if search_type == twitter_handle:
        twitter_user = st.text_input('Enter Twitter Handle: ','@realdonaldtrump')
        twitter_client = Twitter_client(twitter_user)
        tweets = twitter_client.get_user_tweets(num_tweets)
        st.subheader("Live Tweets")
#        st.table(tweets)
#        runanalyzer = Tweet_Sentiment_Analyzer()
#        sentiment_tweets_DF =  runanalyzer.tweet_sentiment_analyzer_list(tweets)
#        st.table(sentiment_tweets_DF)
        for tweet in tweets:
            st.text(tweet)
    elif search_type == twitter_hashtag:
         fetched_tweets_file ='tweets.json'
         tweets = Twitter_Streamer()
         hash_tag_list = st.text_input('Type hashtag and hit enter: ','#COVID-19')
         st.subheader("Live Tweets")
         tweets_DF =  tweets.stream_tweets_new(hash_tag_list,num_tweets)
         st.table(tweets_DF)
#         def highlight_sentiment(df, column):
#             is_max = pd.Series(data=False, index=df.index)
#             is_max[column] = df[column] >= 0.2
#             return ['background-color: yellow' if is_max.any() else 'background-color: red' for v in is_max]
#         
#         st.table(tweets_DF.style.apply(highlight_sentiment,column=['Sentiment_Score'],axis=0))
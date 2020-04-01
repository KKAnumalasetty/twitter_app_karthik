from __future__ import unicode_literals
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy import Cursor
from tweepy import API

import os
import streamlit as st

class Twitter_client():
    def __init__(self,twitter_user=None):
        self.auth = Twitter_Authenticator().twitter_authenticator()
        self.twitter_client = API(self.auth,wait_on_rate_limit=True)
        self.twitter_user = twitter_user
        
        
    def get_user_tweets(self, num_tweets):
        tweets =[]
        print('user = ',self.twitter_client)
        print('timeline = ',self.twitter_client.user_timeline)
        
        # api = API(self.auth)
        api = API(self.auth,wait_on_rate_limit=True)
        print('api  = ',api)
       
        for status in Cursor(api.user_timeline, screen_name='@realDonaldTrump', tweet_mode="extended").items():
            print(status.full_text)


class Twitter_Authenticator():
    
    def twitter_authenticator(self):
        api_key=os.environ.get('TWITTER_API_KEY')
        api_secret_key=os.environ.get('TWITTER_API_SECRET_KEY')
        access_token=os.environ.get('TWITTER_ACCESS_TOKEN')
        access_token_secret=os.environ.get('TWITTER_ACCESS_TOKEN_SECRET')
        
        print(api_key)
        print(api_secret_key)
        print(access_token)
        print(access_token_secret)
        

        auth = OAuthHandler(api_key,api_secret_key)
        auth.set_access_token(access_token,access_token_secret)
        return auth
        
class Twitter_Streamer():
    """
    Create a twitter stream class
    """
    def __init__(self):
        self.twitter_authenticator = Twitter_Authenticator()
    
    
    def stream_tweets(self,fetched_tweets_file,hash_tag_list):
        listener = StdOutListener(fetched_tweets_file)
        auth = self.twitter_authenticator.twitter_authenticator()
        stream = Stream(auth,listener)
        
        ##filter for corona virus, donald trump etc.
        stream.filter(track=hash_tag_list)

        


class StdOutListener(StreamListener):
    
    def __init__(self,fetched_tweets_file):
        self.fetched_tweets_file = fetched_tweets_file
    
    def on_data(self,data):
        try:
            print(data)
            with open(self.fetched_tweets_file,'a') as tf:
                tf.write(data)
            
        except BaseException as e:
            print("Error on data : %s" %str(e))
            
        return True
                         
           
    def on_error(self, status):
        if status==420:
            print('Twitter rate limit breached and need to halt application')
            return False
        print(status)
        
        
        
# class tweet_analytics():
    
        
        
if __name__ =="__main__":
    
    hash_tag_list=['corona virus']
    fetched_tweets_file = "tweets.json"
    
    # tweets = Twitter_Streamer()
    # tweets.stream_tweets(fetched_tweets_file, hash_tag_list)
    # twitter_user = 'pycon'
    twitter_client = Twitter_client()
    twitter_client.get_user_tweets(1)
    
    

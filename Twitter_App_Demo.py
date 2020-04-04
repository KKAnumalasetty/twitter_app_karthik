from __future__ import unicode_literals
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy import Cursor
from tweepy import API

import os
import json
import streamlit as st

class Twitter_client():
    def __init__(self,twitter_user=None):
        self.auth = Twitter_Authenticator().twitter_authenticator()
        self.twitter_client = API(self.auth,wait_on_rate_limit=True)
        self.twitter_user = twitter_user
        
        
    def get_user_tweets(self, num_tweets):
        tweets =[]
#        print('user = ',self.twitter_client)
#        print('timeline = ',self.twitter_client.user_timeline)
        
        # api = API(self.auth)
        api = API(self.auth,wait_on_rate_limit=True)
#        print('api  = ',api)
       
        for status in Cursor(api.user_timeline, screen_name=self.twitter_user, tweet_mode="extended").items(num_tweets):
            tweets.append(status.full_text)
        return tweets

class Twitter_Authenticator():
    
    def twitter_authenticator(self):
        api_key=os.environ.get('TWITTER_API_KEY')
        api_secret_key=os.environ.get('TWITTER_API_SECRET_KEY')
        access_token=os.environ.get('TWITTER_ACCESS_TOKEN')
        access_token_secret=os.environ.get('TWITTER_ACCESS_TOKEN_SECRET')
        
#        print(api_key)
#        print(api_secret_key)
#        print(access_token)
#        print(access_token_secret)
        

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

    
    
    def stream_tweets(self,fetched_tweets_file,hash_tag_list,num_tweets):
        listener = StdOutListener(fetched_tweets_file)
        auth = self.twitter_authenticator.twitter_authenticator()
        stream = Stream(auth,listener)
        
        ##filter for corona virus, donald trump etc.
        stream.filter(track=hash_tag_list)

    def stream_tweets_new(self,hash_tag_list,num_tweets):
        tweets =[]
        api = API(self.auth,wait_on_rate_limit=True)
        for status in Cursor(api.search, q=hash_tag_list).items(num_tweets):
            tweets.append(status.text)
        return tweets

        


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
            print('Twitter rate limit breached and need to halt application')
            return False
        print(status)
        
        
        
# class tweet_analytics():
    
        
        
if __name__ =="__main__":
    
    st.subheader(" Twitter real time data analytics and sentiment analysis by Karthik Anumalasetty ")
    
    linkedin_url = """
    <div id="block_container">

    <div id="bloc1"><a href='https://www.linkedin.com/in/karthikanumalasetty/' target='_blank' > LinkedIn </a></div>  
    <div id="bloc2"><a href='https://www.linkedin.com/in/karthikanumalasetty/' target='_blank' > LinkedIn </a></div>

</div>
    
    """
    st.write(linkedin_url,unsafe_allow_html=True)
    twitter_handle = "I'll search by Person/Twitter Handle (@realdonaldtrump)"
    twitter_hashtag = "I'll search by topic/hashtag (#corona virus)"
    search_type = st.radio("Search Category", [twitter_handle,twitter_hashtag])

#    st.write('user selected = ',search_type)
    num_tweets = st.slider("How many Tweets you want to analyze", 1, 10,1)
    
    
    if search_type == twitter_handle:
        twitter_user = st.text_input('Enter Twitter Handle: ','@realdonaldtrump')
        twitter_client = Twitter_client(twitter_user)
        tweets = twitter_client.get_user_tweets(num_tweets)
        st.subheader("Live Tweets")
        for tweet in tweets:
            st.text(tweet)
    elif search_type == twitter_hashtag:
         fetched_tweets_file ='tweets.json'
         tweets = Twitter_Streamer()
         hash_tag_list = st.text_input('Type hashtag and hit enter: ','#COVID-19')
#         btn = st.button("Run!")
#         st.write('button = ',btn)
         # Button will be inactive/False when clicked
         st.subheader("Live Tweets")
         tweets =  tweets.stream_tweets_new(hash_tag_list,num_tweets)
         for tweet in tweets:
            st.text(tweet)

    
    

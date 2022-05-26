from cProfile import label
from multiprocessing.sharedctypes import Value

from numpy import result_type
from streamlit.elements.arrow import Data
import tweepy
from requests.auth import HTTPBasicAuth
from tweepy import *
import streamlit as st
from pandas import DataFrame
import pandas as pd
import boto3
import plotly.express as px
import plotly.graph_objects as go
import base64
from PIL import Image
import io



st.set_page_config(page_title='Tweet Analysis', layout='wide', initial_sidebar_state='collapsed', page_icon='📈')

st.title(
        'Tweet Analyzer Site'
    )


st.subheader(
            'Welcome to my web app.Here you can search for tweets by specific keywords and you can narrow down your search to your specific coordinates.You will see a result of the sentiment analysis.The sentiment analysis is done via Amazon Aws Comprehend.Enter coordiantes like this : 20.30,-40.79 . Enjoy the Data!'
        )
st.subheader(
    'You can also get to download the data with great visualization!'
        )


join = '<a href="mailto:upalkundu287@gmail.com"><h3>Contact The Developer</h3></a>'
st.markdown(join, unsafe_allow_html=True)


consumer_key = 'sYidKjX3req3N075LcAK9ntD2'
consumer_secret = 's2qbUwtv2u5YBmsSk3LyB61eseiBFSHxBHrYwJN9R8LJv0iD44'
access_token = '1379246348961153027-kPuS3vGfGJf1MCSZDYDJqijEh8RnyO'
access_token_secret ='TpX7Uwbt4dDfP8h1nzsuiHAyn1Qb9MtJU73pFm7FxNpMB'

comprehend = boto3.client(service_name='comprehend', region_name='us-east-2', **{
                        "aws_access_key_id":,
                        "aws_secret_access_key":
            })




        
query = st.text_input(label='Please Enter the query for tweet')

geo = st.text_input('Enter Specific Coordinates ')

start_date = st.date_input(label="Select Starting Date", value = (dt.today()-td(days=55)) ,max_value=(dt.today()-td(days=1)))

end_date = st.date_input(label="Select End Date", max_value = dt.today())

def get_table_download_link(df):
    """Generates a link allowing the data in a given panda dataframe to be downloaded
    in:  dataframe
    out: href string
    """
    csv = df.to_csv()
    b64 = base64.b64encode(csv.encode()).decode('utf-8')  # some strings <-> bytes conversions necessary here
    href = f'<a href="data:file/csv;base64,{b64}" download="output.csv">Download csv file</a>'
    return href

def parse_sentiment_batch(data, tweets, authors):
    df = pd.DataFrame([item['SentimentScore'] for item in data['ResultList']])
    df['Sentiment'] = [item.get('Sentiment') for item in data['ResultList']]
    df['Index'] = [item.get('Index') for item in data['ResultList']]
    df['Tweet'] = tweets
    df['Author'] = authors
    df.set_index('Index', inplace = True)
    return(df)
    



auth = tweepy.OAuthHandler(consumer_key, consumer_secret)

auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth, wait_on_rate_limit=True,)


if query:
  tweet_authors = []
  tweet_texts = []
  tweet_time = []
  for tweet in api.search(q=query, geocode=geo,count=21,lang='en', since= start_date, until = end_date, result_type='popular' ):
        tweet_texts.append(tweet.text)
        tweet_authors.append(tweet.author.screen_name)
        


  tweet_df = DataFrame(columns=['Author', 'Tweet'])

  tweet_df['Author'] = tweet_authors
  tweet_df['Tweet'] = tweet_texts
  tweets = tweet_df['Tweet'].to_list()
  authors= tweet_df['Author'].to_list()
  
  text_list = list(tweet_df['Tweet'])
  if not len(tweets) == 0 :
  #Run a sentiment batch
    sentiment_batch = comprehend.batch_detect_sentiment(TextList=text_list,
                                                    LanguageCode='en')

    sent_df = parse_sentiment_batch(sentiment_batch, tweets=tweets, authors=authors)

    st.subheader('Download The data from here : ')
    st.table(sent_df)
    st.markdown(get_table_download_link(df=sent_df), unsafe_allow_html=True)
    st.title('Tweet Sentement Analysis')
    pie_chat = go.Figure(
    data=[
        go.Pie(
            labels = sent_df['Sentiment'],
            hole=.4,

        )
    ]
    )
    st.plotly_chart(pie_chat, use_container_width=True)
  else:
    st.write("No tweets found for within your filter.")   


elif query and geo:
  tweet_authors = []
  tweet_texts = []
  for tweet in api.search(q=query, geocode=geo,count=21,lang='en', result_type='popular'):
        tweet_texts.append(tweet.text)
        tweet_authors.append(tweet.author.screen_name)



  tweet_df = DataFrame(columns=['Author', 'Tweet'])

  tweet_df['Author'] = tweet_authors
  tweet_df['Tweet'] = tweet_texts
  tweets = tweet_df['Tweet'].to_list()
  authors= tweet_df['Author'].to_list()
  
  text_list = list(tweet_df['Tweet'])
  if not len(tweets) == 0 :
  #Run a sentiment batch
    sentiment_batch = comprehend.batch_detect_sentiment(TextList=text_list,
                                                    LanguageCode='en')

    sent_df = parse_sentiment_batch(sentiment_batch, tweets=tweets, authors=authors)

    st.subheader('Download The data from here : ')
    st.table(sent_df)
    st.markdown(get_table_download_link(df=sent_df), unsafe_allow_html=True)
    st.title('Tweet Sentement Analysis')
    pie_chat = go.Figure(
    data=[
        go.Pie(
            labels = sent_df['Sentiment'],
            hole=.4,

        )
    ]
    )
    st.plotly_chart(pie_chat, use_container_width=True)
else:
    st.write("No tweets found for within your filter.")                




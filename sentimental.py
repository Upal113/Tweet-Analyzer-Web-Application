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

st.set_page_config(page_title='Cognitiev - by atul.cloud', layout='wide', initial_sidebar_state='collapsed', page_icon='📈')

#Hide Streamlit footer
hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        </style>
        """
st.markdown(hide_menu_style, unsafe_allow_html=True)

st.title(
        'Cognitiev'
    )

image = Image.open('cognitiev.png').convert('RGB')
st.image(
    image,
    caption='An Atul.Cloud product',

)
st.subheader(
            "Welcome to Cognitiev one stop place for Sentiment Analysis on Tweets. You can search for any KeyWord and the app will fetch top Twenty tweets on the subject and it will also show the Sentiment Score with the result. \n" + "You can narrow down your search to a specific coordinate (e.g. 20.30,-40.79) or can leave the field blank. The sentiment analysis is performed by applying cutting edge Artificial Intelligence on top of one of the best Machine Learning platform on the planet. \n" + "And yes, you can also download the result as .csv and the with cool visualization as .png"
        )

st.subheader(
    'Please provide your valuable feedback and suggestion on SignUp'
)
logins = pd.read_csv('https://docs.google.com/spreadsheets/d/10FccPZHMook4mOp9j1S8IFWIcpp9ok_kYhCl9SOjm1E/export?format=csv', error_bad_lines=False)

join = '<a href="mailto:hi@cognitiev.com">📧SignUp</a>'
st.markdown(join, unsafe_allow_html=True)


#Twitter developer account credentials
consumer_key = 'EAYUboIGtz7l3rWJUd5yfUL4I'
consumer_secret = 'n62CXUQunmXwcp0b6gJTKNRTDpoACtkSoEcTbRzdYiGV3nyheY'
access_token = '1430054011009257474-dN6ohIfgp8dGFXD7WyUChqWGMel4ZC'
access_token_secret = 'eKshLv9wyUVmtm6f1xzzA1XsoLX6VmMtSMw9lAvOJtApB'

#aws_credentials
aws_credentials = {
                "aws_access_key_id":"AKIASY2FA6YHQSKB2MMM", # os.getenv("AWS_ACCESS_KEY")
                "aws_secret_access_key":"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"
            }

comprehend = boto3.client(service_name='comprehend', region_name='us-east-2', **aws_credentials)


username = st.text_input(label='Enter Your Username')
password = st.text_input(label='Enter your password ', type='password')
if username and password:
    if username in logins['Username'].to_list() and password==logins['Password'][logins['Username'].to_list().index(username)]:
        st.success('Login Successfull')

        query = st.text_input(label='Please Enter the query for tweet')

        geo = st.text_input('Enter Specific Coordinates ')

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
        tweet_authors = []
        tweet_texts = []



        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)

        auth.set_access_token(access_token, access_token_secret)
        api = tweepy.API(auth, wait_on_rate_limit=True,)


        if query:
            for tweet in api.search(q=query, count=20,lang='en', result_type='popular'):
                tweet_texts.append(tweet.text)
                print(tweet.text)
                tweet_authors.append(tweet.author.screen_name)
            if tweet_texts == '' or len(tweet_texts)==0:
                    for tweet in api.search(q=query, count=20,lang='en'):
                        tweet_texts.append(tweet.text)
                        tweet_authors.append(tweet.author.screen_name)



            tweet_df = DataFrame(columns=['Author', 'Tweet'])

            tweet_df['Author'] = tweet_authors
            tweet_df['Tweet'] = tweet_texts
            tweets = tweet_df['Tweet'].to_list()
            authors= tweet_df['Author'].to_list()

            text_list = list(tweet_df.Tweet)

            #Run a sentiment batch
            sentiment_batch = comprehend.batch_detect_sentiment(TextList=text_list,
                                                                LanguageCode='en')

            sent_df = parse_sentiment_batch(sentiment_batch, tweets=tweets, authors=authors)
            st.subheader('Download The data from here : ')

            st.markdown(get_table_download_link(df=sent_df), unsafe_allow_html=True)

            st.table(sent_df)
            st.title('Tweet Sentement Analysis')
            pie_chat = go.Figure(
                data=[
                    go.Pie(
                        labels = sent_df['Sentiment'],
                        hole=.4,

                    )
                ]
            )
            st.plotly_chart(pie_chat)


        elif query and geo:
            for tweet in api.search(q=query, geocode=geo,count=20,lang='en', result_type='popular'):
                tweet_texts.append(tweet.text)
                tweet_authors.append(tweet.author.screen_name)
            if tweet_texts == '' or len(tweet_texts)==0:
                    for tweet in api.search(q=query, count=20,lang='en'):
                        tweet_texts.append(tweet.text)
                        tweet_authors.append(tweet.author.screen_name)




            tweet_df = DataFrame(columns=['Author', 'Tweet'])

            tweet_df['Author'] = tweet_authors
            tweet_df['Tweet'] = tweet_texts
            tweets = tweet_df['Tweet'].to_list()
            authors= tweet_df['Author'].to_list()

            text_list = list(tweet_df.Tweet)

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
            st.error('Wrong Credentials')
            st.empty()
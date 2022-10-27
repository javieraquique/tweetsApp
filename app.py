from tkinter import Y
import streamlit as st
import pandas as pd
import numpy as np
import os
import json
from dotenv import load_dotenv
import requests
import plotly.express as px


def bearer_oauth(r):
    """
    Method required by bearer token authentication.
    """

    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2RecentSearchPython"
    return r

def connect_to_endpoint(url, params):
    response = requests.get(url, auth=bearer_oauth, params=params)
    print(response.status_code)
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
    return response.json()

load_dotenv()
bearer_token = os.getenv("BEARER_TOKEN")

search_url = "https://api.twitter.com/2/tweets/search/recent"

query_params = {
    'query': 'lang=en',
    'place.fields': 'contained_within,country,country_code,full_name,geo,id,name,place_type',
    'tweet.fields': 'author_id,created_at,geo,id,lang,possibly_sensitive,source,text,withheld',
    'user.fields': 'id,location,name,protected,username,verified,withheld',
    'max_results': 100}

def main():

    st.title('The lastest 100 tweets in English')

    # DATE_COLUMN = 'date/time'
    # DATA_URL = ('https://s3-us-west-2.amazonaws.com/'
    #             'streamlit-demo-data/uber-raw-data-sep14.csv.gz')

    @st.cache
    def load_data():
        json_response = connect_to_endpoint(search_url, query_params)
        data = pd.DataFrame.from_dict(json_response['data'])
        # lowercase = lambda x: str(x).lower()
        # data.rename(lowercase, axis='columns', inplace=True)
        # data[DATE_COLUMN] = pd.to_datetime(data[DATE_COLUMN])
        return data

    data_load_state = st.text('Loading data...')
    data = load_data()
    data_load_state.text("Data loaded and ready!")


    st.subheader('Number of twitts by hour')
    st.bar_chart(data['lang'])
    st.dataframe(data)


if __name__ == "__main__":
    main()

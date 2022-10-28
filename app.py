import streamlit as st
import pandas as pd
import numpy as np
import os
import json
import requests
import datetime as dt


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

# load_dotenv()
# bearer_token = os.getenv("BEARER_TOKEN")

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

    @st.cache
    def load_data():
        json_response = connect_to_endpoint(search_url, query_params)
        data = pd.DataFrame.from_dict(json_response['data'])
        return data

    data_load_state = st.text('Loading data...')
    data = load_data()
    data_load_state.text("Data loaded and ready!")


    st.subheader('Distribution by language')

    values = list(data['lang'].value_counts())
    columns = data['lang'].value_counts().index.to_list()
    
    chart_data = pd.DataFrame(values, columns)
    chart_data = chart_data.rename(columns={0: "Number of twitts"})

    st.bar_chart(chart_data)

    st.subheader('Timeline')

    data['time'] = pd.to_datetime(data['created_at'])

    values = list(data['time'].value_counts())
    columns = data['time'].value_counts().index.to_list()
    
    chart_data = pd.DataFrame(values, columns)
    chart_data = chart_data.rename(columns={0: "Number of twitts"})

    st.line_chart(chart_data)

    st.dataframe(data)

    


if __name__ == "__main__":
    main()

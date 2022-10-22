import pandas as pd
import requests
import numpy as np
import streamlit as st

@st.cache
def load_data(query='covid'):
    url = "https://twitter154.p.rapidapi.com/search/search"

    querystring = {"query":f"#{query}","section":"top","start_date":"2022-01-01"}

    headers = {
        "X-RapidAPI-Key": "c6a5a891ecmsh03d9ec66402dd34p18a3c6jsnbe65087e49e4",
        "X-RapidAPI-Host": "twitter154.p.rapidapi.com"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)

    res_dict = response.json()
    res_dict = res_dict['results']
    
    df = pd.DataFrame.from_dict(res_dict)
    return df

st.title('Tweets of ICBMS')
# Create a text element and let the reader know the data is loading.
data_load_state = st.text('Loading data...')
# Load 10,000 rows of data into the dataframe.
data = load_data()
# Notify the reader that the data was successfully loaded.
data_load_state.text("Done! (using st.cache)")

st.subheader('Number of pickups by hour')

hist_values = np.histogram(
    df['creation_date'].dt.hour, bins=24, range=(0,24))[0]


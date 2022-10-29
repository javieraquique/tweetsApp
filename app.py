import streamlit as st
import spacy
import pandas as pd
import numpy as np
import os
import requests
import datetime as dt
import plotly.express as px
import plotly.graph_objects as go

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

st.write(
	"Has environment variables been set:",
	os.environ["BEARER_TOKEN"] == st.secrets["BEARER_TOKEN"])

bearer_token = os.environ["BEARER_TOKEN"]

search_url = "https://api.twitter.com/2/tweets/search/recent"

query_params = {
    'query': 'lang=en',
    'place.fields': 'contained_within,country,country_code,full_name,geo,id,name,place_type',
    'tweet.fields': 'author_id,created_at,geo,id,lang,possibly_sensitive,source,text,withheld',
    'user.fields': 'id,location,name,protected,username,verified,withheld',
    'max_results': 100}

def main():
    
    # Se escribe el título
    st.title('The lastest 100 tweets in English')

    # Se crea una función para cargar los datos con un decorador de cache
    @st.cache(allow_output_mutation=True)
    def load_data():
        json_response = connect_to_endpoint(search_url, query_params)
        data = pd.DataFrame.from_dict(json_response['data'])
        return data

    # Se crea un texto para mostrar mientras se ejecuta la función de carga de datos
    data_load_state = st.text('Loading data...')

    # Se llama a la función de carga de datos
    data = load_data()

    #Se muestra el mensaje indicando que se han cargados los datos correctamente
    data_load_state.text("Data loaded and ready!")

    # Se escribe subtítulo para visualización de distribución por idioma
    st.subheader('Distribution by language')

    # Se almacenan los datos de idioma de cada tiwtt y las vece que se repiten en dos listas
    values = list(data['lang'].value_counts())
    columns = data['lang'].value_counts().index.to_list()
    
    # Se almacenan ambas listas en un Data Frame de nombe chart_data
    chart_data = pd.DataFrame(values, columns)

    # Se cambia el nombre de la columna
    chart_data = chart_data.rename(columns={0: "Number of twitts"})
    
    # Se genera el gráfico de barras para la distribución por idioma
    st.bar_chart(chart_data)

    # Se genera título de línea de tiempo
    st.subheader('Timeline')

    # Se genera la columna time en el Data Frame data transformando la variable created_at en datetime
    data['time'] = pd.to_datetime(data['created_at'])

    # Se almacenan los datos de la hora de cada tiwtt y las veces que se repiten en dos listas
    values = list(data['time'].value_counts())
    columns = data['time'].value_counts().index.to_list()
    
    # Se almacenan ambas listas en un Data Frame de nombe chart_data
    chart_data = pd.DataFrame(values, columns)
    
    # Se cambia el nombre de la columna
    chart_data = chart_data.rename(columns={0: "Number of twitts"})
    
    # Se genera el gráfico de serie temporal
    st.line_chart(chart_data)

    # Lista de palabras a exlcuir
    # nlp = English
    nlp = spacy.load("en_core_web_sm")
    excluded_tags = {"SYM", "PUNCT", "PART", "AUX", "CCONJ", "PRON", "NOUN", "ADV", "ADP", "PROPN"}
    banned = ["the", "a"]

    #Almcenamos las palabras en una lista, excepcionando las palabras a excluir
    single_text = []
    list_of_text = data['text'].str.split()

    for text in list_of_text:
        doc = nlp(' '.join(text))
        for token in doc:
            if (token.pos_ not in excluded_tags) and (token.text.lower() not in banned)  :
                single_text.append(token.text.lower())
    
    # Almacenamos el par de palabra y valor repetido ordenado en un diccionario
    top_rated = pd.DataFrame(pd.Series(single_text).value_counts())
    top_rated = top_rated.reset_index()
    top_rated = top_rated.sort_values(by=[0], ascending=True)
    
    # print(top_rated)
    #Creando gráfico de barras con las palabras más repetidas
    fig = go.Figure(go.Bar(

        x=top_rated[0], 
        y=top_rated['index'], 
        orientation='h'))

    st.plotly_chart(fig, use_container_width=True)


if __name__ == "__main__":
    main()

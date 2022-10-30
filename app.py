import streamlit as st
import spacy
import pandas as pd
import numpy as np
import os
import requests
import datetime as dt
import plotly.express as px
import plotly.graph_objects as go
import en_core_web_sm

# Definir tema
st.set_page_config(
page_title="Latest 100 twitts",
page_icon="🤖",
layout="wide")

# Extraer el token de acceso a la API de twitter
# os.environ["BEARER_TOKEN"] == st.secrets["BEARER_TOKEN"]

# Asgina el secreto a la variable secreto
bearer_token = os.environ["BEARER_TOKEN"]

# Asigna la URL de la API de twitter a una variable
search_url = "https://api.twitter.com/2/tweets/search/recent"

# Establece los parámetros de búsqueda en la API y campos a retornar
query_params = {
    'query': 'lang=en',
    'place.fields': 'contained_within,country,country_code,full_name,geo,id,name,place_type',
    'tweet.fields': 'author_id,created_at,geo,id,lang,possibly_sensitive,source,text,withheld',
    'user.fields': 'id,location,name,protected,username,verified,withheld',
    'max_results': 100}

def bearer_oauth(r):
    """
    Method required by bearer token authentication.
    """

    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2RecentSearchPython"
    return r

def connect_to_endpoint(url, params):
    '''
    Esta función se conecta al punto de acceso de la API
    a través de los argumentos url y params establecidos al
    inicio del programa
    '''
    response = requests.get(url, auth=bearer_oauth, params=params)
    print(response.status_code)
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
    return response.json()

def main():

    '''
    Función principal de la aplicación
    '''

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

    # Primera planta
    with st.container():
        col1, col2 = st.columns([0.4, 1])
        
        with col1:
            st.image("tweetsapp-low-resolution-logo-color-on-transparent-background.png")

        with col2:
            title_alignment = "<h1 style='text-align: right;'>The lastest 100 tweets</h1>"
            st.markdown(title_alignment, unsafe_allow_html=True)
            # st.title('The lastest 100 tweets')
            
    st.header("This app pulls the lastest 100 twitts form the Twitter's Api")

    # Segunda planta
    col1, col2 = st.columns([0.3, 0.7])

    with col1:
        st.subheader('Distribution by language')
        st.write('''
            This is the distribution of tweets by their language.
            ZXX means the language is unknown
            ''')

    with col2:
        # Se escribe subtítulo para visualización de distribución por idioma
        # st.subheader('Distribution by language')
            # Se almacenan los datos de idioma de cada tiwtt y las vece que se repiten en dos listas
        values = list(data['lang'].value_counts())
        columns = data['lang'].value_counts().index.to_list()
        
        # Se almacenan ambas listas en un Data Frame de nombe chart_data
        chart_data = pd.DataFrame(values, columns)

        # Se cambia el nombre de la columna
        chart_data = chart_data.rename(columns={0: "Number of twitts"})
        
        # Se genera el gráfico de barras para la distribución por idioma
        st.bar_chart(chart_data)

    # Tercera planta
    col1, col2 = st.columns([0.7, 0.3])

    with col2:
        st.subheader('Description')
        st.write('''
            This is the distribution of tweets by their source.
            E.G. a phone, a computer or which app.
            ''')

    with col1:
        # Se escribe subtítulo para visualización de distribución por fuente
        st.subheader('Distribution by source')
            # Se almacenan los datos de idioma de cada tiwtt y las vece que se repiten en dos listas

        values = list(data['source'].value_counts())
        columns = data['source'].value_counts().index.to_list()
        
        # Se almacenan ambas listas en un Data Frame de nombe chart_data
        chart_data = pd.DataFrame(values, columns)

        # Se cambia el nombre de la columna
        chart_data = chart_data.rename(columns={0: "Number of twitts"})
        
        # Se genera el gráfico de barras para la distribución por fuente
        fig = px.pie(data, names='source')
        st.plotly_chart(fig)

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
    nlp = en_core_web_sm.load()
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
    
    #Creando gráfico de barras con las palabras más repetidas
    fig = go.Figure(go.Bar(

        x=top_rated[0], 
        y=top_rated['index'], 
        orientation='h'))

    st.plotly_chart(fig, use_container_width=True)


if __name__ == "__main__":
    main()

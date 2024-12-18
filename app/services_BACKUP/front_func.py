import streamlit as st
import pandas as pd
from statsbombpy import sb
import requests


def add_styling():
    st.html("""
        <style>
            /* convert radio to list of buttons */
            div[role="radiogroup"] {
                flex-direction:row;
            }
            input[type="radio"] + div {
                background: #C0C0C0 !important;
                color: #FFF;
                border-radius: 38px !important;
                padding: 8px 18px !important;
            }
            input[type="radio"][tabindex="0"] + div {
                background: #FF4B4B !important;
                color: #FFFFFF !important;
            }
            input[type="radio"][tabindex="0"] + div p {
                color: #FFFFFF !important;
            }
            div[role="radiogroup"] label > div:first-child {
                display: none !important;
            }
            div[role="radiogroup"] label {
                margin-right: 0px !important;
            }
            div[role="radiogroup"] {
                gap: 12px;
            }
        </style>
    """)


def getCompetitions():
    with st.spinner("Carregando..."):
        response = requests.get("http://localhost:8000/competitions")
        response.raise_for_status()
    
    if response.status_code == 200:
        df = pd.DataFrame(response.json())
        return df
    
    else:
        st.error("Erro ao acessar a API /competitions: {}".format(response.status_code))


def filterCompetion(df_comp):

    #Crio a lista de campeonatos
    list_comp = df_comp['competition_name'].drop_duplicates().tolist()
    list_comp.insert(0, 'Selecione')

    #Crio o Seletor
    competition = st.sidebar.selectbox('Filtrar Campeonato', list_comp, key='1')

    df_comp_filt = df_comp.loc[df_comp['competition_name'] == competition]

    return df_comp_filt, competition


def filterYear(df_comp_filt):

    #lista dos anos
    list_year = df_comp_filt['season_name'].drop_duplicates().tolist()
    list_year.insert(0, 'Selecione')
    #seletor de ano
    year = st.sidebar.selectbox('Filtrar Temporada', list_year)

    df_comp_filt_year = df_comp_filt.loc[df_comp_filt['season_name'] == year]
    
    return df_comp_filt_year, year


def getMatches(df_comp_filt_year):

    #Obtem o Dataset Partidas passando como parâmetro o id do campeonato e o id da temporada  
    competition_id = df_comp_filt_year['competition_id'].values[0]  
    season_id = df_comp_filt_year['season_id'].values[0]

    with st.spinner("Carregando..."):
        response = requests.get(f"http://localhost:8000/matches/{competition_id}/{season_id}")
        response.raise_for_status()
    
    if response.status_code == 200:
        df_matches = pd.DataFrame(response.json())
        return df_matches
    
    else:
        st.error("Erro ao acessar a API /matches: {}".format(response.status_code))


def filterMatch(df_matches):
    add_styling()
    #lista das partidas
    df_matches['partida'] = df_matches['home_team'] + ' x ' + df_matches['away_team']
    list_matches = df_matches['partida'].drop_duplicates().tolist()
    list_matches.insert(0, 'Selecione')

    #seletor de partidas
    match = st.sidebar.selectbox('Filtrar Partida', list_matches)
    df_matches_filt = df_matches.loc[df_matches['partida'] == match]
    
    return df_matches_filt, match


def getMatchAnalysis(df_matches_filt, llm_tone):

    with st.spinner("Aguarde alguns instantes, a análise está sendo processada..."):
        match_id=df_matches_filt['match_id'].values[0]
        response = requests.get(f"http://localhost:8000/matchanalysis/{match_id}/{llm_tone}")
        response.raise_for_status()
    
    if response.status_code == 200:
        return response.json()
    
    else:
        st.error("Erro ao acessar a API /matchanalysis: {}".format(response.status_code))


def select_llm_tone():
    add_styling()
    llm_tone = st.radio("Selecione", ["Formal", "Empolgado", "Humorístico", "Técnico"], label_visibility="collapsed")

    return llm_tone
        

    
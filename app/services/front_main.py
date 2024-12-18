import streamlit as st
from front_func import *
from back_main import *
from back_agents import *


st.set_page_config(layout="wide")

#-----------------INICIANDO VARIÁVEIS DE SESSÃO-------------------
if 'competition' not in st.session_state:
    st.session_state.competition = ''
    competition = 'Select'

if 'year' not in st.session_state:
    st.session_state.year = ''
    year = 'Select'

if 'match_temp' not in st.session_state:
    st.session_state.match_temp = ''
    match = 'Select'

if 'match' not in st.session_state:
    st.session_state.match = ''
    match = 'Select'


#-----------------SELETOR DE PÁGINAS-------------------
st.sidebar.header('Navegação')
page = st.sidebar.selectbox("Selecione a Página",["Assistente Virtual", "Estatísticas"], label_visibility="hidden")



#-----------------BARRA DE FILTROS LATERAL-------------------

st.sidebar.header('Filters')

if 'df_comp' not in st.session_state:
    df_comp = getCompetitions()
    st.session_state.df_comp = df_comp

#Só mostra o filtro de campeonato depois de carregar a primeira base
if 'df_comp' in st.session_state:
    st.session_state.df_comp_filt, competition = filterCompetion(st.session_state.df_comp)

#Só mostra o filtro de Ano depois que o Campeonato é selecionado
if competition != 'Select':
    st.session_state.df_comp_filt_year, year = filterYear(st.session_state.df_comp_filt)

#Só carrega o dataset MATCHES se os filtros de Campeonato e Ano estiverem feitos
if competition != 'Select' and year != 'Select':

    #Só prossegue com a execução se os valores forem diferentes dos das variáveis de sessão
    if competition != st.session_state.competition or year != st.session_state.year:
        df_matches = getMatches(st.session_state.df_comp_filt_year)
    
        st.session_state.match_id = df_matches['match_id'][0]
        st.session_state.home_team = df_matches['home_team'][0]
        st.session_state.away_team = df_matches['away_team'][0]
        
        st.session_state.competition = competition
        st.session_state.year = year
        st.session_state.df_matches = df_matches

#Só mostra o filtro de Partida depois que o Ano e Campeonato são Selecionados    
if competition != 'Select' and year != 'Select':
    st.session_state.df_matches_filt, st.session_state.match_temp = filterMatch(st.session_state.df_matches)
    st.session_state.df_events = getEvents(st.session_state.match_id)


#-----------------TROCA DE PÁGINAS------------------
if page == "Assistente Virtual":
    import front_pageChat as front_pageChat
    front_pageChat.exibir()
elif page == "Estatísticas":
    import front_pageStats as front_pageStats
    front_pageStats.exibir()
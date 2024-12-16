import streamlit as st
from front_func import *
from back_main import *
from back_agents import *


st.set_page_config(layout="wide")

############# PRECISO REVER AS VARIÁVEIS DE SESSÃO DEPOIS ###############

#Iniciando as variáveis
if 'competition' not in st.session_state:
    st.session_state.competition = ''
    competition = 'Selecione'

if 'year' not in st.session_state:
    st.session_state.year = ''
    year = 'Selecione'

if 'match' not in st.session_state:
    st.session_state.match = ''
    match = 'Selecione'

if 'llm_tone' not in st.session_state:
    st.session_state.llm_tone = ''
    llm_tone = 'Selecione'


st.sidebar.header('Navegação')
page = st.sidebar.selectbox("",["Análise de Partidas", "Análise de Jogadores"])

st.sidebar.header('Filtros')

if 'df_comp' not in st.session_state:
    df_comp = getCompetitions()
    st.session_state.df_comp = df_comp

#Só mostra o filtro de campeonato depois de carregar a primeira base
if 'df_comp' in st.session_state:
    st.session_state.df_comp_filt, competition = filterCompetion(st.session_state.df_comp)

#Só mostra o filtro de Ano depois que o Campeonato é selecionado
if competition != 'Selecione':
    st.session_state.df_comp_filt_year, year = filterYear(st.session_state.df_comp_filt)

#Só carrega o dataset MATCHES se os filtros de Campeonato e Ano estiverem feitos
if competition != 'Selecione' and year != 'Selecione':

    #Só prossegue com a execução se os valores forem diferentes dos das variáveis de sessão
    if competition != st.session_state.competition or year != st.session_state.year:
        st.session_state.df_matches = getMatches(st.session_state.df_comp_filt_year)
        st.session_state.competition = competition
        st.session_state.year = year

############## AQUI COMEÇA O CONTEÚDO DO BODY DA PÁGINA
############# RADIO BUTTON


st.write(f"### 1° Passo - Filtre o Campeonato e Temporada na Barra Lateral")
    
if competition != 'Selecione' and year != 'Selecione':
    st.write(f"**Selecionado:** {competition} - {year}\n")
    st.write(f"### 2° Passo - Agora Escolha uma Partida")
    df_matches_filt, match = filterMatch(st.session_state.df_matches)



#Só exibe a seleção de TOM e carrega o dataset MATCHES se todos os filtros estiverem feitos.
if competition != 'Selecione' and year != 'Selecione' and match != 'Selecione':
    st.write(f"**Selecionado:** {match}")
    st.write(f"### 3° Passo - Selecione um Tom Narrativo para a Inteligência Artificial")
    llm_tone = select_llm_tone()

    st.write("\n")
    if st.button("GERAR ANÁLISE", type="primary"):
        response = getMatchAnalysis(df_matches_filt, llm_tone)

        st.session_state.match = match
        
        with st.container(border=True):
            st.write(response)



# DEIXEI COMENTADA A PARTE QUE INICIALIZA AS PÁGINAS, POR ENQUANTO O CÓDIGO ESTÁ TODO CONCENTRADO NO MESMO ARQUIVO
# if page == "Análise de Partidas":
#     import Partidas
#     Partidas.exibir()
# elif page == "Análise de Jogadores":
#     import Jogadores
#     Jogadores.exibir()



import streamlit as st
from front_func import *
from back_main import *
from back_agents import *


st.set_page_config(layout="wide")

############# PRECISO REVER AS VARIÁVEIS DE SESSÃO DEPOIS ###############

#Iniciando as variáveis
if 'competition' not in st.session_state:
    st.session_state.competition = ''
    competition = 'Select'

if 'year' not in st.session_state:
    st.session_state.year = ''
    year = 'Select'

if 'match' not in st.session_state:
    st.session_state.match = ''
    match = 'Select'

if 'llm_tone' not in st.session_state:
    st.session_state.llm_tone = ''
    llm_tone = 'Select'

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hi! I can help you retrieving informations about the selected match. Please ask a question to get started."}]


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
        st.session_state.df_matches = getMatches(st.session_state.df_comp_filt_year)
        st.session_state.competition = competition
        st.session_state.year = year

############## AQUI COMEÇA O CONTEÚDO DO BODY DA PÁGINA
############# RADIO BUTTON


st.write(f"### 1st Step - Filter the Championship and Season in the Sidebar")
    
if competition != 'Select' and year != 'Select':
    st.write(f"**Selected:** {competition} - {year}\n")
    st.write(f"### 2nd Step - Now Choose a Match")
    df_matches_filt, match = filterMatch(st.session_state.df_matches)


'''
#Só exibe a seleção de TOM e carrega o dataset MATCHES se todos os filtros estiverem feitos.
if competition != 'Select' and year != 'Select' and match != 'Select':
    st.write(f"**Selected:** {match}")
    st.write(f"### 3rd Step - Select a Narrative Tone for the Artificial Intelligence")
    llm_tone = select_llm_tone()


    st.session_state.match = match
    st.session_state.match = llm_tone


    # -----------------INICIALIZAÇÃO--------------------

    # Exibe as mensagens armazenadas no histórico  (Se não tiver essa parte toda vez que é digitada uma nova mensagem o chat é limpo)
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


    # -----------------USUÁRIO--------------------
    # Cria a caixa de input e exibe um placeholder. Se foi digitado algo na caixa, atribui o valor a variável user_input
    if user_input := st.chat_input("Type here"):

        # Exibe no chat a mensagem que o usuário havia inputado
        with st.chat_message("user"): 
            st.markdown(user_input)

        # Adiciona a mensagem do usuário na variável de ambiente (histórico de mensagens)
        st.session_state.messages.append({"role": "user", "content": user_input})


        #-----------------CHAMADA AO LLM-------------------
        # Adicionar spinner enquanto está aguardando a resposta do LLM

        with st.chat_message("assistant"): 
            with st.spinner("Wait a second..."):    
                
                response = getMatchAnalysis(df_matches_filt, llm_tone, user_input)

                st.write(response)

                st.session_state.messages.append({"role": "assistant", "content": response})
'''      




# DEIXEI COMENTADA A PARTE QUE INICIALIZA AS PÁGINAS, POR ENQUANTO O CÓDIGO ESTÁ TODO CONCENTRADO NO MESMO ARQUIVO
# if page == "Análise de Partidas":
#     import Partidas
#     Partidas.exibir()
# elif page == "Análise de Jogadores":
#     import Jogadores
#     Jogadores.exibir()



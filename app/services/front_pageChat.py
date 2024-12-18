import streamlit as st
from front_func import *


#-----------------INICIANDO VARIÁVEIS DE SESSÃO-------------------
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hi! I can help you retrieving informations about the selected match. Why don't you try one of the following ones?\n - What is the lineup for the match? \n - Show me the match summary\n - Show me the match stats for player X\n - Show me the match stats for team Y \n - Compare match stats for player X and player Y \n - What player had the most shots on goal?"}]

if 'llm_tone' not in st.session_state:
    st.session_state.llm_tone = ''
    llm_tone = 'Select'


def exibir():
    st.write(f"### 1st Step - Filter the Championship and Season in the Sidebar")

    if st.session_state.competition != '' and st.session_state.competition != 'Select' and st.session_state.year != '' and st.session_state.year != 'Select':
        st.write(f"**Selected:** {st.session_state.competition} - {st.session_state.year}\n")
        st.write(f"### 2nd Step - Now Choose a Match")

        if  st.session_state.match_temp != '' and st.session_state.match_temp != 'Select':
            st.write(f"**Selected:** {st.session_state.match_temp}")
            st.write(f"### 3rd Step - Select a Narrative Tone for the Artificial Intelligence")
            llm_tone = select_llm_tone()


            st.session_state.match = st.session_state.match_temp
            st.session_state.llm_tone = llm_tone


            # -----------------IMPRIME TODAS AS MENSAGENS PRESENTES NO SESSION STATE--------------------
            # Exibe as mensagens armazenadas no histórico  (Se não tiver essa parte toda vez que é digitada uma nova mensagem o chat é limpo)
            for messages in st.session_state.messages:
                with st.chat_message(messages["role"]):
                    st.markdown(messages["content"])


            # -----------------CAIXA DE INPUT DO USUÁRIO--------------------
            # Cria a caixa de input e exibe um placeholder. Se foi digitado algo na caixa, atribui o valor a variável user_input
            if user_input := st.chat_input("Type here"):

                # Exibe no chat a mensagem que o usuário havia inputado
                with st.chat_message("user"): 
                    st.markdown(user_input)

                # Adiciona a mensagem do usuário na variável de ambiente (histórico de mensagens)
                st.session_state.messages.append({"role": "user", "content": user_input})


                #-----------------CHAMADA AO LLM-------------------

                with st.chat_message("assistant"): 
                    with st.spinner("Wait a second..."):    

                        response = getMatchAnalysis(
                            match_id = st.session_state.match_id,
                            home_team = st.session_state.home_team,
                            away_team = st.session_state.away_team,
                            llm_tone = llm_tone, 
                            user_input = user_input)
                        
                        st.write(response)

                        #Adiciona a respota do LLM à variável de ambiente (histórico de mensagens)
                        st.session_state.messages.append({"role": "assistant", "content": response})



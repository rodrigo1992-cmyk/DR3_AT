import streamlit as st
import pandas as pd
from front_func import *

def exibir():
    if 'df_events' in st.session_state:
        df_events = st.session_state.df_events

    st.write(f"### 1st Step - Filter the Championship and Season in the Sidebar")

    if st.session_state.competition != '' and st.session_state.competition != 'Select' and st.session_state.year != '' and st.session_state.year != 'Select':
        st.write(f"**Selected:** {st.session_state.competition} - {st.session_state.year}\n")
        st.write(f"### 2nd Step - Now Choose a Match")

        if  st.session_state.match_temp != '' and st.session_state.match_temp != 'Select':
            st.write(f"**Selected:** {st.session_state.match_temp}")

            st.write("## Dashboards")
            col_a, col_b = st.columns(2)

            with col_a:
                st.pyplot(dash_events_per_period(st.session_state.df_events))

            with col_b:
                st.pyplot(dash_events_per_team(st.session_state.df_events))

            st.write("##  Players Comparison")

            with st.form(key='my_form'):
                col_a, col_b = st.columns(2)

                with col_a:
                    jogadorA = st.selectbox("Player A", df_events['player'].unique())

                with col_b:
                    jogadorB = st.selectbox("Player B", df_events['player'].unique())
                
                submit_button = st.form_submit_button(label='Confirm')

                
                if submit_button:
                    dash_player_comparison(df_events, jogadorA, jogadorB)

            st.write("## Dataset Visualization")
            st.dataframe(show_df_events(df_events))
                




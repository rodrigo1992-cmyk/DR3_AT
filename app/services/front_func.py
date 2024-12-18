import streamlit as st
import pandas as pd
from statsbombpy import sb
import requests
import matplotlib.pyplot as plt
import seaborn as sns

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
    with st.spinner("Loading..."):
        response = requests.get("http://localhost:8000/competitions")
        response.raise_for_status()
    
    if response.status_code == 200:
        df = pd.DataFrame(response.json())
        return df
    
    else:
        st.error("Error retrieving data from API competitions: {}".format(response.status_code))


def filterCompetion(df_comp):

    #Crio a lista de campeonatos
    list_comp = df_comp['competition_name'].drop_duplicates().tolist()
    list_comp.insert(0, 'Select')

    #Crio o Seletor
    competition = st.sidebar.selectbox('Competition', list_comp, key='1')

    df_comp_filt = df_comp.loc[df_comp['competition_name'] == competition]

    return df_comp_filt, competition


def filterYear(df_comp_filt):

    #lista dos anos
    list_year = df_comp_filt['season_name'].drop_duplicates().tolist()
    list_year.insert(0, 'Select')
    #seletor de ano
    year = st.sidebar.selectbox('Season', list_year)

    df_comp_filt_year = df_comp_filt.loc[df_comp_filt['season_name'] == year]
    
    return df_comp_filt_year, year


def getMatches(df_comp_filt_year):

    #Obtem o Dataset Partidas passando como parâmetro o id do campeonato e o id da temporada  
    competition_id = df_comp_filt_year['competition_id'].values[0]  
    season_id = df_comp_filt_year['season_id'].values[0]

    with st.spinner("Wait..."):
        response = requests.get(f"http://localhost:8000/matches/{competition_id}/{season_id}")
        response.raise_for_status()

    if response.status_code == 200:
        df_matches = pd.DataFrame(response.json())

        return df_matches
    
    else:
        st.error("Error retrieving data from API Matches: {}".format(response.status_code))


def filterMatch(df_matches):
    add_styling()
    #lista das partidas
    df_matches['partida'] = df_matches['home_team'] + ' x ' + df_matches['away_team']
    list_matches = df_matches['partida'].drop_duplicates().tolist()
    list_matches.insert(0, 'Select')

    #seletor de partidas
    match = st.sidebar.selectbox('Match', list_matches)
    df_matches_filt = df_matches.loc[df_matches['partida'] == match]
    
    return df_matches_filt, match


def getMatchAnalysis(match_id: int, home_team: str, away_team: str, llm_tone: str, user_input: str):

    url = f"http://localhost:8000/matchanalysis"
    params = {
        "match_id": match_id,
        "home_team": home_team,
        "away_team": away_team,
        "llm_tone": llm_tone,
        "user_input": user_input
        }
    
    response = requests.get(url, params=params)
    response.raise_for_status()
    
    if response.status_code == 200:
        return response.json()
    
    else:
        st.error("Error retrieving data from API matchanalysis: {}".format(response.status_code))


def select_llm_tone():
    add_styling()
    llm_tone = st.radio("Select", ["Formal", "Excited", "Humorous", "Technical"], label_visibility="collapsed")

    return llm_tone
        

def getEvents(match_id):

    with st.spinner("Wait..."):
        response = requests.get(f"http://localhost:8000/events/{match_id}")
        response.raise_for_status()

    if response.status_code == 200:
        df_events = pd.DataFrame(response.json())

        return df_events
    
    else:
        st.error("Error retrieving data from API Events: {}".format(response.status_code))



def dash_events_per_period(df):
    options = df['period'].unique()
    options = ['whole match'] + options.tolist()
    period = st.selectbox('Select the Period', options)

    if period != 'whole match':
        df = df[df['period'] == period]

    df = df.groupby(['outcome']).size().reset_index(name='count')
    df = df[df['outcome'].notnull()].sort_values('count', ascending=False)

    sns.set_theme(style="whitegrid")
    fig, ax = plt.subplots(figsize=(8,4))
    sns.barplot(x="outcome", y="count", data=df, ax=ax)
    ax.set_xticks(range(len(df['outcome'])))
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
    ax.set_title('Match Events per Period')
    ax.set_ylabel('Quantity')
    ax.set_xlabel('Events')

    for p in ax.patches:
        ax.annotate(f'{p.get_height()}', (p.get_x() + p.get_width() / 2., p.get_height()), ha = 'center', va = 'center', xytext = (0, 10), textcoords = 'offset points')

    return fig

def dash_events_per_team(df):
    options = df['team'].unique()
    options = ['Both teams'] + options.tolist()
    team = st.selectbox('Select the Team', options)

    if team != 'Both teams':
        df = df[df['team'] == team]

    df = df.groupby(['outcome']).size().reset_index(name='count')
    df = df[df['outcome'].notnull()].sort_values('count', ascending=False)

    sns.set_theme(style="whitegrid")
    fig, ax = plt.subplots(figsize=(8,4))
    sns.barplot(x="outcome", y="count", data=df, ax=ax)
    ax.set_xticks(range(len(df['outcome'])))
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
    ax.set_title('Match Events per Team')
    ax.set_ylabel('Quantity')
    ax.set_xlabel('Events')

    for p in ax.patches:
        ax.annotate(f'{p.get_height()}', (p.get_x() + p.get_width() / 2., p.get_height()), ha = 'center', va = 'center', xytext = (0, 10), textcoords = 'offset points')

    return fig


def show_df_events(df_events):

    df = df_events.groupby(['team', 'period', 'player', 'outcome']).size().reset_index(name='qty')
    
    df = df.pivot_table(index=['team', 'player', 'outcome'], columns='period', values='qty', fill_value=0).reset_index()
    
    teams = df['team'].unique()
    team = st.multiselect('Select the Team', teams, default=teams)
    df = df[df['team'].isin(team)]

    outcomes = df['outcome'].unique()
    select_outcomes = st.multiselect('Event Types', outcomes , default=outcomes)
    df = df[df['outcome'].isin(select_outcomes)]

    desired_order = ['team', 'player', 'outcome', 'first half', 'second half', 'first extra time', 'second extra time', 'penalty shootout']
    df = df.reindex(columns=desired_order + [col for col in df.columns if col not in desired_order], fill_value=0)

    return df

def dash_player_comparison(df_eventos, jogadorA,jogadorB):

    df_jogadorA = df_eventos[df_eventos['player'] == jogadorA]
    df_jogadorB = df_eventos[df_eventos['player'] == jogadorB]

    if not df_jogadorA['player'].empty and not df_jogadorB['player'].empty:

        #Adicionar Métricas JogadorA
        A_count_gols = df_jogadorA.loc[df_jogadorA['outcome'] == 'Goal'].shape[0]
        A_count_assistances = df_jogadorA.loc[(df_jogadorA['outcome'] == 'Goal Assistance')].shape[0]
        A_count_chutes = df_jogadorA.loc[df_jogadorA['outcome'] == 'Total Shots'].shape[0]
        A_count_passes = df_jogadorA.loc[(df_jogadorA['outcome'] == 'Total Passes')].shape[0]
        A_count_dribble = df_jogadorA.loc[(df_jogadorA['outcome'] == 'Dribble')].shape[0]

        #Adicionar Métricas JogadorB
        B_count_gols = df_jogadorB.loc[df_jogadorB['outcome'] == 'Goal'].shape[0]
        B_count_assistances = df_jogadorB.loc[(df_jogadorB['outcome'] == 'Goal Assistance')].shape[0]
        B_count_chutes = df_jogadorB.loc[df_jogadorB['outcome'] == 'Total Shots'].shape[0]
        B_count_passes = df_jogadorB.loc[(df_jogadorB['outcome'] == 'Total Passes')].shape[0]
        B_count_dribble = df_jogadorB.loc[(df_jogadorB['outcome'] == 'Dribble')].shape[0]

        if A_count_chutes >= 1: A_taxa_conversao = int(round((A_count_gols / A_count_chutes)*100,0))
        else: A_taxa_conversao = 0

        if B_count_chutes >= 1: B_taxa_conversao = int(round((B_count_gols / B_count_chutes)*100,0))
        else: B_taxa_conversao = 0

        #Calcular deltas
        A_delta_gols = A_count_gols - B_count_gols
        A_delta_taxa = A_taxa_conversao - B_taxa_conversao
        A_delta_passes = A_count_passes - B_count_passes
        A_delta_dribble = A_count_dribble - B_count_dribble
        A_delta_assistances = A_count_assistances - B_count_assistances
        
        B_delta_gols = A_delta_gols*-1
        B_delta_taxa = A_delta_taxa*-1
        B_delta_passes = A_delta_passes*-1
        B_delta_dribble = A_delta_dribble*-1
        B_delta_assistances = A_delta_assistances*-1

        #crio regras para as cores dos gols
        if A_count_gols == B_count_gols: color_gols = 'off'
        else: color_gols = 'normal'
        
        #crio regras para as cores dos passes bem sucedidos
        if A_count_passes == B_count_passes: color_passes = 'off'
        else: color_passes = 'normal'

        #crio regras para as cores da taxa de conversão
        if A_taxa_conversao == B_taxa_conversao: color_taxa = 'off'
        else: color_taxa = 'normal'

        #crio regras para as cores dos dribles
        if A_count_dribble == B_count_dribble: color_dribble = 'off'
        else: color_dribble = 'normal'

        #crio regras para as cores das assistências
        if A_count_assistances == B_count_assistances: color_assistances = 'off'
        else: color_assistances = 'normal'


        #Adicionar Métricas JogadorA
        col_a, col_b = st.columns(2)
        with col_a:
            col_1, col_2, col_3 = st.columns(3)
            with col_1:
                st.metric(label="Goals", value=A_count_gols, delta=A_delta_gols, delta_color=color_gols, border=True)
            with col_2:
                st.metric(label="Shots", value=f"{A_taxa_conversao}%", delta=A_delta_taxa, delta_color=color_taxa, border=True)
            with col_3:
                st.metric(label="Goal-to-shot ratio", value=f"{A_taxa_conversao}%", delta=A_delta_taxa, delta_color=color_taxa, border=True)

            col_1, col_2, col_3 = st.columns(3)
            with col_1:
                st.metric(label="Goal Assistances", value=A_count_assistances, delta=A_delta_assistances, delta_color=color_assistances, border=True)
            with col_2:
                st.metric(label="Passes", value=A_count_passes, delta=A_delta_passes, delta_color=color_passes, border=True)
            with col_3:
                st.metric(label="Dribbles", value=A_count_dribble, delta=A_delta_dribble, delta_color=color_dribble, border=True)



        #Adicionar Métricas JogadorB
        with col_b:
            col_1, col_2, col_3 = st.columns(3)
            with col_1:
                st.metric(label="Goals", value=B_count_gols, delta=B_delta_gols, delta_color=color_gols, border=True)
            with col_2:
                st.metric(label="Shots", value=f"{B_taxa_conversao}%", delta=B_delta_taxa, delta_color=color_taxa, border=True)
            with col_3:
                st.metric(label="Goal-to-shot ratio", value=f"{B_taxa_conversao}%", delta=B_delta_taxa, delta_color=color_taxa, border=True)

            col_1, col_2, col_3 = st.columns(3)
            with col_1:
                st.metric(label="Goal Assistances", value=B_count_assistances, delta=B_delta_assistances, delta_color=color_assistances, border=True)
            with col_2:
                st.metric(label="Passes", value=B_count_passes, delta=B_delta_passes, delta_color=color_passes, border=True)
            with col_3:
                st.metric(label="Dribbles", value=B_count_dribble, delta=B_delta_dribble, delta_color=color_dribble, border=True)


            
  
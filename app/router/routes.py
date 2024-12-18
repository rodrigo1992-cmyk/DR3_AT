import sys
sys.path.append(r'C:\Users\RodrigoPintoMesquita\Documents\GitHub\DR3_AT')

from fastapi import FastAPI
from statsbombpy import sb
import pandas as pd
 
from app.services.back_main import *
from app.services.back_agents import *
from app.model.models import *


app = FastAPI()

@app.get("/competitions", response_model=List[competitionsBM])
async def get_competitions():
    df = sb.competitions()
    df = df[['competition_name', 'season_name', 'competition_id', 'season_id']]
    dict = df.to_dict(orient='records')
    return dict


@app.get("/matches/{competition_id}/{season_id}", response_model=List[matchesBM])
async def matches(competition_id: int, season_id: int):
    df = sb.matches(competition_id = competition_id, season_id = season_id)
    df = df[['match_id', 'home_team', 'away_team']]
    dict = df.to_dict(orient='records')
    return dict


@app.get("/matchanalysis", response_model=str)
async def matchanalysis(match_id: int, home_team: str, away_team: str, llm_tone: llmtoneBM, user_input: str):
    df = sb.events(match_id = match_id)

    df_main_events = df_main_events_pre_processing(df)
    response = main_llm(
        match_id = match_id, 
        home_team = home_team,
        away_team = away_team,
        llm_tone = llm_tone,
        user_input = user_input, 
        df_main_events = df_main_events
        )
    
    

    return response

@app.get("/player_profile/{match_id}", response_model=List[eventsBM])
async def events(match_id: int):

    df_events = sb.events(match_id = match_id)
    
    colunas_desejadas = set(['team','type', 'period', 'player', 'shot_outcome', 'pass_outcome', 'pass_goal_assist','bad_behaviour_card'])
    colunas_no_df = set(df_events.columns)
    filtro_colunas = list(colunas_desejadas & colunas_no_df)

    df_events = df_events[filtro_colunas]

    jogadas_desejadas = ['Block', 'Dribble', 'Foul Won', 'Shot', 'Pass']
    df_events = df_events[df_events['type'].isin(jogadas_desejadas)]

    df_goals = df_events[df_events['shot_outcome'] == 'Goal'].copy()
    df_goals['outcome'] = 'Goal'
    df_assistances = df_events[df_events['pass_goal_assist'] == True].copy()
    df_assistances['outcome'] = 'Goal Assistance'

    for i, row in df_events.iterrows():
        if row['type'] == 'Shot':
            df_events.at[i, 'outcome'] = 'Total Shots'
        elif row['type'] == 'Pass':
            df_events.at[i, 'outcome'] = 'Total Passes'
        elif row['type'] == 'bad_behaviour_card':
            df_events.at[i, 'outcome'] = row['bad_behaviour_card']
        else:
            df_events.at[i, 'outcome'] = row['type']


    df = pd.concat([df_goals, df_assistances, df_events])
    df = df[['team','period','player', 'outcome']]

    period_map = {
        1: 'first half',
        2: 'second half',
        3: 'first extra time',
        4: 'second extra time',
        5: 'penalty shootout'
    }

    df['period'] = df['period'].apply(lambda k: period_map.get(k, 'Nao Mapeado'))

    dict = df.to_dict(orient='records')

    return dict



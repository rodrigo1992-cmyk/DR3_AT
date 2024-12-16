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


@app.get("/matchanalysis/{match_id}/{llm_tone}", response_model=str)
async def matchanalysis(match_id: int, llm_tone: llmtoneBM):
    df = sb.events(match_id = match_id)

    df_main_events = df_events_pre_processing(df)
    response = invoke_lmms_match_analysis(df_main_events, llm_tone)

    return response




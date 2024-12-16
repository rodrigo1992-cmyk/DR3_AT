from pydantic import BaseModel, RootModel
from typing import List, Optional
from enum import Enum

class competitionsBM(BaseModel):
    competition_name: str
    season_name: str
    competition_id: int
    season_id: int

class matchesBM(BaseModel):
    match_id: int
    home_team: str
    away_team: str


class llmtoneBM(str, Enum):
    Formal = "Formal"
    Empolgado = "Empolgado"
    Humorístico = "Humorístico"
    Técnico = "Técnico"
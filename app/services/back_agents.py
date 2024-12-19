import sys
sys.path.append(r'C:\Users\RodrigoPintoMesquita\Documents\GitHub\DR3_AT')

from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv
import google.generativeai as genai
import pandas as pd
from langchain.agents import Tool
from langchain.tools import tool
from langchain import hub
from langchain.agents import AgentExecutor, create_react_agent
from app.services.back_main import *

load_dotenv()

google_api_key = os.getenv('GOOGLE_API_KEY')

def half_summarizer(df: pd.DataFrame, half: str) -> tuple:
    ''' 
    Cria um agente para analisar um tempo da partida.

    Args:
    df: DataFrame com os eventos da partida.
    half: String com o tempo da partida a ser analisado, esperado os valores "firt half" ou "second half".
    '''


    prompt = f"""
        As a football commentator, summarize in the main events of the match. Follow the instructions bellow:
            1. The data received represent only the events of {half}
            2. It's mandatory to comment on all the goals scored and pennaltys.
            3. Pay attention to the chronological order in the index column, and emphasize the teams and players who made each play. 
            4. End the comment by stating the final score of the half, for example: Team A 1 - 2 Team B.
    """

    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=google_api_key)

    df = df[df['match_period'] == half]
    agent = create_pandas_dataframe_agent(llm, df, verbose=True, allow_dangerous_code = True, return_intermediate_steps=True)

    return agent, prompt



def match_summarizer(df: pd.DataFrame) -> str:
    '''Invoca Agentes para analisar cada tempo da partida de forma separada e depois gera um resumo final

    Args:
    df: DataFrame com os eventos principais da partida, já filtrado e com tratamento dos labels dos eventos.
    '''

    agent,prompt = half_summarizer(df, 'first half')
    first_half_analysis = agent.invoke(prompt)
    first_half_analysis = first_half_analysis['output']

    agent,prompt = half_summarizer(df, 'second half')
    second_half_analysis = agent.invoke(prompt)
    second_half_analysis = second_half_analysis['output']

    match_analyses = "\nObservation: "+ "ANALYSES FIRST HALF: \n" + first_half_analysis + "\nANALYSES SECOND HALF: \n" +second_half_analysis + "\n"
    return match_analyses

def match_stats(df: pd.DataFrame, user_input: str) -> str:
    
    prompt = f"""
        Analyze the dataframe to answer: {user_input}
        Firts, check if the event, team name, or player name is present in the dataset, creating a list of unique values of related column, if not, answer with the available options in the dataset.
        Please provide a complete and detailed response. For example, if the question is 'Which player scored the most goals in the match?', I would like you to respond with something like 'The player who scored the most goals in the match was Ronaldo Gaucho.

        The provided Dataframe has the following fields:
            -match_period: Indication of the period of the game in which the play was made
            -team: Team that executed the play
            -player: Name of the player who executed the play
            -play: Specification of the executed play, also called an event.
        
        Description of each value in the column "play":

            -Yellow Card: Player penalized with a yellow card
            -Red Card: Player penalized with a red card
            -Shot Blocked: Shots on goal that were blocked or saved
            -Goal Scored: Shots on goal that were successful during the match
            -Penalty Goal Scored: Shots on goal that were successful through penalty kicks
            -Assist Pass: Pass of the ball to another player, who scored a goal
        
        Examples of Questions and Instructions:
            -Comparisons between two players: 
                Example: Compare the Player A and Player B.
                Instruction: Filter the players' names in the dataset and aggregate to count the events for each. Analyse the results and give a report.
            -Questions about a particular type of event in the match. 
                Example: How many yellow cards were given in the first half?
                Instruction: Filter the event type in the dataset and aggregate to count the total. Consider the match time and the teams.
            -Questions about rankings. 
                Examples: Which player received the most yellow cards? Wich player did the most assists?
                Instruction: Filter the dataset, aggregate, and sort the values from highest to lowest
        """
    
    df = df.groupby(['match_period','team','player','play']).size().reset_index(name='count')

    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=google_api_key)

    agent = create_pandas_dataframe_agent(llm, df, verbose=True, allow_dangerous_code = True, number_of_head_rows=200, return_intermediate_steps=True)
    response = agent.invoke(prompt)
    response = "\nObservation: "+ response['output']
    return response


    
def create_tools(match_id: int, home_team: str, away_team: str, user_input: str, df: pd.DataFrame) -> list:
    '''
    Cria ferramentas para serem utilizadas pelo agente reAct.

    Args:
    match_id: ID da partida.
    home_team: Nome do time mandante.
    away_team: Nome do time visitante.
    user_input: Pergunta do usuário.
    df: DataFrame com os eventos da partida.

    Returns: Lista de ferramentas.
    '''


    return [
        Tool(
            #O nome do prompt não condiz com o conteúdo, pois não estou conseguindo trocar o nome do meu projeto no LangSmith.
            name="match_summarizer",
            func=lambda x="": match_summarizer(df), 
            description="Creates narrative summaries about the match."
        ),
        Tool(
            name="match_stats", 
            func=lambda  x="": match_stats(df, user_input),  
            description="Provides statistical data about the match, teams, and players. Example: Number of saves, goals, shots on goal, etc."
        ),
        Tool(
            name="match_lineup", 
            func= lambda x="": get_lineup(match_id, home_team, away_team),
            description="Provides the escalation for the match, also know as lineup. The lineup is a list of players that had participated in the match."
        )
    ]
     


def instance_agent(match_id: int, home_team: str, away_team: str, llm_tone: str, user_input: str, df: pd.DataFrame):
    '''
    Cria um agente reAct consolidar as respostas dos demais agentes ou tools e aplicar o TOM narrativo selecionado pelo usuário.

    Args:
    match_id: ID da partida.
    home_team: Nome do time mandante.
    away_team: Nome do time visitante.
    llm_tone: Tom da linguagem do modelo de linguagem.
    user_input: Pergunta do usuário.
    df: DataFrame com os eventos da partida.

    Returns: Agente reAct instanciado.
    
    '''
    tools = create_tools(match_id, home_team, away_team, user_input, df)

    prompt = hub.pull("musicindustrysearch/react")
    
    agent = create_react_agent(
        llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash",temperature=0.7), 
        tools = tools, 
        prompt = prompt.partial(llm_tone=llm_tone)
    )
    
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, max_turns=2, return_intermediate_steps=True, max_iterations=20)
    
    return agent_executor



def main_llm(match_id: int, home_team: str, away_team: str, llm_tone: str, user_input: str, df_main_events: pd.DataFrame) -> str:
    '''
    Chama um agente para analisar os eventos da partida.

    Args:
    match_id: ID da partida.
    home_team: Nome do time mandante.
    away_team: Nome do time visitante.
    llm_tone: Tom da linguagem do modelo de linguagem.
    user_input: Pergunta do usuário.
    df_main_events: DataFrame com os eventos da partida.

    Returns: String com a resposta do modelo LLM.
    '''

    map_llm_tone = {
    "Formal" : "formal (technical and objective)",
    "Excited" :  "excited (vibrant, celebratory)",
    "Humorous" : "humorous (relaxed and creative)",
    "Technical" : "technical (detailed analysis of events)"
    }

    llm_tone = map_llm_tone.get(llm_tone, "Formal") 

    agent = instance_agent(
        match_id = match_id, 
        home_team = home_team,
        away_team = away_team,
        llm_tone = llm_tone,
        user_input = user_input, 
        df = df_main_events
        )
    
    response = agent({"input": user_input})
    return response['output']
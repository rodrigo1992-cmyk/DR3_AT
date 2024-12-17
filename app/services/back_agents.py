from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv
import google.generativeai as genai
import pandas as pd
from langchain.agents import Tool
from langchain.tools import tool

load_dotenv()

google_api_key = os.getenv('GOOGLE_API_KEY')

def agent_half_analyses(df: pd.DataFrame, half: str) -> tuple:
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
    agent = create_pandas_dataframe_agent(llm, df, verbose=True, allow_dangerous_code = True)

    return agent, prompt

def match_summarizer(first_half_analysis: str, second_half_analysis: str, llm_tone: str) -> str:
    '''
    Gera um resumo final da partida, condensando os resumos de cada tempo.

    Args:
    first_half_analysis: Resumo gerado por LLM para o primeiro tempo da partida.
    second_half_analysis: Resumo gerado por LLM para o segundo tempo da partida.
    '''

    map_llm_tone = {
        "Formal" : "formal (técnico e objetivo)",
        "Empolgado" :  "empolgado (vibrante, comemorativo)",
        "Humorístico" : "humorístico (descontraído e criativo)",
        "Técnico" : "técnico (análise detalhada dos eventos)"
    }

    mapped_tone = map_llm_tone.get(llm_tone, "Formal") 

    prompt_final = f"""
    Como um narrador de futebol, analise os resumos de cada tempo da partida e condense em um resumo final. Siga as instruções abaixo:
        1. Você está contando a análise via chat, sobre uma partida antiga. Utilize um tom {mapped_tone}
        2. Os resumos estão em inglês, porém você deve responder em português.
        3. Deixe claro quais eventos foram do primeiro e do segundo tempo.
        4. É obrigatório citar cada gol e se foram feitos por penalti.
        5. Cite os jogadores e times envolvidos em cada jogada.
        6. O placar final corresponde à soma do placar de cada tempo da partida.
        7. Finalize o resumo citando o placar final da partida.
        8. Utilize formatação markdown na resposta

    Resumo Primeiro tempo:
    {first_half_analysis}

    Resumo Segundo tempo:
    {second_half_analysis}
    """

    genai.configure(api_key=os.getenv('GEMINI_KEY'))
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt_final)

    return response.text

def invoke_lmms_match_summary(df: pd.DataFrame, tom_narrativo: str) -> str:
    '''Invoca Agentes para analisar cada tempo da partida de forma separada e depois gera um resumo final

    Args:
    df: DataFrame com os eventos principais da partida, já filtrado e com tratamento dos labels dos eventos.
    '''

    agent,prompt = agent_half_analyses(df, 'first half')
    first_half_analysis = agent.invoke(prompt)
    first_half_analysis = first_half_analysis['output']

    agent,prompt = agent_half_analyses(df, 'second half')
    second_half_analysis = agent.invoke(prompt)
    second_half_analysis = second_half_analysis['output']

    final_response = match_summarizer(first_half_analysis, second_half_analysis, tom_narrativo)

    return final_response

def agent_match_stats(df: pd.DataFrame, user_input: str) -> str:
    
    prompt = f"""
        Analyze the dataframe to answer questions about soccer matches. 
        You need to answer the question {user_input}.
        Firts, check if the event, team name, or player name is present in the dataset, creating a list of unique values of related column, if not, answer with the available options in the dataset.
        Give the answer in portuguese.

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

    agent = create_pandas_dataframe_agent(llm, df, verbose=True, allow_dangerous_code = True, number_of_head_rows=200)

    return agent, prompt


tools = [
    Tool(
        name="invoke_lmms_match_summary",
        func=invoke_lmms_match_summary,
        description="Cria resumos narrativos sobre a partida."
    ),
    Tool(
        name="agent_match_stats",
        func=agent_match_stats,
        description="Fornece dados estatísticos sobre a partida, sobre os times ou sobre os jogadores. Exemplo: Quantidade de defesas, gols, chutes a gol, etc."
    )
]


def main_llm() -> str:

    prompt = f"""
    Como um narrador de futebol, analise os resumos de cada tempo da partida e condense em um resumo final. Siga as instruções abaixo:
        1. Você está contando a análise via chat, sobre uma partida antiga. Utilize um tom {mapped_tone}
        2. Os resumos estão em inglês, porém você deve responder em português.
        3. Deixe claro quais eventos foram do primeiro e do segundo tempo.
        4. É obrigatório citar cada gol e se foram feitos por penalti.
        5. Cite os jogadores e times envolvidos em cada jogada.
        6. O placar final corresponde à soma do placar de cada tempo da partida.
        7. Finalize o resumo citando o placar final da partida.
        8. Utilize formatação markdown na resposta

    Resumo Primeiro tempo:
    {first_half_analysis}

    Resumo Segundo tempo:
    {second_half_analysis}
    """

    genai.configure(api_key=os.getenv('GEMINI_KEY'))
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt_final)

    return response.text

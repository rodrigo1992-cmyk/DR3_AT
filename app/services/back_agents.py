from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv
import google.generativeai as genai
import pandas as pd

load_dotenv()

google_api_key = os.getenv('GOOGLE_API_KEY')

# Faz a consulta
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

def invoke_lmms_match_analysis(df: pd.DataFrame, tom_narrativo: str) -> str:
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




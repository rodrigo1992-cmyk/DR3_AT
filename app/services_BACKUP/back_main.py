
import pandas as pd

def df_events_pre_processing(df_events: pd.DataFrame) -> pd.DataFrame:
    '''
    Função que recebe um DataFrame de eventos de uma partida e retorna um DataFrame com os eventos principais da partida.[Gols, assistências, cartões, etc.]

    Parâmetros:
    df_events: DataFrame - DataFrame de eventos de uma partida (obtido através da função sb.events(match_id=ID_DA_PARTIDA))
    '''

    colunas_desejadas = set(['second','period','team','player','pass_goal_assist','bad_behaviour_card','shot_type','shot_outcome'])
    colunas_no_df = set(df_events.columns)
    filtro_colunas = list(colunas_desejadas & colunas_no_df)

    # Filtrando o DataFrame para incluir apenas as colunas que estão presentes, pois algumas colunas não aparecem para todas as partidas
    X = df_events[filtro_colunas]

    melt_values_desejado = set(['pass_goal_assist','bad_behaviour_card','shot_outcome'])
    melt_values = list(melt_values_desejado & colunas_no_df)

    X = X.melt(id_vars=['second','period','team','player','shot_type'], value_vars=melt_values)
    X = X[X.value.notnull()]

    descartar = ['Saved','Wayward','Post','Off T','Off S']
    X = X[~X['value'].isin(descartar)]

    #Concatenar as colunas "Variable" e "Value", usando ponto e virgula como separador

    X['key'] = X['variable'] + ';' + X['shot_type'].astype(str) + ';' + X['value'].astype(str) 



    #Criando uma coluna única para os eventos
    event_map = {
        ('bad_behaviour_card;nan;Yellow Card'): 'Yellow Card',
        ('bad_behaviour_card;nan;Red Card'): 'Red Card',
        ('shot_outcome;Open Play;Blocked'): 'Shot Blocked',
        ('shot_outcome;Open Play;Goal'): 'Goal Scored',
        ('shot_outcome;Penalty;Goal'): 'Penalty Goal Scored',
        ('pass_goal_assist;nan;True'): 'Assist Pass'

    }

    period_map = {
        1: 'first half',
        2: 'second half'
    }

    # Aplicando a transformação
    X['play'] = X['key'].apply(lambda k: event_map.get(k, 'EVENTO NAO MAPEADO'))

    X['match_period'] = X['period'].apply(lambda k: period_map.get(k, 'EVENTO NAO MAPEADO'))

    #Ordem cronológica
    X = X.sort_values(['period','second']).reset_index()

    X = X.drop(['index','second','variable','period', 'value','shot_type','key'], axis=1)

    #Ordenar colunas
    df_main_events = X[['match_period','team','player','play']]

    return df_main_events



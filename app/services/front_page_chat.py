
def dados_jogador(df_eventos, jogadorA,jogadorB):
    df_jogadorA = df_eventos[df_eventos['player'] == jogadorA]
    df_jogadorB = df_eventos[df_eventos['player'] == jogadorB]

    if not df_jogadorA['player'].empty and not df_jogadorB['player'].empty:

        #Adicionar Métricas JogadorA
        A_count_gols = df_jogadorA.loc[df_jogadorA['shot_outcome'] == 'Goal'].shape[0]
        A_count_chutes = df_jogadorA.loc[df_jogadorA['type'] == 'Shot'].shape[0]
        A_count_passes_sucess = df_jogadorA.loc[(df_jogadorA['type'] == 'Pass') & (df_jogadorA['pass_outcome'].isnull())].shape[0]

        #Adicionar Métricas JogadorB
        B_count_gols = df_jogadorB.loc[df_jogadorB['shot_outcome'] == 'Goal'].shape[0]
        B_count_chutes = df_jogadorB.loc[df_jogadorB['type'] == 'Shot'].shape[0]
        B_count_passes_sucess = df_jogadorB.loc[(df_jogadorB['type'] == 'Pass') & (df_jogadorB['pass_outcome'].isnull())].shape[0]

        if A_count_chutes >= 1: A_taxa_conversao = int(round((A_count_gols / A_count_chutes)*100,0))
        else: A_taxa_conversao = 0

        if B_count_chutes >= 1: B_taxa_conversao = int(round((B_count_gols / B_count_chutes)*100,0))
        else: B_taxa_conversao = 0

        #Calcular deltas
        A_delta_gols = A_count_gols - B_count_gols
        A_delta_taxa = A_taxa_conversao - B_taxa_conversao
        A_delta_passes = A_count_passes_sucess - B_count_passes_sucess
        
        B_delta_gols = A_delta_gols*-1
        B_delta_taxa = A_delta_taxa*-1
        B_delta_passes = A_delta_passes*-1

        #crio regras para as cores dos gols
        if A_count_gols == B_count_gols: color_gols = 'off'
        else: color_gols = 'normal'
        
        #crio regras para as cores dos passes bem sucedidos
        if A_count_passes_sucess == B_count_passes_sucess: color_passes = 'off'
        else: color_passes = 'normal'

        #crio regras para as cores da taxa de conversão
        if A_taxa_conversao == B_taxa_conversao: color_taxa = 'off'
        else: color_taxa = 'normal'

        #Adicionar Métricas JogadorA

        col_a, col_b = st.columns(2)
        with col_a:
            col_1, col_2, col_3 = st.columns(3)
            with col_1:
                st.metric(label="Total de Gols", value=A_count_gols, delta=A_delta_gols, delta_color=color_gols)
            with col_2:
                st.metric(label="Taxa de Conversão", value=f"{A_taxa_conversao}%", delta=A_delta_taxa, delta_color=color_taxa)
            with col_3:
                st.metric(label="Passes Bem-Sucedidos", value=A_count_passes_sucess, delta=A_delta_passes, delta_color=color_passes)

            #Plotar Dataframe
            st.dataframe(df_jogadorA)
            csv = df_jogadorA.to_csv(index=False)
            st.download_button(label="Baixar em CSV", data=csv, file_name=f'dados_{jogadorA}.csv', mime='text/csv',key = 'csv_jogadorA')

        with col_b:
            col_1, col_2, col_3 = st.columns(3)
            with col_1:
                st.metric(label="Total de Gols", value=B_count_gols, delta= B_delta_gols , delta_color=color_gols)
            with col_2:
                st.metric(label="Taxa de Conversão", value=f"{B_taxa_conversao}%", delta=B_delta_taxa, delta_color=color_taxa)
            with col_3:
                st.metric(label="Passes Bem-Sucedidos", value=B_count_passes_sucess, delta=B_delta_passes, delta_color=color_passes)

            #Plotar Dataframe
            st.dataframe(df_jogadorB)
            csv = df_jogadorB.to_csv(index=False)
            st.download_button(label="Baixar em CSV", data=csv, file_name=f'dados_{jogadorB}.csv', mime='text/csv',key = 'csv_jogadorB')
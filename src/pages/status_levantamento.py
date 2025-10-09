import json
import os
from typing import List, Optional


from datetime import datetime
import streamlit as st
import pandas as pd
import altair as alt
import matplotlib.pyplot as plt  # criar gráficos como imagem
import seaborn as sns


def retornar():
    botao_retornar = st.button('Retornar para Credenciamento')
    if botao_retornar:
        st.switch_page('menu_principal.py')

def trocar_ug():
    if st.session_state.username == 'admin':
        botao_trocar_ug = st.button('Trocar UG', width='stretch')
        if botao_trocar_ug:
            st.session_state.selected_ug = st.selectbox("Trocar UG:", options=['Selecione uma UG'] + st.session_state.lista_todas_ugs)

def buscar_e_ler_arquivos_json(caminho_pasta: str, padrao_inicio: str) -> Optional[pd.DataFrame]:
    """
    Busca arquivos .json na pasta que comecem com o padrão especificado, 
    lê cada um em um DataFrame do Pandas e concatena todos.
    
    Args:
        caminho_pasta: O caminho relativo ou absoluto da pasta.
        padrao_inicio: O padrão de início do nome do arquivo.
        
    Returns:
        Um DataFrame do Pandas combinado com os dados de todos os arquivos, 
        ou None se nenhum arquivo for encontrado.
    """
    
    arquivos_encontrados: List[str] = []
    
    # --- 2. Busca de Arquivos usando os ---
    print(f"Buscando arquivos na pasta: {caminho_pasta}")
    print(f"Padrão de início esperado: {padrao_inicio}*.json")
    
    try:
        # 1. Listar todos os itens (arquivos e pastas) no diretório
        for item in os.listdir(caminho_pasta):
            caminho_completo = os.path.join(caminho_pasta, item)
            
            # 2. Filtrar para garantir que seja um arquivo
            if os.path.isfile(caminho_completo):
                
                # 3. Filtrar pelo padrão de início e extensão .json
                if item.startswith(padrao_inicio) and item.lower().endswith('.json'):
                    arquivos_encontrados.append(caminho_completo)
                    
    except FileNotFoundError:
        st.warning(f"ERRO: A pasta '{caminho_pasta}' não foi encontrada.")
        return None
    except Exception as e:
        st.warning(f"Ocorreu um erro ao listar arquivos: {e}")
        return None

    if not arquivos_encontrados:
        st.warning("Nenhum arquivo correspondente foi encontrado.")
        return None

    
    # --- 3. Leitura e Concatenação dos Arquivos JSON ---
    dataframes_concatenados = []
    
    for arquivo in arquivos_encontrados:
        try:
            # pd.read_json lê o arquivo JSON e o converte para um DataFrame
            # O parâmetro 'lines=True' é útil se cada linha do JSON for um objeto JSON separado
            # O parâmetro 'orient' pode precisar ser ajustado dependendo da estrutura do seu JSON
            df = pd.read_json(arquivo).T
            df['data_levantamento'] = arquivo.split('_')[5].split('.')[0]
            df['data_levantamento'] = pd.to_datetime(df['data_levantamento'], format='%Y-%m-%d').dt.date
            df['unidade'] = df.index
            df.set_index('data_levantamento', drop=False, inplace=True)
            df['perc_levantado'] = df['perc_levantado']*100

            dataframes_concatenados.append(df)
            
        except ValueError as e:
            st.warning(f"AVISO: Não foi possível ler o arquivo JSON '{arquivo}'. Erro: {e}")
        except Exception as e:
            st.warning(f"ERRO inesperado ao processar '{arquivo}': {e}")
    
    
    if dataframes_concatenados:
        df_final = pd.concat(dataframes_concatenados, ignore_index=True)
        return df_final
    else:
        st.warning("Nenhum arquivo JSON válido foi lido para concatenação.")
        return None



def pagina_principal():
    """Configura as propriedades da página no Streamlit."""
    st.set_page_config(
        page_title='Status da Base de dados',
        page_icon='📊',
        layout='wide')
    retornar()
    
    if ((st.session_state.selected_ug != None) or (st.session_state.username != None)):
        trocar_ug()
        # CARGA DE ARQUIVO CSV  
        if os.path.exists(f'data_bronze/lista_bens-processado-{st.session_state.selected_ug}.csv'):
            st.title(f'Status do levantamento da UG {st.session_state.selected_ug}')
            df = pd.read_csv(f'data_bronze/lista_bens-processado-{st.session_state.selected_ug}.csv', dtype=str)
            df = df[df['status'].isin(['EFETIVADO','ACAUTELADO','BEM NÃO LOCALIZADO','EM PROCESSO DE ALIENAÇÃO'])]
            total_bens_ativos = df.shape[0]
            col1,col2,col3 = st.columns([0.25,0.25,0.5])
            todos_bens = col1.button('Todos bens')
            if todos_bens:
                df = pd.read_csv(f'data_bronze/lista_bens-processado-{st.session_state.selected_ug}.csv', dtype=str)
            filtro_ativos = col2.button('Bens ativos')
            if filtro_ativos:
                df = df[df['status'].isin(['EFETIVADO','ACAUTELADO','BEM NÃO LOCALIZADO','EM PROCESSO DE ALIENAÇÃO'])]
            filtro_status = col3.multiselect(label='Filtrar por status: ', 
                                             options=df['status'].unique())
            if filtro_status:
                df = df[df['status'].isin(filtro_status)]
            col_grupo, col_unidade = st.columns(2)
            filtro_grupo = col_grupo.multiselect('Filtro por grupo de material',df['grupo de material'].unique())
            st.session_state.titulo_grafico = st.session_state.selected_ug
            if filtro_grupo:
                df = df[df['grupo de material'].isin(filtro_grupo)]
                titulo_grupo = df['grupo de material'].unique()[0]
                st.session_state.titulo_grafico = titulo_grupo
            filtro_unidade = col_unidade.multiselect('Filtro por unidade patrimonial', df['unidade responsavel material'].unique())
            if filtro_unidade:
                df = df[df['unidade responsavel material'].isin(filtro_unidade)]
                titulo_sigla = df['sigla'].unique()[0]
                st.session_state.titulo_grafico = titulo_sigla
                

            # -- MÉTRICAS LEVANTAMENTO --
            col_qtd, col_perc = st.columns(2)
            qtd_bens = df.shape[0]
            ano_atual = str(datetime.today().year)
            qtd_inventariados = len(df[df['ano do levantamento'] == ano_atual])
            col_qtd.metric('Qtde. de bens', qtd_bens)
            col_perc.metric('',None)
            col_qtd.metric('Total inventariados', qtd_inventariados)
            col_perc.metric('Perc. Inventariado', f'{round(qtd_inventariados/qtd_bens*100,2)}%')
            col_qtd.metric('Total não inventariados', qtd_bens-qtd_inventariados)
            col_perc.metric('Perc. não Inventariado', f'{round((1-qtd_inventariados/qtd_bens)*100,2)}%')

            # -- FILTRO NÃO INVENTARIADOS --
            escolhe_inventariados = st.segmented_control("Todos os bens ou apenas não inventariados?",
                                                         options=["Todos os bens", "Apenas não inventariados"],
                                                        key="escolha_inventariados")
            if escolhe_inventariados == "Apenas não inventariados":
                df = df[df['ano do levantamento'] != ano_atual]
                
            # Levantamento por último ano
            st.subheader('Quantidade de bens pelo último ano de levantamento')
            histograma_levantamento = df.groupby('ano do levantamento')['ano do levantamento'].count()
            #plotar histograma
            with sns.axes_style('whitegrid'):
                grafico = histograma_levantamento.plot(kind='bar', 
                                                       title=f'Quantidade de bens ativos pelo último ano de inventário ({st.session_state.titulo_grafico})')
                grafico.set_xlabel('Ano do último levantamento')
                grafico.set_ylabel('Quantidade de bens ativos')
                grafico.set_xticklabels(grafico.get_xticklabels(), rotation=45)
            for i, v in enumerate(histograma_levantamento):
                grafico.text(i, v, str(v), ha='center', va='bottom')
            st.pyplot(grafico.figure, width='stretch')
            st.warning("Levantamentos com último ano 2010 são aqueles nunca levantados")

            
            # POR UNIDADE / LOCALIDADE
            if not filtro_unidade:
                st.subheader('Quantidade de bens levantados por Unidade')
                contagem_unidade = df.groupby(['sigla', 'ano do levantamento']).size().unstack()
            else:
                st.subheader('Quantidade de bens levantados por Localidade')
                contagem_unidade = df.groupby(['localidade', 'ano do levantamento']).size().unstack()
            if escolhe_inventariados == "Apenas não inventariados":
                contagem_unidade[ano_atual] = 0
            contagem_unidade['soma'] = contagem_unidade.sum(axis=1).fillna(0).astype(int)
            contagem_unidade['percentual'] = contagem_unidade[ano_atual]/contagem_unidade['soma']
            contagem_unidade['percentual'] = contagem_unidade['percentual'].mul(100).round(1).fillna(0)
            contagem_unidade['soma'] = contagem_unidade['soma'].astype(str)
            contagem_unidade['percentual'] = contagem_unidade['percentual'].astype(str)
            if not filtro_unidade:
                contagem_unidade['sigla'] = contagem_unidade.index.get_level_values('sigla')
                contagem_unidade['sigla'] = contagem_unidade['sigla'] + ' (' + contagem_unidade['soma'].astype(str) + ' / ' + contagem_unidade['percentual'].astype(str) + '%)'
            else:
                contagem_unidade['localidade'] = contagem_unidade.index.get_level_values('localidade')
                contagem_unidade['localidade'] = contagem_unidade['localidade'] + ' (' + contagem_unidade['soma'].astype(str) + ' / ' + contagem_unidade['percentual'].astype(str) + '%)'
            contagem_unidade = contagem_unidade.drop(columns=['percentual'])
            colunas_numericas = contagem_unidade.select_dtypes(include=['float64', 'int64']).columns
            contagem_unidade['total'] = contagem_unidade[colunas_numericas].sum(axis=1)
            contagem_unidade = contagem_unidade.sort_values(by='total', ascending=False)
            contagem_unidade = contagem_unidade.drop(columns=['total'])
            st.write('**Legenda:** Unidade (Quantidade total de bens / percentual inventariado)')
            # Plotar o gráfico de barras empilhadas
            if not filtro_unidade:
                grafico_contagem_unidade = contagem_unidade.plot(kind='barh',
                                                x = 'sigla',
                                                stacked=True,
                                                title=f'Bens ativos por setor e ano do último levantamento na {st.session_state.titulo_grafico}',
                                                colormap = 'RdBu')
            else:
                grafico_contagem_unidade = contagem_unidade.plot(kind='barh',
                                                x = 'localidade',
                                                stacked=True,
                                                title=f'Bens ativos por setor e ano do último levantamento na {st.session_state.titulo_grafico}',
                                                colormap = 'RdBu')
                
            grafico_contagem_unidade.set_ylabel('Setor (% levantado)')
            grafico_contagem_unidade.set_xlabel('Quantidade de bens ativos')
            grafico_contagem_unidade.set_xticklabels(grafico_contagem_unidade.get_xticklabels(), rotation=45)
            grafico_contagem_unidade.figure.set_size_inches(15, 10)
            st.pyplot(grafico_contagem_unidade.figure)
            st.warning("Levantamentos com último ano 2010 são aqueles nunca levantados")

            # gráfico por valor



            # POR GRUPO DE MATERIAL / SUBGRUPO
            if not filtro_grupo:
                st.subheader('Quantidade de bens levantados por Grupo de Material')
                contagem_grupo = df.groupby(['grupo de material', 'ano do levantamento']).size().unstack()
            else:
                st.subheader('Quantidade de bens levantados por Subgrupo de material')
                contagem_grupo = df.groupby(['subgrupo de material', 'ano do levantamento']).size().unstack()
            if escolhe_inventariados == "Apenas não inventariados":
                contagem_grupo[ano_atual] = 0
            contagem_grupo['soma'] = contagem_grupo.sum(axis=1).fillna(0).astype(int)
            contagem_grupo['percentual'] = contagem_grupo[ano_atual]/contagem_grupo['soma']
            contagem_grupo['percentual'] = contagem_grupo['percentual'].mul(100).round(1).fillna(0)
            contagem_grupo['soma'] = contagem_grupo['soma'].astype(str)
            contagem_grupo['percentual'] = contagem_grupo['percentual'].astype(str)
            if not filtro_grupo:
                contagem_grupo['grupo de material'] = contagem_grupo.index.get_level_values('grupo de material')
                contagem_grupo['grupo de material'] = contagem_grupo['grupo de material'] + ' (' + contagem_grupo['soma'].astype(str) + ' / ' + contagem_grupo['percentual'].astype(str) + '%)'
            else:
                contagem_grupo['subgrupo de material'] = contagem_grupo.index.get_level_values('subgrupo de material')
                contagem_grupo['subgrupo de material'] = contagem_grupo['subgrupo de material'] + ' (' + contagem_grupo['soma'].astype(str) + ' / ' + contagem_grupo['percentual'].astype(str) + '%)'
            contagem_grupo = contagem_grupo.drop(columns=['percentual'])
            colunas_numericas = contagem_grupo.select_dtypes(include=['float64', 'int64']).columns
            contagem_grupo['total'] = contagem_grupo[colunas_numericas].sum(axis=1)
            contagem_grupo = contagem_grupo.sort_values(by='total', ascending=False)
            contagem_grupo = contagem_grupo.drop(columns=['total'])
            st.write('**Legenda:** Unidade (Quantidade total de bens / percentual inventariado)')
            # Plotar o gráfico de barras empilhadas
            if not filtro_grupo:
                grafico_contagem_grupo = contagem_grupo.plot(kind='barh',
                                                x = 'grupo de material',
                                                stacked=True,
                                                title=f'Bens ativos por setor e ano do último levantamento na {st.session_state.titulo_grafico}',
                                                colormap = 'RdBu')
            else:
                grafico_contagem_grupo = contagem_grupo.plot(kind='barh',
                                                x = 'subgrupo de material',
                                                stacked=True,
                                                title=f'Bens ativos por setor e ano do último levantamento na {st.session_state.titulo_grafico}',
                                                colormap = 'RdBu')
                
            grafico_contagem_grupo.set_ylabel('Setor (% levantado)')
            grafico_contagem_grupo.set_xlabel('Quantidade de bens ativos')
            grafico_contagem_grupo.set_xticklabels(grafico_contagem_grupo.get_xticklabels(), rotation=45)
            grafico_contagem_grupo.figure.set_size_inches(15, 10)
            st.pyplot(grafico_contagem_grupo.figure)
            st.warning("Levantamentos com último ano 2010 são aqueles nunca levantados")

            # por valor



            # -- EVOLUÇÃO DO LEVANTAMENTO --
            st.header('Evolução do Levantamento')
            df_levantamento_historico = pd.DataFrame()
            CAMINHO_PASTA = 'data_silver'
            UG = st.session_state.selected_ug
            PADRAO_INICIO = f'{UG}_estatisticas_levantamento_{UG}_'
            
            # Inserir levantamento estimado e data de início, depois salvar em json para chamar, se existir
            col1, col2, col3 = st.columns([3,3,4])
            prazo_levantamento = col1.number_input('Prazo em dias do levantamento:',
                                                    min_value = 15,
                                                    step = 15,
                                                    placeholder=90)
            quantidade_equipes = col2.number_input('Qtde. de equipes de campo:',
                                                    min_value = 1,
                                                    step = 1)
            levantamento_diario_estimado = round(total_bens_ativos / prazo_levantamento)

            col3.metric('Estimativa de bens/dia/equipe', round(levantamento_diario_estimado/quantidade_equipes))

            df_levantamento_historico = buscar_e_ler_arquivos_json(CAMINHO_PASTA, PADRAO_INICIO)
            df_levantamento_historico_geral = df_levantamento_historico[['qtde_levantado','perc_levantado','data_levantamento']].groupby('data_levantamento').sum().reset_index()
            
            # 1. Garante que a coluna de data esteja em formato datetime ANTES de calcular min/max
            df_levantamento_historico_geral['data_levantamento'] = pd.to_datetime(
                df_levantamento_historico_geral['data_levantamento']
            )

            # 2. Define as datas limite (min e max)
            data_inicio_levantamento = df_levantamento_historico_geral['data_levantamento'].min()
            data_atual_levantamento = df_levantamento_historico_geral['data_levantamento'].max()

            # 3. Gera todos os dias úteis no intervalo
            todos_dias_uteis = pd.date_range(
                start=data_inicio_levantamento,
                end=data_atual_levantamento,
                freq='B' # Business Day
            )

            # 4. Define 'data_levantamento' como índice para o preenchimento (resample/reindex)
            df_com_indice = df_levantamento_historico_geral.set_index('data_levantamento')

            # --- Otimização da Lógica de Preenchimento (Substituindo concat/duplicated por reindex) ---

            # A melhor abordagem no Pandas para garantir que todas as datas em um intervalo
            # existam e que dados existentes sejam mantidos é usar .reindex().
            # Isso garante que não haverá duplicatas.
            df_levantamento_completo = df_com_indice.reindex(todos_dias_uteis)

            # 5. Prepara o DataFrame final:
            #    a) Converte o índice de volta para uma coluna chamada 'data_levantamento'
            #    b) O reindex já garante que o DataFrame está ordenado por data
            df_levantamento_historico_geral = df_levantamento_completo.reset_index().rename(
                columns={'index': 'data_levantamento'}
            )

            df_levantamento_historico_geral['qtde_levantado'] = df_levantamento_historico_geral['qtde_levantado'].ffill(axis=0)


            for i in range(len(df_levantamento_historico_geral)):
                if i == 0:
                    # 1. Inicializa o primeiro valor
                    df_levantamento_historico_geral.loc[i, 'levantamento_estimado'] = levantamento_diario_estimado
                else:
                    # 2. Pega o valor acumulado anterior
                    valor_anterior = df_levantamento_historico_geral.loc[i-1, 'levantamento_estimado']
                    
                    # 3. Calcula o novo valor potencial
                    novo_valor = valor_anterior + levantamento_diario_estimado
                    
                    # 4. Checa o limite e atribui
                    # O valor atribuído será o menor entre o novo_valor e o total_bens_ativos
                    valor_final = min(novo_valor, total_bens_ativos)
                    
                    df_levantamento_historico_geral.loc[i, 'levantamento_estimado'] = valor_final
            df_levantamento_historico_geral.drop(columns=['perc_levantado'], inplace=True)

            #guardar o valor máximo entre qtde levantada e levantamento estimado
            if not df_levantamento_historico_geral.empty:
                valor_maximo = df_levantamento_historico_geral[['qtde_levantado','levantamento_estimado']].max().max()
                # -- GRÁFICO HISTÓRICO LEVANTAMENTO --
                linha_levantamento = alt.Chart(df_levantamento_historico_geral).mark_line(color='blue').encode(
                    x=alt.X('data_levantamento:T', title='Data do Levantamento'),
                    y=alt.Y('qtde_levantado:Q', title='Quantidade Levantada', scale=alt.Scale(domain=[0, valor_maximo])),
                    tooltip=['data_levantamento', 'qtde_levantado']
                ).properties(
                    width=800,
                    height=400
                )
                # Adicionar a linha de levantamento estimado
                linha_estimativa = alt.Chart(df_levantamento_historico_geral).mark_line(color='red').encode(
                    x=alt.X('data_levantamento:T', title='Data do Levantamento'),
                    y=alt.Y('levantamento_estimado:Q', title='Levantamento Estimado', scale=alt.Scale(domain=[0, valor_maximo])),
                    tooltip=['data_levantamento', 'levantamento_estimado']
                ).properties(
                    width=800,
                    height=400
                )
                # Adicionar rótulos com os valores da quantidade levantada
                text = alt.Chart(df_levantamento_historico_geral).mark_text(
                    align='center',
                    baseline='bottom', # Alterado para 'bottom' para posicionar acima da área
                    dy=-5  # Ajusta a posição vertical do texto
                ).encode(
                    x=alt.X('data_levantamento:T'),
                    y=alt.Y('qtde_levantado:Q'),
                    text=alt.Text('qtde_levantado:Q'),  # Exibe os valores
                    color=alt.value('black') # Define a cor do texto
                )
                # Mergir os três gráficos (área, linha e texto) e aplicar a configuração de grade
                grafico_levantamento = (linha_levantamento + linha_estimativa 
                                        ).configure_axis(grid=True
                                                        ).configure_view(stroke='transparent',
                                                                        fill='white')
                # Exibir o gráfico no Streamlit
                st.markdown("""
                            <h2 style='text-align: center;'>
                                Histórico de 
                                <span style='color: blue;'>Levantamento</span>
                                e 
                                <span style='color: red;'>Estimado</span>
                            </h2>
                            <hr style='border: 1px solid #ccc;'>
                            """, unsafe_allow_html=True)
                st.altair_chart(grafico_levantamento, use_container_width=True)

            # -- DATAFRAME --
            st.dataframe(df)
            st.divider()

            # -- STATUS BASE --
            st.title('Status da base de dados')
            
            # QUANTIDADE POR STATUS
            st.subheader('Quantidade de bens por status')
            df_status = df['status'].groupby(df['status']).count()
            plt.clf()
            grafico_status = df_status.plot(kind='pie',
                                            title = f'Quantidade de bens por Status ({st.session_state.titulo_grafico})',
                                            #labels= None, # nomes no gráfico
                                            autopct= lambda p: '{:.2f}%({:.0f})'.format(p,(p/100)*df.status.count()),
                                            figsize=(8,8)
                                            )
            #grafico_status.legend(loc="center left", bbox_to_anchor = (1, 0.5))
            plt.tight_layout()
            st.pyplot(grafico_status.figure)

            # BENS ACAUTELADOS
            st.subheader('Assinatura de bens acautelados')
            bens_acautelados = df[df.status == 'ACAUTELADO']
            bens_acautelados = bens_acautelados.groupby('validado eletron')['validado eletron'].count()
            plt.clf()
            grafico_bens_acautelados = bens_acautelados.plot(kind='pie',
                                                             x = bens_acautelados.index,
                                                             y = bens_acautelados,
                                                            title = f'Proporção de bens acautelados por validação de assinatura ({st.session_state.titulo_grafico})',
                                                            autopct= lambda p: '{:.2f}%({:.0f})'.format(p,(p/100)*bens_acautelados.sum(),),
                                                            figsize=(10,10))
            plt.tight_layout()
            st.pyplot(grafico_bens_acautelados.figure)

            # VALORES NULOS
            df_null = df.isnull().sum()/len(df)*100
            df_null = df_null[df_null > 0]
            st.subheader(f'{df_null.shape[0]} colunas com valores nulos')
            df_null = df_null.sort_values(ascending=False)
            # Cria o gráfico de barras e obtém o objeto Axes (eixos)
            plt.clf()
            grafico_colunas_vazias = df_null.plot(kind='barh')
            # Adiciona os rótulos de porcentagem às barras
            grafico_colunas_vazias.bar_label(grafico_colunas_vazias.containers[0], fmt='%.2f%%')
            # Ajusta o layout para garantir que os rótulos não sejam cortados
            plt.tight_layout()
            st.pyplot(grafico_colunas_vazias.figure, width='stretch')
            
            st.divider()

            
            # Dados estatísticos por coluna
            st.subheader('Filtrar colunas')
            coluna = st.selectbox('Selecione a coluna', df.columns)
            col1,col2,col3 = st.columns(3)
            col1.subheader(f'**Tipo de dado:** {df[coluna].dtype}')
            try:
                col1.metric('% de valores nulos', round(df_null[coluna],2))
            except KeyError:
                col1.metric('% de valores nulos', 0.00)
            
            if (df[coluna].dtype == 'int64' or df[coluna].dtype == 'float64'):
                col3.metric('Mínimo', round(df[coluna].min(),2))
                col2.metric('Mediana', round(df[coluna].median(),2))
                col2.metric('Média', round(df[coluna].mean(),2))
                col3.metric('Máximo', round(df[coluna].max(),2))
            

            st.divider()    


            # -- TAMANHOS DE ARQUIVO --
            st.subheader('Comparativo de arquivos iniciais e finais')
            dict_resultados = json.load(open(f'data_silver/resultados_{st.session_state.selected_ug}.json'))
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric('Inicial xls em MB', round(dict_resultados['tamanho_inicial_mb'],2))
            col2.metric('Final csv em MB', round(dict_resultados['tamanho_final_csv_mb'],2),
                        f"{round((dict_resultados['tamanho_final_csv_mb'] - dict_resultados['tamanho_inicial_mb'])/dict_resultados['tamanho_inicial_mb']*100,2)}%",
                            delta_color='inverse')
            col3.metric('Final json em MB', round(dict_resultados['tamanho_final_json_mb'],2),
                        f"{round((dict_resultados['tamanho_final_json_mb'] - dict_resultados['tamanho_inicial_mb'])/dict_resultados['tamanho_inicial_mb']*100,2)}%",
                            delta_color='inverse')
            col4.metric('Final xlsx em MB', round(dict_resultados['tamanho_final_xlsx_mb'],2),
                        f"{round((dict_resultados['tamanho_final_xlsx_mb'] - dict_resultados['tamanho_inicial_mb'])/dict_resultados['tamanho_inicial_mb']*100,2)}%",
                        delta_color='inverse')

            st.subheader('Compara tamanhos de arquivos em mb')
            fig, ax = plt.subplots(figsize=(10, 6))
            tamanhos_arquivo = [dict_resultados['tamanho_inicial_mb'], 
                                dict_resultados['tamanho_final_csv_mb'],
                                dict_resultados['tamanho_final_json_mb'],
                                dict_resultados['tamanho_final_xlsx_mb']]
            labels = ['Original (xlsx)', 'Depois (csv)', 'Depois (json)', 'Depois (xlsx)']
            ax.bar(labels, tamanhos_arquivo)
            ax.set_xlabel('Formato do Arquivo')
            ax.set_ylabel('Tamanho do Arquivo (MB)')
            ax.set_title(f'Tamanho do Arquivo antes e depois do processamento ({st.session_state.selected_ug})')
            for i, tamanho in enumerate(tamanhos_arquivo):
                ax.text(i, tamanho + 0.5, f'{tamanho:.2f} MB', ha='center', va='bottom')
            st.pyplot(fig, width='stretch')

            # -- QUANTIDADES DE COLUNA --
            st.subheader('Quntidade de colunas')
            col_inicial, col_final = st.columns(2)
            col_inicial.metric('Quantidade inicial', dict_resultados['qtde_colunas_inicial'])    
            col_final.metric('Quantidade final', dict_resultados['qtde_colunas_final'],
                        f"{round((dict_resultados['qtde_colunas_final'] - dict_resultados['qtde_colunas_inicial'])/dict_resultados['qtde_colunas_inicial']*100,2)}%",
                        delta_color='inverse')

        else:
            st.warning('Base de dados ainda não processada.')
            
    else:
        st.warning('Por favor, faça o login na página inicial.')
    

pagina_principal()
import json
import os

from datetime import datetime
import streamlit as st
import pandas as pd
import altair as alt
import matplotlib.pyplot as plt  # criar gráficos como imagem
import seaborn as sns


def retornar():
    botao_credenciamento = st.button('Ir para Credenciamento', width='stretch', key='botao_credenciamento')
    if botao_credenciamento:
        st.switch_page('menu_principal.py')

def trocar_ug():
    if st.session_state.username == 'admin':
        botao_trocar_ug = st.button('Trocar UG', width='stretch')
        if botao_trocar_ug:
            st.session_state.selected_ug = st.selectbox("Trocar UG:", options=['Selecione uma UG'] + st.session_state.lista_todas_ugs)


def pagina_principal():
    """Configura as propriedades da página no Streamlit."""
    st.set_page_config(
        page_title='Status da Base de dados',
        page_icon='📊',
        layout='wide')
    retornar()
    
    if 'selected_ug' in st.session_state:
        trocar_ug()
        # CARGA DE ARQUIVO CSV  
        if os.path.exists(f'data_bronze/lista_bens-processado-{st.session_state.selected_ug}.csv'):
            st.title(f'Status do levantamento da UG {st.session_state.selected_ug}')
            df = pd.read_csv(f'data_bronze/lista_bens-processado-{st.session_state.selected_ug}.csv', dtype=str)
            df = df[df['status'].isin(['EFETIVADO','ACAUTELADO','BEM NÃO LOCALIZADO','EM PROCESSO DE ALIENAÇÃO'])]
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
                st.session_state.titulo_grafico = filtro_grupo
            filtro_unidade = col_unidade.multiselect('Filtro por unidade patrimonial', df['unidade responsavel material'].unique())
            if filtro_unidade:
                df = df[df['unidade responsavel material'].isin(filtro_unidade)]
                titulo_sigla = df['sigla'].unique()[0]
                st.session_state.titulo_grafico = titulo_sigla
                

            # -- LEVANTAMENTO --
            col1, col2 = st.columns(2)
            qtd_bens = df.shape[0]
            ano_atual = str(datetime.today().year)
            qtd_inventariados = len(df[df['ano do levantamento'] == ano_atual])
            col1.metric('Qtde. de bens', qtd_bens)
            col2.metric('',None)
            col1.metric('Total inventariados', qtd_inventariados)
            col2.metric('Perc. Inventariado', f'{round(qtd_inventariados/qtd_bens*100,2)}%')
            col1.metric('Total não inventariados', qtd_bens-qtd_inventariados)
            col2.metric('Perc. não Inventariado', f'{round((1-qtd_inventariados/qtd_bens)*100,2)}%')

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

            # Levantamento por grupo (por unidade)
            

            # por valor
            
            # Levantamento por unidade
            if not filtro_unidade:
                st.subheader('Quantidade de bens levantados por Unidade')
                contagem = df.groupby(['sigla', 'ano do levantamento']).size().unstack()
            else:
                st.subheader('Quantidade de bens levantados por Localidade')
                contagem = df.groupby(['localidade', 'ano do levantamento']).size().unstack()
            contagem['soma'] = contagem.sum(axis=1).fillna(0).astype(int)
            contagem['percentual'] = contagem[ano_atual]/contagem['soma']
            contagem['percentual'] = contagem['percentual'].mul(100).round(1).fillna(0)
            contagem['soma'] = contagem['soma'].astype(str)
            contagem['percentual'] = contagem['percentual'].astype(str)
            if not filtro_unidade:
                contagem['sigla'] = contagem.index.get_level_values('sigla')
                contagem['sigla'] = contagem['sigla'] + ' (' + contagem['soma'].astype(str) + ' / ' + contagem['percentual'].astype(str) + '%)'
            else:
                contagem['localidade'] = contagem.index.get_level_values('localidade')
                contagem['localidade'] = contagem['localidade'] + ' (' + contagem['soma'].astype(str) + ' / ' + contagem['percentual'].astype(str) + '%)'
            contagem = contagem.drop(columns=['percentual'])
            colunas_numericas = contagem.select_dtypes(include=['float64', 'int64']).columns
            contagem['total'] = contagem[colunas_numericas].sum(axis=1)
            contagem = contagem.sort_values(by='total', ascending=False)
            contagem = contagem.drop(columns=['total'])
            st.write('**Legenda:** Unidade (Quantidade total de bens / percentual inventariado)')
            # Plotar o gráfico de barras empilhadas
            if not filtro_unidade:
                grafico_contagem = contagem.plot(kind='barh',
                                                x = 'sigla',
                                                stacked=True,
                                                title=f'Bens ativos por setor e ano do último levantamento na {st.session_state.titulo_grafico}',
                                                colormap = 'RdBu')
            else:
                grafico_contagem = contagem.plot(kind='barh',
                                                x = 'localidade',
                                                stacked=True,
                                                title=f'Bens ativos por setor e ano do último levantamento na {st.session_state.titulo_grafico}',
                                                colormap = 'RdBu')
                
            grafico_contagem.set_ylabel('Setor (% levantado)')
            grafico_contagem.set_xlabel('Quantidade de bens ativos')
            grafico_contagem.set_xticklabels(grafico_contagem.get_xticklabels(), rotation=45)
            grafico_contagem.figure.set_size_inches(15, 10)
            st.pyplot(grafico_contagem.figure)
            st.warning("Levantamentos com último ano 2010 são aqueles nunca levantados")


            # gráfico por valor
            # quantidade
            # valor
            
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
                                            legend = True,
                                            #labels= None, # nomes no gráfico
                                            autopct= lambda p: '{:.2f}%({:.0f})'.format(p,(p/100)*df.status.count()),
                                            figsize=(10,10)
                                            )
            grafico_status.legend(loc="center left", bbox_to_anchor = (1, 0.5))
            plt.tight_layout()
            st.pyplot(grafico_status.figure, width='stretch')

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
            st.pyplot(grafico_bens_acautelados.figure, width='stretch')

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

            
           
            #boxplot de valor_atual_tratado por sigla
            st.subheader('Boxplot de valor atual tratado por grupo de material')
            df_boxplot = df[['grupo de material','valor']].dropna()
            df_boxplot['valor_atual_tratado'] = df_boxplot['valor'].astype(float)
            grafico_boxplot = alt.Chart(df_boxplot).mark_boxplot().encode(
                y=alt.Y('grupo de material', sort='-x'),
                x='valor',
                #tooltip=None
            ).properties(
                width=700,
                height=400
            )
            st.altair_chart(grafico_boxplot, width='stretch')

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


            #compara tamanho em MB de planilha data e data_bronze
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

            col2.metric('Quantidade de colunas iniciais', dict_resultados['qtde_colunas_inicial'])    
            col3.metric('Quantidade de colunas finais', dict_resultados['qtde_colunas_final'],
                        f"{round((dict_resultados['qtde_colunas_final'] - dict_resultados['qtde_colunas_inicial'])/dict_resultados['qtde_colunas_inicial']*100,2)}%",
                        delta_color='inverse')

        else:
            st.warning('Base de dados ainda não processada.')
            
    else:
        st.warning('Por favor, selecione uma UG válida na página de credenciamento.')
    

pagina_principal()
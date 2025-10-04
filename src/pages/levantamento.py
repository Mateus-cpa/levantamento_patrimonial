import streamlit as st
import pandas as pd
import datetime as dt
import levantamento.gerar_etiqueta as etiq
import os

#from pages.relatorio_levantamento import gerar_pdf_levantamento


#Funções auxiliares
def obter_localidades():
    localidades = pd.read_csv(f"data_silver/localidades_{st.session_state.selected_ug}.csv").values.tolist()
    return localidades

def adicionar_ao_inventario(id = int):
    """
    Adiciona o ID do patrimônio ao inventário.

    Args:
        id: O ID do patrimônio a ser adicionado.
    """
    if 'df_inventario' not in st.session_state:
        st.session_state.df_inventario = pd.DataFrame(columns=['num tombamento'])
    if not id in st.session_state.df_inventario['num tombamento'].values:
        st.session_state.df_inventario = pd.concat([st.session_state.df_inventario, pd.DataFrame({'num tombamento': [id]})], ignore_index=True)
        st.success(f"Patrimônio {id} adicionado ao inventário.")
    else:
        st.warning(f"Patrimônio {id} já está no inventário.")
    # adicionar usuario, data e localidade
    st.session_state.df_inventario.at[st.session_state.df_inventario.index[-1], 'usuario'] = st.session_state.username
    st.session_state.df_inventario.at[st.session_state.df_inventario.index[-1], 'data_inventario'] = dt.datetime.now()
    if type(st.session_state.localidade_escolhida) == list:
        st.session_state.df_inventario.at[st.session_state.df_inventario.index[-1], 'localidade_inventario'] = st.session_state.localidade_escolhida[0]
    else:
        st.session_state.df_inventario.at[st.session_state.df_inventario.index[-1], 'localidade_inventario'] = st.session_state.localidade_escolhida
    #colocar condição de não adicionar bem com status alienado ou já inventariado no ano

    

def escolhe_dentre_resultados(df, index):
    """
    Exibe uma lista de resultados encontrados e permite ao usuário escolher quais deles.

    Args:
        index: Lista de índices dos resultados encontrados.
    """
    #lista de ano do levantamento
    #lista_anos = df['ano do levantamento'].unique().dropna().sort().tolist()

    col1, col2 = st.columns(2)
    with col1:
        filtro_ativos = col1.button('Selecionar somente os bens ativos')
        if filtro_ativos:
            df = df[df['status'].isin(['EFETIVADO','ACAUTELADO','BEM NÃO LOCALIZADO','EM PROCESSO DE ALIENAÇÃO'])]
    with col2:
        st.write(f"**{len(df)} resultados encontrados:**")
    for index, row in df.iterrows():
        # 1. os demais casos
        if (row['status'] not in ['ALIENADO', 'ANULADO', 'DESMEMBRADO']) and (row['ano do levantamento'] != dt.date.today().year): #status em verde
            if st.checkbox(f"{row['status']} - {row['num tombamento']} - {row['denominacao']} - {row['marca_total']} - {row['modelo_total']} - {row['serie_total']} - {row['localidade']} - {row['acautelado para']} - {row['ultimo levantamento']}",
                        key=f"select_{index}"):
                adicionar_ao_inventario(int(row['num tombamento']))
        # 2. os já inventariados em laranja
        elif (row['ano do levantamento'] == dt.date.today().year): 
            st.markdown(f"{row['status']} - {row['num tombamento']} - {row['denominacao']} - {row['marca_total']} - {row['modelo_total']} - {row['serie_total']} - {row['localidade']} - {row['acautelado para']} - <span style='color:orange'>{row['ultimo levantamento']}</span>", unsafe_allow_html=True)
            if st.checkbox(f"Adicionar {row['num tombamento']} já inventariado ao inventário?", key=f"select_{index}"):
                adicionar_ao_inventario(int(row['num tombamento']))
        # 3. os alienados em vermelho
        else: 
            st.markdown(f"<span style='color:red'>{row['status']}</span> - {row['num tombamento']} - {row['denominacao']} - {row['marca_total']} - {row['modelo_total']} - {row['serie_total']} - {row['localidade']} - {row['acautelado para']} - {row['ultimo levantamento']}", unsafe_allow_html=True)
        st.divider()

    return index

def encontrar_indice_por_id(df: pd.DataFrame, id_busca: str) -> list[int] | None:
    """
    Busca um ID em diferentes colunas de um DataFrame e retorna o(s) índice(s) da linha correspondente.

    A busca é realizada nas colunas 'num tombamento', 'tombo_antigo' e 'serie_total'.

    Args:
        df: O DataFrame pandas onde a busca será realizada.
        id_busca: A string ID a ser procurada.

    Returns:
        Uma lista de índices onde o ID foi encontrado. Retorna None se o ID não for encontrado.
    """
    try:
        # Busca em todas as colunas relevantes
        df.set_index('num tombamento', inplace=True, drop=False)
        df_resultados = df[
            (df['num tombamento'].astype(str) == str(id_busca)) |
            (df['tombo_antigo'].astype(str) == str(id_busca)) |
            (df['serie_total'].astype(str) == str(id_busca))
        ]
        
        if df_resultados.empty:
            st.warning("Patrimônio não encontrado.")
            return None

        # Obtém os índices dos resultados encontrados
        indices = df_resultados.index.tolist()
        if len(indices) == 1:
            # Adiciona diretamente ao inventário se houver apenas um resultado
            adicionar_ao_inventario(indices[0])
            return indices[0]
        else:
            escolhe_dentre_resultados(index = indices, df = df_resultados)

    except KeyError as e:
        st.error(f"Erro ao acessar colunas: {e}")
        return None
    except Exception as e:
        st.error(f"Ocorreu um erro inesperado: {e}")
        return None

def exibir_detalhes_patrimonio(df, resultados_busca):
    """
    Exibe os detalhes do patrimônio encontrado no DataFrame, se 1 resultado, 
    ou uma lista para seleção, se vários resultados.

    Args:
        df: O DataFrame pandas onde a busca será realizada.
        id_busca: O ID do patrimônio a ser buscado.
    """
    df.set_index('num tombamento', inplace=True, drop=False)
    if resultados_busca is None:
        resultados_busca = []
    if isinstance(resultados_busca, int):
        resultados_busca = [resultados_busca]
    if len(resultados_busca) > 0:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.write(f"**Nº Patrimônio:** {df.loc[resultados_busca,'num tombamento'].values[0]}")
            if pd.notna(df.loc[resultados_busca,'tombo_antigo'].values[0]):
                st.write(f"**Tombo Antigo:** {df.loc[resultados_busca,'tombo_antigo'].values[0]}")
            st.write(f"**Nº Serial:** {df.loc[resultados_busca,'serie_total'].values[0]}")
        with col2:
            st.write(f"**Denominação:** {df.loc[resultados_busca,'denominacao'].values[0]}")
            if df.loc[resultados_busca,'localidade'].values[0] == st.session_state['localidade_escolhida'][0]:
                st.write(f"**Divergência de localidade:** :green[{'não'}]")
            else:
                st.write(f"**Divergência de localidade:** :red[{'SIM'}]")
            if df.loc[resultados_busca,'localidade'].values[0] == st.session_state['localidade_escolhida'][0]:
                st.write(f"**Localidade:** :green[{df.loc[resultados_busca,'localidade'].values[0]}]")
            else:
                st.write(f"**Localidade:** :red[{df.loc[resultados_busca,'localidade'].values[0]}]")
            
            
        with col3:
            st.write(f"**Marca:** {df.loc[resultados_busca,'marca_total'].values[0]}")
            if pd.notna(df.loc[resultados_busca,'modelo_total'].values[0]):
                st.write(f"**Modelo:** {df.loc[resultados_busca,'modelo_total'].values[0]}")
            if df.loc[resultados_busca,'ano do levantamento'].values[0] == dt.date.today().year:
                st.write(f"**Levantamento:** :red[{df.loc[resultados_busca,'ultimo levantamento'].values[0]}]")
            else:
                st.write(f"**Levantamento:** :green[{df.loc[resultados_busca,'ultimo levantamento'].values[0]}]")
            st.write(f"**Valor:** R$ {round(df.loc[resultados_busca,'valor'].values[0],2)}")
            
                
        with col4:
            if df.loc[resultados_busca,'status'].values[0] == 'ALIENADO':
                st.write(f"**Status:** :red[ALIENADO]")
            else:
                st.write(f"**Status:** :green[{df.loc[resultados_busca,'status'].values[0]}]")
            if df.loc[resultados_busca,'status'].values[0] == 'ACAUTELADO':
                st.write(f"**Acautelado para:** {df.loc[resultados_busca,'acautelado para'].values[0]}")
            st.write(f"**Descrição:** {df.loc[resultados_busca,'especificacoes'].values[0]}")
        
    
    else:
        # Se não houver resultados, exibir mensagem
        st.write("Patrimônio não encontrado.")
 
def limpar_session_state(key):
    """
    Limpa o estado da sessão para a chave especificada.

    Args:
        key: A chave do estado da sessão a ser limpa.
    """
    if key in st.session_state:
        
        st.session_state[key] = None
        #st.success(f"Estado da sessão para '{key}' limpo.")
    else:
        st.warning(f"Chave '{key}' não encontrada no estado da sessão.")

# --- Tela de Input de Dados ---
def tela_input_dados(df):

    # -- configurações iniciais --
    colunas_de_interesse = ['denominacao', 'status', 'marca_total', 'modelo_total', 'serie_total', 'localidade','acautelado para', 'tombo_antigo', 'ultimo levantamento', 'valor','especificacoes','num tombamento']
    st.title("Levantamento Patrimonial - " + st.session_state.selected_ug)
    if 'df_inventario' not in st.session_state:
        st.session_state.df_inventario = pd.DataFrame(columns=['num tombamento'])
    if 'gerar_etiquetas' not in st.session_state:
        st.session_state.gerar_etiquetas = []
    localidades = obter_localidades()
    
    # Informar localidade e acompanhamento inventario
    with st.expander("Informar Localidade e Acompanhamento do Inventário", expanded=True):
        localidade = st.segmented_control('Inventariar:',['Carregar localidade existente','Adicionar localidade'], key='localidade', selection_mode="single", default="Adicionar localidade") 
        if localidade == 'Carregar localidade existente':
            localidade_escolhida = st.selectbox("Localidade", ['Escolha uma localidade'] + localidades, key="localidade_escolha")
        
        if localidade == 'Adicionar localidade':
            col1, col2 = st.columns(2)
            unidade_patrimonial = col1.text_input("Unidade Patrimonial", key="unidade_patrimonial")
            localidade_escolhida = col2.text_input("Localidade", key="localidade_nova")
            localidade_escolhida = f'{unidade_patrimonial} - {localidade_escolhida}'
        
        st.session_state.localidade_escolhida = localidade_escolhida
        st.session_state.acompanhamento = st.text_input("Acompanhamento inventário")
        
    
    
    # -- Inserção de dados --
    st.subheader("Inserir Dados do Patrimônio")
    busca = st.segmented_control('Buscar por:', ['ID', 'Cautela', 'Características'], key="busca", selection_mode="single", default="ID")
    id, index_cautela, index_caracteristicas = '', [], []
    # -- Campos de entrada --
    if busca == 'ID':
        id = st.text_input("Id. do Patrimônio (Nº Patrimônio, Tombo Antigo ou Nº Serial)", 
                        key="id_input")
                        #, on_change=limpar_session_state, args=('id_input',))
        
    if busca == 'Cautela':
        detentor = st.selectbox("Adicionar bens de detentor", df['acautelado para'].unique(), key="detentor")
        index_cautela = df[df['acautelado para'] == detentor].index.tolist()
    if busca == 'Características':
        st.info('Digite "Não informado" para buscar por itens sem essa característica.')
        col1, col2 = st.columns(2)
        with col1:
            grupo = st.selectbox("Grupo de material",['Escolha um grupo'] + df['grupo de material'].fillna('Não informado').dropna().unique().tolist(), key="grupo")
            if grupo != 'Escolha um grupo':
                df = df[df['grupo de material'].str.contains(grupo, case=False)]
        with col2:
            subgrupo = st.selectbox("Subgrupo de material",['Escolha um subgrupo'] + df['subgrupo de material'].fillna('').dropna().unique().tolist(), 
                                    accept_new_options=True,
                                    key="subgrupo", 
                                    index=0)
            if subgrupo != 'Escolha um subgrupo':
                df = df[df['subgrupo de material'].str.contains(subgrupo, case=False)]
        with col1:
            marca = st.selectbox("Marca",['Escolha uma marca'] + df['marca_total'].fillna('Não informado').dropna().unique().tolist(), 
                                    accept_new_options=True,
                                    key="marca", 
                                    index=0)
            if marca != 'Escolha uma marca':
                df = df[df['marca_total'].str.contains(marca, case=False, na=False)]
        with col2:
            modelo = st.selectbox("Modelo",['Escolha um modelo'] + df['modelo_total'].fillna('Não informado').dropna().unique().tolist(), 
                                    accept_new_options=True,
                                    key="modelo", 
                                    index=0)
            if modelo != 'Escolha um modelo':
                df = df[df['modelo_total'].str.contains(modelo, case=False, na=False)]

        caracteristicas = st.selectbox("Características",
                                        ['Escolha uma característica'] + df['caracteristicas'].dropna().unique().tolist(), 
                                        accept_new_options=True,
                                        key="caracteristicas", 
                                        index=0)
        if caracteristicas != 'Escolha uma característica':
            index_caracteristicas = df[df['caracteristicas'].str.contains(caracteristicas[0], case=False)].index.tolist()
    
    # -- Resultados de busca -- 
    st.subheader("Resultados da Busca")
    resultados_busca = None
    if len(index_cautela) > 0: #retorna resultados por cautela
        resultados_busca = escolhe_dentre_resultados(index = index_cautela, df = df.loc[index_cautela])
        detentor = 'nan'
    elif len(index_caracteristicas) > 0: #retorna resultados por características
        resultados_busca = escolhe_dentre_resultados(index = index_caracteristicas, df = df.loc[index_caracteristicas])
    elif id != '':
        resultados_busca = encontrar_indice_por_id(df=df, id_busca=id)
        exibir_detalhes_patrimonio(df, resultados_busca)
    
    
    st.divider()
    
    
    
    # -- Seção Bens inventariados --
    st.subheader(f"{len(st.session_state.df_inventario)} Bem(ns) Levantado(s) em {st.session_state.localidade_escolhida[0]}")
    if len(st.session_state.df_inventario) == 0:
        st.warning('Nenhum bem foi adicionado ao inventário ainda.')
    else:
        df_inventario = st.session_state.df_inventario.copy()
        if df_inventario.index.name == 'num tombamento':
            df_inventario.reset_index(drop=True, inplace=True)
        df_merge = df[colunas_de_interesse].copy()
        if df_merge.index.name == 'num tombamento':
            df_merge.reset_index(drop=True, inplace=True)
        df_inventario = df_inventario.merge(df_merge, left_on='num tombamento', right_on='num tombamento', how='left')
        df_inventario.drop(columns=['usuario','data_inventario','localidade_inventario'], inplace=True)
        # colocar ' ' e 'num tombamento' na primeira coluna
        df_inventario[' '] = False
        cols = df_inventario.columns
        first_cols = [' ','num tombamento'] 
        other_cols = [col for col in cols if (col not in first_cols)]
        cols = first_cols + other_cols
        df_etiquetas = st.data_editor(df_inventario, 
                                      use_container_width=True,
                                      hide_index=True,
                                      column_order=cols,)
        col_etiq, col_excluir, col_3 = st.columns(3)
        if col_etiq.button('Gerar etiquetas'):
            st.session_state.gerar_etiquetas = df_etiquetas.loc[df_etiquetas[' '] == True].index.tolist()
        if col_excluir.button('Excluir itens'):
            itens_excluir = df_etiquetas.loc[df_etiquetas[' '] == True, 'num tombamento'].tolist()
            st.session_state.df_inventario = st.session_state.df_inventario[~st.session_state.df_inventario['num tombamento'].isin(itens_excluir)]
            st.success(f"Itens {itens_excluir} excluídos do inventário.")
            st.experimental_rerun()
        
    st.divider()
    
    # -- Verificação de duplicidade --
    if st.session_state.df_inventario['num tombamento'].duplicated().any():
        st.warning("Existem itens duplicados no inventário. Verifique os IDs.")
        # Exibir onde num tombamento estiver 
        duplicados = st.session_state.df_inventario['num tombamento'][st.session_state.df_inventario['num tombamento'].duplicated(keep=False)].tolist()
        st.write("Itens duplicados:", duplicados)
        
        st.divider()
    
    # -- Seção bens a inventariar --
    df_localidade = df[df['localidade'].isin(list(st.session_state.localidade_escolhida))]
    df_localidade.set_index('num tombamento', inplace=True,drop=False)
    # excluir bens alienados, anulados ou desmembrados
    df_localidade = df_localidade[~df_localidade['status'].isin(['ALIENADO', 'ANULADO', 'DESMEMBRADO'])]
    #excluir os bens que já foram inventariados
    df_localidade = df_localidade[~df_localidade['num tombamento'].isin(st.session_state.df_inventario['num tombamento'].values)]
    st.session_state.df_localidade = df_localidade
    st.subheader(f"{df_localidade.shape[0]} Bem(ns) a inventariar em {st.session_state.localidade_escolhida[0]}")    
    st.dataframe(df_localidade[colunas_de_interesse], 
                use_container_width=True)

    st.divider()
    
    # -- Gerar etiquetas --
    if len(st.session_state.gerar_etiquetas) > 0:
        st.subheader("Etiquetas a gerar:")
        # permitir selecionar vários itens de df_inventario e adicionar na lista st.session_state['etiquetas'] e após botão de imprimir etiquetas
        st.dataframe(df_inventario.loc[st.session_state.gerar_etiquetas,colunas_de_interesse], use_container_width=True)
        if st.button("Imprimir etiquetas"):
            etiq.gerar_etiquetas(st.session_state.gerar_etiquetas, st.session_state.localidade_escolhida[0])
            st.success("Etiquetas impressas com sucesso!")
        st.divider()

    # -- Concluir levantamento --
    botao_concluir = st.button("Concluir Levantamento")
    if botao_concluir:
        # Transformar st.session_state.df_inventario em txt
        localidade_final = st.session_state.localidade_escolhida[0].replace('/','-')
        path_destino = f'data_gold/{localidade_final}.txt'
        path_destino = path_destino.replace("'", "").replace("[", "").replace("]", "")
        with open(path_destino, 'w') as f:
            for item in st.session_state.df_inventario['num tombamento']:
                f.write(f"{item}\n")    
        with open(path_destino, 'r') as f:        
            conteudo_arquivo = f.read()    
        st.download_button(
            label="Baixar inventário",
            data=conteudo_arquivo,
            file_name=path_destino.split('/')[-1],
            mime='text/plain',
            #icon=':download:'
        )
        botao_assinar = st.button('Assinar e Gerar Relatório em PDF', key='botao_assinar')
        if botao_assinar:
            #oletar assinatura por caneta/desenho
            assinatura = st.canvas()
            #if assinatura.image_data is not None:
                # gerar pdf com dados do inventário
                #gerar_pdf_levantamento()
            # baixar pdf sem alterar págia
            #st.switch_page('pages/relatorio_levantamento.py')
        
        
    
#configurar página wide
st.set_page_config(
    page_title='Levantamento Patrimonial',
    page_icon='📝',
    layout='wide')
st.session_state.concluir_levantamento = False
st.session_state.botao_assinar = False
if 'is_authenticated' not in st.session_state:
    st.session_state.is_authenticated = False
if 'selected_ug' not in st.session_state:
    st.session_state.selected_ug = None
if ((st.session_state.is_authenticated == False) or (st.session_state.selected_ug == None)):
    botao_retornar = st.button('Retornar para Credenciamento')
    if botao_retornar:
        st.switch_page('menu_principal.py')
    st.warning('Por favor, faça o login na página inicial.')
elif not os.path.exists(f'data_bronze/lista_bens-processado-{st.session_state.selected_ug}.csv'):
    st.warning(f"Por favor, solicite ao administrador atualizar base de dados da UG {st.session_state.selected_ug}.")
else:
    df = pd.read_csv(f'data_bronze/lista_bens-processado-{st.session_state.selected_ug}.csv')
    tela_input_dados(df)
    # A autenticação deve ser implementada antes de chamar a função de input de dados
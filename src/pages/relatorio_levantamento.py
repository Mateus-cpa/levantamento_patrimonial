import os
import pandas as pd
import streamlit as st
import datetime as dt
import numpy as np
import tempfile
import math

import cv2       
from fpdf import FPDF
from streamlit_drawable_canvas import st_canvas

def coletar_assinatura():
    """
    Coleta a assinatura do usuário usando um canvas de desenho.
    """
    canvas_result = st_canvas(
        fill_color="rgba(255, 165, 0, 0.3)",  # Cor de preenchimento
        stroke_width=2,
        stroke_color="#000000",
        background_color="#FFFFFF",
        height=150,
        width=400,
        drawing_mode="freedraw",
        key="canvas",
    )
    if canvas_result.image_data is not None:
        st.session_state.assinatura = canvas_result.image_data
        #st.image(st.session_state.assinatura)
    return canvas_result

# --- FUNÇÕES AUXILIARES ---

def draw_dynamic_table(pdf, data_frame, larguras, colunas, alinha):
    """
    Desenha o cabeçalho e os dados de uma tabela com altura de linha dinâmica e 
    gerenciamento de quebra de página.
    """
    
    # Alturas base para cálculo
    h_data_base = 5.5
    h_header_base = 5.5
    h_min_header = 7
    h_min_data = 6
    cell_padding = 2 
    FOOTER_HEIGHT = 15 # Margem de segurança para o rodapé

    # --- FUNÇÃO INTERNA PARA DESENHAR O CABEÇALHO (Para Reutilização) ---
    def draw_header_block(pdf, colunas, larguras, h_header_base, h_min_header):
        pdf.set_font('Arial', 'B', 10)
        
        # CÁLCULO DA ALTURA MÁXIMA PARA O CABEÇALHO (Repetido para garantir o cálculo em novas páginas)
        max_h_header_local = h_min_header
        for i, col in enumerate(colunas):
            largura_coluna = larguras[i] - cell_padding
            largura_texto = pdf.get_string_width(str(col))
            num_linhas = math.ceil(largura_texto / largura_coluna) if largura_coluna > 0 else 1 
            h_calculada = num_linhas * h_header_base
            max_h_header_local = max(max_h_header_local, h_calculada)
        
        y_start_header = pdf.get_y()
        x_start = pdf.get_x()
        largura_total_linha = sum(larguras)
        
        # Borda da linha do cabeçalho
        pdf.cell(largura_total_linha, max_h_header_local, '', 1, 1) 
        pdf.set_xy(x_start, y_start_header) 

        current_x = x_start
        for i, col in enumerate(colunas):
            pdf.set_xy(current_x, y_start_header)
            pdf.multi_cell(
                larguras[i], 
                h_header_base, 
                str(col), 
                0, # Sem borda
                align='C'
            )
            current_x += larguras[i]
        pdf.set_xy(x_start, y_start_header + max_h_header_local)
        
        return max_h_header_local # Retorna a altura para uso na quebra de página
    # --- FIM DA FUNÇÃO INTERNA ---

    # 1. Desenhar o Cabeçalho (Primeira vez)
    max_h_header = draw_header_block(pdf, colunas, larguras, h_header_base, h_min_header)

    # 2. Desenhar o Corpo da Tabela (Dados)
    pdf.set_font('Arial', '', 10)
    largura_total_linha = sum(larguras)
    
    for index, row in data_frame.iterrows():
        max_h_data = h_min_data
        
        # CÁLCULO DA ALTURA MÁXIMA PARA A LINHA DE DADOS
        for i, item in enumerate(row):
            texto = str(item)
            largura_coluna = larguras[i] - cell_padding
            largura_texto = pdf.get_string_width(texto)
            num_linhas = math.ceil(largura_texto / largura_coluna) if largura_coluna > 0 else 1 
            h_calculada = num_linhas * h_data_base
            max_h_data = max(max_h_data, h_calculada)
        
        # --- VERIFICAÇÃO DE QUEBRA DE PÁGINA ---
        # Se a linha atual + rodapé for maior que o espaço restante, quebra a página.
        if pdf.get_y() + max_h_data + FOOTER_HEIGHT > pdf.h - pdf.b_margin:
            pdf.add_page()
            # Redesenha o cabeçalho na nova página
            draw_header_block(pdf, colunas, larguras, h_header_base, h_min_header)
            pdf.set_font('Arial', '', 10) # Volta para a fonte dos dados
        # --------------------------------------
        
        # DESENHO DA LINHA DE DADOS
        y_start_data = pdf.get_y()
        x_start = pdf.get_x()
        
        # Borda da linha de dados
        pdf.cell(largura_total_linha, max_h_data, '', 1, 1) 
        pdf.set_xy(x_start, y_start_data) 

        current_x = x_start
        for i, item in enumerate(row):
            pdf.set_xy(current_x, y_start_data)
            pdf.multi_cell(
                larguras[i], 
                h_data_base, 
                str(item), 
                0, # Sem borda
                align=alinha[i]
            )
            current_x += larguras[i]
            
        pdf.set_xy(x_start, y_start_data + max_h_data)

def gerar_pdf_levantamento(
    levantado,
    localidade,
    acompanhamento,
    matricula,
    assinatura,
    responsavel,
    data_levantamento,
    nao_levantados=None,
    ug=None
):
    """
    Gera um relatório em PDF do levantamento patrimonial com tabelas dinâmicas.
    """
    # 0. Preparação de Dados e Título
    titulo_relatorio = "Relatório de Levantamento"
    data_geracao = data_levantamento.strftime("%d de %B de %Y")
    if nao_levantados is None:
        nao_levantados = pd.DataFrame()
    if ug is None:
        ug = ""
    # Se todos dados de 'acautelado para' forem NaN, remover a coluna
    if levantado['acautelado para'].isna().all():
        levantado = levantado.drop(columns=['acautelado para'], errors='ignore')
    levantado = levantado.drop(columns=['especificacoes', 'localidade'], errors='ignore')
    # Capitalização e formatação dos nomes das colunas
    for i, coluna in enumerate(levantado.columns):
        coluna = coluna.capitalize().replace('_total', '').replace('_', '')
        levantado.columns.values[i] = coluna
    if nao_levantados['acautelado para'].isna().all():
        nao_levantados = nao_levantados.drop(columns=['acautelado para'], errors='ignore')
    nao_levantados = nao_levantados.drop(columns=['especificacoes', 'localidade'], errors='ignore')
    

    for i, coluna in enumerate(nao_levantados.columns):
        coluna = coluna.capitalize().replace('_total', ' ').replace('_', ' ')
        nao_levantados.columns.values[i] = coluna
    # Retirar linhas se ano de 'ultimo levantamento' de não_levantados forem ano atual
    ano_atual = dt.datetime.now().year
    nao_levantados = nao_levantados[~nao_levantados['Ultimo levantamento'].astype(str).str.endswith(str(ano_atual))]

    # 1. Conversão de Valor para Numérico
    if 'Valor' in levantado.columns:
        levantado['Valor'] = pd.to_numeric(
            levantado['Valor'].astype(str).str.replace(',', '.', regex=False), # Se houver vírgula decimal
            errors='coerce'
        ).fillna(0) # Substitui NaN por 0 para a soma

    if not nao_levantados.empty and 'Valor' in nao_levantados.columns:
         nao_levantados['Valor'] = pd.to_numeric(
            nao_levantados['Valor'].astype(str).str.replace(',', '.', regex=False),
            errors='coerce'
        ).fillna(0)

    # 2. Configuração do PDF
    pdf = FPDF()
    pdf.add_page()
    
    # 3. Título e Variáveis Iniciais
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, titulo_relatorio, 0, 1, 'C')
    
    pdf.set_font('Arial', '', 10)
    pdf.cell(0, 10, f'Gerado em: {data_geracao}', 0, 1)
    pdf.cell(0, 10, f'Localidade: {localidade}', 0, 1)
    pdf.ln(5)

    # 4. Cálculo de Larguras da Tabela
    # A largura total é fixa (largura da página - margens)
    largura_total = pdf.w - pdf.l_margin - pdf.r_margin 

    # --- 4.1. CÁLCULO PARA LEVANTADO ---
    colunas_levantado = levantado.columns
    if len(colunas_levantado) > 0:
        larguras_levantado = [largura_total / len(colunas_levantado) for _ in colunas_levantado]
        alinha_levantado = ['L'] * len(colunas_levantado)
    else:
        # Caso extremo de 0 colunas (apenas para evitar ZeroDivisionError)
        larguras_levantado = []
        alinha_levantado = []
    # 5. Tabela de Bens Levantados (USO DA FUNÇÃO MESTRA)
    
    # TÍTULO E ESTATÍSTICA
    pdf.set_font('Arial', 'B', 12)
    valor_total_levantados = levantado['Valor'].sum()
    pdf.cell(0, 10, f'{levantado.shape[0]} Bens Levantados', 0, 1, 'C')
    pdf.cell(0, 10, f'Valor Total: R$ {float(valor_total_levantados):,.2f}', 0, 1, 'C')
    pdf.ln(5)

    if len(colunas_levantado) > 0:
    # Usando os parâmetros específicos para levantado
        draw_dynamic_table(pdf, levantado, larguras_levantado, colunas_levantado, alinha_levantado)


    # 6. Tabela de Bens Não Levantados (USO DA FUNÇÃO MESTRA)

    pdf.ln(10)
    
    # TÍTULO E ESTATÍSTICA
    pdf.set_font('Arial', 'B', 12)
    valor_total_nao_levantados = nao_levantados['Valor'].sum()
    pdf.cell(0, 10, f'{nao_levantados.shape[0]} Bens Não Levantados', 0, 1, 'C')
    pdf.cell(0, 10, f'Valor Total: R$ {float(valor_total_nao_levantados):,.2f}', 0, 1, 'C')
    pdf.ln(5)
    
    if not nao_levantados.empty:
        # --- 6.1. CÁLCULO PARA NÃO LEVANTADOS ---
        colunas_nao_levantados = nao_levantados.columns
        if len(colunas_nao_levantados) > 0:
            larguras_nao_levantados = [largura_total / len(colunas_nao_levantados) for _ in colunas_nao_levantados]
            alinha_nao_levantados = ['L'] * len(colunas_nao_levantados)
            
            # Chamada única: cabeçalho e dados agora
            draw_dynamic_table(pdf, nao_levantados, larguras_nao_levantados, colunas_nao_levantados, alinha_nao_levantados)


    # 7. Rodapé e Assinatura
    pdf.ln(10)
    pdf.set_font('Arial', '', 10)
    
    pdf.cell(0, 10, f'Acompanhamento: {acompanhamento}', 0, 1)
    pdf.cell(0, 10, f'Matrícula: {matricula}', 0, 1)
    
    if assinatura is not None:
        # Lógica para inclusão da imagem da assinatura
        try:
            # Salvar a imagem temporariamente
            img_array = np.array(assinatura)
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
            cv2.imwrite(temp_file.name, img_array)
            pdf.image(temp_file.name, x=10, y=pdf.get_y(), w=100)
            
            # Adiciona um espaço após a imagem
            pdf.ln(30) 
        except Exception as e:
            # Em caso de erro na imagem, apenas pula a linha
            print(f"Erro ao incluir assinatura: {e}")
            pdf.ln(10)
            
    pdf.cell(0, 10, f'Responsável levantamento: {responsavel}', 0, 1)

    # 8. Salvar o PDF
    file_path = f"data_gold/{ug}/{localidade}.pdf"
    
    # É bom garantir que o diretório exista antes de salvar
    # import os
    # os.makedirs(f"data_gold/{ug}", exist_ok=True)
    
    pdf.output(file_path)
    st.success(f"PDF '{file_path}' gerado com sucesso!")
    
    return file_path # Retorna o caminho do arquivo para facilitar o uso externo

def tela_relatorio_levantamento():
    st.set_page_config(
    page_title='Relatório de Levantamento',
    page_icon='📄',
    layout='wide')

    # Título da Página
    st.title("📄 Emitir Relatório de Levantamento")
    
    # Instruções
    st.markdown("""
    Este relatório apresenta um resumo dos dados coletados durante o levantamento patrimonial.
    """)
    if 'selected_ug' not in st.session_state:
        st.warning('Por favor, faça o login e selecione uma UG na página de Levantamento antes de acessar o relatório.')
        botao_retornar = st.button("Ir para Credenciamento", on_click=lambda: st.session_state.update(page='Levantamento'))
        if botao_retornar:
            st.switch_page('menu_principal.py')
            st.stop()
        # 1. Dados de Exemplo
    else:
        st.subheader(f"Selecione uma localidade da UG {st.session_state.selected_ug} para visualizar o relatório")
        
        

        # Obter localidade_escolhida de lista de arquivos txt em data_gold
        localidades_levantadas = [file.replace('.txt', '') for file in os.listdir(f'data_gold/{st.session_state.selected_ug}') if file.endswith('.txt')]
        localidade_escolhida = st.selectbox("Localidade", ['Escolha uma localidade'] + localidades_levantadas, key="localidade_escolha")

        
        if localidade_escolhida is not None and localidade_escolhida != 'Escolha uma localidade':
            df = pd.read_csv(f'data_bronze/lista_bens-processado-{st.session_state.selected_ug}.csv', dtype=str)
            df['localidade'] = df['localidade'].apply(lambda x: x.replace("/","-"))
            
            # mostrar dados levantados
            with open (f'data_gold/{st.session_state.selected_ug}/{localidade_escolhida}.txt', 'r') as file:
                bens_levantados = [line.strip() for line in file.readlines()]
            df_levantado = df[df['num tombamento'].isin(bens_levantados)]
            st.subheader(f"{df_levantado.shape[0]} Bem(ns) levantado(s) em {localidade_escolhida}")
            st.dataframe(df_levantado[st.session_state.colunas_de_interesse], width='stretch')
                         
            # mostrar bens da localidade que não foram levantados
            df_localidade = df[df['localidade'] == localidade_escolhida].copy()
            df_localidade.set_index('num tombamento', inplace=True,drop=False)
            # excluir bens alienados, anulados ou desmembrados
            df_nao_levantado = df_localidade[~df_localidade['status'].isin(['ALIENADO', 'ANULADO', 'DESMEMBRADO'])]
            #excluir os bens que já foram inventariados
            df_nao_levantado = df_nao_levantado[~df_nao_levantado['num tombamento'].isin(bens_levantados)]
            st.session_state.df_localidade = df_localidade
            st.subheader(f"{df_nao_levantado.shape[0]} Bem(ns) não levantados em {localidade_escolhida}")
            st.markdown(f'Valor: R$ {df_nao_levantado["valor"].replace(",",".").astype(float).sum():,.2f}'.replace(",", "X").replace(".", ",").replace("X", "."))
            st.dataframe(df_nao_levantado[st.session_state.colunas_de_interesse], width='stretch')

            # Acompanhamento
            st.subheader("Acompanhamento")
            acompanhamento = st.text_input("Nome do Acompanhamento", value="")
            matricula = st.number_input("Matrícula do Acompanhamento", placeholder="Digite a matrícula", format="%d",step=1)
            coletar_assinatura() # coletar assinatura com desenho de caneta


            if st.button("Gerar Relatório em PDF"):
                gerar_pdf_levantamento(
                    levantado=df_levantado[st.session_state.colunas_de_interesse],
                    localidade=localidade_escolhida,
                    acompanhamento=acompanhamento,
                    matricula=matricula,
                    assinatura=st.session_state.get('assinatura', None),
                    responsavel=st.session_state.get('username', 'Desconhecido'),
                    data_levantamento=dt.datetime.now(),
                    nao_levantados=df_nao_levantado[st.session_state.colunas_de_interesse],
                    ug=st.session_state.selected_ug
                )
                with open(f"data_gold/{st.session_state.selected_ug}/{localidade_escolhida}.pdf", "rb") as file:
                    st.download_button(
                        label="Download do Relatório em PDF",
                        data=file,
                        file_name=f"{st.session_state.selected_ug}/{localidade_escolhida}.pdf",
                        mime="application/pdf"
                    )
                

if __name__ == "__main__":
    tela_relatorio_levantamento()

import os
import pandas as pd
import streamlit as st
import datetime as dt
import numpy as np
import tempfile

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
    Gera um relatório em PDF do levantamento patrimonial.
    """
    # 1. Título do Relatório e Data
    titulo_relatorio = "Relatório de Levantamento"
    data_geracao = data_levantamento.strftime("%d de %B de %Y")
    if nao_levantados is None:
        nao_levantados = pd.DataFrame()
    if ug is None:
        ug = ""

    # 2. Configuração do PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)

    # 3. Inserindo Variáveis
    pdf.cell(0, 10, titulo_relatorio, 0, 1, 'C')
    pdf.set_font('Arial', '', 10)
    pdf.cell(0, 10, f'Gerado em: {data_geracao}', 0, 1)
    pdf.cell(0, 10, f'Localidade: {localidade}', 0, 1)
    

    pdf.ln(5)

    # 4. Inserindo o DataFrame como Tabela
    pdf.set_font('Arial', 'B', 10)
    colunas = levantado.columns

    # Corrige cálculo das larguras das células
    margem_esquerda = pdf.l_margin
    margem_direita = pdf.r_margin
    largura_total = pdf.w - margem_esquerda - margem_direita
    larguras = [largura_total / len(colunas) for _ in colunas]
    alinha = ['L'] * len(colunas)

    # Cabeçalho da Tabela
    for i, col in enumerate(colunas):
        pdf.cell(larguras[i], 7, str(col), 1, 0, 'C')
    pdf.ln()

    # Dados de bens levantados como tabela
    pdf.set_font('Arial', '', 10)
    pdf.cell(0, 10, f'{levantado.shape[0]} Bens Levantados', 0, 1, 'C')
    # valor total dos bens levantados
    valor_total_levantados = levantado['valor'].sum()
    pdf.cell(0, 10, valor_total_levantados, 0, 1, 'C')
    pdf.ln(5)
    for _, row in levantado.iterrows():
        for i, item in enumerate(row):
            pdf.cell(larguras[i], 6, str(item), 1, 0, alinha[i])
        pdf.ln()

    # Dados de bens não levantados
    pdf.ln(10)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, f'{nao_levantados.shape[0]} Bens Não Levantados', 0, 1, 'C')
    # valor total dos bens não levantados
    valor_total_nao_levantados = nao_levantados['valor'].sum()
    pdf.cell(0, 10, valor_total_nao_levantados, 0, 1, 'C')
    pdf.ln(5)
    pdf.set_font('Arial', '', 10)
    if not nao_levantados.empty:
        for _, row in nao_levantados.iterrows():
            for i, item in enumerate(row):
                pdf.cell(larguras[i], 6, str(item), 1, 0, alinha[i])
            pdf.ln()

    # incluir imagem da assinatura ao pdf
    pdf.cell(0, 10, f'Acompanhamento: {acompanhamento}', 0, 1)
    pdf.cell(0, 10, f'Matrícula: {matricula}', 0, 1)
    if assinatura is not None:
        # Salvar a imagem temporariamente
        img_array = np.array(assinatura)
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        cv2.imwrite(temp_file.name, img_array)
        pdf.image(temp_file.name, x=10, y=pdf.get_y(), w=100)
        
    pdf.cell(0, 10, f'Responsável levantamento: {responsavel}', 0, 1)

    # 5. Salvar o PDF
    file_path = f"data_gold/{ug}/{localidade}.pdf"
    pdf.output(file_path)
    st.success(f"PDF '{file_path}' gerado com sucesso!")

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
            df_nao_levantado = df_nao_levantado[~df_nao_levantado['num tombamento'].isin(st.session_state.df_inventario['num tombamento'].values)]
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

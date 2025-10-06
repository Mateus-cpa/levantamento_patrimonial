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
        st.image(st.session_state.assinatura)
    return canvas_result

def gerar_pdf_levantamento(
    inventario,
    localidade,
    acompanhamento,
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
    pdf.cell(0, 10, f'Acompanhamento: {acompanhamento}', 0, 1)
    pdf.cell(0, 10, f'Responsável: {responsavel}', 0, 1)

    pdf.ln(5)

    # 4. Inserindo o DataFrame como Tabela
    pdf.set_font('Arial', 'B', 10)
    colunas = inventario.columns
    larguras = [pdf.w / len(colunas) - 10 for _ in colunas]
    alinha = ['L'] * len(colunas)

    # Cabeçalho da Tabela
    for i, col in enumerate(colunas):
        pdf.cell(larguras[i], 7, str(col), 1, 0, 'C')
    pdf.ln()

    # Dados do DataFrame
    pdf.set_font('Arial', '', 10)
    for _, row in inventario.iterrows():
        for i, item in enumerate(row):
            pdf.cell(larguras[i], 6, str(item), 1, 0, alinha[i])
        pdf.ln()

    # não levantados
    pdf.ln(10)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Bens Não Levantados', 0, 1, 'C')
    pdf.set_font('Arial', '', 10)
    if not nao_levantados.empty:
        for _, row in nao_levantados.iterrows():
            for i, item in enumerate(row):
                pdf.cell(larguras[i], 6, str(item), 1, 0, alinha[i])
            pdf.ln()

    # incluir imagem da assinatura ao pdf
    if assinatura is not None:
        # Salvar a imagem temporariamente
        img_array = np.array(assinatura)
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        cv2.imwrite(temp_file.name, img_array)
        pdf.image(temp_file.name, x=10, y=pdf.get_y(), w=100)

    # 5. Salvar o PDF
    file_path = f"data_gold/{ug}_{localidade}.pdf"
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
        
        #Retirar após testar
        #localidades = obter_localidades()
        #localidade_escolhida = selecionar_localidade(localidades)

        # Obter localidade_escolhida de lista de arquivos txt em data_gold
        localidades_levantadas = [file.replace('.txt', '') for file in os.listdir('data_gold') if file.endswith('.txt')]
        localidade_escolhida = st.selectbox("Localidade", ['Escolha uma localidade'] + localidades_levantadas, key="localidade_escolha")

        #mostrar dados levantados e não levantados
        if localidade_escolhida is not None and localidade_escolhida != 'Escolha uma localidade':
            df = pd.read_csv(f'data_bronze/lista_bens-processado-{st.session_state.selected_ug}.csv', dtype=str)
            with open (f'data_gold/{localidade_escolhida}.txt', 'r') as file:
                bens_levantados = [line.strip() for line in file.readlines()]
            df_levantado = df[df['num tombamento'].isin(bens_levantados)]
            # bens da localidade que não foram levantados
            df_localidade = df[df['localidade'] == localidade_escolhida]
            df_nao_levantado = df_localidade[~df_localidade['num tombamento'].isin(bens_levantados)]
            st.subheader(f"{df_levantado.shape[0]} Bem(ns) levantado(s) em {localidade_escolhida}")
            st.dataframe(df_levantado, use_container_width=True)

            st.subheader(f"{df_nao_levantado.shape[0]} Bem(ns) não levantados em {localidade_escolhida}")
            st.dataframe(df_nao_levantado, use_container_width=True)

            # coletar assinatura com desenho de caneta
            st.subheader("Assinatura")
            coletar_assinatura()

            if st.button("Gerar Relatório em PDF"):
                gerar_pdf_levantamento()
                with open(f"data_gold/{st.session_state.selected_ug}_{st.session_state.localidade_escolhida[0]}.pdf", "rb") as file:
                    btn = st.download_button(
                        label="Download do Relatório em PDF",
                        data=file,
                        file_name=f"{st.session_state.selected_ug}_{st.session_state.localidade_escolhida[0]}.pdf",
                        mime="application/pdf"
                    )
                    btn.download()
                st.success("Relatório gerado com sucesso!")


if __name__ == "__main__":
    tela_relatorio_levantamento()

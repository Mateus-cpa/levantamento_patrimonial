import pandas as pd
import streamlit as st
import datetime as dt

from fpdf import FPDF

def gerar_pdf_levantamento():
    
    titulo_relatorio = "Relatório de Levantamento"
    data_geracao = dt.datetime.now().strftime("%d de %B de %Y")
    levantados = st.session_state.df_inventario
    nao_levantados = st.session_state.df_localidade

    # 2. Configuração do PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)

    # 3. Inserindo Variáveis
    pdf.cell(0, 10, titulo_relatorio, 0, 1, 'C') # Título (centralizado)
    pdf.set_font('Arial', '', 10)
    pdf.cell(0, 10, f'Gerado em: {data_geracao}', 0, 1)

    # Adiciona um espaço
    pdf.ln(5)

    # 4. Inserindo o DataFrame como Tabela
    pdf.set_font('Arial', 'B', 10)
    larguras = [50, 50, 50] # Larguras das colunas
    alinha = ['L', 'C', 'R'] # Alinhamento L=Left, C=Center, R=Right

    # Cabeçalho da Tabela
    colunas = levantados.columns
    for i, col in enumerate(colunas):
        pdf.cell(larguras[i], 7, col, 1, 0, 'C') # 1 = borda
    pdf.ln()

    # Dados do DataFrame
    pdf.set_font('Arial', '', 10)
    for index, row in levantados.iterrows():
        for i, item in enumerate(row):
            pdf.cell(larguras[i], 6, str(item), 1, 0, alinha[i])
        pdf.ln()
    
    # não levantados
    pdf.ln(10)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Bens Não Levantados', 0, 1, 'C')
    pdf.set_font('Arial', '', 10)

    # Dados do DataFrame
    for index, row in nao_levantados.iterrows():
        for i, item in enumerate(row):
            pdf.cell(larguras[i], 6, str(item), 1, 0, alinha[i])
        pdf.ln()

    # 5. Salvar o PDF
    pdf.output(f"data_gold/{st.session_state.selected_ug}_{st.session_state.localidade_escolhida[0]}.pdf")
    st.success(f"PDF 'data_gold/{st.session_state.selected_ug}_{st.session_state.localidade_escolhida[0]}.pdf' gerado com sucesso!")


def tela_relatorio_levantamento():
    st.set_page_config(
    page_title='Relatório de Levantamento',
    page_icon='📄',
    layout='wide')

    # Título da Página
    st.title("📄 Relatório de Levantamento")
    
    # Instruções
    st.markdown("""
    Este relatório apresenta um resumo dos dados coletados durante o levantamento patrimonial.
    """)
        # 1. Dados de Exemplo
    if 'localidade_escolhida' not in st.session_state:
        st.session_state.localidade_escolhida = ['NUMAT - SALA 325 - 1864']
    if 'df_localidade' not in st.session_state:
        st.session_state.df_localidade = pd.DataFrame()
    
    #mostrar dados levantados e não levantados
    st.subheader(f"{st.session_state.df_inventario.shape[0]} Bem(ns) Levantado(s) em {st.session_state.localidade_escolhida[0]}")
    st.dataframe(st.session_state.df_inventario, use_container_width=True)

    st.subheader(f"{st.session_state.df_localidade.shape[0]} Bem(ns) a inventariar em {st.session_state.localidade_escolhida[0]}")
    st.dataframe(st.session_state.df_localidade, use_container_width=True)

    # coletar assinatura com desenho de caneta
    st.subheader("Assinatura")
    assinatura = st.canvas()
    if assinatura.image_data is not None:
        st.image(assinatura.image_data)

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


tela_relatorio_levantamento()

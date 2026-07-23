import streamlit as st
import requests
import pandas as pd
from datetime import date

st.set_page_config(
    page_title="Conversor de Moedas",
    page_icon="💱",
    layout="wide"
)

st.title("💱 Conversor de Moedas - Banco Central (PTAX)")

# Dicionário de moedas
moedas = {
    "Real Brasileiro (BRL)": "BRL",
    "Dólar Americano (USD)": "USD",
    "Euro (EUR)": "EUR",
    "Libra Esterlina (GBP)": "GBP",
    "Iene Japonês (JPY)": "JPY",
    "Franco Suíço (CHF)": "CHF",
    "Dólar Canadense (CAD)": "CAD",
    "Dólar Australiano (AUD)": "AUD"
}

# ==========================
# FILTROS
# ==========================

col1, col2, col3, col4 = st.columns(4)

with col1:
    moeda_origem_nome = st.selectbox(
        "Moeda de origem",
        list(moedas.keys()),
        index=1
    )

with col2:
    moeda_destino_nome = st.selectbox(
        "Moeda de destino",
        list(moedas.keys()),
        index=2
    )

with col3:
    valor = st.number_input(
        "Valor",
        min_value=0.0,
        value=100.0,
        step=10.0
    )

with col4:
    data = st.date_input(
        "Data",
        value=date.today(),
        max_value=date.today()
    )

data_api = data.strftime("%m-%d-%Y")

moeda_origem = moedas[moeda_origem_nome]
moeda_destino = moedas[moeda_destino_nome]


# ==========================
# FUNÇÃO CONSULTA PTAX
# ==========================

@st.cache_data(ttl=3600)
def consultar_moeda(moeda, data_api):

    if moeda == "BRL":
        return {
            "cotacaoVenda": 1.0,
            "cotacaoCompra": 1.0
        }

    url = (
        "https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/"
        f"CotacaoMoedaDia(moeda=@moeda,dataCotacao=@dataCotacao)?"
        f"@moeda='{moeda}'&"
        f"@dataCotacao='{data_api}'&"
        "$top=100&"
        "$format=json&"
        "$select=cotacaoCompra,cotacaoVenda,dataHoraCotacao"
    )

    resposta = requests.get(url)
    resposta.raise_for_status()

    dados = resposta.json()

    if not dados["value"]:
        return None

    return dados["value"][-1]


# ==========================
# CONSULTAS
# ==========================

try:

    origem = consultar_moeda(
        moeda_origem,
        data_api
    )

    destino = consultar_moeda(
        moeda_destino,
        data_api
    )

    if origem is None or destino is None:
        st.warning(
            "Não existem dados para uma das moedas na data selecionada."
        )

    else:

        cotacao_origem = float(origem["cotacaoVenda"])
        cotacao_destino = float(destino["cotacaoVenda"])

        taxa_cruzada = (
            cotacao_origem /
            cotacao_destino
        )

        valor_convertido = valor * taxa_cruzada

        st.divider()

        st.subheader("💱 Resultado da Conversão")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Taxa de Conversão",
                f"{taxa_cruzada:.6f}"
            )

        with col2:
            st.metric(
                "Valor Informado",
                f"{valor:,.2f}"
            )

        with col3:
            st.metric(
                "Valor Convertido",
                f"{valor_convertido:,.2f}"
            )

        st.success(
            f"{valor:,.2f} {moeda_origem} = "
            f"{valor_convertido:,.2f} {moeda_destino}"
        )

        st.divider()

        st.subheader("📊 Cotações Utilizadas")

        tabela = pd.DataFrame({
            "Moeda": [
                moeda_origem,
                moeda_destino
            ],
            "Cotação Venda (R$)": [
                cotacao_origem,
                cotacao_destino
            ]
        })

        st.dataframe(
            tabela,
            use_container_width=True
        )

except Exception as e:
    st.error(f"Erro ao consultar API: {e}")
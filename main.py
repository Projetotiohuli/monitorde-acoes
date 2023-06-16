import streamlit as st
import pandas as pd
import yfinance as yf
import investpy as ip
import plotly.graph_objs as go
from datetime import datetime, timedelta

acoes =  ip.get_stocks_list('brazil')
intervalos = ['1 dia', '1 mês', '6 meses', '12 meses']
data_inicial = datetime.today() - timedelta(days=30)
data_final = datetime.today()

with open('styles.css') as f:
    st.markdown(f'<style> {f.read()} </style>', unsafe_allow_html= True)

@st.cache_data
def consultar_acao(acao, data_inicial, data_final, intervalo):
    df = pd.DataFrame(yf.download(tickers=f'{acao}.SA', start=data_inicial, end=data_final))
    df.index = pd.to_datetime(df.index)
    if intervalo != 'D':
        df = df.resample(intervalo).last()
    return df

def format_data(data, format='%d/%m/%Y'):
    return data.strftime(format)

def plot_grafico(df, acao):
    tracel = {
        'x': df.index,
        'open': df['Open'],
        'close': df['Close'],
        'high': df['High'],
        'low': df['Low'],
        'type': 'candlestick',
        'name': acao,
        'showlegend': False
    }

    data = [tracel]
    layout = go.Layout()

    fig = go.Figure(data=data, layout=layout)
    return fig

st.title('Análise de Ações do Mercado Brasileiro')
barra_lateral = st.sidebar.empty()
acao_selecionada = st.sidebar.selectbox('Ação', acoes)
intervalo_selecionado = st.sidebar.selectbox('Intervalo', intervalos)


if intervalo_selecionado == '1 dia':
    intervalo = 'D'
elif intervalo_selecionado == '1 mês':
    intervalo = 'M'
elif intervalo_selecionado == '6 meses':
    intervalo = '6M'
elif intervalo_selecionado == '12 meses':
    intervalo = 'Y'

inicio_selecionado = st.sidebar.date_input('De: ', data_inicial)
fim_selecionado = st.sidebar.date_input('Até: ', data_final)
carregar_dados = st.sidebar.checkbox('Carregar dados')

grafico_candle = st.empty()
grafico_linhas = st.empty()
retorno_acumulado = st.empty()

if inicio_selecionado > fim_selecionado:
    st.sidebar.error('Data de início maior do que data final')
else:
    dados = consultar_acao(acao_selecionada, inicio_selecionado, fim_selecionado, intervalo)
    try:
        candle = plot_grafico(dados, acao_selecionada)
        grafico_candle = st.plotly_chart(candle)
        grafico_linhas = st.line_chart(dados['Close'])
        retorno_acumulado_title = st.header('Retorno Acumulado')

        retorno_acumulado = (dados['Adj Close'].iloc[-1] - dados['Adj Close'].iloc[0]) / dados['Adj Close'].iloc[0]
        st.subheader(f'{retorno_acumulado:.2%}')

        if carregar_dados:
            dataframe_titulo = st.subheader('dados')
            dataframe_dados = st.dataframe(dados)

    except Exception as e:
        st.error(e)
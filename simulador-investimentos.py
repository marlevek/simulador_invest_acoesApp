import streamlit as st
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import plotly.graph_objs as go

st.set_page_config(
    page_title='Simulador de Investimentos em Ações',
    page_icon='📈'
)

# Centralizando elementos com CSS
st.markdown("""
    <style>
    .center-text {
        text-align: center;
    }
    .center-dataframe {
        display: flex;
        justify-content: center;
    }
    </style>
    """, unsafe_allow_html=True)

# Título do App Centralizado
st.markdown('<h1 class="center-text">Simulador de Investimentos em Ações</h1>', unsafe_allow_html=True)

with st.sidebar:
    # Input para o ticker da ação
    ticker = st.text_input("Digite o ticker da ação (ex: AAPL para Apple):", "AAPL")

    # Seleção de intervalo de datas
    start_date = st.date_input("Data de início", pd.to_datetime("2023-01-01"))
    end_date = st.date_input("Data de fim", pd.to_datetime("today"))

    # Estado do simulador
    if "saldo" not in st.session_state:
        st.session_state.saldo = 10000  # Saldo inicial fictício
    if "historico" not in st.session_state:
        st.session_state.historico = []
    if "dados_acao" not in st.session_state:
        st.session_state.dados_acao = pd.DataFrame()

    # Botão para buscar dados
    if st.button("Buscar Dados"):
        # Obter dados históricos da ação e armazenar no estado da sessão
        st.session_state.dados_acao = yf.download(ticker, start=start_date, end=end_date)
        st.write(f"Exibindo dados de {ticker} de {start_date} a {end_date}")

# Exibir tabela de dados
st.dataframe(st.session_state.dados_acao)

# Checa se há dados disponíveis para exibir o gráfico e realizar operações
if not st.session_state.dados_acao.empty:
    # Escolha do tipo de gráfico
    st.subheader("Escolha o tipo de gráfico")
    tipo_grafico = st.selectbox('Selecione o tipo de gráfico', ['Linha', 'Candlestick'])
    
    # Gráfico de preço da ação
    if tipo_grafico == 'Linha':
        st.subheader('Gráfico de Preço de Fechamento')    
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=st.session_state.dados_acao.index, 
                             y=st.session_state.dados_acao['Close'], 
                             mode='lines', 
                             name='Preço de Fechamento'))
        fig.update_layout(title=f"Preço de Fechamento de {ticker}", 
                      xaxis_title="Data", 
                      yaxis_title="Preço (USD)")
        st.plotly_chart(fig)
    
    elif tipo_grafico == 'Candlestick':
        st.subheader('Gráfico Candlestick')
        fig = go.Figure(data=[go.Candlestick(x=st.session_state.dados_acao.index,
                                             open=st.session_state.dados_acao['Open'],
                                             high=st.session_state.dados_acao['High'],
                                             low=st.session_state.dados_acao['Low'],
                                             close=st.session_state.dados_acao['Close']
                                             )])
        fig.update_layout(title=f'Gráfico Candlestick de {ticker}', xaxis_title='Data', yaxis_title='Preço (USD)')
        st.plotly_chart(fig)
        

    # Input para simulação de compra e venda
    st.subheader("Simulação de Compra e Venda")
    quantidade = st.number_input("Quantidade de ações", min_value=1, value=1, step=1, key='quantidade')
    operacao = st.selectbox("Operação", ["Comprar", "Vender"])
    preco_atual = st.session_state.dados_acao["Close"].iloc[-1]

    if st.button("Executar Operação"):
        if operacao == "Comprar":
            custo = quantidade * preco_atual
            if custo <= st.session_state.saldo:
                st.session_state.saldo -= custo
                st.session_state.historico.append({
                    "Operação": "Compra",
                    "Ticker": ticker,
                    "Quantidade": quantidade,
                    "Preço": preco_atual,
                    "Custo": custo
                })
                st.success(f"Compra executada! Custo: ${custo:.2f}")
            else:
                st.error("Saldo insuficiente para a compra.")
        elif operacao == "Vender":
            venda = quantidade * preco_atual
            st.session_state.saldo += venda
            st.session_state.historico.append({
                "Operação": "Venda",
                "Ticker": ticker,
                "Quantidade": quantidade,
                "Preço": preco_atual,
                "Receita": venda
            })
            st.success(f"Venda executada! Receita: ${venda:.2f}")

    # Exibir saldo e histórico de operações
    st.write(f"Saldo atual: ${st.session_state.saldo:.2f}")
    st.subheader("Histórico de Operações")
    st.write(pd.DataFrame(st.session_state.historico))
else:
    st.error("Dados da ação não disponíveis. Por favor, clique em 'Buscar Dados'.")

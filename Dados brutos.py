import streamlit as st
import requests
import pandas as pd
import time 

#função conversão data frame para arquivo csv

#primeira função para manter o csv  armazenado na memória cache do app
#caso o data frame não seja filtrado não é necessário fazer a conversao novamente
# da base de dados 
@st.cache_data
def converte_csv(df):
    return df.to_csv(index = False).encode('utf-8')

#função de mensagem de sucesso para o dowload do arquivo
def mensagem_sucesso():
    sucesso = st.sucess('Arquivo baixado com sucesso!', icon = "✅")
    time.sleep(5)
    sucesso.empty


st.title('Dados Brutos')

url = "https://labdados.com/produtos"
response = requests.get(url)
dados = pd.DataFrame.from_dict(response.json())
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format = '%d/%m/%Y')

#criacao de escolha da coluna
with st.expander('Colunas'):
    colunas =st.multiselect('Selecione as Colunas', list(dados.columns))

#criacao dos elementos da barra lateral
st.sidebar.title('Filtros')
with st.sidebar.expander('Nome do Produto'):
    produtos = st.multiselect('Selecione os produtos', dados['Produto'].unique(), dados['Produto'].unique())
with st.sidebar.expander('Preço do Produto'):
    preco =st.slider('Selecione o preço', 0, 5000, (0, 5000))
with st.sidebar.expander('Data da Compra'):
    data_compra = st.date_input('Selecione a data', (dados['Data da Compra'].min(), dados['Data da Compra'].max()))

query ='''
Produto in @produtos and \
@preco[0] <= Preço <= @preco[1] and\
@data_compra[0] <= `Data da Compra` <= @data_compra[1]
'''

dados_filtrados = dados.query(query)
dados_filtrados = dados_filtrados[colunas]

st.dataframe(dados_filtrados)
st.markdown(f'A tabela possui :blue[{dados_filtrados.shape[0]}] linhas e :blue[{dados_filtrados.shape[1]}] colunas')
st.markdown("Escreva um nome para o arquivo")

coluna3, coluna4 = st.columns(2)
with coluna3:
        nome_arquivo= st.text_input('', label_visibility = 'collapsed', value = 'dados')
        nome_arquivo +='.csv'
with coluna4:
        st.download_button('Fazer o dowload da tabela em csv', data = converte_csv(dados_filtrados), file_name= nome_arquivo, mime = 'text/csv', on_click = mensagem_sucesso)


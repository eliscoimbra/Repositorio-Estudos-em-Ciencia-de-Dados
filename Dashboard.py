import streamlit as st
import pandas as pd
import requests
import plotly.express as px
st.set_page_config(layout = 'wide')

#maneiras de rodar o codigo no terminal: streamlit run dashboard.py
def formata_numero(valor, prefixo = ' '):
    for unidade in ['', 'mil']:
        if valor < 1000: 
            return f'{prefixo} {valor:.2f} {unidade}'
        else:
            valor /= 1000
    return f'{prefixo} {valor:.2f} milhões'


#titulo da página
st.title("DASHBOARD DE VENDAS :shopping_trolley:")


#leitura da api 
#filtrando os vendedores e o ano na api
url = "https://labdados.com/produtos"
regioes =['Brasil', 'Centro Oeste', 'Nordeste', 'Norte', 'Sudeste', 'Sul']

st.sidebar.title('Filtros')
regiao = st.sidebar.selectbox('Região', regioes)

if regiao == 'Brasil':
    regiao = ' '

todos_anos = st.sidebar.checkbox('Dados de todo o período', value = True)
if todos_anos:
    ano = ' '
else:
    ano = st.sidebar.slider('Ano', 2020, 2023)

#query_string = {'regiao':regiao.lower(), 'ano':ano}
#response = requests.get(url, params= query_string)
response = requests.get(url)
dados = pd.DataFrame.from_dict(response.json())

dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format = '%d/%m/%Y')

#dados.set_index('Data da Compra', inplace=True)

##alterando a coluna de dados para datetime


## filtro dos vendedores
#filtro_vendedores = st.sidebar.multiselect('Vendedores', dados['Vendedor'].unique())
#if filtro_vendedores:
#    dados =dados[ dados['Vendedor'].isin(filtro_vendedores)]



## tabelas
#tabela gráfico de estados
receita_estados = dados.groupby('Local da compra')[['Preço']].sum()
receita_estados = dados.drop_duplicates(subset = 'Local da compra')[['lat','lon', 'Local da compra']].merge(receita_estados, left_on = 'Local da compra', right_index =True).sort_values('Preço', ascending = False)

#tabela gráfico  de linhasreceita mensal
receita_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq = 'M'))['Preço'].sum().reset_index()
receita_mensal['Ano'] = receita_mensal['Data da Compra'].dt.year
receita_mensal['Mes'] = receita_mensal['Data da Compra'].dt.month_name()

#tabela categoria do produto para o gráfico de barras
receita_categorias = dados.groupby('Categoria do Produto')[['Preço']].sum().sort_values('Preço', ascending=False)

#tabelas de vendedores 
vendedores = pd.DataFrame(dados.groupby('Vendedor')['Preço'].agg(['sum', 'count']))

##gráficos
#gráfico de mapa
fig_mapa_receita = px.scatter_geo(receita_estados,
                                    lat = 'lat',
                                    lon = 'lon',
                                    scope = 'south america',
                                    size = 'Preço',
                                    template = 'seaborn',
                                    hover_name = 'Local da compra',
                                    hover_data = {'lat': False, 'lon': False},
                                    title = 'Receita por Estado'
                                     )
##gráfico de linhas
fig_receita_mensal = px.line(receita_mensal,
                              x= 'Mes',
                              y = 'Preço',
                              markers = True,
                              range_y = (0,receita_mensal.max()),
                              color = 'Ano',
                              line_dash = 'Ano',
                              title = 'Receita Mensal')
fig_receita_mensal.update_layout(yaxis_title = 'Receita')

## gráfico de barras estado por receita
fig_receita_estado = px.bar(receita_estados.head(),
                             x ='Local da compra',
                             y = 'Preço',
                             text_auto = True,
                             title = 'Top Estados(receita)')

fig_receita_estado.update_layout(yaxis_title = 'Receita')

## gráfico de barras categoria
fig_receita_categorias = px.bar( receita_categorias,
                                text_auto= True,
                                title = 'Receita por categorias')

fig_receita_categorias.update_layout(yaxis_title = 'Receita')

## criar as colunas e mostra as métricas
##visualização no streamlit
##construção das abas do dashboard
aba1, aba2, aba3 = st.tabs(['Receita', 'Quantidade de Vendas', 'Vendedores'])
with aba1:
    coluna1, coluna2 = st.columns(2)
    with coluna1:
        st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$'))
        st.plotly_chart(fig_mapa_receita, use_container_width = True)
        st.plotly_chart(fig_receita_estado, use_container_width = True)
    with coluna2:
        st.metric("Quantidade de vendas", formata_numero(dados.shape[0]))
        st.plotly_chart(fig_receita_mensal, use_container_width = True)
        st.plotly_chart(fig_receita_categorias, use_container_width = True)

with aba2:
    coluna1, coluna2 = st.columns(2)
    with coluna1:
        st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$'))
    with coluna2:
        st.metric("Quantidade de vendas", formata_numero(dados.shape[0]))

with aba3:
    qtd_vendedores = st.number_input('Quantidade de Vendedores', 2, 10, 5)

    coluna1, coluna2 = st.columns(2)
    with coluna1:
        st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$'))
        fig_receita_vendedores = px.bar(vendedores[['sum']].sort_values('sum', ascending = False).head(qtd_vendedores),
                                        x= 'sum',
                                        y =vendedores[['sum']].sort_values('sum', ascending = False).head(qtd_vendedores).index,
                                        text_auto = True,
                                        title = f'Top{qtd_vendedores} vendedores(receita)')
        st.plotly_chart(fig_receita_vendedores)
                                            

    with coluna2:
        st.metric("Quantidade de vendas", formata_numero(dados.shape[0]))
        fig_receita_vendas = px.bar(vendedores[['count']].sort_values('count', ascending = False).head(qtd_vendedores),
                                        x= 'count',
                                        y =vendedores[['count']].sort_values('count', ascending = False).head(qtd_vendedores).index,
                                        text_auto = True,
                                        title = f'Top{qtd_vendedores} vendedores(quantidade de vendas)')
        st.plotly_chart(fig_receita_vendas)
#forma de inserir um dataframe no dashboard

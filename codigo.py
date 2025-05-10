import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração da página
st.set_page_config(
    page_title='Tabela de Jogos',
    layout='centered',
    page_icon='atividade_avaliativa_04/logo.png'
)

# Carregar dados
caminho = r'atividade_avaliativa_04/vgsales.csv'
dados_df = pd.read_csv(caminho)

# Filtros na sidebar
with st.sidebar:
    st.header("Filtros Gerais")
    
    # Filtro de plataforma
    lista_plataforma = dados_df['Platform'].unique().tolist()
    plataforma_selecionada = st.multiselect('Plataforma', lista_plataforma)
    
    # Filtro de ano
    lista_ano = dados_df['Year'].fillna(0).unique().tolist()
    ano_selecionado = st.number_input(
        "Ano", 
        value=None, 
        placeholder="Digite o Ano",
        min_value=1980,
        max_value=2020
    )
    
    # Filtro por gênero
    lista_genero = dados_df['Genre'].unique().tolist()
    genero_selecionado = st.multiselect('Gênero', lista_genero)
    
    # Filtrar por Empresa
    lista_empresas = dados_df['Publisher'].unique().tolist()
    empresa_selecionada = st.multiselect("Editora", lista_empresas)

# Layout principal
st.title('Descubra sobre a venda do seu jogo favorito')
st.markdown('----')

# Funções de métricas
def aplicar_filtros():
    dados_filtrados = dados_df.copy()
    
    if plataforma_selecionada:
        dados_filtrados = dados_filtrados[dados_filtrados['Platform'].isin(plataforma_selecionada)]
    
    if ano_selecionado:
        dados_filtrados = dados_filtrados[dados_filtrados['Year'] == ano_selecionado]
    
    if genero_selecionado:
        dados_filtrados = dados_filtrados[dados_filtrados['Genre'].isin(genero_selecionado)]
    
    if empresa_selecionada:
        dados_filtrados = dados_filtrados[dados_filtrados['Publisher'].isin(empresa_selecionada)]
    
    return dados_filtrados

col1, col2, col3, col4 = st.columns([1.5, 1.5, 2, 1.5])

def total_de_jogos():
    with col1:
        dados_filtrados = aplicar_filtros()
        contagem = dados_filtrados['Name'].nunique()
        st.metric("Quantidade de Jogos", contagem)

def total_de_vendas():
    with col2:
        dados_filtrados = aplicar_filtros()
        total_vendas = dados_filtrados['Global_Sales'].sum()
        st.metric("Total de Vendas", f"${total_vendas:.2f} milhões")

def ano_do_jogo_mais_antigo_e_recente():
    with col3:
        dados_filtrados = aplicar_filtros()
        ano_minimo = dados_filtrados['Year'].min()
        ano_maximo = dados_filtrados['Year'].max()
        st.metric("Ano do jogo mais antigo", int(ano_minimo) if not pd.isna(ano_minimo) else "N/A")
        st.metric('Ano do jogo mais recente', int(ano_maximo) if not pd.isna(ano_maximo) else "N/A")

def empresa_mais_jogos():
    with col4:
        dados_filtrados = aplicar_filtros()
        editora_popular = dados_filtrados['Publisher'].mode()[0] if not dados_filtrados.empty else "N/A"
        st.metric('Editora com mais jogos', editora_popular)

def lista_de_jogos():
    st.markdown("-------")
    with st.expander("📋 Lista de Jogos Filtrados", expanded=False):
        dados_filtrados = aplicar_filtros()
        if not dados_filtrados.empty:
            st.dataframe(
                dados_filtrados[['Name', 'Platform', 'Year', 'Genre', 'Publisher', 'Global_Sales']],
                column_config={
                    "Name": "Jogo",
                    "Platform": "Plataforma",
                    "Year": "Ano",
                    "Genre": "Gênero",
                    "Publisher": "Editora",
                    "Global_Sales": "Vendas Globais (mi)"
                },
                hide_index=True
            )
        else:
            st.warning("Nenhum jogo encontrado com os filtros selecionados!")

# Abas para os gráficos
tab1, tab2,tab3,tab4 = st.tabs(["📊 Top Jogos por Vendas", "🍕 Distribuição de Vendas por Região",
                                '📊 Venda Por Gênero', '📊 Venda Global por Ano'])

def top_jogos():
    with tab1:
        st.markdown("----")
        col1, col2 = st.columns(2)
        with col1:
            regiao_venda = st.radio(
                "Qual o jogo mais vendido na Região",
                ["EU_Sales", "NA_Sales", "JP_Sales", "Other_Sales", "Global_Sales"],
                index=None,
            )
        with col2:    
            if regiao_venda:
                dados_filtrados = aplicar_filtros()
                if not dados_filtrados.empty:
                    jogo_mais_vendido = dados_filtrados.loc[dados_filtrados[regiao_venda] == dados_filtrados[regiao_venda].max(), 'Name'].iloc[0]
                    valor_vendas = dados_filtrados[regiao_venda].max()
                    st.metric(
                        label=f"Jogo mais vendido na região {regiao_venda.replace('_', ' ')}",
                        value=jogo_mais_vendido,
                        help=f"Vendas: {valor_vendas:.2f} milhões"
                    )
                else:
                    st.warning("Nenhum jogo encontrado com os filtros selecionados!")

def graficos_top_jogos_por_venda():
    with tab1:
        try:
            with st.expander('Configurações do Gráfico', expanded=False):
                tipo_vendas = st.radio(
                    "Tipo de Vendas:",
                    ["Global", "América do Norte (NA)", "Europa (EU)", "Japão (JP)"],
                    index=0
                )
                
                coluna_vendas = {
                    "Global": "Global_Sales",
                    "América do Norte (NA)": "NA_Sales",
                    "Europa (EU)": "EU_Sales",
                    "Japão (JP)": "JP_Sales"
                }[tipo_vendas]
                
                num_jogos = st.selectbox("Número de Jogos:", [5, 10, 20], index=1)
            
            dados_filtrados = aplicar_filtros()
            
            if not dados_filtrados.empty:
                top_jogos = dados_filtrados.sort_values(by=coluna_vendas, ascending=False).head(num_jogos)
                
                fig = px.bar(
                    top_jogos,
                    x=coluna_vendas,
                    y='Name',
                    orientation='h',
                    color='Platform',
                    hover_data=['Platform', 'Year', 'Genre', 'Publisher'],
                    labels={coluna_vendas: f'Vendas (mi) - {tipo_vendas}'},
                    title=f'Top {num_jogos} Jogos por Vendas {tipo_vendas}'
                )
                
                fig.update_layout(
                    height=600,
                    yaxis={'categoryorder': 'total ascending'},
                    hovermode='closest',
                    xaxis_title='Vendas (em milhões)',
                    yaxis_title='Jogo'
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                with st.expander("Ver dados completos"):
                    st.dataframe(
                        top_jogos[['Name', 'Platform', 'Year', 'Genre', 'Publisher', coluna_vendas]],
                        column_config={
                            "Name": "Jogo",
                            "Platform": "Plataforma",
                            "Year": "Ano",
                            "Genre": "Gênero",
                            "Publisher": "Editora",
                            coluna_vendas: "Vendas (mi)"
                        }
                    )
            else:
                st.warning("Nenhum jogo encontrado com os filtros selecionados!")
                
        except Exception as e:
            st.error(f"Ocorreu um erro: {str(e)}")

def distribuicao_vendas_por_regiao():
    with tab2:
        
        # Pré-processamento
        dados_df['Decada'] = (dados_df['Year'] // 10) * 10
        dados_df['Faixa_Decada'] = dados_df['Decada'].apply(
            lambda x: f"{x}-{x+9}" if not pd.isna(x) else None
        )
        
        with st.expander('Configurações do Gráfico', expanded=False):
            # Filtro por faixa de década
            faixas_decada = sorted(dados_df['Faixa_Decada'].dropna().unique())
            faixa_selecionada = st.selectbox(
                "Selecione a faixa de década:",
                options=["Todas"] + faixas_decada,
                index=0
            )
            
            # Seleção do tipo de gráfico
            tipo_grafico = st.radio(
                "Tipo de visualização:",
                ["Pizza", "Treemap", "Barras"],
                index=0
            )
        
        # Aplicar filtros
        dados_filtrados = aplicar_filtros()
        if faixa_selecionada != "Todas":
            dados_filtrados = dados_filtrados[dados_filtrados['Faixa_Decada'] == faixa_selecionada]
        
        if not dados_filtrados.empty:
            # Calcular totais por região
            totais = {
                'América do Norte': dados_filtrados['NA_Sales'].sum(),
                'Europa': dados_filtrados['EU_Sales'].sum(),
                'Japão': dados_filtrados['JP_Sales'].sum(),
                'Outras Regiões': dados_filtrados['Other_Sales'].sum()
            }
            
            df_vendas = pd.DataFrame({
                'Região': list(totais.keys()),
                'Vendas (mi)': list(totais.values()),
                'Percentual': [f"{(v/sum(totais.values()))*100:.1f}%" for v in totais.values()]
            })
            
            if tipo_grafico == "Pizza":
                fig = px.pie(
                    df_vendas,
                    names='Região',
                    values='Vendas (mi)',
                    title=f"Distribuição de Vendas por Região<br><sup>{faixa_selecionada if faixa_selecionada != 'Todas' else 'Todas as décadas'}</sup>",
                    hover_data=['Percentual'],
                    hole=0.3
                )
                fig.update_traces(textposition='inside', textinfo='percent+label')
                
            elif tipo_grafico == "Treemap":
                fig = px.treemap(
                    df_vendas,
                    path=['Região'],
                    values='Vendas (mi)',
                    title=f"Distribuição de Vendas por Região - {faixa_selecionada if faixa_selecionada != 'Todas' else 'Todas as décadas'}",
                    hover_data=['Vendas (mi)', 'Percentual'],
                    color='Vendas (mi)',
                    color_continuous_scale='Blues'
                )
                fig.update_traces(textinfo='label+percent entry')
                
            else:  # Barras
                fig = px.bar(
                    df_vendas.sort_values('Vendas (mi)', ascending=False),
                    x='Região',
                    y='Vendas (mi)',
                    text='Percentual',
                    title=f"Vendas por Região - {faixa_selecionada if faixa_selecionada != 'Todas' else 'Todas as décadas'}",
                    color='Região',
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                fig.update_layout(showlegend=False)
            
            st.plotly_chart(fig, use_container_width=True)
            
            with st.expander("📊 Ver dados detalhados"):
                st.dataframe(
                    df_vendas.sort_values('Vendas (mi)', ascending=False),
                    column_config={
                        "Região": st.column_config.TextColumn("Região"),
                        "Vendas (mi)": st.column_config.NumberColumn("Vendas (mi)", format="%.2f"),
                        "Percentual": st.column_config.TextColumn("Participação")
                    },
                    hide_index=True
                )
        else:
            st.warning("Nenhum jogo encontrado com os filtros selecionados!")
def vendas_por_genero():
    with tab3:
        st.header("📊 Popularidade por Gêneros")
        
        # Aplicar filtros selecionados na sidebar
        dados_filtrados = aplicar_filtros()
        
        # Verificar se há dados após filtrar
        if dados_filtrados.empty:
            st.warning("Nenhum dado encontrado com os filtros selecionados!")
            return
        
        try:
            # Agrupar por gênero e somar as vendas por região
            vendas_por_genero = dados_filtrados.groupby('Genre')[['NA_Sales', 'EU_Sales', 'JP_Sales', 'Other_Sales']].sum().reset_index()
            st.write(vendas_por_genero)
            # Criar o gráfico de barras empilhadas sem usar melt
            fig = px.bar(
                vendas_por_genero,
                x='Genre',  # Eixo X: gêneros
                y=['NA_Sales', 'EU_Sales', 'JP_Sales', 'Other_Sales'],  # Valores para cada região
                title='Vendas por Gênero e Região',
                labels={
                    'Genre': 'Gênero',
                    'value': 'Vendas (em milhões)',
                    'variable': 'Região'
                },
                color_discrete_map={
                    'NA_Sales': '#1f77b4',  # Azul para América do Norte
                    'EU_Sales': '#ff7f0e',  # Laranja para Europa
                    'JP_Sales': '#2ca02c',  # Verde para Japão
                    'Other_Sales': '#d62728'  # Vermelho para outras regiões
                },
                barmode='stack',  # Barras empilhadas,
                
            )
            
            # Melhorar a legenda (traduzir nomes das regiões)
            fig.for_each_trace(lambda t: t.update(name=t.name.replace('NA_Sales', 'América do Norte')
                                                 .replace('EU_Sales', 'Europa')
                                                 .replace('JP_Sales', 'Japão')
                                                 .replace('Other_Sales', 'Outras Regiões')))
            
            # Ajustar layout
            fig.update_layout(
                xaxis={'categoryorder': 'total descending'},  # Ordenar por vendas totais
                yaxis_title='Vendas (em milhões)',
                xaxis_title='Gênero',
                legend_title='Região',
                hovermode='x unified'  # Mostrar info de todas as barras ao passar mouse
            )
            
            # Mostrar o gráfico
            st.plotly_chart(fig, use_container_width=True)
            
            # Mostrar tabela com os dados detalhados
            with st.expander("🔍 Ver dados detalhados"):
                # Renomear colunas para exibição
                dados_exibicao = vendas_por_genero.rename(columns={
                    'Genre': 'Gênero',
                    'NA_Sales': 'América do Norte (mi)',
                    'EU_Sales': 'Europa (mi)',
                    'JP_Sales': 'Japão (mi)',
                    'Other_Sales': 'Outras Regiões (mi)'
                })
                
                st.dataframe(
                    dados_exibicao.sort_values('América do Norte (mi)', ascending=False),
                    column_config={
                        "Gênero": st.column_config.TextColumn("Gênero"),
                        "América do Norte (mi)": st.column_config.NumberColumn(format="%.2f"),
                        "Europa (mi)": st.column_config.NumberColumn(format="%.2f"),
                        "Japão (mi)": st.column_config.NumberColumn(format="%.2f"),
                        "Outras Regiões (mi)": st.column_config.NumberColumn(format="%.2f")
                    },
                    hide_index=True
                )
                
        except Exception as e:
            st.error(f"Ocorreu um erro ao gerar o gráfico: {str(e)}")

def global_por_ano():
    with tab4:
        st.header("Vendas Globais por Ano")
        
        dados_filtrados = aplicar_filtros()

        if dados_filtrados.empty:
            st.warning("Nenhum dado encontrado com os filtros selecionados!")
            return
        
        # Agrupar por ano e somar as vendas globais
        vendas_por_ano = dados_filtrados.groupby('Year')['Global_Sales'].sum().reset_index()
        
        # Criar o gráfico de barras
        fig = px.bar(
            vendas_por_ano,
            x='Year',
            y='Global_Sales',
            title='Vendas Globais por Ano',
            labels={
                'Year': 'Ano',
                'Global_Sales': 'Vendas Globais (em milhões)'
            }
        )
        
        # Melhorar a formatação do eixo X (anos)
        fig.update_xaxes(type='category')
        
        st.plotly_chart(fig, use_container_width=True)
# Adicione esta função após as outras funções e antes da execução das funções principais
def busca_jogos():
    st.markdown("----")
    st.header("🔍 Busca de Jogos")
    
    # Campo de busca
    termo_busca = st.text_input("Digite o nome do jogo:", placeholder="Ex: Mario, Call of Duty, FIFA...")
    
    if termo_busca:
        # Filtrar jogos que contêm o termo de busca (case insensitive)
        jogos_encontrados = dados_df[dados_df['Name'].str.contains(termo_busca, case=False, na=False)]
        
        if not jogos_encontrados.empty:
            # Seção de resultados
                st.subheader("Resultados da Busca")
                st.dataframe(
                    jogos_encontrados[['Name', 'Platform', 'Year', 'Genre', 'Publisher', 'Global_Sales']],
                    column_config={
                        "Name": "Jogo",
                        "Platform": "Plataforma",
                        "Year": "Ano",
                        "Genre": "Gênero",
                        "Publisher": "Editora",
                        "Global_Sales": "Vendas Globais (mi)"
                    },
                    hide_index=True,
                    height=400
                )
            
                st.subheader("Distribuição de Vendas por Região")
                
                # Calcular totais por região
                totais = {
                    'América do Norte': jogos_encontrados['NA_Sales'].sum(),
                    'Europa': jogos_encontrados['EU_Sales'].sum(),
                    'Japão': jogos_encontrados['JP_Sales'].sum(),
                    'Outras Regiões': jogos_encontrados['Other_Sales'].sum()
                }
                
                df_vendas = pd.DataFrame({
                    'Região': list(totais.keys()),
                    'Vendas (mi)': list(totais.values())
                })
                
            
                fig = px.pie(
                    df_vendas,
                    names='Região',
                    values='Vendas (mi)',
                    title=f"Distribuição de Vendas para '{termo_busca}'",
                    hole=0.3,
                    color='Região',
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                fig.update_traces(textposition='inside', textinfo='percent+label')
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Estatísticas resumidas
                st.metric("Total de jogos encontrados", len(jogos_encontrados))
                st.metric("Vendas globais totais", f"${jogos_encontrados['Global_Sales'].sum():.2f} milhões")
        else:
            st.warning(f"Nenhum jogo encontrado com o termo '{termo_busca}'")


# Executar as funções
total_de_jogos()
total_de_vendas()
empresa_mais_jogos()
ano_do_jogo_mais_antigo_e_recente()
lista_de_jogos()
top_jogos()
graficos_top_jogos_por_venda()
distribuicao_vendas_por_regiao()
vendas_por_genero()
global_por_ano()
busca_jogos()
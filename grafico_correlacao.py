import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime
import numpy as np

def criar_grafico_correlacao(caminho_dados_entrada, caminho_saida_grafico):
    """
    Cria e salva um gráfico de correlação a partir dos dados de matérias regulares,
    após aplicar os filtros especificados.
    """
    print("\nIniciando a criação do gráfico de correlação...")

    try:
        # 1. Carregar os dados
        df = pd.read_csv(caminho_dados_entrada, encoding='utf-8')
    except FileNotFoundError:
        print(f"ERRO: Arquivo de entrada não encontrado em {caminho_dados_entrada}. Execute o script principal primeiro.")
        return

    # 2. Aplicar Filtros
    print(f"Total de registros antes dos filtros: {len(df)}")
    df_filtrado = df[
        (df['total_alunos_disciplina'] >= 5) &
        (df['bloco'] != 'N/A') &
        (df['carga_semanal_dias'] <= 3)
    ].copy()
    print(f"Total de registros após os filtros: {len(df_filtrado)}")

    if df_filtrado.empty:
        print("AVISO: Nenhum dado restou após os filtros. O gráfico de correlação não será gerado.")
        return

    # 3. Selecionar e Converter Colunas para Análise
    colunas_para_correlacao = [
        'media_disciplina',
        'turno_predominante',
        'taxa_aprovacao',
        'taxa_reprovacao',
        'bloco'
      
    ]
    df_analise = df_filtrado[colunas_para_correlacao].copy()

    # Converter colunas de texto para numérico
    for col in ['media_disciplina','taxa_aprovacao', 'taxa_reprovacao']:
        df_analise[col] = pd.to_numeric(df_analise[col], errors='coerce')

    # Converter a coluna categórica 'turno' para numérica (One-Hot Encoding)
    # Isso cria novas colunas (turno_MANHA, turno_TARDE, etc.) para a correlação
    df_analise = pd.get_dummies(df_analise, columns=['turno_predominante'], prefix='turno', dtype=float)
 
    df_analise = pd.get_dummies(df_analise, columns=['bloco'],  dtype=float)

    # 4. Calcular a Matriz de Correlação
    matriz_corr = df_analise.corr()
    mask = np.triu(np.ones_like(matriz_corr, dtype=bool))

    # 5. Gerar o Gráfico (Heatmap)
    plt.figure(figsize=(12, 10)) # Aumentei um pouco o tamanho para melhor visualização
    heatmap = sns.heatmap(
        matriz_corr,
        mask=mask,           # Aplica a máscara para esconder a parte de cima
        annot=True,
        cmap='coolwarm',
        fmt=".2f",
        linewidths=.5
    )
    plt.title('Matriz de Correlação das Variáveis das Disciplinas', fontsize=16)
    heatmap.set_xticklabels(heatmap.get_xticklabels(), rotation=45, horizontalalignment='right')
    plt.tight_layout()

    plt.savefig(caminho_saida_grafico, dpi=300)
    print(f"\nGráfico de correlação salvo com sucesso em: {caminho_saida_grafico}")



if __name__ == "__main__":
    csv_in = "resultados/materias_regulares_pandas.csv"
    csv_out = "resultados/grafico_correlacao.png"

    criar_grafico_correlacao(csv_in,csv_out)
    


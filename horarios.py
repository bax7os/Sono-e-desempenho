import csv
import pandas as pd

# Leitura do arquivo resultados.csv
df = pd.read_csv('resultados/resultados.csv')

# Função para selecionar as colunas corretas
def selecionar_colunas(row):
   
    if pd.notna(row[6]) and pd.notna(row[7]):
        return pd.Series([row[6], row[7]])
    else:
        return pd.Series([row[2], row[3]])

# Aplicar a função para cada linha do DataFrame
df_horarios = df.apply(selecionar_colunas, axis=1)

# Remoção de horários repetidos
df_horarios = df_horarios.drop_duplicates()

# Ordenação dos horários
df_horarios = df_horarios.sort_values(by=[0, 1])

# Criação de um novo arquivo com os horários ordenados
df_horarios.to_csv('horarios_ordenados.csv', index=False, header=False)
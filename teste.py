import pandas as pd

# Carregar o arquivo CSV
df = pd.read_csv('resultados/materias_regulares_enriquecido.csv')


# Filtrar linhas onde a coluna 7 é '2017/2'
filtro_2017_2 = df[df.iloc[:,6] == '2017/2']  # colunas começam do 0

# Filtrar linhas onde a coluna 15 é 'INMA'
linhas_inma = filtro_2017_2[filtro_2017_2.iloc[:,14] == 'INMA']

if not linhas_inma.empty:
    print("Existe matéria do bloco INMA em 2017/2? Sim")
    print(linhas_inma)
else:
    print("Existe matéria do bloco INMA em 2017/2? Não")
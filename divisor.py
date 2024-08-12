import csv
from pathlib import Path
import pandas as pd


# Exemplo de caminho relativo usando pathlib
csv_path = Path(__file__).parent / 'dados' / 'data.csv'
csv_path_out = Path(__file__).parent / 'resultados' / 'resultados.csv'

# Conjunto para rastrear valores únicos de row[2]
valores_unicos = set()

# Abrindo o arquivo de entrada para leitura
with csv_path.open('r', encoding='utf-8') as file_in:
    reader = csv.reader(file_in)
    
    # Abrindo o arquivo de saída para escrita
    with csv_path_out.open('w', newline='', encoding='utf-8') as file_out:
        writer = csv.writer(file_out)
        cont = 0
        for row_in in reader:
           cont += 1
           # Verifica o semestre do ano e o curso
           if row_in[6] == "2010/1" and row_in[0] == 'ANÁLISE DE SISTEMAS - BACHARELADO':
                
                # Combina os valores que não podem se repetir  (RGA, Ano/Semestre, disciplina, curso) 
                combinacao = (row_in[6], row_in[7], row_in[0], row_in[1], row_in[2])

                # Saida com os dados relevantes 
                saida = row_in[0:3] + row_in[6:13]
                
                # Se row não existir no arquivo de saída, escreve o novo
                if combinacao not in valores_unicos:
                    
                    writer.writerow(saida)
              
                    valores_unicos.add(combinacao)
                # Se existir, só pega o horário da disciplina e o nome dela
                else:
                     writer.writerow(row_in[7:11])

# Removendo linhas duplicadas dos horários        

df = pd.read_csv(csv_path_out)
df_sem_duplicatas = df.drop_duplicates()
df_sem_duplicatas.to_csv(csv_path_out, index=False)

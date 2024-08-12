import csv
from pathlib import Path

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
        
        for row_in in reader:
           if row_in[6] == '2010/1' and row_in[0] == 'ANÁLISE DE SISTEMAS - BACHARELADO':
                combinacao = (row_in[6], row_in[7], row_in[0], row_in[1], row_in[2])
                saida = row_in[0:3] + [row_in[7]] + row_in[8:13]
                if combinacao not in valores_unicos:
                    writer.writerow(saida)
                    valores_unicos.add(combinacao)
                else:
                     writer.writerow(row_in[7:11])
       

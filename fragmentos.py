import csv
from pathlib import Path
import pandas as pd
from datetime import datetime, timedelta

# Exemplo de caminho relativo usando pathlib
csv_path = Path(__file__).parent / 'resultados' / 'resultados_tudo.csv'
csv_path_out = Path(__file__).parent / 'resultados' / 'disciplinas.csv'

# Crie um conjunto para armazenar as linhas que já foram escritas
linhas_escritas = set()

with csv_path.open('r', encoding='utf-8') as file_in:
    reader = csv.reader(file_in)
    
    # Abrindo o arquivo de saída para escrita
    with csv_path_out.open('w', newline='', encoding='utf-8') as file_out:
        writer = csv.writer(file_out)
        for row_in in reader:
            linha = row_in[4]
            if linha not in linhas_escritas:
                if linha == "Segunda-feira":
                    print(row_in[3])
                writer.writerow([linha])
                linhas_escritas.add(linha)
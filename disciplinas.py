import csv
from pathlib import Path
import pandas as pd
from datetime import datetime, timedelta

# Exemplo de caminho relativo usando pathlib
csv_path = Path(__file__).parent / 'include' / 'dados.csv'
csv_path_out = Path(__file__).parent / 'resultados' / 'resultados_disciplinas.csv'

# Conjunto para rastrear valores únicos de disciplinas
valores_unicos_disciplinas = set()

# Dicionários para armazenar cargas e pesos
cargas = {}
pesos = {}

# Intervalos de horários das aulas
horario1 = ["07:00:00", "08:59:00"]
horario2 = ["09:00:00", "11:25:00"]
horario3 = ["13:00:00", "14:40:00"]
horario4 = ["15:00:00", "16:59:00"] 
horario5 = ["17:00:00", "20:29:00"]
horario6 = ["20:30:00", "23:00:00"]

formato = "%H:%M:%S"

def horario_no_intervalo(horario, inicio, fim):
    formato = "%H:%M:%S"
    horario = datetime.strptime(horario, formato)
    horario_inicio = datetime.strptime(inicio, formato)
    horario_fim = datetime.strptime(fim, formato)
    return horario_inicio <= horario <= horario_fim

def horario_entre_aulas(horario, inicio, fim):
    formato = "%H:%M:%S"
    horario = datetime.strptime(horario, formato)
    horario_inicio = datetime.strptime(inicio, formato)
    horario_fim = datetime.strptime(fim, formato)
    return horario_inicio < horario < horario_fim

def validar_formato_tempo(valor):
    try:
        tempo = datetime.strptime(valor, "%H:%M:%S")
        if len(valor.split(":")[0]) == 1:
            return False
        return True
    except ValueError:
        return False

with csv_path.open('r', encoding='utf-8') as file_in:
    reader = csv.reader(file_in)
    
    with csv_path_out.open('w', newline='', encoding='utf-8') as file_out:
        writer = csv.writer(file_out)
        cont = 0
        nao_validos = 0
        for row_in in reader:
            cont += 1

            if row_in[8] != "EAD" and validar_formato_tempo(row_in[9]):
                # Combinação única para identificar a disciplina
                unicos = (row_in[0], row_in[6], row_in[7])
                dia = row_in[8]
                unicos_dias_iguais = (row_in[0], row_in[6], row_in[7], row_in[8])  # Inclui o dia da semana
                horario_inicio = row_in[9]
                horario_fim = row_in[10]


                time1 = datetime.strptime(row_in[9], formato).time()
                time2 = datetime.strptime(row_in[10], formato).time()
                time3 = datetime.strptime(horario1[0], formato).time()
                time4 = datetime.strptime(horario6[1], formato).time()

                if time1 >= time3 and time2 <= time4:
                    if unicos not in valores_unicos_disciplinas:
                        cargas[unicos] = 1
                        pesos[unicos] = 0
                        valores_unicos_disciplinas.add(unicos)
                    else:
                        cargas[unicos] += 1

                    # Atualiza o peso com base no horário
                    if horario_no_intervalo(row_in[9], horario1[0], horario1[1]):
                        pesos[unicos] += 1
                    elif horario_no_intervalo(row_in[9], horario2[0], horario2[1]):
                        pesos[unicos] += 2
                    elif horario_no_intervalo(row_in[9], horario3[0], horario3[1]):
                        pesos[unicos] += 3
                    elif horario_no_intervalo(row_in[9], horario4[0], horario4[1]):
                        pesos[unicos] += 4
                    elif horario_no_intervalo(row_in[9], horario5[0], horario5[1]):
                        pesos[unicos] += 5
                    elif horario_no_intervalo(row_in[9], horario6[0], horario6[1]):
                        pesos[unicos] += 6

                    saida = [row_in[0]] + row_in[6:10]
                    saida.extend([cargas[unicos], pesos[unicos]])
                    writer.writerow(saida)
            else:
                nao_validos += 1

# Removendo linhas duplicadas dos horários        
df = pd.read_csv(csv_path_out)
df_sem_duplicatas = df.drop_duplicates()
df_sem_duplicatas.to_csv(csv_path_out, index=False)
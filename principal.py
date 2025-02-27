import csv
from pathlib import Path
import pandas as pd
from datetime import datetime, timedelta

# Exemplo de caminho relativo usando pathlib
csv_path = Path(__file__).parent / 'include' / 'dados.csv'
csv_path_out = Path(__file__).parent / 'resultados' / 'resultados_tudo.csv'

# Conjunto para rastrear valores únicos de row[2](RGA):
# evita a repetição de notas de um aluno x, visto que se um alunos está em uma 
# matéria y irá aparecer os dados de todos os dias da semana dessa matéria, então
# não é necessário salvar novamente esses dados. 
valores_unicos = set()

# Cargas e pesos dos horários:
# cargas: quantidade de vezes que essa aula acontece na semana
# Exemplo: se a aula X acontece terça e quinta, seu peso seria 2
# pesos: em que período do dia essa aula fica
# Exemplo: os pesos vão de 1 a 6, quanto mais tarde a aula for maior é 
# esse peso. Aulas "quebradas" que ocupam um horário que ultrapassa os intervalos
# pre definidos dos horarios, são somadas com horario anterior + 0.5.
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




# funcao pra checar se o horário ta no intervalo
# horario: horario a ser analisado
# inicio-fim: horarioN do conjunto de horários pre estabelecidos

def horario_no_intervalo(horario, inicio, fim):
    formato = "%H:%M:%S"
    # converte para o formato
    horario = datetime.strptime(horario, formato)
    horario_inicio = datetime.strptime(inicio, formato)
    horario_fim = datetime.strptime(fim, formato)
    
    return horario_inicio <= horario <= horario_fim


def horario_entre_aulas(horario, inicio, fim):
    formato = "%H:%M:%S"
    # converte para o formato
    horario = datetime.strptime(horario, formato)
    horario_inicio = datetime.strptime(inicio, formato)
    horario_fim = datetime.strptime(fim, formato)

    return  horario_inicio < horario < horario_fim
# analisa se é possível fazer a conversão do formato 
# filtra os horários 00:00:00
def validar_formato_tempo(valor):
    try:
        # Tenta analisar o valor como "%H:%M:%S"
        tempo = datetime.strptime(valor, "%H:%M:%S")
        # Rejeita valores como "0:00:00"
        if len(valor.split(":")[0]) == 1:
            zero+= 1
            return False
        return True
    except ValueError:
        return False

# Abrindo o arquivo de entrada para leitura
with csv_path.open('r', encoding='utf-8') as file_in:
    reader = csv.reader(file_in)
    
    # Abrindo o arquivo de saída para escrita
    with csv_path_out.open('w', newline='', encoding='utf-8') as file_out:
        writer = csv.writer(file_out)
        cont = 0
        nao_validos = 0
        for row_in in reader:
           cont += 1


           # Verifica o semestre do ano e o curso
           
           if row_in[8] != "EAD" and validar_formato_tempo(row_in[9]):
                    
                # Combina os valores que não podem se repetir  (RGA, Ano/Semestre, disciplina, curso) 
                combinacao = ( row_in[0], row_in[1], row_in[2],row_in[6], row_in[7])
              
                # Saida com os dados relevantes 
                
                time1 = datetime.strptime(row_in[9], formato).time() #converte o horario_inicio para datetime
                time2 = datetime.strptime(row_in[10], formato).time() #converte o horario_fim para datetime
                time3 = datetime.strptime(horario1[0], formato).time() #converte o primeiro horario para datetime
                time4 = datetime.strptime(horario6[1], formato).time() #converte o ultimo horario para datetime


                
                # Se row não existir no arquivo de saída, escreve o novo
      
                if combinacao not in valores_unicos and time1 >= time3 and time2 <= time4: # o horario inicio deve ser >= que o nosso primeiro horario 
                    carga = 1                                                                                     # e o fim deve ser <= que o nosso ultimo horario
                    cargas[combinacao] = carga
                    if horario_no_intervalo(row_in[9],horario1[0],horario1[1]):
                        time_aux = datetime.strptime(horario2[0], formato).time()
                        if time1 <= time_aux:
                            pesos[combinacao] = 1
                            #print(row_in[0:3] + row_in[6:13] + [cargas[combinacao], pesos[combinacao]])
                        else:
                            pesos[combinacao] = 1.5
                    elif horario_entre_aulas(row_in[9],horario1[1],horario2[0]): 
                        pesos[combinacao] = 1.5
                    
                    if horario_no_intervalo(row_in[9],horario2[0],horario2[1]): 
                        time_aux = datetime.strptime(horario3[0], formato).time()
                        if time1 <= time_aux:
                            pesos[combinacao] = 2 
                        else:
                            pesos[combinacao] = 2.5 
                    
                    elif horario_entre_aulas(row_in[9],horario2[1],horario3[0]): 
                        pesos[combinacao] = 2.5


                    if horario_no_intervalo(row_in[9],horario3[0],horario3[1]): 
                        time_aux = datetime.strptime(horario4[0], formato).time()
                        if time1 <= time_aux:
                            pesos[combinacao] = 3 
                        else:
                            pesos[combinacao] = 3.5 
                    
                    elif horario_entre_aulas(row_in[9],horario3[1],horario4[0]): 
                        pesos[combinacao] = 3.5
                    if horario_no_intervalo(row_in[9],horario4[0],horario4[1]): 
                        time_aux = datetime.strptime(horario5[0], formato).time()
                        if time1 <= time_aux:
                            pesos[combinacao] = 4 
                        else:
                            pesos[combinacao] = 4.5 
                    elif horario_entre_aulas(row_in[9],horario4[1],horario5[0]): 
                        pesos[combinacao ] = 4.5
                    if horario_no_intervalo(row_in[9],horario5[0],horario5[1]): 
                        time_aux = datetime.strptime(horario6[0], formato).time()
                        if time1 <= time_aux:
                            pesos[combinacao] = 5 
                        else:
                            pesos[combinacao] = 5.5 
                    elif horario_entre_aulas(row_in[9],horario5[1],horario6[0]): 
                        pesos[combinacao] = 5.5
                    if horario_no_intervalo(row_in[9],horario6[0],horario6[1]): 
                        pesos[combinacao] = 6
                    saida = row_in[0:3] + row_in[6:13] + [cargas[combinacao], pesos[combinacao]]
                    writer.writerow(saida)
                    valores_unicos.add(combinacao)



                # Se existir, só pega o horário da disciplina e o nome dela
                elif (time1 >= time3 and time2 <= time4):
                    cargas[combinacao] = cargas[combinacao] + 1
                    if horario_no_intervalo(row_in[9],horario1[0],horario1[1]):
                        time_aux = datetime.strptime(horario2[0], formato).time()
                        if time1 <= time_aux:
                            pesos[combinacao] += 1
                            if(cargas[combinacao] > 2):
                                print(row_in[0:3] + row_in[6:13] + [cargas[combinacao], pesos[combinacao]])
                       
                    if horario_no_intervalo(row_in[9],horario2[0],horario2[1]): 
                        time_aux = datetime.strptime(horario3[0], formato).time()
                        if time1 <= time_aux:
                            pesos[combinacao] += 2 
                       
                    if horario_no_intervalo(row_in[9],horario3[0],horario3[1]): 
                        time_aux = datetime.strptime(horario4[0], formato).time()
                        if time1 <= time_aux:
                            pesos[combinacao] += 3 
                        
                    if horario_no_intervalo(row_in[9],horario4[0],horario4[1]): 
                        time_aux = datetime.strptime(horario5[0], formato).time()
                        if time1 <= time_aux:
                            pesos[combinacao] += 4 
                       
                    if horario_no_intervalo(row_in[9],horario5[0],horario5[1]): 
                        time_aux = datetime.strptime(horario6[0], formato).time()
                        if time1 <= time_aux:
                            pesos[combinacao] += 5 
                    if horario_no_intervalo(row_in[9],horario6[0],horario6[1]): 
                        pesos[combinacao] += 6

                    saida = row_in[0:3] + row_in[6:13] + [cargas[combinacao], pesos[combinacao]]
                    #print(saida)
                    writer.writerow(saida)
           else:
                nao_validos += 1

# Removendo linhas duplicadas dos horários        
#print(cont)
#print(nao_validos)
df = pd.read_csv(csv_path_out)
df_sem_duplicatas = df.drop_duplicates()
df_sem_duplicatas.to_csv(csv_path_out, index=False)
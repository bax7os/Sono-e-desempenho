import csv
from pathlib import Path
from datetime import datetime

# definiçao dos turnos
MANHA = ("07:00:00", "11:25:00")
TARDE = ("13:00:00", "16:59:00")
NOITE = ("17:00:00", "23:00:00")

# função para verificar se um horário está dentro de um turno
# turno [0,1] -> exemplo: MANHA["07:00:00", "11:25:00"]

def horario_no_turno(horario, turno):
    formato = "%H:%M:%S"
    horario = datetime.strptime(horario, formato).time()
    inicio = datetime.strptime(turno[0], formato).time()
    fim = datetime.strptime(turno[1], formato).time()
    return inicio <= horario <= fim

# função para determinar o turno de um horário
def determinar_turno(horario):
    if horario_no_turno(horario, MANHA):
        return "MANHA"
    elif horario_no_turno(horario, TARDE):
        return "TARDE"
    elif horario_no_turno(horario, NOITE):
        return "NOITE"
    else:
        return None

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


# função para encontrar e escrever matérias irregulares
# materias irregulares = matérias que acontecem em mais de 1 turno
# durante a semana

def encontrar_materias_irregulares(csv_path, csv_path_out):

    # dicionário para agrupar disciplinas por nome, seu semestre e curso
    disciplinas = {}

  
    with open(csv_path, 'r', encoding='utf-8') as file_in:
        reader = csv.reader(file_in)
        next(reader) 

        for row in reader:

            if row[8] != "EAD" and validar_formato_tempo(row[9]):    
                nome_disciplina = row[7]
                semestre = row[6]
                curso = row[0]
                horario_inicio = row[9]
                dia_semana = row[8]

                # chave única para agrupar disciplinas
                chave = (nome_disciplina, semestre, curso)

                # determinar o turno do horário atual
                turno = determinar_turno(horario_inicio)

                # se a disciplina ainda não está no dicionário, adicionar
                if chave not in disciplinas:
                    disciplinas[chave] = {
                        "turnos": set(),
                        "rows": [row],
                        "horarios_unicos": set(),
                    }
                    disciplinas[chave]["turnos"].add(turno)
                else:

                    # verificar se o turno é consistente
                    if turno not in disciplinas[chave]["turnos"]:
                        disciplinas[chave]["turnos"].add(turno)
                    disciplinas[chave]["rows"].append(row)
                    
                horario_unico = (dia_semana)
                disciplinas[chave]["horarios_unicos"].add(horario_unico)

    # escrever as matérias regulares em um novo arquivo
    with open(csv_path_out, 'w', newline='', encoding='utf-8') as file_out:
        writer = csv.writer(file_out)
        for chave, dados in disciplinas.items():
            turnos = len(dados["turnos"])
            if turnos > 1:  # apenas matérias irregulares
                # calcular a carga com base nos horários únicos (conta somente a quantidade de dias que a matéria acontece)
                carga = len(dados["horarios_unicos"])
                if carga > 4:
                    print(chave, carga)
                    print("\n")
                for row in dados["rows"]:
                    # adicionar a carga e a quantidade de turnos ao final da linha
                    row.append(carga)
                    row.append(turnos)
                    writer.writerow(row)


# caminhos dos arquivos
csv_path = Path(__file__).parent / 'include' / 'dados.csv'
csv_path_out = Path(__file__).parent / 'resultados' / 'materias_irregulares.csv'

# executar a função
encontrar_materias_irregulares(csv_path, csv_path_out)
print("Matérias regulares foram salvas em:", csv_path_out)
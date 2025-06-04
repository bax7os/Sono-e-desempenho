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


# função para encontrar e escrever matérias regulares
# materias regulares = matérias que acontecem em um único turno
# durante a semana

def encontrar_disciplinas_com_poucos_alunos(csv_path, csv_path_out, min_alunos=1, max_alunos=5):
    disciplinas = {}
    disciplinasForaDoRange = []
  
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

                chave = (nome_disciplina, semestre)

                turno = determinar_turno(horario_inicio)

                if chave not in disciplinas:
                    disciplinas[chave] = {
                        "turno": turno,
                        "rows": [row],
                        "horarios_unicos": set()
                    }
                else:
                    if disciplinas[chave]["turno"] != turno:
                        disciplinas[chave]["turno"] = None
                    disciplinas[chave]["rows"].append(row)
                    
                horario_unico = (dia_semana)
                disciplinas[chave]["horarios_unicos"].add(horario_unico)
            else:
                disciplinasForaDoRange.append(row)
    
    # Filtrar disciplinas com número de alunos no intervalo desejado
    disciplinas_filtradas = {
        chave: dados for chave, dados in disciplinas.items() 
        if min_alunos <= len(dados["rows"]) <= max_alunos
    }
    
    # Escrever no arquivo de saída
    with open(csv_path_out, 'w', newline='', encoding='utf-8') as file_out:
        writer = csv.writer(file_out)
        # Escrever cabeçalho (opcional, se quiser manter o original)
        writer.writerow(["Curso", "Semestre", "Disciplina", "Total Alunos", "Turno"])
        
        for chave, dados in disciplinas_filtradas.items():
            nome_disciplina, semestre = chave
            total_alunos = len(dados["rows"])
            turno = dados["turno"]
            
            writer.writerow([curso, semestre, nome_disciplina, total_alunos, turno])
    
    print(f"Disciplinas com entre {min_alunos} e {max_alunos} alunos encontradas: {len(disciplinas_filtradas)}")
    print(f"Arquivo salvo em: {csv_path_out}")

# Caminhos dos arquivos
csv_path = Path(__file__).parent / 'include' / 'dados.csv'
csv_path_out = Path(__file__).parent / 'resultados' / 'disciplinas_poucos_alunos.csv'

# Executar a função
encontrar_disciplinas_com_poucos_alunos(csv_path, csv_path_out)
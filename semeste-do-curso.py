import csv
import os
import unicodedata
import re
from pathlib import Path
from datetime import datetime

# definiçao dos turnos
MANHA = ("07:00:00", "11:25:00")
TARDE = ("13:00:00", "16:59:00")
NOITE = ("17:00:00", "23:00:00")

# Função para normalizar nomes de cursos (para agrupamento)
def normalizar_nome_curso(nome_curso):
    # Converter para minúsculas
    nome = nome_curso.lower()
    # Remover acentos
    nome = unicodedata.normalize('NFKD', nome).encode('ASCII', 'ignore').decode('ASCII')
    # Substituir termos equivalentes
    nome = nome.replace("curso superior de tecnologia em", "")
    nome = nome.replace("bacharelado", "")
    nome = nome.replace("-", "")
    nome = re.sub(r'\s+', ' ', nome)  # Substituir múltiplos espaços por um único
    # Remover espaços no início e fim
    nome = nome.strip()
    # Mapear variações para um nome consistente
    if "analise de sistemas" in nome or "analise e desenvolvimento de sistemas" in nome:
        return "analise e desenvolvimento de sistemas"
    elif "ciencia da computacao" in nome:
        return "ciencia da computacao"
    elif "engenharia de computacao" in nome:
        return "engenharia de computacao"
    elif "sistemas de informacao" in nome:
        return "sistemas de informacao"
    return nome

# Função para formatar nomes de arquivo
def formatar_nome_arquivo(curso, semestre):
    # Remover caracteres especiais e normalizar
    curso = re.sub(r'[\\/*?:"<>|]', "-", curso)
    curso = re.sub(r'\s+', ' ', curso).strip()
    # Formatar semestre (remover barras se existirem)
    semestre = semestre.replace("/", "-")
    return f"{curso}-{semestre}.csv"

# função para verificar se um horário está dentro de um turno
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
def validar_formato_tempo(valor):
    try:
        # Tenta analisar o valor como "%H:%M:%S"
        tempo = datetime.strptime(valor, "%H:%M:%S")
        # Rejeita valores como "0:00:00"
        if len(valor.split(":")[0]) == 1:
            return False
        return True
    except ValueError:
        return False

def separar_por_curso_e_semestre(csv_path, output_directory):
    # Create output directory if it doesn't exist
    os.makedirs(output_directory, exist_ok=True)

    # dicionário para agrupar cursos e seus respectivos semestres
    cursos_semestre = {}
  
    with open(csv_path, 'r', encoding='utf-8') as file_in:
        reader = csv.reader(file_in)
        header = next(reader)
        next(reader) 

        for row in reader:
            if len(row) > 9 and row[8] != "EAD" and validar_formato_tempo(row[9]):    
                nome_disciplina = row[7]
                semestre = row[1]
                curso = row[0]
                # Normaliza o nome do curso para agrupamento
                curso_normalizado = normalizar_nome_curso(curso)
                horario_inicio = row[9]
                dia_semana = row[8]

                # chave única para agrupar disciplinas (usando o curso normalizado)
                chave = (curso_normalizado)

                if chave not in cursos_semestre:
                    cursos_semestre[chave] = {
                        "rows": [row],
                        "curso_original": curso  # Mantém o nome original para usar no arquivo
                    }
                else:
                    cursos_semestre[chave]["rows"].append(row)

    # escrever os cursos/semestre em arquivos separados
    for chave in cursos_semestre:
        curso_normalizado = chave
        # Usa o nome original do curso (o primeiro encontrado para este grupo)
        curso_original = cursos_semestre[chave]["curso_original"]
        # Formata o nome do arquivo
        nome_arquivo = formatar_nome_arquivo(curso_original, semestre)
        file_path = os.path.join(output_directory, nome_arquivo)
        
        with open(file_path, 'w', newline='', encoding='utf-8') as file_out:
            writer = csv.writer(file_out)
            writer.writerow(header)
            for row in cursos_semestre[chave]["rows"]:
                writer.writerow(row)

# caminhos dos arquivos
csv_path = Path(__file__).parent / 'include' / 'dados.csv'
csv_path_out = Path(__file__).parent / 'resultados' 

separar_por_curso_e_semestre(csv_path, csv_path_out)
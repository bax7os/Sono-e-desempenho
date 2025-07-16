import pandas as pd
import csv
from datetime import datetime
import numpy as np

# Define the ranges for morning, afternoon, and evening
# and the specific time intervals for weight calculation
MANHA = ("07:00:00", "11:25:00")
TARDE = ("13:00:00", "16:59:00")
NOITE = ("17:00:00", "23:00:00")
HORARIO_PESOS = {
    1: ("07:00:00", "08:59:00"), 2: ("09:00:00", "11:25:00"),
    3: ("13:00:00", "14:40:00"), 4: ("15:00:00", "16:59:00"),
    5: ("17:00:00", "20:29:00"), 6: ("20:30:00", "23:00:00")
}


# Horário no intervalo definido
# Retorna True se o horário estiver dentro do intervalo, False caso contrário.
def horario_no_intervalo(horario, intervalo):
    formato = "%H:%M:%S"
    try:
        inicio = datetime.strptime(intervalo[0], formato).time()
        fim = datetime.strptime(intervalo[1], formato).time()
        return inicio <= horario <= fim
    except ValueError:
        return False

# Determina o turno baseado no horário
# Retorna "MANHA", "TARDE", "NOITE" ou "IN
def determinar_turno(horario):
    if horario_no_intervalo(horario, MANHA): return "MANHA"
    if horario_no_intervalo(horario, TARDE): return "TARDE"
    if horario_no_intervalo(horario, NOITE): return "NOITE"
    return "INDEFINIDO"

# Determina o peso do horário 
def determinar_peso_horario(horario):
    for peso, intervalo in HORARIO_PESOS.items():
        if horario_no_intervalo(horario, intervalo):
           # print("dentro de determinar_peso_horario")
           # print(f"  Peso {peso} para horário {horario} no intervalo {intervalo}")
           # print("fim do determinar_peso_horario")
            return peso
    return 0

# Valida o formato de tempo no padrão HH:MM:SS
# Retorna True se o formato for válido e o horário não for de um dígito
def validar_formato_tempo(valor):
    try:
        datetime.strptime(valor, "%H:%M:%S")
        return len(valor.split(":")[0]) != 1
    except ValueError:
        return False

# Mapeia cada disciplina a um bloco específico
# Carrega o mapa de blocos a partir de um arquivo CSV
def carregar_mapa_blocos(caminho_mapa):
   
    mapa_blocos = {}
    try:
        with open(caminho_mapa, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader) 
            for row in reader:
                if len(row) >= 2:
                    nome_disciplina = row[0]
                    bloco = row[1].strip() 
                    mapa_blocos[nome_disciplina] = bloco
        #print(f"Mapa de blocos carregado com sucesso com {len(mapa_blocos)} entradas.")
        return mapa_blocos
    except FileNotFoundError:
        #print(f"AVISO: Arquivo de mapa de blocos não encontrado em {caminho_mapa}. A coluna 'bloco' ficará vazia.")
        return {}


def analise_csv(csv_path, csv_path_out, mapa_blocos_path):

    # Leitura dos dados do CSV/ Criação do DataFrame
    try:
        df = pd.read_csv(csv_path, encoding='utf-8')
    except FileNotFoundError:
        print(f"Erro: O arquivo {csv_path} não foi encontrado.")
        return
    except pd.errors.EmptyDataError:
        print("Erro: O arquivo CSV está vazio.")
        return
    except pd.errors.ParserError:
        print("Erro: O arquivo CSV está mal formatado.")
        return 

    df = df[df['Dia da Semana'] != 'EAD'].copy()

    df['Horário-Início'] = pd.to_datetime(df['Horário Início'], format='%H:%M:%S', errors='coerce').dt.time
    df['Horário-Fim'] = pd.to_datetime(df['Horário Fim'], format='%H:%M:%S', errors='coerce').dt.time
    df.dropna(subset=['Horário-Início'], inplace=True)
    df.dropna(subset=['Horário-Fim'], inplace=True)

    df['Média-Final'] = pd.to_numeric(df['Média Final'].astype(str).str.replace(',', '.'), errors='coerce')

    df['Turno'] = df['Horário-Fim'].apply(determinar_turno)
    df['Peso-Horário'] = df['Horário-Fim'].apply(determinar_peso_horario)

    # apply executa uma função para cada grupo que for encontrado
    grade_por_aluno = df.groupby(['RGA', 'Ano/Semestre Disciplina', 'Disciplina'])[['Dia da Semana', 'Horário-Início', 'Horário-Fim']].apply( lambda x: frozenset(sorted(tuple(y) for y in x.values)))
    grade_por_aluno.name = 'grade-horarios-aluno'

    #print(grade_por_aluno.head())

    df = df.merge(grade_por_aluno, on=['RGA', 'Disciplina', 'Ano/Semestre Disciplina'], how='left')


    chave_grupo = ['Disciplina', 'Ano/Semestre Disciplina', 'grade_horarios']
    # Cálculo das metricas
    agregacoes = {
        'total_alunos_disciplina': pd.NamedAgg(column='RGA', aggfunc='nunique'),
        'carga_semanal_dias': pd.NamedAgg(column='Dia da Semana', aggfunc='nunique'),
        'turnos_distintos': pd.NamedAgg(column='Turno', aggfunc=lambda x: frozenset(x.unique())),
        'media_disciplina': pd.NamedAgg(column='Média-Final', aggfunc='mean'),
        'desvio_padrao': pd.NamedAgg(column='Média-Final', aggfunc='std')
    }

    peso_por_turma = df.drop_duplicates(subset=chave_grupo + ['Dia da Semana']) \
                       .groupby(chave_grupo)['peso_horario'].sum().reset_index(name='soma_pesos_horario')
    turmas_df = df.groupby(chave_grupo).agg(**agregacoes).reset_index()

    turmas_df = turmas_df.merge(peso_por_turma, on=chave_grupo, how='left')

    


if __name__ == "__main__":
    csv_path = 'include/dados.csv'
    csv_path_out = 'resultados/materias_regulares.csv'
    mapa_blocos_path = 'disciplinas-bloco.csv'

    mapa_blocos = carregar_mapa_blocos(mapa_blocos_path)
    analise_csv(csv_path, csv_path_out, mapa_blocos)
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

# (O início da sua função)
def filtrar_e_salvar_csv_sem_poucos_alunos(csv_path, csv_path_out, min_alunos=1, max_alunos=5):
    disciplinas = {}
    # ... (resto das variáveis)
    
    with open(csv_path, 'r', encoding='utf-8') as file_in:
        reader = csv.reader(file_in)
        cabecalho = next(reader)
        
        # Para controlar o número de linhas a processar durante o teste
        contador_linhas = 0

        for row in reader:
            # (Seus filtros aqui)
            if row[8] != "EAD" and validar_formato_tempo(row[9]):    
                nome_disciplina = row[7]
                semestre = row[6]
                chave = (nome_disciplina, semestre)
                
                # Matrícula do aluno na linha atual
                matricula_aluno_atual = row[2]

                print(f"--- Processando Linha: ---")
                print(f"Chave identificada: {chave}")

                if chave not in disciplinas:
                    print(f"-> Chave é NOVA. Criando entrada para '{chave}'.")
                    # Cria a chave e adiciona a PRIMEIRA linha inteira
                    disciplinas[chave] = [row] 
                    print(f"-> Estado ATUAL de '{chave}': {disciplinas[chave]}")

                else:
                    print(f"-> Chave JÁ EXISTE: '{chave}'. Verificando se aluno '{matricula_aluno_atual}' já foi adicionado.")
                    print(f"-> Estado ANTES da adição: {disciplinas[chave]}")

                    # --- CORREÇÃO DO BUG ESTÁ AQUI ---
                    # Precisamos verificar apenas a matrícula (índice 2) em cada linha já salva
                    matriculas_ja_salvas = [linha_salva[2] for linha_salva in disciplinas[chave]]
                    
                    if matricula_aluno_atual not in matriculas_ja_salvas:
                        print(f"-> Aluno '{matricula_aluno_atual}' é NOVO para esta disciplina. Adicionando.")
                        disciplinas[chave].append(row)
                        print(f"-> Estado DEPOIS da adição: {disciplinas[chave]}")
                    else:
                        print(f"-> Aluno '{matricula_aluno_atual}' já existe na lista. Ignorando linha duplicada.")
                
                print("="*50) 

            
    

   
    cabecalho_saida = ['Nome_Disciplina', 'Semestre', 'Quantidade_Alunos']

    with open(csv_path_out, 'w', newline='', encoding='utf-8') as file_out:
        writer = csv.writer(file_out)
        writer.writerow(cabecalho_saida) 

  
        for chave, linhas in disciplinas.items():
           
            nome_disciplina = chave[0]
            semestre = chave[1]
            
     
            quantidade_alunos = len(linhas)
           
            writer.writerow([nome_disciplina, semestre, quantidade_alunos])

    print(f"Arquivo de resumo salvo em: {csv_path_out}")





# Caminhos dos arquivos
csv_path = Path(__file__).parent / 'include' / 'teste.csv'
csv_path_out = Path(__file__).parent / 'resultados' / 'numero_de_alunos.csv'

# Executar a função
filtrar_e_salvar_csv_sem_poucos_alunos(csv_path, csv_path_out)


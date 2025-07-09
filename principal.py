import csv
from pathlib import Path
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
def horario_no_intervalo(horario_str, intervalo):
    formato = "%H:%M:%S"
    try:
        horario = datetime.strptime(horario_str, formato).time()
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




def processar_disciplinas(lista_caminhos_entrada, caminho_mapa_blocos, caminho_saida_regulares, caminho_saida_irregulares):
    mapa_blocos = carregar_mapa_blocos(caminho_mapa_blocos)
    
    ### FASE PRELIMINAR: MAPEAMENTO ALUNO-DISCIPLINA -> GRADE DE HORÁRIOS ###
    #print("FASE PRELIMINAR: Mapeando alunos às suas grades de horários...")
    mapa_aluno_horarios = {}
    for caminho_entrada in lista_caminhos_entrada:
        if not caminho_entrada.exists(): continue
        with open(caminho_entrada, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader) 
            for row in reader:
                if len(row) > 9 and validar_formato_tempo(row[9]):
                    matricula = row[2] # rga
                    nome_disciplina = row[7]
                    semestre = row[6] # semestre da disciplina
                    dia = row[8]
                    horario = row[9]
                    
                    chave_aluno = (matricula, nome_disciplina, semestre)
                    if chave_aluno not in mapa_aluno_horarios:
                        mapa_aluno_horarios[chave_aluno] = set()
                    
                    mapa_aluno_horarios[chave_aluno].add((dia, horario))

    # Converte os sets de horários em frozensets (que podem ser usados em chaves de dicionário)
    for chave, valor in mapa_aluno_horarios.items():
        mapa_aluno_horarios[chave] = frozenset(sorted(list(valor))) # Ordenar para consistência

   
    #print("\nFASE 1: Lendo todos os cursos e agregando dados por turma...")
    disciplinas_globais = {}
    cabecalho_original = None

    for caminho_entrada in lista_caminhos_entrada:
        if not caminho_entrada.exists(): continue
        #print(f"  Lendo: {caminho_entrada.name}")
        with open(caminho_entrada, 'r', encoding='utf-8') as file_in:
           
            reader = csv.reader(file_in)
            current_header = next(reader)
            if cabecalho_original is None: cabecalho_original = current_header

            for row in reader:
                if len(row) > 11 and row[8] != "EAD" and validar_formato_tempo(row[9]):
                   # print("\n")
                    #print("==============================================================================================")
                    matricula = row[2]
                    nome_disciplina = row[7]
                    semestre = row[6]

                    # Busca a grade de horários específica deste aluno para esta disciplina
                    chave_aluno_lookup = (matricula, nome_disciplina, semestre)
                    grade_horarios = mapa_aluno_horarios.get(chave_aluno_lookup)
                    #print(f"  Chave aluno: {chave_aluno_lookup} -> Grade de horários: {grade_horarios}")
                    if grade_horarios is None: continue 
                    #print("\n")
                    # A NOVA CHAVE GLOBAL INCLUI A GRADE DE HORÁRIOS
                    chave_global = (nome_disciplina, semestre, grade_horarios)
                    #print(f"  Chave global: {chave_global}")
                    #print("\n")
                    if chave_global not in disciplinas_globais:
                        disciplinas_globais[chave_global] = {
                            "turnos": set(), "alunos": set(), "soma_notas": 0.0,
                            "contagem_notas": 0, "dias_semana": set(), "soma_pesos_horario": 0,
                            "rows": [],
                            "notas": [],
                            "dias_checked": set()
                        }

                    # Adiciona os dados da disciplina à chave global
                    dados_disciplina = disciplinas_globais[chave_global]
                    #print(f"  Dados da disciplina: {dados_disciplina}")
                    #print("\n")
                    dados_disciplina["turnos"].add(determinar_turno(row[9]))
                    #print(f"  Turnos até agora: {dados_disciplina['turnos']}")
                    #print("\n")
                    dados_disciplina["dias_semana"].add(row[8])
                    #print(f"  Dias da semana até agora: {dados_disciplina['dias_semana']}")
                    #print("\n")
             
                   
                    #print(f"  Processando {nome_disciplina} ({semestre}) para aluno {matricula} com horários {grade_horarios})")
                    #print("\n")
                    if row[8] not in dados_disciplina["dias_checked"]:
                        dados_disciplina["soma_pesos_horario"] += determinar_peso_horario(row[9])
                        dados_disciplina["dias_checked"].add(row[8])
                  
                    #print("\n")
                    #print(f"  Peso horário: {determinar_peso_horario(row[9])} para horário {row[9]}")
                    #print(f"  Soma pesos até agora: {dados_disciplina['soma_pesos_horario']}")
                    #print("\n")

                    #print("\n")

                    if matricula not in dados_disciplina["alunos"]:
                        dados_disciplina["alunos"].add(matricula)
                        try:
                            nota = float(row[11].replace(',', '.'))
                            dados_disciplina["soma_notas"] += nota
                            dados_disciplina["contagem_notas"] += 1
                            dados_disciplina["notas"].append(nota)
                        except (ValueError, IndexError): pass
                    
                    dados_disciplina["rows"].append(row)


    if cabecalho_original is None:
      #  print("\nERRO CRÍTICO: Nenhum arquivo de entrada foi lido. O programa não pode continuar.")
        return

    
   # print("\nFASE 2: Calculando métricas e escrevendo arquivos de saída unificados...")
    
    with open(caminho_saida_regulares, 'w', newline='', encoding='utf-8') as f_reg, \
         open(caminho_saida_irregulares, 'w', newline='', encoding='utf-8') as f_irreg:
        
        writer_reg = csv.writer(f_reg)
        writer_irreg = csv.writer(f_irreg)

        # Define cabeçalhos. 'bloco_disciplina' é adicionada em ambos.
        cabecalho_irregulares = cabecalho_original + ["bloco_disciplina"]
        cabecalho_regulares = cabecalho_original + ["bloco_disciplina", "turno_predominante", "total_alunos_disciplina", "carga_semanal_dias", "peso_final", "media_disciplina", "desvio_padrao"]
        
        writer_reg.writerow(cabecalho_regulares)
        writer_irreg.writerow(cabecalho_irregulares)

        for chave, dados in disciplinas_globais.items():
            nome_disciplina_chave = chave[0]
            bloco_disciplina = mapa_blocos.get(nome_disciplina_chave, 'N/A') # Consulta o bloco

            num_alunos = len(dados["alunos"])
            carga = len(dados["dias_semana"])
            media_disciplina = (dados["soma_notas"] / dados["contagem_notas"]) if dados["contagem_notas"] > 0 else 0.0
            peso_final = (dados["soma_pesos_horario"] / carga) if carga > 0 else 0.0
            notas = dados.get("notas", [])
            desvio_padrao = (np.std(notas) if notas else 0.0)
            is_regular = len(dados["turnos"]) == 1

            for linha in dados["rows"]:
                if is_regular:
                    turno_predominante = list(dados["turnos"])[0]
                    linha_enriquecida = linha + [
                        bloco_disciplina, turno_predominante, num_alunos, carga,
                        f"{peso_final:.2f}", f"{media_disciplina:.2f}", f"{desvio_padrao:.2f}"
                    ]
                    #if num_alunos > 90:
                        #print(f"AVISO: Disciplina com mais de 90 alunos: {linha_enriquecida}")
                    writer_reg.writerow(linha_enriquecida)
                else:
                    linha_enriquecida = linha + [bloco_disciplina]
                    writer_irreg.writerow(linha_enriquecida)

    print("\nProcessamento concluído.")
    print(f"Matérias regulares salvas em: {caminho_saida_regulares}")
    print(f"Matérias irregulares salvas em: {caminho_saida_irregulares}")


if __name__ == "__main__":
    pasta_base = Path(__file__).parent
    pasta_entrada = pasta_base / 'include'
    pasta_saida = pasta_base / 'resultados'
    pasta_saida.mkdir(exist_ok=True)

    # Lista de nomes dos arquivos de curso para processar

    nomes_dos_cursos_csv = [
        "AS.csv", "CC.csv", "CSRC.csv",
        "EC.csv", "ES.csv", "SI.csv"
    ]
    # Cria a lista completa de caminhos para os arquivos de entrada
    caminhos_entrada = [pasta_entrada / nome for nome in nomes_dos_cursos_csv]

    # Caminho para o novo arquivo de mapeamento
    caminho_mapa_blocos = pasta_base / "disciplinas-bloco.csv"

    # Caminhos para os DOIS arquivos de saída finais
    caminho_saida_regulares = pasta_saida / "materias_regulares_enriquecido.csv"
    caminho_saida_irregulares = pasta_saida / "materias_irregulares.csv"
    
    processar_disciplinas(
        caminhos_entrada,
        caminho_mapa_blocos,
        caminho_saida_regulares,
        caminho_saida_irregulares
    )
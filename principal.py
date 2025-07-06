import csv
from pathlib import Path
from datetime import datetime

# ==============================================================================
# 1. DEFINIÇÕES E FUNÇÕES AUXILIARES
# ==============================================================================

# Definições de turno, peso, e funções de validação (sem alterações)
MANHA = ("07:00:00", "11:25:00")
TARDE = ("13:00:00", "16:59:00")
NOITE = ("17:00:00", "23:00:00")
HORARIO_PESOS = {
    1: ("07:00:00", "08:59:00"), 2: ("09:00:00", "11:25:00"),
    3: ("13:00:00", "14:40:00"), 4: ("15:00:00", "16:59:00"),
    5: ("17:00:00", "20:29:00"), 6: ("20:30:00", "23:00:00")
}

def horario_no_intervalo(horario_str, intervalo):
    formato = "%H:%M:%S"
    try:
        horario = datetime.strptime(horario_str, formato).time()
        inicio = datetime.strptime(intervalo[0], formato).time()
        fim = datetime.strptime(intervalo[1], formato).time()
        return inicio <= horario <= fim
    except ValueError:
        return False

def determinar_turno(horario):
    if horario_no_intervalo(horario, MANHA): return "MANHA"
    if horario_no_intervalo(horario, TARDE): return "TARDE"
    if horario_no_intervalo(horario, NOITE): return "NOITE"
    return "INDEFINIDO"

def determinar_peso_horario(horario):
    for peso, intervalo in HORARIO_PESOS.items():
        if horario_no_intervalo(horario, intervalo):
            return peso
    return 0

def validar_formato_tempo(valor):
    try:
        datetime.strptime(valor, "%H:%M:%S")
        return len(valor.split(":")[0]) != 1
    except ValueError:
        return False

### NOVA FUNÇÃO ###
def carregar_mapa_blocos(caminho_mapa):
    """Lê o arquivo de disciplinas-bloco e retorna um dicionário para consulta."""
    mapa_blocos = {}
    try:
        with open(caminho_mapa, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader) # Pula o cabeçalho
            for row in reader:
                if len(row) >= 2:
                    nome_disciplina = row[0]
                    bloco = row[1]
                    mapa_blocos[nome_disciplina] = bloco
        print(f"Mapa de blocos carregado com sucesso com {len(mapa_blocos)} entradas.")
        return mapa_blocos
    except FileNotFoundError:
        print(f"AVISO: Arquivo de mapa de blocos não encontrado em {caminho_mapa}. A coluna 'bloco' ficará vazia.")
        return {}


# ==============================================================================
# 2. FUNÇÃO PRINCIPAL DE PROCESSAMENTO (LÓGICA REVISADA)
# ==============================================================================

def processar_disciplinas(lista_caminhos_entrada, caminho_mapa_blocos, caminho_saida_regulares, caminho_saida_irregulares):
    mapa_blocos = carregar_mapa_blocos(caminho_mapa_blocos)
    
    ### FASE PRELIMINAR: MAPEAMENTO ALUNO-DISCIPLINA -> GRADE DE HORÁRIOS ###
    print("FASE PRELIMINAR: Mapeando alunos às suas grades de horários...")
    mapa_aluno_horarios = {}
    for caminho_entrada in lista_caminhos_entrada:
        if not caminho_entrada.exists(): continue
        with open(caminho_entrada, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader) # Pula cabeçalho
            for row in reader:
                if len(row) > 9 and validar_formato_tempo(row[9]):
                    matricula = row[2]
                    nome_disciplina = row[7]
                    semestre = row[6]
                    dia = row[8]
                    horario = row[9]
                    
                    chave_aluno = (matricula, nome_disciplina, semestre)
                    if chave_aluno not in mapa_aluno_horarios:
                        mapa_aluno_horarios[chave_aluno] = set()
                    mapa_aluno_horarios[chave_aluno].add((dia, horario))

    # Converte os sets de horários em frozensets (que podem ser usados em chaves de dicionário)
    for chave, valor in mapa_aluno_horarios.items():
        mapa_aluno_horarios[chave] = frozenset(sorted(list(valor))) # Ordenar para consistência

    ### FASE 1: AGREGAR DADOS DE TODOS OS ARQUIVOS ###
    print("\nFASE 1: Lendo todos os cursos e agregando dados por turma...")
    disciplinas_globais = {}
    cabecalho_original = None

    for caminho_entrada in lista_caminhos_entrada:
        if not caminho_entrada.exists(): continue
        print(f"  Lendo: {caminho_entrada.name}")
        with open(caminho_entrada, 'r', encoding='utf-8') as file_in:
            reader = csv.reader(file_in)
            current_header = next(reader)
            if cabecalho_original is None: cabecalho_original = current_header

            for row in reader:
                if len(row) > 11 and row[8] != "EAD" and validar_formato_tempo(row[9]):
                    matricula = row[2]
                    nome_disciplina = row[7]
                    semestre = row[6]

                    # Busca a grade de horários específica deste aluno para esta disciplina
                    chave_aluno_lookup = (matricula, nome_disciplina, semestre)
                    grade_horarios = mapa_aluno_horarios.get(chave_aluno_lookup)

                    if grade_horarios is None: continue # Ignora se não encontrar o mapeamento

                    # A NOVA CHAVE GLOBAL INCLUI A GRADE DE HORÁRIOS
                    chave_global = (nome_disciplina, semestre, grade_horarios)

                    if chave_global not in disciplinas_globais:
                        disciplinas_globais[chave_global] = {
                            "turnos": set(), "alunos": set(), "soma_notas": 0.0,
                            "contagem_notas": 0, "dias_semana": set(), "soma_pesos_horario": 0,
                            "rows": []
                        }

                    # O resto da lógica de agregação permanece o mesmo
                    dados_disciplina = disciplinas_globais[chave_global]
                    dados_disciplina["turnos"].add(determinar_turno(row[9]))
                    dados_disciplina["dias_semana"].add(row[8])
                    dados_disciplina["soma_pesos_horario"] += determinar_peso_horario(row[9])
                    
                    if matricula not in dados_disciplina["alunos"]:
                        dados_disciplina["alunos"].add(matricula)
                        try:
                            nota = float(row[11].replace(',', '.'))
                            dados_disciplina["soma_notas"] += nota
                            dados_disciplina["contagem_notas"] += 1
                        except (ValueError, IndexError): pass
                    
                    dados_disciplina["rows"].append(row)


    if cabecalho_original is None:
        print("\nERRO CRÍTICO: Nenhum arquivo de entrada foi lido. O programa não pode continuar.")
        return

    # --- FASE 2: CALCULAR MÉTRICAS E ESCREVER ARQUIVOS DE SAÍDA UNIFICADOS ---
    print("\nFASE 2: Calculando métricas e escrevendo arquivos de saída unificados...")
    
    with open(caminho_saida_regulares, 'w', newline='', encoding='utf-8') as f_reg, \
         open(caminho_saida_irregulares, 'w', newline='', encoding='utf-8') as f_irreg:
        
        writer_reg = csv.writer(f_reg)
        writer_irreg = csv.writer(f_irreg)

        # Define cabeçalhos. 'bloco_disciplina' é adicionada em ambos.
        cabecalho_irregulares = cabecalho_original + ["bloco_disciplina"]
        cabecalho_regulares = cabecalho_original + ["bloco_disciplina", "turno_predominante", "total_alunos_disciplina", "carga_semanal_dias", "peso_final", "media_disciplina"]
        
        writer_reg.writerow(cabecalho_regulares)
        writer_irreg.writerow(cabecalho_irregulares)

        for chave, dados in disciplinas_globais.items():
            nome_disciplina_chave = chave[0]
            bloco_disciplina = mapa_blocos.get(nome_disciplina_chave, 'N/A') # Consulta o bloco

            num_alunos = len(dados["alunos"])
            carga = len(dados["dias_semana"])
            media_disciplina = (dados["soma_notas"] / dados["contagem_notas"]) if dados["contagem_notas"] > 0 else 0.0
            peso_final = (dados["soma_pesos_horario"] / carga) if carga > 0 else 0.0
            
            is_regular = len(dados["turnos"]) == 1

            for linha in dados["rows"]:
                if is_regular:
                    turno_predominante = list(dados["turnos"])[0]
                    linha_enriquecida = linha + [
                        bloco_disciplina, turno_predominante, num_alunos, carga,
                        f"{peso_final:.2f}", f"{media_disciplina:.2f}"
                    ]
                    if num_alunos > 90:
                        print(f"AVISO: Disciplina com mais de 90 alunos: {linha_enriquecida}")
                    writer_reg.writerow(linha_enriquecida)
                else:
                    linha_enriquecida = linha + [bloco_disciplina]
                    writer_irreg.writerow(linha_enriquecida)

    print("\nProcessamento concluído.")
    print(f"Matérias regulares salvas em: {caminho_saida_regulares}")
    print(f"Matérias irregulares salvas em: {caminho_saida_irregulares}")

# ==============================================================================
# 3. EXECUÇÃO PRINCIPAL
# ==============================================================================
if __name__ == "__main__":
    pasta_base = Path(__file__).parent
    pasta_entrada = pasta_base / 'include'
    pasta_saida = pasta_base / 'resultados'
    pasta_saida.mkdir(exist_ok=True)

    # Lista de nomes dos arquivos de curso para processar
    nomes_dos_cursos_csv = [
        "AS.csv", "CC.csv", "CSRC.csv",
        "EC.csv", "ES.csv", "SI.csv"
        # Adicione mais arquivos de curso aqui, se necessário
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
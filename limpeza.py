import csv
from pathlib import Path

def limpar_arquivos_finais(caminho_entrada, caminho_saida, eh_regular):
    """
    Lê um arquivo de saída processado e aplica filtros para limpá-lo,
    removendo disciplinas com poucos alunos, sem bloco definido ou com carga excessiva.

    :param caminho_entrada: Path do arquivo a ser lido.
    :param caminho_saida: Path do arquivo limpo a ser salvo.
    :param eh_regular: Booleano que indica se o arquivo é de matérias regulares
                        (para saber quais colunas esperar).
    """
    linhas_mantidas = []
    cabecalho = None

    try:
        with open(caminho_entrada, 'r', encoding='utf-8') as file_in:
            reader = csv.reader(file_in)
            cabecalho = next(reader)
            linhas_mantidas.append(cabecalho) # Mantém o cabeçalho no novo arquivo

            # Encontra os índices das colunas importantes pelo nome
            # Isso torna o código mais robusto a mudanças na ordem das colunas
            try:
                if eh_regular:
                    idx_bloco = cabecalho.index('bloco_disciplina')
                    idx_total_alunos = cabecalho.index('total_alunos_disciplina')
                    idx_carga = cabecalho.index('carga_semanal_dias')
                else: # Arquivo de irregulares tem menos colunas
                    idx_bloco = cabecalho.index('bloco_disciplina')
                    # Para irregulares, não temos as colunas de métricas, então não podemos filtrar por elas.
                    # Se precisar filtrar, os dados teriam que ser adicionados no script anterior.
                    # Por enquanto, filtraremos irregulares apenas por bloco.
                    idx_total_alunos = -1 # Indica que o filtro não se aplica
                    idx_carga = -1 # Indica que o filtro não se aplica

            except ValueError as e:
                print(f"ERRO: Coluna não encontrada no arquivo {caminho_entrada.name}: {e}")
                return # Interrompe a função se o cabeçalho estiver incorreto

            # Itera sobre cada linha do arquivo de dados
            for row in reader:
                # Condições de filtro
                bloco_ok = row[idx_bloco] != 'N/A'

                # Aplica filtros de alunos e carga apenas se as colunas existirem (para arq. regulares)
                alunos_ok = True
                carga_ok = True
                
                if idx_total_alunos != -1:
                    try:
                        total_alunos = int(row[idx_total_alunos])
                        alunos_ok = total_alunos >= 5
                    except ValueError:
                        alunos_ok = False # Se o valor não for um número, remove a linha

                if idx_carga != -1:
                    try:
                        carga = int(row[idx_carga])
                        carga_ok = carga <= 3
                    except ValueError:
                        carga_ok = False # Se o valor não for um número, remove a linha

                # Se todas as condições forem atendidas, mantém a linha
                if bloco_ok and alunos_ok and carga_ok:
                    linhas_mantidas.append(row)

    except FileNotFoundError:
        print(f"AVISO: Arquivo de entrada para limpeza não encontrado: {caminho_entrada}")
        return

    # Escreve o novo arquivo "limpo"
    with open(caminho_saida, 'w', newline='', encoding='utf-8') as file_out:
        writer = csv.writer(file_out)
        writer.writerows(linhas_mantidas)
    
    # -1 para não contar o cabeçalho
    print(f"Arquivo limpo salvo em: {caminho_saida.name} com {len(linhas_mantidas) - 1} linhas de dados.")

# ==============================================================================
# EXECUÇÃO PRINCIPAL
# ==============================================================================
if __name__ == "__main__":
    pasta_resultados = Path(__file__).parent / 'resultados'
    
    # Garante que a pasta de saída exista
    pasta_resultados.mkdir(exist_ok=True)

    print("Iniciando processo de limpeza dos arquivos finais...")
    print("-" * 50)

    # 1. Limpar o arquivo de matérias REGULARES
    # Para este arquivo, aplicamos TODOS os filtros.
    caminho_reg_entrada = pasta_resultados / "materias_regulares_enriquecido.csv"
    caminho_reg_saida = pasta_resultados / "materias_regulares_FINAL_LIMPO.csv"
    limpar_arquivos_finais(caminho_reg_entrada, caminho_reg_saida, eh_regular=True)
    
    print("-" * 50)

    # 2. Limpar o arquivo de matérias IRREGULARES
    # Para este arquivo, só podemos aplicar o filtro de 'bloco', pois não
    # temos as colunas de 'total_alunos' e 'carga'.
    caminho_irreg_entrada = pasta_resultados / "materias_irregulares.csv"
    caminho_irreg_saida = pasta_resultados / "materias_irregulares_FINAL_LIMPO.csv"
    limpar_arquivos_finais(caminho_irreg_entrada, caminho_irreg_saida, eh_regular=False)

    print("-" * 50)
    print("Limpeza concluída.")
import pandas as pd
from pathlib import Path
import logging

BASE_PATH = Path(__file__).resolve().parent.parent
RESULTS_FOLDER = BASE_PATH / "results"
INPUT_CSV_PATH = RESULTS_FOLDER / "materias_regulares.csv"


logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')


def load_data(file_path: Path) -> pd.DataFrame:
    """Carrega os dados de um arquivo CSV."""
    logging.info(f"Carregando dados de: {file_path}")
    if not file_path.exists():
        logging.error(f"Arquivo de entrada não encontrado: {file_path}")
        raise FileNotFoundError(f"O arquivo especificado não foi encontrado.")
    return pd.read_csv(file_path, encoding='utf-8')

def verify_discipline_grouping(df: pd.DataFrame):
    """
    Agrupa o DataFrame por 'bloco' e imprime as disciplinas únicas de cada um.
    """
    # Verifica se as colunas necessárias existem no DataFrame
    required_columns = ['bloco', 'Disciplina']
    if not all(col in df.columns for col in required_columns):
        logging.error(f"O DataFrame não contém as colunas necessárias: {required_columns}")
        return

    logging.info("Iniciando a verificação do agrupamento de disciplinas por bloco...")

    # A linha principal: agrupa por 'bloco' e, para cada grupo,
    # pega os valores únicos da coluna 'Disciplina' e os coloca em uma lista ordenada.
    grouping = df.groupby('bloco')['Disciplina'].agg(lambda x: sorted(list(x.unique())))

    if grouping.empty:
        logging.warning("Nenhum agrupamento pôde ser criado. O DataFrame pode estar vazio ou sem blocos definidos.")
        return

    print("\n--- Relatório de Agrupamento de Disciplinas por Bloco ---")
    # Itera sobre o resultado (que é uma pandas Series) e imprime de forma legível
    for block_name, disciplines in grouping.items():
        print(f"\nBLOCO: {block_name} ({len(disciplines)} disciplinas únicas)")
        print("-" * (len(block_name) + 8))
        for discipline in disciplines:
            print(f"  - {discipline}")
    
    print("\n---------------------------------------------------------")
    logging.info(f"Verificação concluída. Total de {len(grouping)} blocos encontrados.")


# =============================================================================
# 3. FUNÇÃO PRINCIPAL (ORQUESTRADORA)
# =============================================================================

def run_verification():
    """Orquestra o processo de verificação."""
    try:
        processed_df = load_data(INPUT_CSV_PATH)
        verify_discipline_grouping(processed_df)
    except FileNotFoundError as e:
        logging.error(e)
    except Exception as e:
        logging.error(f"Ocorreu um erro inesperado: {e}", exc_info=True)

# =============================================================================
# 4. EXECUÇÃO
# =============================================================================

if __name__ == "__main__":
    run_verification()
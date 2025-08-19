import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime
import numpy as np
import logging
from typing import List, Dict, Any

BASE_PATH = Path(__file__).parent.parent
print(BASE_PATH)
RESULTS_FOLDER = BASE_PATH / 'results'
INPUT_CSV_PATH = RESULTS_FOLDER / 'materias_regulares.csv'
OUTPUT_PLOT_PATH = RESULTS_FOLDER / 'grafico_correlacao.png'

MIN_STUDENTS_FILTER = 5
MAX_WEEKLY_CLASSES_FILTER = 3
BLOCK_NUN = "N/A"

COLS_FOR_CORRELATION = [
    'media_disciplina',
    'turno_predominante',
    'taxa_aprovacao',
    'taxa_reprovacao',
    'bloco'
]

NUMERIC_COLS_TO_CONVERT = [
    'media_disciplina',
    'taxa_aprovacao',
    'taxa_reprovacao']
CATEGORICAL_COLS_TO_CONVERT = [
    'turno_predominante',
    'bloco'
]

PLOT_CONFIG = {
    "figsize": (12, 10),
    "cmap": "coolwarm",
    "annot": True,
    "fmt": ".2f",
    "linewidths": 0.5,
    "title": "Matriz de Correlação das Variáveis das Disciplinas",
    "fontsize": 16,
    "dpi": 300
}

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_analysis_data(file_path: Path) -> pd.DataFrame:
    if not file_path.exists():
        logging.error(f"Arquivo nao encontrado em: '{file_path}'...")
        raise FileNotFoundError(f"Arquivo nao encontrado em: '{file_path}'...")
    return pd.read_csv(file_path, encoding='utf-8')

def filter_data(df: pd.DataFrame, min_students: int, max_weekly_classes: int) -> pd.DataFrame:
    return df[
        (df['total_alunos_disciplina'] >= min_students) &
        (df['carga_semanal_dias'] <= max_weekly_classes) &
        (df['bloco'] != BLOCK_NUN)
    ].copy()

def prepare_data_for_correlation(df: pd.DataFrame, num_cols: list, cat_cols: list) -> pd.DataFrame:
    
    analysis_df = df[COLS_FOR_CORRELATION].copy()

    for col in num_cols:
        analysis_df[col] = pd.to_numeric(analysis_df[col], errors='coerce')
    
    analysis_df.dropna(inplace=True)
    analysis_df = pd.get_dummies(analysis_df, columns=cat_cols, dtype=float)
    
    return analysis_df

def generate_and_save_heatmap(df: pd.DataFrame, output_path: Path, config: Dict[str, Any]):
    corr_matrix = df.corr()
    mask = np.triu(np.ones_like(corr_matrix, dtype=bool))

    plt.figure(figsize=config['figsize'])
    heatmap = sns.heatmap(corr_matrix, mask=mask, cmap=config['cmap'], annot=config['annot'], fmt=config['fmt'], linewidths=config['linewidths'])
    plt.title(config['title'], fontsize=config['fontsize'])
    heatmap.set_xticklabels(heatmap.get_xticklabels(), rotation=45, ha='right', fontsize=config['fontsize'])
    plt.tight_layout()

    plt.savefig(output_path, dpi=config['dpi'])
    logging.info(f"Gráfico salvo com sucesso em: {output_path}")

def run_correlation_analysis():
    try:
        raw_df = load_analysis_data(INPUT_CSV_PATH)
        filtered_df = filter_data(raw_df, MIN_STUDENTS_FILTER, MAX_WEEKLY_CLASSES_FILTER)

        if filtered_df.empty:
            logging.warning("Nenhum dado restou depois dos filtros. O gráfico de correlação nao sera gerado.")
            return
        
        correlation_ready_df = prepare_data_for_correlation(filtered_df, NUMERIC_COLS_TO_CONVERT, CATEGORICAL_COLS_TO_CONVERT)

        generate_and_save_heatmap(correlation_ready_df, OUTPUT_PLOT_PATH, PLOT_CONFIG)
    except FileNotFoundError as e:
        logging.error(str(e))
    except Exception as e:
        logging.error(str(e))
 
if __name__ == "__main__":
    RESULTS_FOLDER.mkdir(parents=True, exist_ok=True)
    run_correlation_analysis()
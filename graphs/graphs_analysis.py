import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path
import logging

BASE_PATH = Path(__file__).resolve().parent.parent
RESULTS_FOLDER = BASE_PATH / 'results'
INPUT_CSV_PATH = RESULTS_FOLDER / 'materias_regulares.csv'
OUTPUT_PLOT_PATH = RESULTS_FOLDER / 'media_turno_bloco_inma.png'
OUTPUT_CSV_PATH = RESULTS_FOLDER / 'analise_bloco_inma_agregado.csv'

TARGET_BLOCK = 'INMA'

PLOT_CONFIG = {
    "figsize": (15, 8),
    "title": f"Média de Notas por Turno ao Longo do Tempo - Bloco {TARGET_BLOCK}",
    "xlabel": "Ano/Semestre da Disciplina",
    "ylabel": "Média Final da Disciplina",
    "dpi": 300
}

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_data(file_path: Path) -> pd.DataFrame:
    logging.info(f"Carregando dados de: {file_path}")
    if not file_path.exists():
        logging.error(f"Arquivo de entrada não encontrado: {file_path}")
        raise FileNotFoundError(f"Arquivo de entrada não encontrado: {file_path}.")
    return pd.read_csv(file_path, encoding='utf-8')

def prepare_data_for_plot(df: pd.DataFrame, target_block: str) -> pd.DataFrame:
    logging.info(f"Preparando dados para gráfico com média ponderada por alunos...")
    
    COLUNA_ALUNOS = 'total_alunos_disciplina' 

    if COLUNA_ALUNOS not in df.columns:
        logging.error(f"A coluna '{COLUNA_ALUNOS}' não foi encontrada no CSV!")
        raise KeyError(f"A coluna de alunos '{COLUNA_ALUNOS}' não existe no DataFrame.")

    df['media_disciplina'] = pd.to_numeric(df['media_disciplina'], errors='coerce')
    df[COLUNA_ALUNOS] = pd.to_numeric(df[COLUNA_ALUNOS], errors='coerce')
    df.dropna(subset=['media_disciplina', COLUNA_ALUNOS], inplace=True)
    df = df[df[COLUNA_ALUNOS] > 0].copy()

    df['bloco'] = df['bloco'].astype(str).str.upper()
    analysis_df = df[df['bloco'] == target_block.upper()].copy()

    unique_classes_df = analysis_df.drop_duplicates(
        subset=['Ano/Semestre Disciplina', 'Disciplina', 'turno_predominante']
    )
    logging.info(f"Registros únicos de turmas encontrados: {len(unique_classes_df)}")
    
    if unique_classes_df.empty:
        logging.warning("Nenhuma turma encontrada para o bloco especificado após a filtragem.")
        return pd.DataFrame()

    unique_classes_df['soma_ponderada'] = unique_classes_df['media_disciplina'] * unique_classes_df[COLUNA_ALUNOS]

    grouped = unique_classes_df.groupby(['Ano/Semestre Disciplina', 'turno_predominante'])

    agg_calcs = grouped.agg(
        soma_total_ponderada=('soma_ponderada', 'sum'),
        soma_total_alunos=(COLUNA_ALUNOS, 'sum'),
        desvio_padrao_das_medias=('media_disciplina', 'std')
    ).reset_index()

    agg_calcs['media_das_medias'] = agg_calcs['soma_total_ponderada'] / agg_calcs['soma_total_alunos']
    agg_calcs['desvio_padrao_das_medias'] = agg_calcs['desvio_padrao_das_medias'].fillna(0)
    
    aggregated_df = agg_calcs[['Ano/Semestre Disciplina', 'turno_predominante', 'media_das_medias', 'desvio_padrao_das_medias']]
    aggregated_df = aggregated_df.sort_values(by='Ano/Semestre Disciplina')

    logging.info(f"Dados agregados (média ponderada) prontos para plotagem.")
    return aggregated_df

def create_performance_over_time_plot(df: pd.DataFrame, output_path: Path):
    if df.empty:
        logging.warning("DataFrame vazio após a preparação. O gráfico não será gerado.")
        return
    
    logging.info("Gerando gráfico a partir de dados agregados...")

    plt.style.use('seaborn-v0_8-whitegrid')
    fig, ax = plt.subplots(figsize=PLOT_CONFIG['figsize']) 

    colors = sns.color_palette("colorblind", n_colors=len(df['turno_predominante'].unique()))
    turnos = df['turno_predominante'].unique()
    for i, turno in enumerate(turnos):
        turno_df = df[df['turno_predominante'] == turno]
        
        ax.plot(
            turno_df['Ano/Semestre Disciplina'],
            turno_df['media_das_medias'],
            marker='o',
            linestyle='-',
            label=turno,
            color=colors[i]
        )

        ax.fill_between(
            turno_df['Ano/Semestre Disciplina'],
            turno_df['media_das_medias'] - turno_df['desvio_padrao_das_medias'], # Limite inferior
            turno_df['media_das_medias'] + turno_df['desvio_padrao_das_medias'], # Limite superior
            color=colors[i],
            alpha=0.2 
        )

    ax.set_title(PLOT_CONFIG['title'], fontsize=16, weight='bold')
    ax.set_xlabel(PLOT_CONFIG['xlabel'], fontsize=12)
    ax.set_ylabel(PLOT_CONFIG['ylabel'], fontsize=12)
    plt.xticks(rotation=45, ha='right')
    ax.legend(title='Turno')
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.tight_layout()

    plt.savefig(output_path, dpi=PLOT_CONFIG['dpi'])
    logging.info(f"Gráfico salvo com sucesso em: {output_path}")

def run_block_performance_analysis():
    try:
        raw_df = load_data(INPUT_CSV_PATH)
        filtered_df = prepare_data_for_plot(raw_df, TARGET_BLOCK)

        if not filtered_df.empty:
            logging.info(f"Salvando dados agregados em arquivo CSV...")
      
            filtered_df.to_csv(OUTPUT_CSV_PATH, index=False, encoding='utf-8-sig')
            logging.info(f"Dados agregados salvos com sucesso em: {OUTPUT_CSV_PATH}")
        else:
            logging.warning("DataFrame de análise está vazio. Nenhum arquivo CSV será gerado.")
    

        create_performance_over_time_plot(filtered_df, OUTPUT_PLOT_PATH)
        
    except FileNotFoundError as e:
        logging.error(str(e))
    except Exception as e:
        logging.error(str(e))


if __name__ == "__main__":
    run_block_performance_analysis()
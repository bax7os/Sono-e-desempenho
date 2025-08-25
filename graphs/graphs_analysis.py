import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path
import logging


BASE_PATH = Path().resolve()
RESULTS_FOLDER = BASE_PATH / 'results'
RESULTS_FOLDER.mkdir(exist_ok=True) 
INPUT_CSV_PATH = RESULTS_FOLDER / 'materias_regulares.csv'


MIN_STUDENTS_FILTER = 5
MAX_WEEKLY_CLASSES_FILTER = 3
BLOCK_NUN = "N/A"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_data(file_path: Path) -> pd.DataFrame:
    """Carrega os dados do arquivo CSV."""
    logging.info(f"Carregando dados de: {file_path}")
    if not file_path.exists():
        logging.error(f"Arquivo de entrada não encontrado: {file_path}")
        raise FileNotFoundError(f"Arquivo de entrada não encontrado: {file_path}.")
    return pd.read_csv(file_path, encoding='utf-8')

def apply_filters_and_cleaning(df: pd.DataFrame, min_students: int, max_weekly_classes: int) -> pd.DataFrame:
    """Aplica a limpeza inicial e os filtros definidos."""
    logging.info(f"Aplicando filtros: total_alunos >= {min_students} e carga_horaria <= {max_weekly_classes}")
    
   
    required_cols = ['media_disciplina', 'total_alunos_disciplina', 'carga_semanal_dias', 'bloco', 'turno_predominante']
    for col in required_cols:
        if col not in df.columns:
            logging.error(f"A coluna obrigatória '{col}' não foi encontrada no CSV!")
            raise KeyError(f"A coluna '{col}' não existe no DataFrame.")
            
   
    for col in ['media_disciplina', 'total_alunos_disciplina', 'carga_semanal_dias']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df.dropna(subset=required_cols, inplace=True)

   
    filtered_df = df[
        (df['total_alunos_disciplina'] >= min_students) &
        (df['carga_semanal_dias'] <= max_weekly_classes) &
        (df['bloco'] != BLOCK_NUN)
    ].copy()
    
    filtered_df['bloco'] = filtered_df['bloco'].astype(str).str.upper()
    return filtered_df

def aggregate_data(df: pd.DataFrame, group_by_cols: list) -> pd.DataFrame:
    """Agrega os dados calculando a média aritmética simples e o desvio padrão."""
    logging.info(f"Agregando dados por {group_by_cols} usando média aritmética...")
    
    unique_classes_df = df.drop_duplicates(
        subset=['Ano/Semestre Disciplina', 'Disciplina', 'turno_predominante', 'bloco']
    )
    
    if unique_classes_df.empty:
        logging.warning("Nenhum dado restante após a remoção de duplicatas para agregação.")
        return pd.DataFrame()

    aggregated_df = unique_classes_df.groupby(group_by_cols)['media_disciplina'].agg(['mean', 'std']).reset_index()
    aggregated_df.rename(columns={'mean': 'media_das_medias', 'std': 'desvio_padrao_das_medias'}, inplace=True)
    aggregated_df['desvio_padrao_das_medias'] = aggregated_df['desvio_padrao_das_medias'].fillna(0)
    aggregated_df = aggregated_df.sort_values(by='Ano/Semestre Disciplina')
    
    logging.info("Agregação por média aritmética concluída.")
    return aggregated_df


def create_comparison_plot(df: pd.DataFrame, output_path: Path, title: str, hue: str):
    """Cria e salva um gráfico de comparação ao longo do tempo."""
    if df.empty:
        logging.warning(f"DataFrame para '{title}' está vazio. Gráfico não será gerado.")
        return

    logging.info(f"Gerando gráfico: {title}")
    
    plt.style.use('seaborn-v0_8-whitegrid')
    fig, ax = plt.subplots(figsize=(18, 10))

    sns.lineplot(
        data=df,
        x='Ano/Semestre Disciplina',
        y='media_das_medias',
        hue=hue,
        marker='o',
        ax=ax
    )

    ax.set_title(title, fontsize=18, weight='bold')
    ax.set_xlabel("Ano/Semestre da Disciplina", fontsize=12)
    ax.set_ylabel("Média Final (Aritmética)", fontsize=12)
    plt.xticks(rotation=45, ha='right')
    ax.legend(title=hue.replace('_', ' ').capitalize(), bbox_to_anchor=(1.05, 1), loc='upper left')
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.tight_layout(rect=[0, 0, 0.85, 1])

    plt.savefig(output_path, dpi=300)
    logging.info(f"Gráfico salvo com sucesso em: {output_path}")
    plt.close(fig)


def run_comparative_analysis():
    """Executa a análise completa, gerando os gráficos de comparação."""
    try:
        raw_df = load_data(INPUT_CSV_PATH)
        base_filtered_df = apply_filters_and_cleaning(raw_df, MIN_STUDENTS_FILTER, MAX_WEEKLY_CLASSES_FILTER)

        turnos_data = aggregate_data(base_filtered_df, group_by_cols=['Ano/Semestre Disciplina', 'turno_predominante'])
        turnos_output_path = RESULTS_FOLDER / 'comparacao_turnos_media_simples.png'
        create_comparison_plot(
            df=turnos_data,
            output_path=turnos_output_path,
            title="Média de Notas por Turno (Todos os Blocos - Filtros Aplicados)",
            hue='turno_predominante'
        )

        blocos_data = aggregate_data(base_filtered_df, group_by_cols=['Ano/Semestre Disciplina', 'bloco'])
        
        top_10_blocos = blocos_data['bloco'].value_counts().nlargest(10).index
        blocos_data_filtrado = blocos_data[blocos_data['bloco'].isin(top_10_blocos)]
        
        blocos_output_path = RESULTS_FOLDER / 'comparacao_blocos_media_simples.png'
        create_comparison_plot(
            df=blocos_data_filtrado,
            output_path=blocos_output_path,
            title="Média de Notas por Bloco (Top 10 com Mais Registros - Filtros Aplicados)",
            hue='bloco'
        )
        
        logging.info("Análise comparativa completa executada com sucesso!")

    except (FileNotFoundError, KeyError) as e:
        logging.error(f"ERRO CRÍTICO: {e}")
    except Exception as e:
        logging.error(f"Ocorreu um erro inesperado: {e}")


if __name__ == "__main__":
    run_comparative_analysis()
import pandas as pd
from pathlib import Path
from datetime import time
import numpy as np
import logging
from typing import List

MORNING_SHIFT = (time(7, 0, 0), time(11, 25, 0))
AFTERNOON_SHIFT = (time(13, 0, 0), time(16, 59, 0))
NIGHT_SHIFT = (time(17, 0, 0), time(23, 0, 0))

KEY_COLS = ['RGA', 'Disciplina', 'Ano/Semestre Disciplina']
GRADE_KEY_COLS = ['Disciplina', 'Ano/Semestre Disciplina', 'grade_horarios_aluno']
FINAL_SITUATION_COL = 'Situação Final'
APPROVED_STATUS = 'AP'

SHIFTS = {
    "MANHA": MORNING_SHIFT,
    "TARDE": AFTERNOON_SHIFT,
    "NOITE": NIGHT_SHIFT
}
TIME_WEIGHT = {
    1: (time(7, 0, 0), time(8, 59, 0)), 
    2: (time(9, 0, 0), time(11, 25, 0)), 
    3: (time(13, 0, 0), time(14, 40, 0)), 
    4: (time(15, 0, 0), time(16, 59, 0)), 
    5: (time(17, 0, 0), time(20, 29, 0)), 
    6: (time(20, 30, 0), time(23, 0, 0))
}

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def is_time_in_valid_ranges(current_time: time) -> bool:
    if not isinstance(current_time, time):
        return False
    
    for start_time, end_time in TIME_WEIGHT.values():
        if start_time <= current_time <= end_time:
            return True
    return False
def is_time_in_range(time_to_check: time, interval: tuple[time, time]) -> bool:
        start_time, end_time = interval
        return start_time <= time_to_check <= end_time
      
def get_shift(current_time: time):
    for shift, interval in SHIFTS.items():
        if is_time_in_range(current_time, interval):
            return shift
    return "shift_undefined"

def get_time_weight(current_time: time) -> int:
    for weight, interval in TIME_WEIGHT.items():
        if is_time_in_range(current_time, interval): return weight
        
    raise ValueError(f"Time weight undefined for the time {current_time}.")

def load_data_csv(input_path: Path) -> pd.DataFrame:

        logging.info(f"Carregando dados de '{input_path}'...")

        if not input_path:
            raise FileNotFoundError(f"Arquivo nao encontrado em: '{input_path}'...")
        
        df = pd.read_csv(input_path, encoding='utf-8')
        logging.info(f"Dados carregados com sucesso. Total de {len(df)} registros.")
        return df

def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:

    df = df[df['Dia da Semana'] != 'EAD'].copy()
   

    df['Horario-Inicio-Time'] = pd.to_datetime(df['Horário Início'], format='%H:%M:%S', errors='coerce').dt.time
    df.dropna(subset=['Horario-Inicio-Time'], inplace=True)

    before_register = len(df)
    df = df[df['Horario-Inicio-Time'].apply(is_time_in_valid_ranges)]
    after_register = len(df)
    logging.info(f"Removidos {before_register - after_register} registros de horarios invalidos.")

    df['Media-Final-Float'] = pd.to_numeric(df['Média Final'].astype(str).str.replace(',', '.'), errors='coerce')

    df['Turno'] = df['Horario-Inicio-Time'].apply(get_shift)
    df['Peso-Horario'] = df['Horario-Inicio-Time'].apply(get_time_weight)

    student_schedule = df.groupby(['RGA', 'Disciplina', 'Ano/Semestre Disciplina'])[['Dia da Semana', 'Horário Início']].apply(
        lambda x: frozenset(sorted(tuple(y) for y in x.values))
    )
    student_schedule.name = 'grade_horarios_aluno'
    df = df.merge(student_schedule, on=['RGA', 'Disciplina', 'Ano/Semestre Disciplina'], how='left')

    return df


def calculate_approval_rates(df: pd.DataFrame) -> pd.DataFrame:
    
    group_sizes = df.groupby(GRADE_KEY_COLS).size().reset_index(name='total_na_turma')

    approved = df[df[FINAL_SITUATION_COL] == APPROVED_STATUS].groupby(GRADE_KEY_COLS).size().reset_index(name='total_aprovados')

    rates_df = pd.merge(group_sizes, approved, on=GRADE_KEY_COLS, how='left')
    rates_df['total_aprovados'] = rates_df['total_aprovados'].fillna(0)

    rates_df['taxa_aprovacao'] = rates_df['total_aprovados'] / rates_df['total_na_turma']
    rates_df['taxa_reprovacao'] = 1 - rates_df['taxa_aprovacao']

    return rates_df.drop(columns=['total_na_turma', 'total_aprovados'])

def aggregate_class_metrics (df: pd.DataFrame) -> pd.DataFrame:
    
    aggregations = {
        'total_alunos_disciplina': pd.NamedAgg(column='RGA', aggfunc='nunique'),
        'carga_semanal_dias': pd.NamedAgg(column='Dia da Semana', aggfunc='nunique'),
        'turnos_distintos': pd.NamedAgg(column='Turno', aggfunc=lambda x: frozenset(x.unique())),
        'media_disciplina': pd.NamedAgg(column='Media-Final-Float', aggfunc='mean'),
        'desvio_padrao': pd.NamedAgg(column='Media-Final-Float', aggfunc='std')
    }
    classes_df = df.groupby(GRADE_KEY_COLS).agg(**aggregations).reset_index()

    classes_weight = df.drop_duplicates(subset=GRADE_KEY_COLS + ['Dia da Semana']) \
                       .groupby(GRADE_KEY_COLS)['Peso-Horario'].sum().reset_index(name='soma_pesos_horario')

    classes_df = classes_df.merge(classes_weight, on=GRADE_KEY_COLS, how='left')

    return classes_df

def merge_classes_metrics(df: pd.DataFrame, classes_df: pd.DataFrame) -> pd.DataFrame:
    return pd.merge(df, classes_df, on=GRADE_KEY_COLS, how='left')

def calculate_derived_metrics(df: pd.DataFrame) -> pd.DataFrame:

    df['peso_final'] = df['soma_pesos_horario'] / df['carga_semanal_dias']
    df['turno_predominante'] = df['turnos_distintos'].apply(lambda x: list(x)[0] if len(x) == 1 else 'MISTO')
    df['desvio_padrao'] = df['desvio_padrao'].fillna(0.0)
    
    return df

def add_block_information(df: pd.DataFrame, blocks_map_path: str) -> pd.DataFrame:
    try:
        blocks_map_df = pd.read_csv(blocks_map_path, header=0, names=['Disciplina', 'bloco'])
        df = df.merge(blocks_map_df, on='Disciplina', how='left')
        df['bloco'] = df['bloco'].str.strip()
        df['bloco'] = df['bloco'].fillna('N/A')
    except FileNotFoundError:
        print(f"ATTENTION: File not found: {blocks_map_path}.")
        df['bloco'] = 'N/A'
    return df

def format_data_for_output(df: pd.DataFrame) -> pd.DataFrame:

    logging.info("Formatando colunas numéricas para o relatório final...")
    df_formatted = df.copy() 

    format_cols = ['peso_final', 'media_disciplina', 'desvio_padrao', 'taxa_aprovacao', 'taxa_reprovacao']
    for col in format_cols:
        if col in df_formatted.columns:
            df_formatted[col] = df_formatted[col].map('{:.2f}'.format)
    return df_formatted
def separate_regular_and_irregular_classes(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    
    logging.info("Separando turmas em regulares e irregulares...")
    is_regular = df['turnos_distintos'].apply(len) == 1

    regular_df = df[is_regular]
    irregular_df = df[~is_regular]

    return regular_df, irregular_df

def prepare_and_save_csv(df: pd.DataFrame, columns_to_keep: List[str], output_path: Path):

    final_columns = [col for col in columns_to_keep if col in df.columns]
    
    output_df = df[final_columns].drop_duplicates()
    
    output_df.to_csv(output_path, index=False, encoding='utf-8')
    logging.info(f"Relatório salvo com sucesso em: {output_path}")

def run_analysis_pipeline(input_path: Path, regular_output_path: Path, irregular_output_path: Path, blocks_map_path: Path):
    try:
        raw_df = load_data_csv(input_path)
        original_header = raw_df.columns.tolist()

        processed_df = preprocess_data(raw_df)
        
        rates_df = calculate_approval_rates(processed_df)
        class_metrics_df = aggregate_class_metrics(processed_df)
        class_metrics_df = class_metrics_df.merge(rates_df, on=GRADE_KEY_COLS, how='left')

        df_with_metrics = merge_classes_metrics(processed_df, class_metrics_df)
        df_with_derived_metrics = calculate_derived_metrics(df_with_metrics)
        final_df = add_block_information(df_with_derived_metrics, blocks_map_path)

        formatted_df = format_data_for_output(final_df)
        regular_df, irregular_df = separate_regular_and_irregular_classes(formatted_df)

        base_metrics = ["bloco", "total_alunos_disciplina", "carga_semanal_dias", "media_disciplina", 
                        "desvio_padrao", "taxa_aprovacao", "taxa_reprovacao"]
        
        regular_cols = original_header + ["turno_predominante", "peso_final"] + base_metrics
        irregular_cols = original_header + base_metrics

        prepare_and_save_csv(regular_df, regular_cols,regular_output_path)
        prepare_and_save_csv(irregular_df, irregular_cols, irregular_output_path)

        logging.info("Pipeline de análise concluído com sucesso.")
    except Exception as e:
        logging.error(f"Erro ao executar o pipeline de análise: {e}")

if __name__ == "__main__":
    base_path = Path(__file__).parent
    input_folder = base_path / 'include'
    out_folder = base_path / 'results'
    out_folder.mkdir(exist_ok=True)

    input_csv_path = input_folder / "data.csv"

    regular_output_path = out_folder / 'materias_regulares.csv'
    irregular_output_path = out_folder /  'materias_irregulares.csv'
    blocks_map_path = base_path / 'include' / 'disciplinas-bloco.csv'

    run_analysis_pipeline(
        input_path=input_csv_path,  
        regular_output_path=regular_output_path,
        irregular_output_path=irregular_output_path,
        blocks_map_path=blocks_map_path
    )
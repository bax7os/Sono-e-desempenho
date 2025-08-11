import pandas as pd
from pathlib import Path
from datetime import datetime
import numpy as np

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

def load_and_combine_csvs(input_paths: list[Path]) -> pd.DataFrame:

        dfs = [pd.read_csv(path, encoding='utf-8') for path in input_paths if path.exists()]
        if not dfs:
            raise FileNotFoundError("Input files not found.")            
            
        combined_df = pd.concat(dfs, ignore_index=True)
        header = combined_df.columns.tolist()
        logging.info(f"Loading and combining {len(dfs)} CSV files.")
        return combined_df

def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:

    df = df[df['Dia da Semana'] != 'EAD'].copy()

    df['Horario-Inicio-Time'] = pd.to_datetime(df['Horário Início'], format='%H:%M:%S', errors='coerce').dt.time
    df.dropna(subset=['Horario-Inicio-Time'], inplace=True)

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

def save_to_csv(df: pd.DataFrame, output_path: str) -> None:
    
    format_cols = ['peso_final', 'media_disciplina', 'desvio_padrao', 'taxa_aprovacao', 'taxa_reprovacao']
    for col in format_cols:
        if col in df_final.columns:
            df_final[col] = df_final[col].map('{:.2f}'.format)

    # Separação de turmas regulares e irregulares
    is_regular = df_final['turnos_distintos'].apply(len) == 1

    # Define as colunas para o arquivo de irregulares
    col_irregulares = cabecalho_original + [
        "bloco", "total_alunos_disciplina", "carga_semanal_dias",
        "media_disciplina", "desvio_padrao", "taxa_aprovacao", "taxa_reprovacao"
    ]
    df_irregulares = df_final[~is_regular][[col for col in col_irregulares if col in df_final.columns]].drop_duplicates()

    # Define as colunas para o arquivo de regulares
    col_regulares = cabecalho_original + [
        "bloco", "turno_predominante", "total_alunos_disciplina", 
        "carga_semanal_dias", "peso_final", "media_disciplina", "desvio_padrao",
        "taxa_aprovacao", "taxa_reprovacao"
    ]
    df_regulares = df_final[is_regular][[col for col in col_regulares if col in df_final.columns]].drop_duplicates()

    # Salva os arquivos CSV
    df_regulares.to_csv(caminho_saida_regulares, index=False, encoding='utf-8')
    df_irregulares.to_csv(caminho_saida_irregulares, index=False, encoding='utf-8')

    print("\nProcessamento concluído com sucesso.")
    print(f"Matérias regulares salvas em: {caminho_saida_regulares}")
    print(f"Matérias irregulares salvas em: {caminho_saida_irregulares}")


def analise_csv(lista_caminhos_entrada, caminho_saida_regulares, caminho_saida_irregulares, mapa_blocos_path):
   
   

   
  
  

    

   
    # Formatação das colunas numéricas para a saída
   


if __name__ == "__main__":
    pasta_base = Path(__file__).parent
    pasta_entrada = pasta_base / 'include'
    pasta_saida = pasta_base / 'resultados'
    pasta_saida.mkdir(exist_ok=True)

    nomes_dos_cursos_csv = [
        "AS.csv", "CC.csv", "CSRC.csv",
        "EC.csv", "ES.csv", "SI.csv"
    ]
    caminhos_entrada = [pasta_entrada / nome for nome in nomes_dos_cursos_csv]
    caminho_mapa_blocos = pasta_base / "disciplinas-bloco.csv"
    caminho_saida_regulares = pasta_saida / "materias_regulares_pandas.csv"
    caminho_saida_irregulares = pasta_saida / "materias_irregulares_pandas.csv"
    
    analise_csv(
        caminhos_entrada,
        caminho_saida_regulares,
        caminho_saida_irregulares,
        caminho_mapa_blocos
    )
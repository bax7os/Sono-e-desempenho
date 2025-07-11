import matplotlib.pyplot as plt
import csv
from collections import defaultdict




def plotar_grafico_turno(dados_por_turno, semestres):
    plt.figure(figsize=(10, 6))
    cores = {'MANHA': 'blue', 'TARDE': 'orange', 'NOITE': 'green'}
    for turno, medias in dados_por_turno.items():
        plt.plot(semestres, medias, marker='o', label=turno, color=cores.get(turno, 'gray'))
    plt.xlabel('Semestres')
    plt.ylabel('Média das Disciplinas')
    plt.title('Média das Disciplinas por Turno ao Longo dos Semestres')
    plt.xticks(rotation=45)
    plt.legend(title='Turnos')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()

def plotar_grafico_bloco(dados_por_bloco, semestres):
    plt.figure(figsize=(10, 6))
    cores_base = {'FACOM': 'blue', 'INMA': 'orange', 'INFI': 'green', 'ESAN': 'red', 'FACH': 'purple', 'FAENG': 'brown'}
    cores = {}
    for bloco in dados_por_bloco:
        if bloco in cores_base:
            cores[bloco] = cores_base[bloco]
        else:
            continue
     
    for bloco, medias in dados_por_bloco.items():
        try:
            plt.plot(semestres, medias, marker='o', label=bloco, color=cores[bloco])
        except KeyError:
            print(f"Bloco {bloco} não encontrado nas cores definidas. Ignorando.")
            continue
    plt.xlabel('Semestres')
    plt.ylabel('Média das Disciplinas')
    plt.title('Média das Disciplinas por Bloco ao Longo dos Semestres')
    plt.xticks(rotation=45)
    plt.legend(title='Blocos')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()

def media_por_turno(csv_in):

    in_csv = csv_in
    disciplinas_semestres = defaultdict(lambda: defaultdict(list))  # {turno: {semestre: [notas]}}
    semestres_set = set()
    with open(in_csv, 'r', newline='', encoding='utf-8') as file_in:
        reader = csv.reader(file_in)
        next(reader)
       
        for row in reader:
            carga = int(row[17])
            alunos = int(row[16])
            bloco = row[14]
            if carga <= 3 and alunos > 5 and bloco != "N/A":
                semestre_ano = row[6]
                turno = row[15]
                media_sala = row[19]
                disciplinas_semestres[turno][semestre_ano].append(float(media_sala))
                semestres_set.add(semestre_ano)
            else:
                continue
    semestres_list = sorted(semestres_set)
    dados_por_turno = {}
    for turno, semestres in disciplinas_semestres.items():
        medias = []
        for semestre in semestres_list:
            medias_semestre = semestres.get(semestre, [])
            media = sum(medias_semestre) / len(medias_semestre) if medias_semestre else 0
            medias.append(media)
        dados_por_turno[turno] = medias
    plotar_grafico_turno(dados_por_turno, semestres_list)

def plotar_grafico_horario(dados_por_peso, semestres):
    plt.figure(figsize=(10, 6))
    cores = {'primeira_manha': 'blue', 'primeira_tarde': 'orange', 'primeira_noite': 'green', 
             'segunda_manha': 'red', 'segunda_tarde': 'purple', 'segunda_noite': 'brown'}
    for subgrupo, medias in dados_por_peso.items():
        plt.plot(semestres, medias, marker='o', label=subgrupo, color=cores.get(subgrupo, 'gray'))
    plt.xlabel('Semestres')
    plt.ylabel('Média das Disciplinas')
    plt.title('Média das Disciplinas por peso ao Longo dos Semestres')
    plt.xticks(rotation=45)
    plt.legend(title='Pesos')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()

def media_INMA_por_horario(csv_in):
    in_csv = csv_in
    disciplinas_semestres = defaultdict(lambda: defaultdict(list))  # {turno: {semestre: [notas]}}
    semestres_set = set()
    
    with open(in_csv, 'r', newline='', encoding='utf-8') as file_in:
        reader = csv.reader(file_in)
        next(reader)
        
        for row in reader:
            carga = int(row[17])
            alunos = int(row[16])
            bloco = row[14]
            if carga <= 3 and alunos > 5 and bloco != "N/A" and bloco == "INMA":
          
                semestre_ano = row[6]
                peso = float(row[18])
                turno = row[15]
                media_sala = float(row[19].replace(',', '.'))
                # MANHA POSSIVEIS
                #if peso == 1:
                 #   subgrupo = f"primeira_{turno.lower()}"
                #elif peso > 1 and peso <= 2:
                 #   subgrupo = f"segunda_{turno.lower()}"
                # TARDE POSSIVEIS
                #if peso == 3:
                 #   subgrupo = f"primeira_{turno.lower()}"
                #elif peso > 3 and peso <= 4:
                 #   subgrupo = f"segunda_{turno.lower()}"
               
                # NOITE POSSIVEIS
                if peso == 5:
                    subgrupo = f"primeira_{turno.lower()}"
                elif peso > 5 and peso <= 6:
                    subgrupo = f"segunda_{turno.lower()}"
                else:
                   # print(f"Peso {peso} não mapeado para o turno {turno}. Ignorando. carga: {carga}")
                    continue
                disciplinas_semestres[subgrupo][semestre_ano].append(media_sala)
                semestres_set.add(semestre_ano)
    semestres_list = sorted(semestres_set)
    dados_por_peso = {}
    for subgrupo, semestres in disciplinas_semestres.items():
        medias = []
        for semestre in semestres_list:
            medias_semestre = semestres.get(semestre, [])
            media = sum(medias_semestre) / len(medias_semestre) if medias_semestre else None
            medias.append(media)
        dados_por_peso[subgrupo] = medias
        
    plotar_grafico_horario(dados_por_peso, semestres_list)

def media_por_horario(csv_in):
    in_csv = csv_in
    disciplinas_semestres = defaultdict(lambda: defaultdict(list))  # {turno: {semestre: [notas]}}
    semestres_set = set()
 
    with open(in_csv, 'r', newline='', encoding='utf-8') as file_in:
        reader = csv.reader(file_in)
        next(reader)
        
        for row in reader:
            carga = int(row[17])
            alunos = int(row[16])
            bloco = row[14]
            if carga <= 3 and alunos > 5 and bloco != "N/A":
          
                semestre_ano = row[6]
                peso = float(row[18])
                turno = row[15]
                media_sala = float(row[19].replace(',', '.'))
                # MANHA POSSIVEIS
                if peso == 1:
                    subgrupo = f"primeira_{turno.lower()}"
                elif peso > 1 and peso <= 2:
                    subgrupo = f"segunda_{turno.lower()}"
                # TARDE POSSIVEIS
                elif peso == 3:
                    subgrupo = f"primeira_{turno.lower()}"
                elif peso > 3 and peso <= 4:
                    subgrupo = f"segunda_{turno.lower()}"
               
                # NOITE POSSIVEIS
                elif peso == 5:
                    subgrupo = f"primeira_{turno.lower()}"
                elif peso > 5 and peso <= 6:
                    subgrupo = f"segunda_{turno.lower()}"
                else:
                   # print(f"Peso {peso} não mapeado para o turno {turno}. Ignorando. carga: {carga}")
                    continue
                
                disciplinas_semestres[subgrupo][semestre_ano].append(media_sala)
                semestres_set.add(semestre_ano)
   
    semestres_list = sorted(semestres_set)
    dados_por_peso = {}
    for subgrupo, semestres in disciplinas_semestres.items():
        medias = []
        for semestre in semestres_list:
            medias_semestre = semestres.get(semestre, [])
            media = sum(medias_semestre) / len(medias_semestre) if medias_semestre else None
            medias.append(media)
        dados_por_peso[subgrupo] = medias
        
    plotar_grafico_horario(dados_por_peso, semestres_list)

def media_por_bloco(csv_in):
    in_csv = csv_in
    disciplinas_semestres = defaultdict(lambda: defaultdict(list))  # {bloco: {semestre: [notas]}}
    semestres_set = set()
    with open(in_csv, 'r', newline='', encoding='utf-8') as file_in:
        reader = csv.reader(file_in)
        next(reader)
        for row in reader:
            carga = int(row[17])
            alunos = int(row[16])
            bloco = row[14]
            if carga <= 3 and alunos > 5 and bloco != "N/A" and bloco != "FACH" and bloco != "FAALC" and bloco != "INQUI":
                semestre_ano = row[6]
                try:
                    media_sala = float(row[19].replace(',', '.'))
                except (ValueError, IndexError):
                    continue
                disciplinas_semestres[bloco][semestre_ano].append(media_sala)
                #print(f"Adicionando {media_sala} ao bloco {bloco} no semestre {semestre_ano}")
                semestres_set.add(semestre_ano)
            else:
                continue
    semestres_list = sorted(semestres_set)
    dados_por_bloco = {}
    for bloco, semestres in disciplinas_semestres.items():
        medias = []
        for semestre in semestres_list:
            medias_semestre = semestres.get(semestre, [])
            # Use None para semestres sem dados, assim o matplotlib não plota ponto
            media = sum(medias_semestre) / len(medias_semestre) if medias_semestre else None
            medias.append(media)
        dados_por_bloco[bloco] = medias
    plotar_grafico_bloco(dados_por_bloco, semestres_list)

def visualizar_pesos_por_turno(csv_in):
    in_csv = csv_in
    pesos_por_turno = defaultdict(set)
    with open(in_csv, 'r', newline='', encoding='utf-8') as file_in:
        reader = csv.reader(file_in)
        next(reader)
        for row in reader:
            carga = int(row[17])
            alunos = int(row[16])
            bloco = row[14]
            if carga <= 3 and alunos > 5 and bloco != "N/A":
                turno = row[15].upper()
                try:
                    peso = float(row[18])
                except ValueError:
                    continue
                pesos_por_turno[turno].add(peso)
    for turno, pesos in pesos_por_turno.items():
        print(f"Turno {turno} tem esses pesos possíveis: {sorted(pesos)}")
if __name__ == "__main__":
    in_csv = 'resultados/materias_regulares_enriquecido.csv'
    #media_por_turno(in_csv
    #media_por_horario(in_csv)
    #media_por_bloco(in_csv)
    media_INMA_por_horario(in_csv)
    #visualizar_pesos_por_turno(in_csv)
    print("Gráfico gerado com sucesso!")

          

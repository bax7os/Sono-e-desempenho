# Análise de Desempenho e Sono

Este repositório contém scripts para análise de desempenho acadêmico, agrupamento de disciplinas, geração de gráficos e limpeza de dados, utilizando dados de cursos de graduação.

## Estrutura do Projeto

```
main.py
plotar_grafico.py
graphs/
    graphs_analysis.py
    main.py
    verificar_agrupamento.py
include/
    AS.csv
    CC.csv
    CSRC.csv
    data.csv
    disciplinas-bloco.csv
    EC.csv
    ES.csv
    SI.csv
results/
    grafico_correlacao.png
    materias_irregulares.csv
    materias_regulares.csv
    media_turno_bloco_inma.png
```

## Pré-requisitos

- Python 3.8+
- Instale as dependências necessárias:
    ```sh
    pip install pandas numpy matplotlib seaborn
    ```

## Execução Principal

### 1. Processamento e Geração dos Relatórios

Execute o pipeline principal para processar os dados e gerar os arquivos de matérias regulares e irregulares:

```sh
python main.py
```

- Entrada: arquivos `.csv` em `include/` (ex: `data.csv`, `disciplinas-bloco.csv`)
- Saída: arquivos em `results/`:
    - `materias_regulares.csv`
    - `materias_irregulares.csv`

### 2. Geração de Gráficos

#### a) Matriz de Correlação

Gera um heatmap de correlação das variáveis das disciplinas:

```sh
python graphs/main.py
```

- Saída: `results/grafico_correlacao.png`

#### b) Gráfico de Média por Turno e Bloco

Gera gráfico de desempenho ao longo do tempo para um bloco específico:

```sh
python graphs/graphs_analysis.py
```

- Saída: `results/media_turno_bloco_inma.png`

## Observações

- Os arquivos de entrada devem estar na pasta `include/`.
- Os resultados e gráficos são salvos na pasta `results/`.
- Para modificar blocos ou parâmetros de análise, edite os scripts em `graphs/`.

---

**Contato:** [Ana Clara](mailto:clarabaxtos@hotmail.com)
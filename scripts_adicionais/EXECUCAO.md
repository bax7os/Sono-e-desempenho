## Guia de Execução: split_coco_dataset.py

Este documento explica, do zero, como preparar o ambiente, obter o dataset e executar o script `split_coco_dataset.py` para dividir um dataset no formato COCO em treino/validação/teste e opcionalmente copiar as imagens.

### 1. Requisitos

- **Sistema**: Linux, macOS ou Windows
- **Python**: 3.8+ ou >
- **Pacotes Python**:
  - `gdown` (apenas se desejar que o script baixe automaticamente o dataset do Google Drive)

### 2. Estrutura esperada do projeto

A partir da raiz do repositório `document-layout-detection/`:

```
document-layout-detection/
├── scripts_adicionais/
│   ├── split_coco_dataset.py
│   ├── download_utils.py
│   ├── result.json              # COCO JSON (pode ser baixado automaticamente)
│   └── images/                  # Diretório com imagens (pode ser baixado automaticamente)
└── data/
    └── split/                   # Saída gerada pelo
```

### 3. Preparar ambiente Python (opcional, porém recomendado)

```bash
# Na raiz do projeto
dcdocument-layout-detecction

# Instalar dependências opcionais (para download automático do dataset)
pip install gdown
```

### 4. Dataset: automático (via Google Drive) ou manual

O script possui integração com `download_utils.ensure_dataset_downloaded`, que:

- Verifica se `scripts_adicionais/result.json` e `scripts_adicionais/images/` existem;
- Caso não, faz o download de um arquivo do Google Drive (link configurável dentro de `download_utils.py`),
- Tenta extrair se for `.zip` ou `.tar.*` e valida a presença de `result.json` e `images/`.

Você pode utilizar de duas formas:

- **Automático (recomendado)**: basta executar o script; ele chamará `ensure_dataset_downloaded(dest_dir=scripts_adicionais)` antes de iniciar o split. Para isso, é necessário ter `gdown` instalado e acesso ao link do Drive configurado em `download_utils.py`.

- **Manual**: coloque manualmente o arquivo `result.json` e a pasta `images/` dentro de `scripts_adicionais/`.

### 5. Execução padrão

A partir da raiz do projeto:

```bash
cd scripts_adicionais
python split_coco_dataset.py
```

O script irá:

- Garantir a presença do dataset (`ensure_dataset_downloaded`), se habilitado no código;
- Ler `result.json` e a pasta `images/` do diretório atual (`scripts_adicionais/`);
- Criar a saída em `../data/split/` contendo:
  - `train.json`, `val.json`, `test.json`
  - pastas `train/`, `val/`, `test/` com as imagens (se `copy_images=True`)

### 6. Parâmetros e personalização

O `main` dentro de `split_coco_dataset.py` chama:

```python
split_coco_dataset(
    coco_json_path=os.path.join(script_dir, 'result.json'),
    images_dir=os.path.join(script_dir, 'images'),
    output_dir=os.path.join(script_dir, '..', 'data', 'split'),
    split_ratio=(0.7, 0, 0.3),
    copy_images=True,
)
```

Você pode ajustar:

- `split_ratio`: tupla `(train, val, test)` em frações. Ex.: `(0.8, 0.1, 0.1)`
- `copy_images`: `True` para copiar imagens para cada split, `False` para gerar apenas os JSONs
- `seed`: para tornar o embaralhamento reproduzível (padrão 42 dentro da função)

Para uso programático em outro script:

```python
from scripts_adicionais.split_coco_dataset import split_coco_dataset
split_coco_dataset(
    coco_json_path='scripts_adicionais/result.json',
    images_dir='scripts_adicionais/images',
    output_dir='data/split',
    split_ratio=(0.8, 0.1, 0.1),
    copy_images=False,
    seed=123,
)
```

### 7. Comando rápido (resumo)

```bash
# Na raiz do projeto
python -m venv .venv && source .venv/bin/activate
pip install gdown
cd scripts_adicionais
python split_coco_dataset.py
```

Pronto!! Seu dataset foi dividido e os arquivos de saída gerados em `data/split/`... Assim é previsto :).

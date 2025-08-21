# Modificações Necessárias no `split_coco_dataset.py`

## 📋 **Resumo do Problema**

O script `split_coco_dataset.py` original apresentava vários problemas que impediam seu funcionamento correto para divisão de datasets COCO. Este documento explica as modificações implementadas para resolver esses problemas.

## 🚨 **Problemas Identificados**

### 1\. **Caminhos de Arquivos Incorretos**

- **Problema**: O script estava sendo executado de diretórios incorretos, resultando em erros de "Arquivo não encontrado"
- **Sintoma**: `AssertionError: Arquivo COCO JSON não encontrado`
- **Causa**: Uso de caminhos relativos que não funcionavam dependendo do diretório de execução

### 2\. **Prefixo 'images/' nos Nomes dos Arquivos**

- **Problema**: Os nomes dos arquivos no JSON COCO incluíam o prefixo `images/` (ex: `images/arquivo.png`)
- **Sintoma**: Todas as imagens eram ignoradas com mensagem "Ignorando imagem inválida ou ausente"
- **Causa**: O script procurava por `images/images/arquivo.png` em vez de `images/arquivo.png`

### 3\. **Lógica de Cópia de Imagens com problema**

- **Problema**: As imagens não eram copiadas corretamente para os diretórios de saída
- **Sintoma**: Diretórios de saída vazios ou com estrutura incorreta
- **Causa**: Uso de nomes de arquivo incorretos durante a cópia

## ✅ **Soluções Implementadas**

### 1\. **Correção de Caminhos Absolutos**

```python
if __name__ == '__main__':
    # Obter o diretório onde este script está localizado
    script_dir = os.path.dirname(os.path.abspath(__file__))

    split_coco_dataset(
        coco_json_path=os.path.join(script_dir, 'result.json'),
        images_dir=os.path.join(script_dir, 'images'),
        output_dir=os.path.join(script_dir, '..', '..', 'data', 'split'),
        split_ratio=(0.7, 0, 0.3),
        copy_images=True
    )
```

**Benefício**: O script agora deve funciona independentemente do diretório de execução

### 2\. **Remoção do Prefixo 'images/'**

```python
for img in images:
    file_name = img.get('file_name')
    if not file_name:
        continue

    # Remover o prefixo 'images/' se existir
    if file_name.startswith('images/'):
        file_name = file_name[7:]  # Remove 'images/'

    img_path = os.path.join(images_dir, file_name)
    if os.path.exists(img_path):
        valid_images.append(img)
        valid_image_ids.add(img['id'])
    else:
        print(f"[!] Ignorando imagem inválida ou ausente: {file_name}")
```

### 3\. **Correção da Lógica de Cópia**

```python
if copy_images:
    split_img_dir = os.path.join(output_dir, split_name)
    os.makedirs(split_img_dir, exist_ok=True)
    for img in split_images:
        # Obter o nome do arquivo limpo (sem prefixo 'images/')
        file_name = img.get('file_name')
        if file_name.startswith('images/'):
            file_name = file_name[7:]  # Remove 'images/'

        src = os.path.join(images_dir, file_name)
        dst = os.path.join(split_img_dir, file_name)
        if os.path.exists(src):
            shutil.copy2(src, dst)
```

### **Depois**

```python
# Caminhos absolutos baseados no diretório do script
script_dir = os.path.dirname(os.path.abspath(__file__))
split_coco_dataset(
    coco_json_path=os.path.join(script_dir, 'result.json'),
    images_dir=os.path.join(script_dir, 'images'),
    output_dir=os.path.join(script_dir, '..', '..', 'data', 'split'),
    split_ratio=(0.7, 0, 0.3),
    copy_images=True
)

# Tratamento do prefixo 'images/'
if file_name.startswith('images/'):
    file_name = file_name[7:]

file_name = img.get('file_name')
if file_name.startswith('images/'):
    file_name = file_name[7:]
src = os.path.join(images_dir, file_name)
dst = os.path.join(split_img_dir, file_name)
```

## 📊 **Resultados Após as Correções**

- **Total de imagens processadas**: 3.074
- **Imagens de treino**: 2.151 (70%)
- **Imagens de teste**: 923 (30%)
- **Arquivos JSON gerados**: ✅ Funcionando
- **Cópia de imagens**: ✅ Funcionando
- **Estrutura de saída**: ✅ Correta

## 📝 **OBS Importantes**

1.  **Estrutura de Diretórios**: O script espera:

    - `result.json` no mesmo diretório do script
    - Diretório `images/` no mesmo diretório do script
    - Diretório de saída em `../../data/split/`

2.  **Formato do JSON**: O script lida automaticamente com nomes de arquivo que incluem o prefixo `images/`

3.  **Configuração de Split**: Atualmente configurado para 70% treino, 0% validação, 30% teste

4.  **Cópia de Imagens**: As imagens são copiadas para os diretórios de saída correspondentes

**Data da Modificação**: 20 de Agosto de 2025

**Status**: ✅ Funcionando

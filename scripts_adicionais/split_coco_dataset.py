import json
import os
import random
import shutil
from typing import Tuple

# Garantir dataset antes de prosseguir
try:
    from .download_utils import ensure_dataset_downloaded
except Exception:
    # fallback para import relativo ao caminho do arquivo
    import sys
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.append(current_dir)
    from download_utils import ensure_dataset_downloaded  

def split_coco_dataset(
    coco_json_path: str,
    images_dir: str,
    output_dir: str,
    split_ratio: Tuple[float, float, float] = (0.7, 0.25, 0.05),
    copy_images: bool = True,
    seed: int = 42
):
    assert os.path.exists(coco_json_path), "Arquivo COCO JSON não encontrado"

    os.makedirs(output_dir, exist_ok=True)

    # Load COCO annotations
    with open(coco_json_path, 'r', encoding='utf-8') as f:
        coco = json.load(f)

    images = coco['images']
    annotations = coco['annotations']
    categories = coco['categories']

    print(f"[i] Total de imagens no JSON: {len(images)}")

    # Filtrar imagens inválidas
    valid_images = []
    valid_image_ids = set()

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

    print(f"[i] Imagens válidas: {len(valid_images)}")

    # Filtrar anotações que referenciam imagens válidas
    valid_annotations = [ann for ann in annotations if ann['image_id'] in valid_image_ids]

    # Shuffle e split das imagens
    random.seed(seed)
    random.shuffle(valid_images)

    num_total = len(valid_images)
    num_train = int(split_ratio[0] * num_total)
    num_val = int(split_ratio[1] * num_total)
    num_test = num_total - num_train - num_val

    splits = {
        'train': valid_images[:num_train],
        'val': valid_images[num_train:num_train + num_val],
        'test': valid_images[num_train + num_val:]
    }

    for split_name, split_images in splits.items():
        split_image_ids = {img['id'] for img in split_images}
        split_annotations = [ann for ann in valid_annotations if ann['image_id'] in split_image_ids]

        coco_split = {
            'images': split_images,
            'annotations': split_annotations,
            'categories': categories
        }

        split_json_path = os.path.join(output_dir, f'{split_name}.json')
        with open(split_json_path, 'w', encoding='utf-8') as f:
            json.dump(coco_split, f, indent=2, ensure_ascii=False)

        print(f"[✓] {split_name} salvo em: {split_json_path} ({len(split_images)} imagens)")

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


if __name__ == '__main__':
    # Obter o diretorio onde estee scrip esta localizado
    script_dir = os.path.dirname(os.path.abspath(__file__))
    print("Teste", script_dir)
    
    output_dir = os.path.join(script_dir, '..', 'data', 'split')

    # Garantir dataset antes de prosseguir
    ensure_dataset_downloaded(dest_dir=script_dir)
    
    split_coco_dataset(
        coco_json_path=os.path.join(script_dir, 'result.json'),
        images_dir=os.path.join(script_dir, 'images'),
        output_dir=output_dir,
        split_ratio=(0.7, 0, 0.3),
        copy_images=True
    )

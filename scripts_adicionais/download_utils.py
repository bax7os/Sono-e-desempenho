import os
import sys
import zipfile
import tarfile
from typing import Optional

DATASET_DRIVE_URL = "https://drive.google.com/file/d/1LS4yzZQP2ytybwin00fwez3sugo6R8Ep/view?usp=sharing"


def _import_gdown():
    try:
        import gdown  
        return gdown
    except Exception as exc:
        raise RuntimeError(
            "O pacote 'gdown' é necessário para baixar o dataset. "
            "Instale com: pip install gdown"
        ) from exc


def _extract_if_archive(archive_path: str, extract_to: str) -> bool:
    os.makedirs(extract_to, exist_ok=True)

    # ZIP
    if archive_path.lower().endswith(".zip"):
        with zipfile.ZipFile(archive_path, "r") as zf:
            zf.extractall(extract_to)
        return True

    # TAR / TAR.GZ
    if archive_path.lower().endswith((".tar", ".tar.gz", ".tgz")):
        with tarfile.open(archive_path, "r:*") as tf:
            tf.extractall(extract_to)
        return True

    return False


def ensure_dataset_downloaded(
    dest_dir: str,
    drive_url: Optional[str] = None,
    expected_json_name: str = "result.json",
    expected_images_dir: str = "images",
) -> None:
    """
    Garante que o dataset esteja disponível em dest_dir baixando do Google Drive se necessário.

    - Verifica se `dest_dir/expected_json_name` e `dest_dir/expected_images_dir` existem.
    - Caso não existam, usa gdown para baixar o arquivo do Drive e extrai se for .zip/.tar.*

    Parâmetros:
        dest_dir: Diretório onde o dataset deve existir.
        drive_url: URL do arquivo no Google Drive. Se None, usa DATASET_DRIVE_URL.
        expected_json_name: Nome do arquivo COCO JSON esperado.
        expected_images_dir: Nome do diretório de imagens esperado.
    """

    dataset_json_path = os.path.join(dest_dir, expected_json_name)
    dataset_images_path = os.path.join(dest_dir, expected_images_dir)

    if os.path.exists(dataset_json_path) and os.path.isdir(dataset_images_path):
        print("[i] Dataset já encontrado. Pulando download.")
        return

    drive_url = drive_url or DATASET_DRIVE_URL
    gdown = _import_gdown()

    os.makedirs(dest_dir, exist_ok=True)

    # Baixa dentro de dest_dir preservando aa  extensão original
    print(f"[i] Baixando dataset do Drive dentro de: {dest_dir}")
    current_cwd = os.getcwd()
    try:
        os.chdir(dest_dir)
        # output=None -> gdown vai decidir o nome pelo Content-Disposition - fuzzy=True aceita links /view
        downloaded_file = gdown.download(url=drive_url, output=None, quiet=False, fuzzy=True)
        # Normalizza p caminho absoluto
        if downloaded_file and not os.path.isabs(downloaded_file):
            downloaded_file = os.path.join(dest_dir, downloaded_file)
    finally:
        os.chdir(current_cwd)

    if not downloaded_file or not os.path.exists(downloaded_file):
        raise RuntimeError("Falha no download do dataset pelo gdown.")

    # Tenta extrair se for um arquivo compactado
    was_extracted = _extract_if_archive(downloaded_file, dest_dir)

    if not was_extracted:
        print("[i] Arquivo baixado não parece ser um .zip/.tar.*. Nenhuma extração realizada.")

    if not (os.path.exists(dataset_json_path) and os.path.isdir(dataset_images_path)):
        raise FileNotFoundError(
            "Após o download, não foi possível localizar 'images' e/ou 'result.json' em "
            f"{dest_dir}. Verifique o conteúdo baixado."
        )

    print("Dataset disponível para uso.")



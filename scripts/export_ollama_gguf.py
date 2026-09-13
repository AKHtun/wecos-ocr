"""Export Ollama GGUF Master Blobs for Hugging Face Upload.

Extracts:
1. Master model weights (16.38 GB BF16) -> wecos-myanmar-ocr-8b-master.gguf
2. Multimodal projector (1.16 GB F16) -> mmproj-wecos-ocr-f16.gguf
"""

from pathlib import Path
import shutil
import sys

# Locate Ollama blobs directory portably
OLLAMA_BLOBS = Path.home() / ".ollama" / "models" / "blobs"

MODEL_BLOB_SHA = "sha256-d028337f6d394f9762e6961df71bcbb2602e1d0940bda9037b9741aeebc4979b"
MMPROJ_BLOB_SHA = "sha256-de42fb98aecba45b0153cd912344715b35150ac8855cc097485640827eb8f960"


def export_blobs(output_dir: Path):
    output_dir.mkdir(parents=True, exist_ok=True)
    
    model_src = OLLAMA_BLOBS / MODEL_BLOB_SHA
    mmproj_src = OLLAMA_BLOBS / MMPROJ_BLOB_SHA

    if not model_src.exists():
        print(f"Error: Model blob not found at {model_src}", file=sys.stderr)
        return False

    if not mmproj_src.exists():
        print(f"Error: Multimodal projector blob not found at {mmproj_src}", file=sys.stderr)
        return False

    print(f"[*] Found master model blob: {model_src.stat().st_size / (1024**3):.2f} GB")
    print(f"[*] Found mmproj blob: {mmproj_src.stat().st_size / (1024**3):.2f} GB")

    target_model = output_dir / "wecos-myanmar-ocr-8b-master.gguf"
    target_mmproj = output_dir / "mmproj-wecos-ocr-f16.gguf"

    print(f"[*] Copying to: {target_model} ...")
    shutil.copyfile(model_src, target_model)

    print(f"[*] Copying to: {target_mmproj} ...")
    shutil.copyfile(mmproj_src, target_mmproj)

    print("[+] Successfully exported GGUF model files for Hugging Face upload!")
    return True


if __name__ == "__main__":
    out = Path("./exported_models")
    export_blobs(out)

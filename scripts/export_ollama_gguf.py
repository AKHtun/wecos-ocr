"""Export and Quantize Ollama GGUF Blobs for Hugging Face Distribution.

Extracts:
1. Multimodal projector (1.16 GB F16) -> mmproj-wecos-ocr-f16.gguf
2. Quantizes master model (16.38 GB BF16) directly to Q4_K_M (~4.9 GB)
"""

import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys

OLLAMA_BLOBS = Path.home() / ".ollama" / "models" / "blobs"
MODEL_BLOB_SHA = "sha256-d028337f6d394f9762e6961df71bcbb2602e1d0940bda9037b9741aeebc4979b"
MMPROJ_BLOB_SHA = "sha256-de42fb98aecba45b0153cd912344715b35150ac8855cc097485640827eb8f960"
LLAMA_QUANTIZE = Path(r"C:\Dev\llama.cpp\llama-quantize.exe")


def run_export(output_dir: Path, quant_type: str = "Q4_K_M", threads: int = 16):
    output_dir.mkdir(parents=True, exist_ok=True)

    model_src = OLLAMA_BLOBS / MODEL_BLOB_SHA
    mmproj_src = OLLAMA_BLOBS / MMPROJ_BLOB_SHA

    if not model_src.exists():
        print(f"[-] Error: Master model blob not found at {model_src}", file=sys.stderr)
        return False

    if not mmproj_src.exists():
        print(f"[-] Error: Multimodal projector blob not found at {mmproj_src}", file=sys.stderr)
        return False

    # 1. Copy mmproj
    target_mmproj = output_dir / "mmproj-wecos-ocr-f16.gguf"
    if not target_mmproj.exists() or target_mmproj.stat().st_size == 0:
        print(f"[*] Copying multimodal projector ({mmproj_src.stat().st_size / (1024**3):.2f} GB) to {target_mmproj} ...")
        shutil.copyfile(mmproj_src, target_mmproj)
        print("[+] Copied multimodal projector.")
    else:
        print(f"[+] Multimodal projector already exists at {target_mmproj}")

    # 2. Quantize model directly from blob
    target_quant = output_dir / f"wecos-myanmar-ocr-8b-{quant_type}.gguf"
    if not target_quant.exists() or target_quant.stat().st_size == 0:
        if not LLAMA_QUANTIZE.exists():
            print(f"[-] Error: llama-quantize executable not found at {LLAMA_QUANTIZE}", file=sys.stderr)
            return False

        print(f"[*] Quantizing master weights ({model_src.stat().st_size / (1024**3):.2f} GB) -> {target_quant.name} ({quant_type}) with {threads} threads ...")
        cmd = [str(LLAMA_QUANTIZE), str(model_src), str(target_quant), quant_type, str(threads)]
        ret = subprocess.run(cmd)
        if ret.returncode != 0:
            print(f"[-] Quantization failed with return code {ret.returncode}", file=sys.stderr)
            return False
        print(f"[+] Quantization successful! Final size: {target_quant.stat().st_size / (1024**3):.2f} GB")
    else:
        print(f"[+] Quantized model already exists at {target_quant} ({target_quant.stat().st_size / (1024**3):.2f} GB)")

    # 3. Copy Modelfile and README
    repo_root = Path(__file__).resolve().parent.parent
    modelfile_src = repo_root / "models" / "Modelfile"
    readme_src = repo_root / "models" / "README.md"
    if modelfile_src.exists():
        shutil.copyfile(modelfile_src, output_dir / "Modelfile")
    if readme_src.exists():
        shutil.copyfile(readme_src, output_dir / "README.md")

    print("[+] All assets ready in:", output_dir)
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export & quantize WEcoS Myanmar OCR GGUF models")
    parser.add_argument("-o", "--output", type=Path, default=Path("./exported_models"), help="Output directory")
    parser.add_argument("-q", "--quant", default="Q4_K_M", help="Quantization type (default: Q4_K_M)")
    parser.add_argument("-t", "--threads", type=int, default=16, help="Thread count")
    args = parser.parse_args()

    success = run_export(args.output, args.quant, args.threads)
    if not success:
        sys.exit(1)

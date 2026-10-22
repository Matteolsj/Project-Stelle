from pathlib import Path
from scripts.utils import download_file

VAD_DIR = Path(__file__).parents[1] / "web" / "vad"
FILES = [
    ("ort.wasm.min.js", "https://cdn.jsdelivr.net/npm/onnxruntime-web@1.22.0/dist/ort.wasm.min.js", "65e09376df69107e881b5c34d2d37aed333a366b6d941073ec518168e269b87d"),
    ("ort-wasm-simd-threaded.wasm", "https://cdn.jsdelivr.net/npm/onnxruntime-web@1.22.0/dist/ort-wasm-simd-threaded.wasm", "71aef04959c5c1b6de461b6538e2058e306610034a85aad2742d0c7fd4533fe4"),
    ("ort-wasm-simd-threaded.mjs", "https://cdn.jsdelivr.net/npm/onnxruntime-web@1.22.0/dist/ort-wasm-simd-threaded.mjs", "30dd851d9c00622940500f71ddd2ff8820c5cb65270816080175b958705385a8"),    
    ("bundle.min.js", "https://cdn.jsdelivr.net/npm/@ricky0123/vad-web@0.0.31/dist/bundle.min.js", "4b3f72db78dc5f65c0ba9047a9033581e15fe57810a3ac5742aca274d1702e1f"),
    ("vad.worklet.bundle.min.js", "https://cdn.jsdelivr.net/npm/@ricky0123/vad-web@0.0.31/dist/vad.worklet.bundle.min.js", "8a48fdc7429948a2fde3d29a84bb1a64c1f67b4ba578ccaa7548b7f989f06a74"),
    ("silero_vad_v5.onnx", "https://cdn.jsdelivr.net/npm/@ricky0123/vad-web@0.0.31/dist/silero_vad_v5.onnx", "2623a2953f6ff3d2c1e61740c6cdb7168133479b267dfef114a4a3cc5bdd788f"),
]

def main():
    VAD_DIR.mkdir(parents=True, exist_ok=True)
    print("[download] Downloading VAD files (this may take a few minutes)...")
    for filename, url, expected_hash in FILES:
        dest = VAD_DIR / filename
        download_file(url, dest, expected_hash)
    print("\nAll VAD files are ready in web/vad/\n")

if __name__ == "__main__":
    main()
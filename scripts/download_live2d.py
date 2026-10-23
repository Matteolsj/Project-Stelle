from pathlib import Path
from scripts.utils import download_file

LIB_DIR = Path(__file__).parents[1] / "web" / "live2d" / "lib"

FILES = [
    ("live2dcubismcore.min.js", "https://cubism.live2d.com/sdk-web/cubismcore/live2dcubismcore.min.js", "25ae938cb4fe282ce189b357bcc97e603d1e1f7ec78bf04150d401c23cdc792f"),
    ("pixi.min.js", "https://cdn.jsdelivr.net/npm/pixi.js@6.5.10/dist/browser/pixi.min.js", "403f2f2ee8145fa17f60c5c89403056efe2680e5096ec2762036486914ed19c5"),
    ("cubism4.min.js", "https://cdn.jsdelivr.net/npm/pixi-live2d-display@0.4.0/dist/cubism4.min.js", "af1267e6d52759b245766c578d905bfa025b532d5c3cc727c370957c4409e21b")
]

def main():
    LIB_DIR.mkdir(parents=True, exist_ok=True)
    print("[download] Downloading Live2D web libraries...")
    
    for filename, url, expected_hash in FILES:
        dest = LIB_DIR / filename
        download_file(url, dest, expected_hash)
        
    print("\nAll Live2D libraries are ready in web/live2d/lib/\n")

if __name__ == "__main__":
    main()

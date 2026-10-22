import hashlib
import sys
from urllib.request import urlretrieve

def compute_hash(file_path):
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def download_file(url, dest, expected_hash):
    filename = dest.name
    if dest.exists():
        actual_hash = compute_hash(dest)
        if actual_hash == expected_hash:
            print(f"[skip] {filename} is valid (hash OK).")
            return
        else:
            print(f"[warn] {filename} is corrupted (hash mismatch). Re-downloading...")
            dest.unlink()
    print(f"[download] {filename} ...")
    tmp = dest.with_suffix(dest.suffix + ".part")
    try:
        urlretrieve(url, tmp)
        actual_hash = compute_hash(tmp)
        if actual_hash != expected_hash:
            tmp.unlink()
            print(f"[error] {filename}: hash mismatch after download.")
            sys.exit(1)
        tmp.rename(dest)
        print(f"[done] {filename} ({dest.stat().st_size // 1024 // 1024} MB)")
    except Exception as e:
        if tmp.exists():
            tmp.unlink()
        print(f"[error] Failed to download {filename}: {e}")
        sys.exit(1)
"""
Upload Bronze/Silver/Gold Parquet files to Azure Data Lake Storage Gen2.
Run after bronze_export.py, silver.py, and gold.py have produced local Parquet files.

Run:  python azure/upload_adls.py
Requires: AZURE_STORAGE_ACCOUNT + AZURE_STORAGE_KEY in .env
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

STORAGE_ACCOUNT = os.getenv("AZURE_STORAGE_ACCOUNT", "")
STORAGE_KEY     = os.getenv("AZURE_STORAGE_KEY", "")
DATA_DIR        = Path(os.getenv("DATA_DIR", "./data"))

LAYER_MAP = {
    "bronze": DATA_DIR / "bronze",
    "silver": DATA_DIR / "silver",
    "gold":   DATA_DIR / "gold",
}


def upload_layer(layer: str, local_dir: Path):
    from azure.storage.filedatalake import DataLakeServiceClient

    service = DataLakeServiceClient(
        account_url=f"https://{STORAGE_ACCOUNT}.dfs.core.windows.net",
        credential=STORAGE_KEY,
    )
    fs = service.get_file_system_client(layer)

    parquet_files = list(local_dir.glob("*.parquet"))
    if not parquet_files:
        print(f"  ⚠  No Parquet files found in {local_dir}")
        return

    for pf in parquet_files:
        file_client = fs.get_file_client(pf.name)
        with open(pf, "rb") as f:
            data = f.read()
        file_client.upload_data(data, overwrite=True)
        print(f"  ✓ {layer}/{pf.name}  ({len(data) // 1024} KB)")


def main():
    if not STORAGE_ACCOUNT or not STORAGE_KEY:
        print("ERROR: Set AZURE_STORAGE_ACCOUNT and AZURE_STORAGE_KEY in .env")
        return

    for layer, path in LAYER_MAP.items():
        if path.exists():
            print(f"--- Uploading {layer} layer ---")
            upload_layer(layer, path)
        else:
            print(f"  ⚠  {path} not found — run export/bronze_export.py first")

    print("\nADLS upload complete.")


if __name__ == "__main__":
    main()

"""
Upload the raw CSV to Azure Data Lake Storage Gen2.

Install:
    pip install azure-identity azure-storage-file-datalake

Required environment variables:
    AZURE_STORAGE_ACCOUNT_URL
    AZURE_CONTAINER
    AZURE_ADLS_PATH
    AZURE_TENANT_ID
    AZURE_CLIENT_ID
    AZURE_CLIENT_SECRET
    LOCAL_CSV (optional; defaults to data/raw/Indian_Startup_Funding.csv)
"""

import os
from pathlib import Path

from azure.identity import ClientSecretCredential
from azure.storage.filedatalake import DataLakeServiceClient


def main():
    local_csv = Path(
        os.getenv("LOCAL_CSV", "data/raw/Indian_Startup_Funding.csv")
    )

    if not local_csv.exists():
        raise FileNotFoundError(f"CSV not found: {local_csv}")

    credential = ClientSecretCredential(
        tenant_id=os.environ["AZURE_TENANT_ID"],
        client_id=os.environ["AZURE_CLIENT_ID"],
        client_secret=os.environ["AZURE_CLIENT_SECRET"],
    )

    service = DataLakeServiceClient(
        account_url=os.environ["AZURE_STORAGE_ACCOUNT_URL"],
        credential=credential,
    )

    filesystem = service.get_file_system_client(
        os.environ["AZURE_CONTAINER"]
    )

    base_path = os.getenv("AZURE_ADLS_PATH", "startup-funding").strip("/")
    remote_path = f"{base_path}/{local_csv.name}"

    file_client = filesystem.get_file_client(remote_path)

    with local_csv.open("rb") as data:
        file_client.upload_data(data, overwrite=True)

    print(f"Uploaded local file : {local_csv}")
    print(f"ADLS remote path    : {remote_path}")


if __name__ == "__main__":
    main()

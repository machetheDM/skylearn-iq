#!/bin/bash
# ============================================================
# SKYLearn IQ — Azure Data Lake + Synapse Provisioning
# ============================================================
# Prerequisites:
#   1. Azure CLI installed + logged in: az login
#   2. .env file at cloud-bi/ populated with your values
# Run: bash azure/provision.sh
# ============================================================

source .env

RG=$AZURE_RESOURCE_GROUP
LOC=${AZURE_LOCATION:-southafricanorth}
STORAGE=$AZURE_STORAGE_ACCOUNT
SYNAPSE="skylearn-synapse"
DATABRICKS="skylearn-databricks"

echo "=== SKYLearn IQ — Azure provisioning ==="
echo "Resource Group : $RG"
echo "Location       : $LOC"
echo ""

# 1. Resource group
az group create --name $RG --location $LOC --output table

# 2. ADLS Gen2 (hierarchical namespace = Data Lake)
echo "--- Creating ADLS Gen2 storage account ---"
az storage account create \
  --name $STORAGE \
  --resource-group $RG \
  --location $LOC \
  --sku Standard_LRS \
  --kind StorageV2 \
  --hns true \
  --output table

# 3. Containers (filesystem) — Bronze / Silver / Gold
az storage fs create --name bronze --account-name $STORAGE
az storage fs create --name silver --account-name $STORAGE
az storage fs create --name gold   --account-name $STORAGE
echo "  ✓ Containers: bronze, silver, gold"

# 4. Synapse Analytics workspace
echo "--- Creating Synapse Analytics workspace ---"
az synapse workspace create \
  --name $SYNAPSE \
  --resource-group $RG \
  --location $LOC \
  --storage-account $STORAGE \
  --file-system "gold" \
  --sql-admin-login-user synadmin \
  --sql-admin-login-password "SKYLearn@Azure2026!" \
  --output table

# 5. Synapse serverless SQL pool (built-in, no extra cost)
echo "  ✓ Synapse serverless SQL pool enabled by default"

# 6. Azure Databricks workspace (for PySpark transforms)
echo "--- Creating Azure Databricks workspace ---"
az databricks workspace create \
  --name $DATABRICKS \
  --resource-group $RG \
  --location $LOC \
  --sku standard \
  --output table

echo ""
echo "=== Provisioning complete ==="
echo "Next steps:"
echo "  1. python azure/upload_adls.py           # upload Parquet to ADLS"
echo "  2. Run transform/silver.py + gold.py     # or as Databricks notebook"
echo "  3. Execute azure/synapse_ddl.sql          # in Synapse Studio"
echo "  4. streamlit run main.py                 # local BI dashboard"

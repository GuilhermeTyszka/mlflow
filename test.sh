#!/bin/bash

# Configurações essenciais
PROJECT_DIR=${PROJECT_DIR:-/home/cdsw}
ARTIFACT_ROOT="$PROJECT_DIR/mlflow-artifacts"
DB_FILE="$PROJECT_DIR/mlflow.db"
ARTIFACT_PORT=8000
MLFLOW_PORT=5000

# Criar diretórios necessários
mkdir -p "$ARTIFACT_ROOT"

# Iniciar servidor de artefatos em segundo plano
python artifact_server.py --artifact-root="$ARTIFACT_ROOT" --port=$ARTIFACT_PORT > artifact-server.log 2>&1 &

# Aguardar inicialização do servidor de artefatos
sleep 3

# Obter URL base do projeto
PROJECT_URL="${CDSW_ENGINE_ID}.${CDSW_DOMAIN}"
ARTIFACT_URL="http://${PROJECT_URL}:${ARTIFACT_PORT}"

# Iniciar servidor MLflow
mlflow server \
  --backend-store-uri "sqlite:///$DB_FILE" \
  --default-artifact-root "$ARTIFACT_URL" \
  --host 0.0.0.0 \
  --port $MLFLOW_PORT

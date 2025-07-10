from flask import Flask, request, Response, redirect
import subprocess
import threading
import requests

USERNAME = "admin"
PASSWORD = "senha123"

MLFLOW_PORT = 5001  # MLflow real rodará internamente aqui

# Inicia o MLflow em uma thread paralela
def start_mlflow():
    subprocess.call([
        "mlflow", "server",
        "--host", "127.0.0.1",
        "--port", str(MLFLOW_PORT),
        "--backend-store-uri", "sqlite:///mlflow.db",
        "--default-artifact-root", "/home/cdsw/mlruns"
    ])

# Thread para rodar MLflow
threading.Thread(target=start_mlflow, daemon=True).start()

# Proxy com autenticação
app = Flask(__name__)

def check_auth(username, password):
    return username == USERNAME and password == PASSWORD

def authenticate():
    return Response(
        "Acesso restrito", 401,
        {"WWW-Authenticate": 'Basic realm="Login Required"'}
    )

@app.before_request
def require_auth():
    auth = request.authorization
    if not auth or not check_auth(auth.username, auth.password):
        return authenticate()

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
def proxy(path):
    mlflow_url = f"http://127.0.0.1:{MLFLOW_PORT}/{path}"
    resp = requests.request(
        method=request.method,
        url=mlflow_url,
        headers={key: value for key, value in request.headers if key.lower() != 'host'},
        data=request.get_data(),
        cookies=request.cookies,
        allow_redirects=False,
    )
    excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
    headers = [(name, value) for name, value in resp.raw.headers.items() if name.lower() not in excluded_headers]
    response = Response(resp.content, resp.status_code, headers)
    return response

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

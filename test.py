from mlflow.tracking.request_header.abstract_request_header_provider import RequestHeaderProvider

class BasicAuthHeaderProvider(RequestHeaderProvider):
    def __init__(self, token):
        self.token = token

    def in_context(self):
        return True

    def request_headers(self):
        return {"Authorization": self.token}

# Registra o provider globalmente
import mlflow.tracking.request_header.registry
mlflow.tracking.request_header.registry.register_request_header_provider(
    BasicAuthHeaderProvider(auth_header)
)

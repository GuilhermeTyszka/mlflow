import os
import http.server
import socketserver
from functools import partial

class ArtifactHTTPHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, artifact_root=None, **kwargs):
        self.artifact_root = artifact_root
        super().__init__(*args, directory=artifact_root, **kwargs)
    
    def do_PUT(self):
        path = self.translate_path(self.path)
        if not path.startswith(self.artifact_root):
            self.send_error(403, "Forbidden")
            return
            
        os.makedirs(os.path.dirname(path), exist_ok=True)
        content_length = int(self.headers['Content-Length'])
        
        with open(path, 'wb') as f:
            f.write(self.rfile.read(content_length))
        
        self.send_response(201)
        self.end_headers()
        self.wfile.write(b"Artifact uploaded successfully")

def run_artifact_server(port=8000, artifact_root=None):
    handler = partial(ArtifactHTTPHandler, artifact_root=artifact_root)
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"Serving artifacts from {artifact_root} on port {port}")
        httpd.serve_forever()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--artifact-root", required=True)
    args = parser.parse_args()
    
    run_artifact_server(port=args.port, artifact_root=args.artifact_root)

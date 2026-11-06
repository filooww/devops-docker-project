import os
import socket
from datetime import datetime, timezone

from flask import Flask, jsonify

app = Flask(__name__)

# Settings come from environment variables (set them in docker-compose.yml)
APP_NAME = os.getenv("APP_NAME", "demo-app")
APP_ENV = os.getenv("APP_ENV", "development")
PORT = int(os.getenv("PORT", "5000"))


@app.route("/")
def index():
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    return f"""<!doctype html>
<html><head><meta charset="utf-8"><title>{APP_NAME}</title>
<style>
  body {{ margin:0; min-height:100vh; display:flex; align-items:center; justify-content:center;
         background:#0f172a; font-family:-apple-system,Segoe UI,Helvetica,Arial,sans-serif; color:#e2e8f0; }}
  .card {{ background:#1e293b; border:1px solid #334155; border-radius:16px; padding:36px 44px;
          box-shadow:0 20px 50px rgba(0,0,0,.4); min-width:380px; }}
  h1 {{ margin:0 0 4px; font-size:28px; }}
  .sub {{ color:#94a3b8; margin-bottom:24px; font-size:14px; }}
  .badge {{ display:inline-block; background:#16a34a; color:#fff; font-size:12px; font-weight:600;
           padding:3px 10px; border-radius:999px; margin-left:8px; vertical-align:middle; }}
  .row {{ display:flex; justify-content:space-between; gap:32px; padding:10px 0; border-top:1px solid #334155; }}
  .k {{ color:#94a3b8; }}
  .v {{ font-family:Menlo,Consolas,monospace; }}
</style></head>
<body><div class="card">
  <h1>{APP_NAME}<span class="badge">running</span></h1>
  <div class="sub">Flask app in a Docker container</div>
  <div class="row"><span class="k">Environment</span><span class="v">{APP_ENV}</span></div>
  <div class="row"><span class="k">Container hostname</span><span class="v">{socket.gethostname()}</span></div>
  <div class="row"><span class="k">Port</span><span class="v">{PORT}</span></div>
  <div class="row"><span class="k">Server time (UTC)</span><span class="v">{now}</span></div>
</div></body></html>"""


@app.route("/health")
def health():
    # Used by HEALTHCHECK and monitoring
    return jsonify(status="ok")


if __name__ == "__main__":
    # 0.0.0.0 is required inside a container, 127.0.0.1 would not be reachable from outside
    app.run(host="0.0.0.0", port=PORT)

import os
import random
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

VERSION = os.getenv("APP_VERSION", "v1")
FEATURE_NEW_SCORER = os.getenv("FEATURE_NEW_SCORER", "false").lower() == "true"
EXTRA_DELAY_MS = int(os.getenv("EXTRA_DELAY_MS", "0"))
ERROR_RATE = float(os.getenv("ERROR_RATE", "0.0"))  # e.g., 0.15 for 15% 500 errors


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if EXTRA_DELAY_MS > 0:
            time.sleep(EXTRA_DELAY_MS / 1000.0)

        if random.random() < ERROR_RATE:
            self.send_response(500)
            self.end_headers()
            print(f'level=ERROR version={VERSION} path={self.path} reason="simulated_500"')
            self.wfile.write(f"error from {VERSION}\n".encode("utf-8"))
            return

        scorer_mode = "v2_model" if FEATURE_NEW_SCORER else "v1_baseline"
        self.send_response(200)
        self.end_headers()
        print(
            f"level=INFO version={VERSION} scorer={scorer_mode} "
            f"delay_ms={EXTRA_DELAY_MS} path={self.path}"
        )
        body = f"version={VERSION} scorer={scorer_mode} path={self.path}\n"
        self.wfile.write(body.encode("utf-8"))

    def log_message(self, format, *args):
        # Suppress default stderr access log noise; our structured stdout prints appear in Cloud Logging
        return


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))
    server = HTTPServer(("0.0.0.0", port), Handler)
    print(
        f"level=INFO event=startup version={VERSION} port={port} "
        f"feature_new_scorer={FEATURE_NEW_SCORER} error_rate={ERROR_RATE}"
    )
    server.serve_forever()

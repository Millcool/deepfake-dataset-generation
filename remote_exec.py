import argparse
import json
import os
import ssl
import sys
import uuid

import requests
import websocket

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", required=True)
    parser.add_argument("--token", required=True)
    parser.add_argument("--code-file", required=True)
    parser.add_argument("--kernel", default="python3")
    parser.add_argument("--session-name", default="remote_exec.ipynb")
    parser.add_argument("--timeout", type=int, default=300)
    args = parser.parse_args()

    for key in [
        "HTTP_PROXY",
        "HTTPS_PROXY",
        "http_proxy",
        "https_proxy",
        "ALL_PROXY",
        "all_proxy",
    ]:
        os.environ.pop(key, None)

    with open(args.code_file, "r", encoding="utf-8") as f:
        code = f.read()

    s = requests.Session()
    s.trust_env = False
    headers = {"Authorization": f"token {args.token}"}

    payload = {
        "kernel": {"name": args.kernel},
        "name": args.session_name,
        "path": args.session_name,
        "type": "notebook",
    }
    r = s.post(f"{args.base}/api/sessions", headers=headers, json=payload, timeout=30)
    r.raise_for_status()
    session = r.json()
    kernel_id = session["kernel"]["id"]
    session_id = session["id"]

    ws_url = (
        f"wss://ws.miem3.vmnet.top/user/ilanmironov@edu.hse.ru/api/kernels/"
        f"{kernel_id}/channels?token={args.token}"
    )
    ws = websocket.create_connection(
        ws_url,
        sslopt={"cert_reqs": ssl.CERT_NONE},
        timeout=args.timeout,
        http_proxy_host=None,
        http_proxy_port=None,
        header=[f"Authorization: token {args.token}"],
        origin="https://ws.miem3.vmnet.top",
    )

    msg_id = str(uuid.uuid4())
    req = {
        "header": {
            "msg_id": msg_id,
            "msg_type": "execute_request",
            "username": "",
            "session": str(uuid.uuid4()),
            "version": "5.3",
        },
        "parent_header": {},
        "metadata": {},
        "content": {
            "code": code,
            "silent": False,
            "store_history": True,
            "user_expressions": {},
            "allow_stdin": False,
            "stop_on_error": True,
        },
        "buffers": [],
        "channel": "shell",
    }
    ws.send(json.dumps(req))

    status = None
    while True:
        opcode, data = ws.recv_data()
        if opcode == websocket.ABNF.OPCODE_TEXT:
            msg = json.loads(data.decode("utf-8"))
        else:
            text = data.decode("utf-8", errors="ignore")
            idx = text.find("{")
            if idx < 0:
                continue
            msg = json.loads(text[idx:])

        if msg.get("parent_header", {}).get("msg_id") != msg_id:
            continue

        msg_type = msg.get("msg_type")
        if msg_type == "stream":
            sys.stdout.write(msg.get("content", {}).get("text", ""))
            sys.stdout.flush()
        elif msg_type == "error":
            content = msg.get("content", {})
            print("REMOTE_ERROR:", content.get("ename"), content.get("evalue"))
        elif msg_type == "execute_reply":
            status = msg.get("content", {}).get("status")
            print(f"EXEC_STATUS {status}")
            break

    ws.close()
    s.delete(f"{args.base}/api/sessions/{session_id}", headers=headers, timeout=30)
    return 0 if status == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())

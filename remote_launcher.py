import argparse
import json
import os
import socket
import subprocess
import sys
import threading
from pathlib import Path

DEFAULT_PORT = 50505

TOKEN = "qwertyuiopasdfghjklzxcvbnm"

DEFAULT_MAIN_PY = str(Path(__file__).with_name("main.py"))


def send_command(ip: str, port: int, token: str, cmd: str) -> None:
    msg = {"token": token, "cmd": cmd}
    data = json.dumps(msg).encode("utf-8")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(6)
        s.connect((ip, port))
        s.sendall(data)
        resp = s.recv(65535)

    print(resp.decode("utf-8", errors="replace"))


def _handle_client(conn: socket.socket, addr, token: str, main_py: str, python_exe: str):
    try:
        raw = conn.recv(65535)
        if not raw:
            return

        try:
            msg = json.loads(raw.decode("utf-8", errors="replace"))
        except json.JSONDecodeError:
            conn.sendall(b'{"ok":false,"error":"bad_json"}')
            return

        if msg.get("token") != token:
            conn.sendall(b'{"ok":false,"error":"bad_token"}')
            return

        cmd = msg.get("cmd", "")
        if cmd == "ping":
            conn.sendall(b'{"ok":true,"result":"pong"}')
            return

        if cmd == "launch_5":
            p = Path(main_py)
            if not p.exists():
                conn.sendall(b'{"ok":false,"error":"main_py_not_found","detail":"check --main path"}')
                return

            subprocess.Popen([python_exe, str(p)], cwd=str(p.parent))
            conn.sendall(b'{"ok":true,"result":"launched"}')
            return

        conn.sendall(b'{"ok":false,"error":"unknown_cmd"}')

    finally:
        try:
            conn.close()
        except Exception:
            pass


def run_agent(host: str, port: int, token: str, main_py: str, python_exe: str) -> None:
    print(f"[agent] host={host} port={port}")
    print(f"[agent] main_py={main_py}")
    print(f"[agent] python={python_exe}")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((host, port))
        s.listen(30)

        while True:
            conn, addr = s.accept()
            t = threading.Thread(
                target=_handle_client,
                args=(conn, addr, token, main_py, python_exe),
                daemon=True
            )
            t.start()


def parse_args():
    ap = argparse.ArgumentParser(description="Remote launcher: agent + sender in one file")

    ap.add_argument("--token", default=TOKEN, help="shared secret token (same on both PCs)")
    ap.add_argument("--port", type=int, default=DEFAULT_PORT)

    sub = ap.add_subparsers(dest="mode", required=True)

    a = sub.add_parser("agent", help="run as agent (server) on remote PC")
    a.add_argument("--host", default="0.0.0.0")
    a.add_argument("--main", default=DEFAULT_MAIN_PY, help="path to main.py on this PC")
    a.add_argument("--python", dest="python_exe", default=sys.executable,
                   help="python exe to run main.py (default: current interpreter)")

    s = sub.add_parser("send", help="send command to agent from main PC")
    s.add_argument("ip", help="remote agent IP (LAN)")
    s.add_argument("cmd", choices=["ping", "launch_5"], help="command")

    return ap.parse_args()


def main():
    args = parse_args()

    if args.mode == "agent":
        run_agent(args.host, args.port, args.token, args.main, args.python_exe)
        return

    if args.mode == "send":
        send_command(args.ip, args.port, args.token, args.cmd)
        return


if __name__ == "__main__":
    main()

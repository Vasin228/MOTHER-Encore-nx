import hashlib
import http.client
import json
import os
import sys
import time

SWITCH_IP = "192.168.0.7"
PORT = 4150

FILES = [
    (r"d:\Anti\mother-encore-nx\build\mother_encore.nro", "/switch/mother-encore/mother_encore.nro"),
    (r"d:\Anti\mother-encore-nx\build\mother_encore.pck", "/switch/mother-encore/mother_encore.pck"),
]


def get_remote_hash(remote_path: str) -> str:
    last_err = None
    for attempt in range(1, 4):
        try:
            conn = http.client.HTTPConnection(SWITCH_IP, PORT, timeout=120)
            conn.request("GET", f"/files/hash?path={remote_path}")
            resp = conn.getresponse()
            raw = resp.read().decode("utf-8", "ignore")
            conn.close()
            if resp.status == 200:
                return json.loads(raw).get("hash", "")
            last_err = f"HTTP {resp.status}: {raw}"
        except (ConnectionResetError, OSError, json.JSONDecodeError) as e:
            last_err = repr(e)
        if attempt < 3:
            time.sleep(3)
    print(f"WARN: hash check failed for {remote_path}: {last_err}")
    return ""


def upload_one(local_path: str, remote_path: str) -> None:
    size = os.path.getsize(local_path)
    with open(local_path, "rb") as f:
        data = f.read()
    local_hash = hashlib.sha256(data).hexdigest()

    existing_hash = get_remote_hash(remote_path)
    if existing_hash == local_hash:
        print(f"SKIP {remote_path}: remote SHA256 already matches ({local_hash})")
        return

    print(f"Uploading {local_path} ({size} bytes, SHA256={local_hash}) -> http://{SWITCH_IP}:{PORT}/files?path={remote_path}")
    t0 = time.time()
    conn = http.client.HTTPConnection(SWITCH_IP, PORT, timeout=300)
    headers = {
        "Content-Length": str(size),
        "Content-Type": "application/octet-stream",
    }
    conn.request("PUT", f"/files?path={remote_path}", body=data, headers=headers)
    resp = conn.getresponse()
    body = resp.read().decode("utf-8", "ignore")
    conn.close()
    elapsed = max(time.time() - t0, 0.001)
    speed = (size / (1024 * 1024)) / elapsed
    print(f"Response: HTTP {resp.status} {body}")
    if resp.status not in (200, 201):
        print(f"ERROR: unexpected HTTP status {resp.status}")
        sys.exit(1)
    print(f"Transfer complete: 100% in {elapsed:.2f}s ({speed:.2f} MB/s)")

    time.sleep(2)
    remote_hash = get_remote_hash(remote_path)
    if remote_hash != local_hash:
        print(f"ERROR: SHA256 mismatch! local={local_hash} remote={remote_hash}")
        sys.exit(1)
    print(f"SHA256 MATCH: {remote_hash}")


if __name__ == "__main__":
    for lp, rp in FILES:
        upload_one(lp, rp)

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


def upload_one(local_path: str, remote_path: str) -> None:
    size = os.path.getsize(local_path)
    with open(local_path, "rb") as f:
        data = f.read()
    local_hash = hashlib.sha256(data).hexdigest()
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

    conn = http.client.HTTPConnection(SWITCH_IP, PORT, timeout=60)
    conn.request("GET", f"/files/hash?path={remote_path}")
    resp = conn.getresponse()
    hash_info = json.loads(resp.read().decode("utf-8"))
    conn.close()
    remote_hash = hash_info.get("hash")
    if remote_hash != local_hash:
        print(f"ERROR: SHA256 mismatch! local={local_hash} remote={remote_hash}")
        sys.exit(1)
    print(f"SHA256 MATCH: {remote_hash}")


if __name__ == "__main__":
    for lp, rp in FILES:
        upload_one(lp, rp)

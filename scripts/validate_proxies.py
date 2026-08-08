#!/usr/bin/env python3
"""Validate proxies from a proxy list file and update PROXY_LIST in .env with alive ones.

Usage:
    python3 scripts/validate_proxies.py /home/jitanshu/Downloads/Free_Proxy_List.txt
    python3 scripts/validate_proxies.py /path/to/file.txt --timeout 10 --threads 20 --write
"""

import argparse
import concurrent.futures
import csv
import os
import re

import requests


def read_proxies_from_file(path: str) -> list[str]:
    if path.endswith(".csv") or path.endswith(".txt"):
        with open(path, newline="") as f:
            sample = f.read(2000)
        if "protocols" in sample and "ip," in sample:
            proxies = []
            with open(path, newline="") as f:
                for row in csv.DictReader(f):
                    if "http" not in row.get("protocols", "").lower():
                        continue
                    proxies.append(f"http://{row['ip'].strip()}:{row['port'].strip()}")
            return proxies
    proxies = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            line = line.replace("http://", "").replace("https://", "")
            if ":" in line:
                proxies.append(f"http://{line}")
    return proxies


def read_env_proxies(env_path: str) -> list[str]:
    if not os.path.exists(env_path):
        return []
    with open(env_path) as f:
        for line in f:
            if line.startswith("PROXY_LIST="):
                return [p.strip() for p in line.split("=", 1)[1].split(",") if p.strip()]
    return []


def test_proxy(proxy: str, timeout: int) -> tuple[str, bool, float]:
    try:
        r = requests.get(
            "https://api.ipify.org?format=json",
            proxies={"http": proxy, "https": proxy},
            timeout=timeout,
        )
        if r.status_code == 200:
            return proxy, True, r.elapsed.total_seconds()
    except Exception:
        pass
    return proxy, False, 0.0


def update_env(env_path: str, proxies: list[str]):
    with open(env_path) as f:
        content = f.read()
    new_line = "PROXY_LIST=" + ",".join(proxies)
    if re.search(r"^PROXY_LIST=.*$", content, re.MULTILINE):
        content = re.sub(r"^PROXY_LIST=.*$", new_line, content, flags=re.MULTILINE)
    else:
        content += "\n" + new_line + "\n"
    with open(env_path, "w") as f:
        f.write(content)
    print(f"Updated {env_path} with {len(proxies)} alive proxies")


def main():
    parser = argparse.ArgumentParser(description="Validate proxies and update .env")
    parser.add_argument("file", help="Path to proxy list file (txt or csv)")
    parser.add_argument("--timeout", type=int, default=10, help="Per-proxy connect timeout (s)")
    parser.add_argument("--threads", type=int, default=20, help="Concurrent test threads")
    parser.add_argument("--write", action="store_true", help="Write alive proxies to .env")
    parser.add_argument("--env", default=".env", help="Path to .env file")
    args = parser.parse_args()

    file_proxies = read_proxies_from_file(args.file)
    env_proxies = read_env_proxies(args.env)
    proxies = list(dict.fromkeys(env_proxies + file_proxies))
    print(f"Testing {len(proxies)} proxies ({len(file_proxies)} from file, {len(env_proxies)} from .env)...")

    alive = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.threads) as ex:
        futures = {ex.submit(test_proxy, p, args.timeout): p for p in proxies}
        for fut in concurrent.futures.as_completed(futures):
            proxy, ok, latency = fut.result()
            if ok:
                alive.append(proxy)
                print(f"ALIVE {proxy} ({latency*1000:.0f}ms)")
            else:
                print(f"DEAD  {proxy}")

    alive.sort(key=lambda p: proxies.index(p))
    print(f"\n{len(alive)}/{len(proxies)} proxies alive")
    if alive:
        print("PROXY_LIST=" + ",".join(alive))

    if args.write:
        update_env(args.env, alive)


if __name__ == "__main__":
    main()

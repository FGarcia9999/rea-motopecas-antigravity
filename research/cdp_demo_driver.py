"""Authorized CDP stimulus on the synthetic Rota 2 browser page.

This is NOT REA and is NOT a hidden-oracle or experimental agent. It only
produces the user action REA is passively observing in an ephemeral CI runner.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import time
import urllib.request


def select_target(backend: str, origin: str) -> dict:
    if backend != "http://127.0.0.1:9222" or origin != "http://127.0.0.1:8000":
        raise ValueError("Only the fixed synthetic Rota 2 local test scope is allowed")
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with opener.open(backend + "/json/list", timeout=5) as r:
        pages = json.loads(r.read(100_000))
    candidates = [x for x in pages if x.get("type") == "page" and
                  x.get("url", "").startswith(origin + "/")]
    if len(candidates) != 1 or not candidates[0].get("webSocketDebuggerUrl", "").startswith("ws://127.0.0.1:9222/"):
        raise ValueError("Exactly one local page with local WebSocket debugger required")
    return candidates[0]


def evaluate(ws, command_id: int, expression: str):
    ws.send(json.dumps({"id": command_id, "method": "Runtime.evaluate",
                        "params": {"expression": expression, "returnByValue": True}}))
    for _ in range(120):
        data = json.loads(ws.recv())
        if data.get("id") != command_id:
            continue
        result = data.get("result", {})
        if result.get("exceptionDetails") or data.get("error"):
            raise RuntimeError("CDP runtime evaluation failed")
        return result.get("result", {}).get("value")
    raise RuntimeError("Timed out waiting for CDP evaluate reply")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--output", type=pathlib.Path, required=True)
    args = p.parse_args()
    from websocket import create_connection  # pinned externally for CI smoke only
    target = select_target("http://127.0.0.1:9222", "http://127.0.0.1:8000")
    ws = create_connection(target["webSocketDebuggerUrl"], timeout=5, suppress_origin=True)
    try:
        clicked = evaluate(ws, 100, """(()=>{const b=[...document.querySelectorAll('#category-tabs button')].find(x=>x.textContent.trim()==='Freios');if(!b)throw Error('Freios tab not ready');b.click();return 'Freios';})()""")
        time.sleep(1.3)
        after = evaluate(ws, 101, """JSON.stringify({category:document.querySelector('#category')?.value,count:document.querySelectorAll('.product-card').length,label:document.querySelector('#result-count')?.textContent})""")
        data = json.loads(after)
        if clicked != 'Freios' or data.get('category') != 'Freios' or data.get('count') != 2:
            raise RuntimeError('Unexpected local category-filter result')
        args.output.write_text(json.dumps({
            'driver': 'CDP_RUNTIME_EVALUATE_SEPARATE_FROM_PASSIVE_REA',
            'action': 'CLICK_CATEGORY_FREIOS',
            'observed_ui': data,
            'scope': 'http://127.0.0.1:8000',
            'scientific_status': 'DEMO_STIMULUS_ONLY_NOT_A_RECONSTRUCTION_TRIAL',
        }, indent=2) + '\n', encoding='utf-8')
        print('LOCAL_CDP_STIMULUS_CLICK_FREIOS_OK')
        return 0
    finally:
        ws.close()


if __name__ == '__main__':
    raise SystemExit(main())

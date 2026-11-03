"""Smoke da ferramenta administrativa sem interface HTTP."""
import os
import subprocess
import sys
from app.db import connect


def execute(*args):
    return subprocess.run([sys.executable, '-m', 'app.manage', *args],capture_output=True,text=True,env=os.environ.copy())


def test_cli_stock(client):
    r = execute('stock','R2-FR-001','37')
    assert r.returncode == 0, r.stderr
    assert client.get('/api/products/1').json()['stock'] == 37


def test_cli_rejects_negative_stock(client):
    assert execute('stock','R2-FR-001','-3').returncode != 0
    assert client.get('/api/products/1').json()['stock'] == 20


def test_cli_list_orders(client):
    assert execute('orders').returncode == 0

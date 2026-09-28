"""Lets the parity tools talk to an in-process pyatlas (FastAPI TestClient) instead of HTTP."""


class TestClientAdapter:
    __test__ = False

    def __init__(self, client, name="pyatlas-test"):
        self.c = client
        self.name = name

    def request(self, method, path, params=None, json=None, headers=None):
        r = self.c.request(method, path, params=params, json=json, headers=headers)
        try:
            body = r.json()
        except ValueError:
            body = r.text or None
        return r.status_code, body

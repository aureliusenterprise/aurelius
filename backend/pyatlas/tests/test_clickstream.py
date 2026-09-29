"""Clickstream of the Aurelius frontend, stored for the "Aurelius usage" dashboard."""
from pyatlas.aurelius import clickstream as cs
from tests.conftest import _fresh_client

V2 = "/api/atlas/v2"


def events(c):
    st = c.app.state.services.store

    async def dump():
        return [d async for _id, d in st.scan(st.index("clickstream"), {"match_all": {}}, sort_field="timestamp")]
    return sorted(c.portal.call(dump), key=lambda d: (d["timestamp"], d["step"]))


def test_page_names():
    g = "6f3a7542-9f15-4753-bb19-65d29fcdc330"
    assert cs.parse_url("/search/browse") == ("browse", "/search/browse", None, None)
    assert cs.parse_url("/search/results?query=hourly%20data") == ("search results", "/search/results", "hourly data", None)
    assert cs.parse_url(f"/search/details/{g}") == ("entity details", "/search/details/:id", None, g)
    assert cs.parse_url(f"/search/edit-entity/{g}")[0] == "edit entity"
    assert cs.parse_url("/") == ("home", "/", None, None)
    assert cs.parse_url("/something/else")[0] == "/something/else"


def test_visits_and_navigation(monkeypatch):
    clock = [1_800_000_000.0]
    monkeypatch.setattr(cs.time, "time", lambda: clock[0])
    c = _fresh_client()
    try:
        g = c.post(f"{V2}/entity", json={"entity": {"typeName": "m4i_data_domain", "attributes": {
            "qualifiedName": "sales", "name": "Sales"}}}).json()["mutatedEntities"]["CREATE"][0]["guid"]
        for url, wait in [("/search/browse", 0), ("/search/results?query=sales", 12), (f"/search/details/{g}", 5),
                          ("/search/browse", 40 * 60)]:          # 40 minutes later: a new visit
            clock[0] += wait
            r = c.post("/api/aurelius/repository/log", json={"app": "atlas", "timestamp": 1, "url": url,
                                                             "userid": "someone-else"})
            assert r.status_code == 204
        ev = events(c)
        assert [(e["page"], e["step"], e["entry"], e["previousPage"], e["secondsOnPreviousPage"]) for e in ev] == [
            ("browse", 1, True, None, None), ("search results", 2, False, "browse", 12.0),
            ("entity details", 3, False, "search results", 5.0), ("browse", 1, True, None, None)]
        assert ev[1]["query"] == "sales"
        assert (ev[2]["entityType"], ev[2]["entityName"], ev[2]["entityGuid"]) == ("m4i_data_domain", "Sales", g)
        assert {e["user"] for e in ev} == {"admin"}                     # the logged-in user, not the sent userid
        assert len({e["session"] for e in ev[:3]}) == 1 and ev[3]["session"] != ev[0]["session"]
    finally:
        c.__exit__(None, None, None)

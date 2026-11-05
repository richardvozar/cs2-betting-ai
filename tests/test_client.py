import httpx
from app.api.client import CS2APIClient

def test_client_auth_and_json(monkeypatch):
    seen = {}
    def fake_get(url, headers, params, timeout):
        seen.update(headers=headers, params=params, url=url)

        request = httpx.Request("GET", url)

        return httpx.Response(
            200,
            json={"success": True, "data": []},
            request=request,
        )
    monkeypatch.setattr(httpx, "get", fake_get)
    client = CS2APIClient("https://api.citoapi.com/api/v1", "secret")
    result = client.get_json("/cs2/matches/recent", {"limit": 1, "page": 1})
    assert result["success"] is True
    assert seen["headers"]["x-api-key"] == "secret"
    assert seen["params"]["limit"] == 1

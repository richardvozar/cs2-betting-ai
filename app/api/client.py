import httpx

class ProviderAPIError(RuntimeError):
    pass

class CS2APIClient:
    def __init__(self, base_url: str, api_key: str, timeout: int = 30):
        if not base_url:
            raise ValueError("API base URL is empty")
        self.base_url = base_url.rstrip("/")
        self.headers = {"Accept": "application/json"}
        if api_key:
            self.headers["x-api-key"] = api_key
        self.timeout = timeout

    def get_json(self, path: str, params: dict | None = None):
        path = "/" + path.lstrip("/")
        try:
            response = httpx.get(self.base_url + path, headers=self.headers, params=params, timeout=self.timeout)
            response.raise_for_status()
            payload = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise ProviderAPIError(f"Request failed for {path}: {exc}") from exc
        if isinstance(payload, dict) and payload.get("success") is False:
            raise ProviderAPIError(f"Provider returned success=false: {payload}")
        return payload

import base64
from typing import Dict, Any, List
import requests
import urllib3

from .exceptions import APIError, APIConnectionError, AuthenticationError

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class VirtualizorAPI:
    TIMEOUT = 30

    def __init__(self, api_url: str, api_key: str, api_pass: str):
        self.api_url = api_url.rstrip("/")
        self.api_key = api_key
        self.api_pass = api_pass

    @classmethod
    def from_db_config(cls, config: Dict[str, Any]) -> "VirtualizorAPI":
        api_pass = base64.b64decode(config["api_pass"]).decode()
        return cls(config["api_url"], config["api_key"], api_pass)

    def _build_url(self, action: str, **params) -> str:
        base_params = {
            "act": action,
            "api": "json",
            "apikey": self.api_key,
            "apipass": self.api_pass,
        }
        base_params.update(params)
        query = "&".join(f"{k}={v}" for k, v in base_params.items())
        return f"{self.api_url}?{query}"

    def _request(self, action: str, **params) -> Dict[str, Any]:
        url = self._build_url(action, **params)
        try:
            response = requests.get(url, timeout=self.TIMEOUT, verify=False)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout as e:
            raise APIConnectionError("Connection timeout") from e
        except requests.exceptions.ConnectionError as e:
            raise APIConnectionError(f"Connection failed: {e}") from e
        except requests.exceptions.HTTPError as e:
            if e.response is not None and e.response.status_code == 401:
                raise AuthenticationError("Invalid API credentials") from e
            raise APIError(f"HTTP error: {e}") from e
        except requests.exceptions.JSONDecodeError as e:
            raise APIError("Invalid response from server") from e

    def test_connection(self) -> Dict[str, Any]:
        response = self._request("listvs")
        if "error" in response and response["error"]:
            raise AuthenticationError("Invalid API credentials")

        vs_count = len(response.get("vs", {})) if response.get("vs") else 0
        return {"success": True, "vm_count": vs_count}

    def list_vms(self) -> List[Dict[str, Any]]:
        response = self._request("listvs")
        vs_data = response.get("vs", {})
        if not vs_data:
            return []

        vms = []
        for vpsid, data in vs_data.items():
            ips = data.get("ips", {})
            ipv4 = None
            for ip in ips.values():
                if isinstance(ip, str) and "." in ip and ":" not in ip:
                    ipv4 = ip
                    break

            vms.append({
                "vpsid": vpsid,
                "hostname": data.get("hostname", ""),
                "ipv4": ipv4,
                "status": "running" if data.get("status") == 1 else "stopped",
            })
        return vms

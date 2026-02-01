import base64
from typing import Dict, Any, List
import requests
import urllib3

from .exceptions import APIError, APIConnectionError, AuthenticationError

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class VirtualizorAPI:
    TIMEOUT = 30

    def __init__(
        self, api_url: str, api_key: str, api_pass: str, verify_ssl: bool = False
    ):
        self.api_url = api_url.rstrip("/")
        self.api_key = api_key
        self.api_pass = api_pass
        self.verify_ssl = verify_ssl

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
            response = requests.get(url, timeout=self.TIMEOUT, verify=self.verify_ssl)
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
            ipv6 = None
            for ip in ips.values():
                if isinstance(ip, str):
                    if ":" in ip and not ipv6:
                        ipv6 = ip
                    elif "." in ip and ":" not in ip and not ipv4:
                        ipv4 = ip

            status = "stopped"
            if data.get("status") == 1:
                status = "running"
            elif data.get("suspended") and str(data.get("suspended")) not in ("0", ""):
                status = "suspended"

            vms.append(
                {
                    "vpsid": vpsid,
                    "hostname": data.get("hostname", ""),
                    "ipv4": ipv4,
                    "ipv6": ipv6,
                    "status": status,
                    "vcpu": data.get("cores", 0),
                    "ram": data.get("ram", 0),
                    "disk": data.get("space", 0),
                    "bandwidth": data.get("bandwidth", 0),
                    "used_bandwidth": data.get("used_bandwidth", 0),
                    "os": data.get("os_name", ""),
                    "virt": data.get("virt", ""),
                }
            )
        return vms

    def get_vm_stats(self, vpsid: str) -> Dict[str, Any]:
        stats = {
            "ram_used": 0,
            "ram_total": 0,
            "disk_used": 0,
            "disk_total": 0,
            "bandwidth_used": 0,
            "bandwidth_total": 0,
            "nw_rules": 0,
        }

        try:
            ram = self._request("ram", svs=vpsid)
            if ram.get("ram"):
                info = ram["ram"]
                stats["ram_used"] = float(info.get("used", 0))
                stats["ram_total"] = float(info.get("limit", 0))
        except Exception:
            pass

        try:
            disk = self._request("disk", svs=vpsid)
            if disk.get("disk"):
                info = disk["disk"]
                stats["disk_used"] = float(info.get("used_gb", 0))
                stats["disk_total"] = float(info.get("limit_gb", 0))
        except Exception:
            pass

        try:
            bw = self._request("bandwidth", svs=vpsid)
            if bw.get("bandwidth"):
                info = bw["bandwidth"]
                stats["bandwidth_used"] = float(info.get("used_gb", 0))
                stats["bandwidth_total"] = float(info.get("limit_gb", 0))
        except Exception:
            pass

        try:
            nw = self._request("managevdf", svs=vpsid)
            if nw.get("haproxydata"):
                stats["nw_rules"] = len(nw["haproxydata"])
        except Exception:
            pass

        return stats

    def vm_action(self, vpsid: str, action: str) -> Dict[str, Any]:
        valid_actions = ["start", "stop", "restart", "poweroff"]
        if action not in valid_actions:
            raise APIError(f"Invalid action: {action}")

        response = self._request(action, svs=vpsid)

        if "error" in response and response["error"]:
            error_msg = response.get("error", {})
            if isinstance(error_msg, dict):
                error_msg = (
                    list(error_msg.values())[0] if error_msg else "Unknown error"
                )
            raise APIError(str(error_msg))

        return {"success": True, "action": action, "vpsid": vpsid}

import json
import socket
import urllib.request
import urllib.parse
import urllib.error
from django.conf import settings


REQUEST_TIMEOUT = 10


def _request_json(method: str, url: str, data: dict = None, params: dict = None):
    try:
        if params:
            query_string = urllib.parse.urlencode(
                {k: ("true" if v is True else "false" if v is False else v)
                 for k, v in params.items() if v is not None}
            )
            sep = "&" if "?" in url else "?"
            url = f"{url}{sep}{query_string}"

        body_bytes = None
        headers = {
            "User-Agent": "TechGearDjango/1.0",
            "Accept": "application/json",
        }
        if data is not None:
            body_bytes = json.dumps(data).encode("utf-8")
            headers["Content-Type"] = "application/json"

        req = urllib.request.Request(url, data=body_bytes, method=method, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
                charset = resp.headers.get_content_charset() or "utf-8"
                raw = resp.read().decode(charset)
                if not raw:
                    return {}, None
                return json.loads(raw), None
        except urllib.error.HTTPError as e:
            try:
                detail_raw = e.read().decode("utf-8")
            except Exception:
                detail_raw = str(e)
            try:
                detail_json = json.loads(detail_raw)
                detail = detail_json.get("detail", detail_raw) if isinstance(detail_json, dict) else detail_raw
            except json.JSONDecodeError:
                detail = detail_raw
            return None, f"Error {e.code}: {detail}"
    except (urllib.error.URLError, socket.timeout, ConnectionError, OSError) as e:
        return None, f"Error de conexión: {str(e)}"
    except json.JSONDecodeError as e:
        return None, f"Error al decodificar respuesta JSON: {str(e)}"
    except Exception as e:
        return None, f"Error inesperado: {str(e)}"


class TechGearAPI:
    def __init__(self):
        self.base_url = settings.API_BASE_URL.rstrip('/')

    def listar_productos(self, categoria: str = None, activo: bool = True):
        params = {}
        if categoria:
            params['categoria'] = categoria
        if activo is not None:
            params['activo'] = activo
        return _request_json("GET", f"{self.base_url}/productos", params=params)

    def obtener_producto(self, producto_id: str):
        return _request_json("GET", f"{self.base_url}/productos/{producto_id}")

    def crear_pedido(self, datos_pedido: dict):
        return _request_json("POST", f"{self.base_url}/pedidos", data=datos_pedido)

    def listar_pedidos(self, email: str = None):
        params = {}
        if email:
            params['cliente_email'] = email
        return _request_json("GET", f"{self.base_url}/pedidos", params=params)

    def obtener_pedido(self, pedido_id: str):
        return _request_json("GET", f"{self.base_url}/pedidos/{pedido_id}")

    def estado_api(self):
        return _request_json("GET", f"{self.base_url}/health")


api_client = TechGearAPI()

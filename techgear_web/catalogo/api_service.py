import json
import socket
from django.conf import settings

try:
    import requests
    USING_REQUESTS = True
except ImportError:
    USING_REQUESTS = False
    import urllib.request
    import urllib.parse
    import urllib.error


REQUEST_TIMEOUT = 10


def _convert_underscore_ids(obj):
    if isinstance(obj, dict):
        nuevo = {}
        for k, v in obj.items():
            if k == "_id":
                nuevo["id"] = _convert_underscore_ids(v)
            else:
                nuevo[k] = _convert_underscore_ids(v)
        return nuevo
    elif isinstance(obj, list):
        return [_convert_underscore_ids(x) for x in obj]
    else:
        return obj


def _request_json(method: str, url: str, data: dict = None, params: dict = None):
    if USING_REQUESTS:
        result, err = _request_json_requests(method, url, data, params)
    else:
        result, err = _request_json_urllib(method, url, data, params)
    if result is not None:
        result = _convert_underscore_ids(result)
    return result, err


def _filtered_params(params):
    if not params:
        return {}
    filtered = {}
    for k, v in params.items():
        if v is not None:
            if isinstance(v, bool):
                filtered[k] = "true" if v else "false"
            else:
                filtered[k] = v
    return filtered


def _build_url_with_params(url, params):
    filtered = _filtered_params(params)
    if not filtered:
        return url
    try:
        import urllib.parse
        query_string = urllib.parse.urlencode(filtered)
    except Exception:
        parts = []
        for k, v in filtered.items():
            parts.append(f"{k}={v}")
        query_string = "&".join(parts)
    sep = "&" if "?" in url else "?"
    return f"{url}{sep}{query_string}"


def _request_json_requests(method: str, url: str, data: dict = None, params: dict = None):
    try:
        headers = {
            "User-Agent": "TechGearDjango/1.0",
            "Accept": "application/json",
        }

        kwargs = {
            "params": _filtered_params(params) or None,
            "headers": headers,
            "timeout": REQUEST_TIMEOUT,
        }
        if data is not None:
            kwargs["json"] = data

        response = requests.request(method, url, **kwargs)

        try:
            response.raise_for_status()
        except requests.HTTPError:
            try:
                detail_json = response.json()
                detail = detail_json.get("detail", response.text) if isinstance(detail_json, dict) else response.text
            except ValueError:
                detail = response.text
            return None, f"Error {response.status_code}: {detail}"

        if not response.content:
            return {}, None

        try:
            return response.json(), None
        except ValueError as e:
            return None, f"Error al decodificar respuesta JSON: {str(e)}"

    except requests.ConnectionError as e:
        return None, f"Error de conexión: {str(e)}"
    except requests.Timeout:
        return None, "Tiempo de espera agotado al conectar con la API"
    except requests.RequestException as e:
        return None, f"Error inesperado: {str(e)}"


def _request_json_urllib(method: str, url: str, data: dict = None, params: dict = None):
    try:
        url = _build_url_with_params(url, params)

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

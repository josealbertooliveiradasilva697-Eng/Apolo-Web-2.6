"""Cliente REST pequeno para Auth e PostgREST; sem estado global compartilhado."""
import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import HTTPRedirectHandler, Request, build_opener


class ErroSupabase(RuntimeError):
    def __init__(self, mensagem, status=None):
        super().__init__(mensagem)
        self.status = status


class SessaoExpirada(ErroSupabase):
    pass


class SemRedirecionamento(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class ClienteSupabase:
    def __init__(self, config, access_token=None, opener=None):
        self.url = config.supabase_url
        self._key = config.supabase_key
        self._token = access_token
        self._opener = opener or build_opener(SemRedirecionamento())

    def request(self, method, path, payload=None, query=None):
        if not path.startswith(("/auth/v1/", "/rest/v1/")) or ".." in path:
            raise ValueError("Endpoint Supabase inválido.")
        headers = {"apikey": self._key, "Content-Type": "application/json"}
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"
        if method == "POST" and "/rest/v1/" in path:
            headers["Prefer"] = "return=representation"
        url = self.url + path
        if query:
            url += "?" + urlencode(query)
        data = None if payload is None else json.dumps(payload, allow_nan=False).encode("utf-8")
        req = Request(url, data=data, headers=headers, method=method)
        try:
            with self._opener.open(req, timeout=15) as response:
                body = response.read()
                return json.loads(body) if body else None
        except HTTPError as exc:
            # Não imprimir corpo/URL/headers: podem carregar dados ou tokens.
            if exc.code == 401:
                raise SessaoExpirada("Sessão inválida ou expirada. Entre novamente.", 401) from None
            if exc.code == 403:
                raise PermissionError("Acesso não permitido pelo banco.") from None
            raise ErroSupabase("Não foi possível concluir a operação no Supabase.", exc.code) from None
        except (URLError, TimeoutError, OSError):
            raise ErroSupabase("Supabase indisponível. Tente novamente.") from None
        except (ValueError, UnicodeError):
            raise ErroSupabase("Resposta inválida do Supabase.") from None

"""Configuração validada: produção falha fechada, sem SQLite/provider local."""
import base64
from dataclasses import dataclass, field
import json
import os
from urllib.parse import urlsplit


@dataclass(frozen=True)
class Configuracao:
    ambiente: str
    auth_mode: str
    repository_mode: str
    supabase_url: str = ""
    supabase_key: str = field(default="", repr=False)

    @classmethod
    def carregar(cls, env=None):
        env = os.environ if env is None else env
        ambiente = env.get("APOLO_ENV", "production" if env.get("RENDER") == "true" else "development")
        auth = env.get("APOLO_AUTH_MODE", "local")
        repo = env.get("APOLO_REPOSITORY_MODE", "supabase" if auth == "supabase" else "sqlite")
        if ambiente not in {"development", "production"}:
            raise ValueError("APOLO_ENV deve ser development ou production.")
        if (auth, repo) not in {("local", "sqlite"), ("supabase", "supabase")}:
            raise ValueError("Use local/sqlite ou supabase/supabase em conjunto.")
        if ambiente == "production" and auth != "supabase":
            raise ValueError("Produção exige autenticação e persistência Supabase.")
        url = env.get("SUPABASE_URL", "").rstrip("/")
        key = env.get("SUPABASE_PUBLISHABLE_KEY", "")
        if auth == "supabase":
            partes = urlsplit(url)
            if (partes.scheme != "https" or not partes.hostname or partes.username
                    or partes.password or partes.path or partes.query or partes.fragment):
                raise ValueError("SUPABASE_URL deve ser a URL HTTPS do projeto.")
            if not key.startswith("sb_publishable_"):
                try:
                    payload = json.loads(base64.urlsafe_b64decode(
                        key.split(".")[1] + "=" * (-len(key.split(".")[1]) % 4)))
                    publico = payload["role"] == "anon"
                except (ValueError, KeyError, IndexError, TypeError):
                    publico = False
                if not publico:
                    raise ValueError("Use uma chave publishable ou anon; nunca service_role/secret.")
        return cls(ambiente, auth, repo, url, key)

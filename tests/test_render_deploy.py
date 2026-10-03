from pathlib import Path
import sys
from types import SimpleNamespace

import pytest

from tools.iniciar_online import argumentos
from tools import iniciar_online


def producao():
    return {"APOLO_ENV": "production", "APOLO_AUTH_MODE": "supabase",
            "APOLO_REPOSITORY_MODE": "supabase",
            "SUPABASE_URL": "https://example.supabase.co",
            "SUPABASE_PUBLISHABLE_KEY": "sb_publishable_teste", "PORT": "12345"}


def test_iniciador_respeita_porta_render_sem_secrets_na_linha():
    args = argumentos(producao())
    assert args[0] == sys.executable
    assert args[args.index("--server.address") + 1] == "0.0.0.0"
    assert args[args.index("--server.port") + 1] == "12345"
    assert "sb_publishable_teste" not in " ".join(args)
    assert not any("enableXsrfProtection" in arg or "enableCORS" in arg for arg in args)


@pytest.mark.parametrize("port", ["0", "65536", "abc", "12345;comando"])
def test_iniciador_rejeita_porta_invalida(port):
    env = producao()
    env["PORT"] = port
    with pytest.raises(ValueError):
        argumentos(env)


def test_iniciador_rejeita_provider_local_e_ambiente_dev():
    with pytest.raises(ValueError):
        argumentos({})
    with pytest.raises(ValueError):
        argumentos({"APOLO_ENV": "production", "APOLO_AUTH_MODE": "local"})


@pytest.mark.parametrize("platform", ["nt", "posix"])
def test_iniciador_preserva_argumentos_com_espacos(monkeypatch, platform):
    calls = []
    args = ["C:/Python com espaços/python.exe", "-m", "streamlit", "run",
            "C:/Projeto Apolo/app.py"]
    monkeypatch.setattr(iniciar_online, "argumentos", lambda: args)
    monkeypatch.setattr(iniciar_online, "os", SimpleNamespace(
        name=platform, execv=lambda executable, values: calls.append(values)))
    monkeypatch.setattr(iniciar_online.subprocess, "call",
                        lambda values: calls.append(values) or 0)
    if platform == "nt":
        with pytest.raises(SystemExit) as result:
            iniciar_online.main()
        assert result.value.code == 0
    else:
        iniciar_online.main()
    assert calls == [args]


def test_configuracoes_minimas_blueprint_e_ci():
    root = Path(__file__).resolve().parents[1]
    # Guardas de regressão do template; não substituem a validação no Render.
    blueprint = (root / "render.yaml").read_text(encoding="utf-8")
    assert "startCommand: python -m tools.iniciar_online" in blueprint
    assert "plan: free" in blueprint and "autoDeployTrigger: 'off'" in blueprint
    assert "disk:" not in blueprint and "databases:" not in blueprint
    for key in ("SUPABASE_URL", "SUPABASE_PUBLISHABLE_KEY"):
        assert f"- key: {key}\n        sync: false" in blueprint
    workflow = (root / ".github/workflows/tests.yml").read_text(encoding="utf-8")
    assert "image: postgres:16" in workflow
    assert "APOLO_TEST_POSTGRES_ISOLATED: '1'" in workflow
    assert "pytest tests -q" in workflow

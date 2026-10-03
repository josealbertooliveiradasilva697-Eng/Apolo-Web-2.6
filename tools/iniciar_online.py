"""Iniciador de produção: valida configuração antes de expor Streamlit."""
import os
from pathlib import Path
import subprocess
import sys

from config import Configuracao


def argumentos(env=None):
    env = os.environ if env is None else env
    config = Configuracao.carregar(env)
    if config.ambiente != "production":
        raise ValueError("O iniciador online exige APOLO_ENV=production.")
    try:
        port = int(env.get("PORT", "10000"))
    except (TypeError, ValueError):
        raise ValueError("PORT deve ser uma porta numérica válida.") from None
    if not 1 <= port <= 65535:
        raise ValueError("PORT deve estar entre 1 e 65535.")
    app = Path(__file__).resolve().parents[1] / "app.py"
    return [sys.executable, "-m", "streamlit", "run", str(app),
            "--server.address", "0.0.0.0", "--server.port", str(port),
            "--server.headless", "true", "--browser.gatherUsageStats", "false"]


def main():
    try:
        args = argumentos()
    except ValueError as exc:
        print(f"Configuração online inválida: {exc}", file=sys.stderr)
        raise SystemExit(1) from None
    # Não usa shell e não incorpora secrets na linha de comando.
    if os.name == "nt":
        # subprocess preserva caminhos com espaços no Windows; execv não os cita.
        raise SystemExit(subprocess.call(args))
    os.execv(sys.executable, args)


if __name__ == "__main__":
    main()

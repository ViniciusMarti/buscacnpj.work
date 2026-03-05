#!/usr/bin/env python3
"""
supervisor.py — BuscaCNPJ.work
Roda ampliar_seeds.py e gerador_v4_b.py em loop infinito durante a noite.
- Reinicia automaticamente se qualquer um travar ou der erro
- Alterna entre os dois: ampliar (busca CNPJs) → gerar (cria HTML) → repete
- Log completo em supervisor.log
- Para parar: Ctrl+C
"""

import subprocess
import time
import logging
import sys
import os
from datetime import datetime

# ── Config ────────────────────────────────────────────────────────────────────
PYTHON       = sys.executable          # usa o mesmo Python que está rodando
SCRIPT_SEED  = "ampliar_seeds.py"      # busca novos CNPJs
SCRIPT_GERAR = "gerador_v4_b.py"       # gera páginas HTML
LOG_FILE     = "supervisor.log"

# Tempo de espera entre ciclos (segundos)
PAUSA_ENTRE_CICLOS = 10
# Se um script travar por mais que isso, mata e reinicia (segundos)
TIMEOUT_SCRIPT = 3600  # 1 hora por script

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
    ],
)
log = logging.getLogger(__name__)

# ── Executor ──────────────────────────────────────────────────────────────────
def rodar(script: str, ciclo: int) -> bool:
    """Roda um script e retorna True se terminou com sucesso."""
    if not os.path.exists(script):
        log.error("❌  Script não encontrado: %s", script)
        return False

    log.info("▶️   [Ciclo %d] Iniciando: %s", ciclo, script)
    inicio = time.time()

    try:
        proc = subprocess.Popen(
            [PYTHON, script],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

        # Lê saída em tempo real e loga
        while True:
            line = proc.stdout.readline()
            if line:
                log.info("    [%s] %s", script, line.rstrip())
            elif proc.poll() is not None:
                break

            # Timeout
            if time.time() - inicio > TIMEOUT_SCRIPT:
                log.warning("⏰  Timeout! Matando %s após %.0f min...",
                            script, TIMEOUT_SCRIPT/60)
                proc.kill()
                return False

        rc = proc.returncode
        elapsed = (time.time() - inicio) / 60
        if rc == 0:
            log.info("✅  [%s] Concluído em %.1f min", script, elapsed)
            return True
        else:
            log.warning("⚠️   [%s] Saiu com código %d após %.1f min", script, rc, elapsed)
            return False

    except Exception as e:
        log.error("💥  Erro ao rodar %s: %s", script, e)
        return False

# ── Git auto-push ─────────────────────────────────────────────────────────────
def git_push(ciclo: int):
    """Faz commit e push automático após cada ciclo completo."""
    try:
        log.info("📤  [Ciclo %d] Fazendo git push...", ciclo)
        ts = datetime.now().strftime("%d/%m/%Y %H:%M")

        subprocess.run(["git", "add", "."], check=True, capture_output=True)
        result = subprocess.run(
            ["git", "commit", "-m", f"Auto-update {ts} — ciclo {ciclo}"],
            capture_output=True, text=True
        )
        if "nothing to commit" in result.stdout:
            log.info("    ℹ️  Nada novo para commitar.")
            return

        subprocess.run(["git", "push"], check=True, capture_output=True)
        log.info("    ✅  Push feito — ciclo %d", ciclo)
    except subprocess.CalledProcessError as e:
        log.warning("    ⚠️  Git push falhou: %s", e)
    except Exception as e:
        log.error("    💥  Erro no git push: %s", e)

# ── Main loop ─────────────────────────────────────────────────────────────────
def main():
    log.info("=" * 60)
    log.info("🚀  Supervisor iniciado — BuscaCNPJ.work")
    log.info("    Scripts : %s → %s", SCRIPT_SEED, SCRIPT_GERAR)
    log.info("    Timeout : %d min por script", TIMEOUT_SCRIPT // 60)
    log.info("    Para parar: Ctrl+C")
    log.info("=" * 60)

    ciclo = 1
    erros_consecutivos = 0

    while True:
        try:
            log.info("")
            log.info("━" * 55)
            log.info("🔄  CICLO %d — %s", ciclo, datetime.now().strftime("%d/%m/%Y %H:%M"))
            log.info("━" * 55)

            # 1. Busca novos CNPJs
            ok1 = rodar(SCRIPT_SEED, ciclo)

            time.sleep(PAUSA_ENTRE_CICLOS)

            # 2. Gera páginas HTML para os CNPJs encontrados
            ok2 = rodar(SCRIPT_GERAR, ciclo)

            # 3. Git push automático
            git_push(ciclo)

            if ok1 and ok2:
                erros_consecutivos = 0
                log.info("🎉  Ciclo %d completo com sucesso!", ciclo)
            else:
                erros_consecutivos += 1
                log.warning("⚠️   Ciclo %d teve falhas (%d consecutivos)",
                            ciclo, erros_consecutivos)

            # Se muitos erros seguidos, espera mais antes de tentar
            if erros_consecutivos >= 5:
                espera = 300  # 5 min
                log.warning("😴  Muitos erros — aguardando %d seg antes de continuar...", espera)
                time.sleep(espera)
                erros_consecutivos = 0
            else:
                time.sleep(PAUSA_ENTRE_CICLOS)

            ciclo += 1

        except KeyboardInterrupt:
            log.info("")
            log.info("🛑  Supervisor encerrado pelo usuário após %d ciclos.", ciclo - 1)
            log.info("    Fazendo push final...")
            git_push(ciclo)
            break

        except Exception as e:
            log.error("💥  Erro inesperado no supervisor: %s", e)
            log.info("    Aguardando 60s antes de retomar...")
            time.sleep(60)

if __name__ == "__main__":
    main()

"""Registro en texto de cada predicción válida y el reporte que sale de ese archivo."""

from __future__ import annotations

import json
import os
import threading
from datetime import datetime
from pathlib import Path

from predictor import STATES, Prediction

_WRITE_LOCK = threading.Lock()


def resolve_path(configured: str | os.PathLike[str] | None = None) -> str:
    """Elige la ruta del registro: argumento, STATS_FILE_PATH o data/predictions_log.jsonl."""
    if configured:
        return str(configured)
    from_env = os.environ.get("STATS_FILE_PATH")
    if from_env:
        return from_env
    return str(Path("data") / "predictions_log.jsonl")


def record(result: Prediction, path: str | os.PathLike[str]) -> None:
    """Agrega una predicción válida al archivo. No llama al clasificador."""
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "fecha": datetime.now().astimezone().isoformat(timespec="seconds"),
        "estado": result.state,
        "entrada": {
            "fiebre": result.fever_celsius,
            "intensidad_dolor": result.pain_intensity,
            "dias_sintomas": result.symptom_days,
            "numero_sintomas": result.symptom_count,
        },
    }
    line = json.dumps(entry, ensure_ascii=False)
    with _WRITE_LOCK:
        with destination.open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")


def report(path: str | os.PathLike[str]) -> dict[str, object]:
    """Cuenta por estado, las últimas cinco predicciones y la fecha de la última.

    Si el archivo no existe o está vacío, cada estado queda en 0, la lista
    queda vacía y la fecha queda en None.
    """
    counts = {state: 0 for state in STATES}
    entries = _read_entries(Path(path))
    for entry in entries:
        state = entry.get("estado")
        if isinstance(state, str) and state in counts:
            counts[state] += 1
    last_five = entries[-5:]
    latest = last_five[-1]["fecha"] if last_five else None
    return {
        "conteos": counts,
        "ultimas_predicciones": last_five,
        "fecha_ultima_prediccion": latest,
    }


def _read_entries(path: Path) -> list[dict[str, object]]:
    if not path.is_file():
        return []
    entries: list[dict[str, object]] = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        try:
            parsed = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict) and isinstance(parsed.get("fecha"), str):
            entries.append(parsed)
    return entries

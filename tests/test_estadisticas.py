"""Pruebas del registro y del reporte de predicciones."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from app import create_app
from predictor import STATES


class PruebasDeEstadisticas(unittest.TestCase):
    def setUp(self) -> None:
        self.directorio = tempfile.TemporaryDirectory()
        self.ruta = str(Path(self.directorio.name) / "predictions_log.jsonl")
        self.cliente = create_app(self.ruta).test_client()

    def tearDown(self) -> None:
        self.directorio.cleanup()

    def test_debe_empezar_en_cero_cuando_no_hay_archivo(self) -> None:
        respuesta = self.cliente.get("/api/estadisticas")
        self.assertEqual(respuesta.status_code, 200)
        cuerpo = respuesta.get_json()
        self.assertEqual(set(cuerpo["conteos"]), set(STATES))
        self.assertTrue(all(total == 0 for total in cuerpo["conteos"].values()))
        self.assertEqual(cuerpo["ultimas_predicciones"], [])
        self.assertIsNone(cuerpo["fecha_ultima_prediccion"])

    def test_no_debe_registrar_una_prediccion_invalida(self) -> None:
        respuesta = self.cliente.post(
            "/api/predecir",
            json={
                "fiebre": 30,
                "intensidad_dolor": 1,
                "dias_sintomas": 1,
                "numero_sintomas": 0,
            },
        )
        self.assertEqual(respuesta.status_code, 400)
        cuerpo = self.cliente.get("/api/estadisticas").get_json()
        self.assertEqual(cuerpo["ultimas_predicciones"], [])
        self.assertFalse(Path(self.ruta).exists())

    def test_debe_registrar_la_prediccion_en_el_archivo_y_en_la_pagina(self) -> None:
        prediccion = self.cliente.post(
            "/api/predecir",
            json={
                "fiebre": 36.6,
                "intensidad_dolor": 1,
                "dias_sintomas": 1,
                "numero_sintomas": 0,
            },
        )
        self.assertEqual(prediccion.status_code, 200)

        cuerpo = self.cliente.get("/api/estadisticas").get_json()
        self.assertEqual(cuerpo["conteos"]["NO ENFERMO"], 1)
        self.assertEqual(len(cuerpo["ultimas_predicciones"]), 1)
        self.assertEqual(cuerpo["ultimas_predicciones"][0]["estado"], "NO ENFERMO")
        self.assertEqual(cuerpo["ultimas_predicciones"][0]["entrada"]["fiebre"], 36.6)
        self.assertEqual(cuerpo["fecha_ultima_prediccion"], cuerpo["ultimas_predicciones"][0]["fecha"])

        lineas = Path(self.ruta).read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(lineas), 1)
        guardado = json.loads(lineas[0])
        self.assertEqual(guardado["estado"], "NO ENFERMO")

        pagina = self.cliente.get("/estadisticas")
        self.assertEqual(pagina.status_code, 200)
        texto = pagina.get_data(as_text=True)
        self.assertIn("NO ENFERMO", texto)
        self.assertIn(cuerpo["fecha_ultima_prediccion"], texto)


if __name__ == "__main__":
    unittest.main()

# Valoración de síntomas

Servicio para que un médico estime, a partir de los síntomas de un episodio, si la presentación corresponde a una persona sin enfermedad o a una enfermedad leve, aguda, crónica o terminal.

El mismo flujo sirve cuando hay muchos casos (enfermedades comunes) y cuando hay muy pocos (enfermedades huérfanas). La respuesta apoya la decisión clínica; no reemplaza al médico.

## Propósito

- Recibir fiebre, intensidad del dolor, días con síntomas y número de síntomas.
- Devolver uno de los cinco estados.
- Conservar un registro de las consultas para informar cuántas predicciones hay por estado, las últimas cinco y la fecha de la última.
- Publicar el servicio en una imagen de contenedor y verificar cada cambio con integración continua.

## Estructura

| Ruta | Contenido |
| --- | --- |
| `predictor.py` | Función que clasifica el episodio |
| `app.py` | Página y API |
| `stats_store.py` | Registro de predicciones y reporte |
| `templates/` y `static/` | Formulario y reporte |
| `tests/` | Pruebas de la clasificación y del reporte |
| `Dockerfile` | Imagen del servicio |
| `.github/workflows/` | Integración continua y publicación de la imagen |

Las instrucciones para construir la imagen, ejecutarla y consultar una predicción están más abajo, en este mismo archivo, a medida que el servicio queda disponible.

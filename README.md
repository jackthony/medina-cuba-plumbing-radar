# Medina Cuba Plumbing — DFW Project Radar

[![CI](https://github.com/jackthony/medina-cuba-plumbing-radar/actions/workflows/ci.yml/badge.svg)](https://github.com/jackthony/medina-cuba-plumbing-radar/actions/workflows/ci.yml)

## En una frase

Este radar encuentra proyectos de construcción nuevos en fuentes públicas de Dallas–Fort Worth y los convierte en una lista priorizada de oportunidades para que Medina Cuba Plumbing sepa **qué proyectos investigar y qué empresas contactar primero**.

## El problema que resuelve

Hoy una empresa de plumbing puede depender de referidos o enterarse tarde de una obra. El radar busca señales tempranas en permisos municipales para responder tres preguntas:

1. ¿Dónde se está construyendo?
2. ¿Qué proyecto, builder o developer está detrás?
3. ¿Cuál oportunidad parece tener mejor encaje para plumbing subcontracting?

## Cómo funciona

```text
Permisos públicos de Fort Worth y Frisco
                    ↓
       Proyectos residenciales/comerciales
                    ↓
 Score 0–100 según recencia, tipo, tamaño y empresa
                    ↓
 Lista priorizada para investigar, contactar y ofertar
```

El sistema no garantiza contratos. Reduce el tiempo necesario para encontrar oportunidades que merecen investigación comercial.

## Qué entrega hoy

- Un radar web local en <http://127.0.0.1:8765>.
- Una lista de proyectos priorizados.
- Una lista de builders/developers con varios permisos activos.
- Evidencia enlazada al permiso municipal original.
- Exportaciones CSV para revisión o uso posterior en Google Sheets.

Consulta el [guion sencillo para presentar el MVP](docs/GUIA-DE-PRESENTACION.md) y el [resumen autocontenido para ChatGPT](docs/RESUMEN-PARA-CHATGPT.md).

## Resultados de la ejecución validada

- 900 permisos únicos recientes de Fort Worth.
- 713 permisos activos de Frisco.
- 1,613 señales almacenadas en DuckDB.
- 50 oportunidades finales: 35 de Fort Worth y 15 de Frisco.
- Empresas detectadas incluyen D.R. Horton, Perry Homes, LGI Homes, Forestar y GRBK Edgewood.

Los resultados cambian cuando las ciudades actualizan sus datos.

## Límites importantes

- Un permiso es una señal comercial, no un contrato disponible confirmado.
- Fort Worth no siempre identifica claramente al builder o GC.
- Frisco publica proyecto, dirección y tamaño, pero no siempre publica empresa o valor.
- Toda empresa debe verificarse antes de iniciar outreach.
- El score ordena la investigación; no sustituye el criterio comercial.

## Ejecución técnica

Requiere Python 3.9 o superior. Python 3.11+ es recomendado.

```bash
python3 -m venv .venv
.venv/bin/pip install --only-binary=:all: 'duckdb==1.3.2'
.venv/bin/python -m src.main demo
```

Por etapas:

```bash
.venv/bin/python -m src.main collect --source all
.venv/bin/python -m src.main rank --top 50
.venv/bin/python -m src.main serve
```

## Seguridad

El MVP utiliza HTTP estándar y una sola dependencia de ejecución fijada por versión: DuckDB. No incluye contraseñas, no ejecuta scripts remotos, no automatiza navegadores, no evita CAPTCHA y no accede a plataformas privadas.

## Integración continua (CI)

GitHub Actions ejecuta automáticamente una verificación en cada `push` y `pull request` dirigido a `main`:

1. prepara Python 3.11;
2. instala únicamente las versiones exactas de DuckDB y pytest usando paquetes binarios;
3. compila `src` y `tests` para detectar errores de sintaxis;
4. ejecuta toda la suite de pruebas.

El workflow tiene permisos de solo lectura, utiliza acciones oficiales de GitHub fijadas a commits exactos y no contiene secretos ni despliegue continuo (CD). El archivo está en [`.github/workflows/ci.yml`](.github/workflows/ci.yml).

## Próximo paso recomendado

Validar manualmente las 10 empresas con más actividad, confirmar el decision maker correcto y registrar si cada señal termina en conversación, estimate o bid. Solo después conviene integrar TDLR, Apollo o automatización de outreach.

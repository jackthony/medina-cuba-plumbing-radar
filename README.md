# Medina Cuba Plumbing — DFW Project & Builder Radar

MVP reproducible que convierte permisos públicos de Fort Worth en oportunidades comerciales priorizadas para plumbing subcontracting.

## Demo rápida

```bash
python3 -m venv .venv
.venv/bin/pip install -e '.[dev]'
.venv/bin/python -m src.main demo
```

Abre <http://127.0.0.1:8765>. El comando consulta datos reales, conserva el payload original en DuckDB, deduplica, calcula un score determinístico y exporta `data/top_opportunities.csv`.

También se puede ejecutar por etapas:

```bash
.venv/bin/python -m src.main collect --source arcgis
.venv/bin/python -m src.main rank --top 50
.venv/bin/python -m src.main serve
```

## Fuente y supuestos

- Fuente: City of Fort Worth Development Permits, ArcGIS Feature Service público.
- Ventana: últimos 120 días; permisos residenciales y comerciales.
- `B1_SPECIAL_TEXT` se trata como candidato a builder/GC, no como contacto verificado.
- `File_Date` indica fecha del permiso, no fecha contractual de inicio.
- El score es configurable en `config/settings.json` y no utiliza LLM.
- Algunos registros municipales no publican dirección, valor o contratista. Esas ausencias se conservan; no se inventan.

## Seguridad

El MVP usa la biblioteca estándar de Python para HTTP y una sola dependencia de ejecución fijada por versión: DuckDB. No ejecuta scripts remotos, no usa credenciales, no automatiza navegadores y no evade controles de acceso.

## Próximo vertical slice

Agregar una segunda fuente DFW/TDLR y deduplicar proyectos entre municipios antes de integrar Apollo o outreach.

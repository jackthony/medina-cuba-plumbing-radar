# Contexto autocontenido para analizar el proyecto en ChatGPT

## Proyecto

**Medina Cuba Plumbing — DFW Project & Builder Radar**

## Objetivo empresarial

Ayudar a Medina Cuba Plumbing LLC a reducir su dependencia de referidos y construir un pipeline B2B más predecible con home builders, developers, general contractors y empresas de construcción residencial en Dallas–Fort Worth.

El sistema busca el proyecto antes de buscar a la persona:

```text
Public data → Project signal → Qualification score → Builder/developer
→ Decision maker → Outreach → Conversation → Estimate/bid → Opportunity
```

## Qué hace el MVP

1. Consulta permisos públicos de Fort Worth y permisos activos de Frisco.
2. Convierte los diferentes campos municipales a un modelo común `ProjectSignal`.
3. Conserva el payload original para auditoría.
4. Elimina duplicados por fuente e identificador del permiso.
5. Calcula un score explicable de 0 a 100.
6. Guarda los datos en DuckDB.
7. Produce un dashboard local y dos CSV: proyectos y empresas objetivo.

## Fuentes actuales

- City of Fort Worth Development Permits: permisos residenciales y comerciales recientes.
- City of Frisco Active Building Permits: proyectos activos con nombre, dirección, tipo, fecha, superficie y enlace eTRAKiT.

Dallas no fue añadido porque el dataset abierto localizado es histórico y el propio portal indica que ya no se actualiza con permisos activos.

## Reglas principales del score

- +25 por geografía DFW.
- +25 por construcción residencial nueva con buen fit.
- +15 por permiso reciente.
- +10 por valor o tamaño atractivo.
- +10 si existe builder/developer investigable.
- +10 por alta probabilidad de trabajo de plumbing.
- +5 si la información permite investigación adicional.
- Penalizaciones para remodelación, reparación o estado inactivo.

Los pesos están en `config/settings.json`. El scoring no utiliza un LLM.

## Resultado validado el 22 de agosto de 2026

- 1,000 registros recientes recibidos de Fort Worth y 900 permisos únicos guardados.
- 715 registros activos recibidos de Frisco y 713 permisos únicos guardados.
- 1,613 señales totales en DuckDB.
- Exportación final balanceada: 35 oportunidades Fort Worth y 15 Frisco.
- 9 pruebas automatizadas aprobadas.

Ejemplos de empresas con múltiples permisos: GRBK Edgewood LLC, D.R. Horton–Texas Ltd, Forestar, Perry Homes y LGI Homes.

Ejemplos de proyectos Frisco: Fields–Brookside, Silverleaf, Collinsbrook Farm y The Link at PGA.

## Interpretación correcta

Una fila es una **señal para investigar**, no una oportunidad contractual confirmada. El score indica prioridad relativa. Los builders, owners y GCs deben verificarse antes de outreach. No se deben prometer contratos ni atribuir una empresa cuando la fuente municipal no lo demuestre.

## Estado técnico

- Python compatible con 3.9+; 3.11+ recomendado.
- Una dependencia de ejecución: `duckdb==1.3.2`.
- Sin credenciales ni secretos.
- Sin browser automation, CAPTCHA bypass ni scraping de plataformas privadas.
- Comando completo: `.venv/bin/python -m src.main demo`.

## Siguiente decisión recomendada

Antes de añadir más tecnología, revisar manualmente las diez empresas principales y medir:

- empresa confirmada;
- decision maker encontrado;
- contacto válido;
- conversación iniciada;
- solicitud de estimate;
- invitación a bid;
- resultado ganado o perdido.

El objetivo de esa validación es demostrar que las señales públicas se convierten en pipeline comercial real.

# Guía sencilla para presentar el DFW Project Radar

## Explicación de 30 segundos

> Construimos un radar que revisa permisos públicos de Fort Worth y Frisco para detectar builders y desarrollos residenciales antes de buscar contactos. Medina Cuba Plumbing busca proyectos compatibles con su capacidad actual: idealmente 300–600 viviendas por año. Un proyecto mayor no se descarta, pero se considera secundario o se evalúa por fases.

## El mensaje principal

No estamos vendiendo “scraping” ni una lista de datos. Estamos construyendo un proceso:

```text
Encontrar el proyecto
→ entender si necesita plumbing
→ identificar la empresa
→ verificar al decision maker
→ iniciar conversación
→ conseguir estimate o bid
```

## Demostración de 3 minutos

### 1. Mostrar el problema

“Hoy muchas oportunidades llegan por referidos o cuando la obra ya está avanzada. Queremos detectar señales públicas más temprano.”

### 2. Mostrar la parte superior del radar

Explicar las tres bandas de capacidad. Aclarar que todavía medimos permisos observados, no viviendas anuales confirmadas.

### 3. Mostrar Frisco

Abrir un proyecto como Fields, Silverleaf o The Link at PGA. Enseñar el nombre, dirección, tipo, superficie y el enlace al permiso municipal.

### 4. Mostrar un score

“El Opportunity Score no adivina quién nos contratará. Prioriza señales. Después usamos Company Confidence para validar quién es la empresa, qué papel tiene y si realmente puede contratar el plumbing.”

### 5. Cerrar con el siguiente paso

“Ahora debemos agrupar permisos por desarrollo y builder, estimar la escala con evidencia, validar las primeras diez empresas y solamente entonces usar Apollo para encontrar al responsable correcto.”

## Guion de 90 segundos

1. “No estamos mostrando una lista comprada: son señales municipales con evidencia.”
2. “El foco de MCP son desarrollos de 300–600 viviendas por año; más de 600 puede interesar por fases.”
3. “El score actual dice qué investigar primero, no quién contratará.”
4. “La siguiente capa confirma empresa, rol en el proyecto y escala anual.”
5. “Apollo entra al final para encontrar a la persona; no reemplaza el radar.”

## Qué sí está terminado

- Dos fuentes municipales reales y activas.
- Normalización y conservación del registro original.
- Eliminación de permisos duplicados por identificador.
- Score determinístico y explicable.
- Base local DuckDB.
- Dashboard local y CSV.
- Enlaces a la evidencia municipal.

## Qué todavía no está terminado

- Confirmación manual de cada builder o general contractor.
- Contactos y decision makers.
- Integración con Apollo.
- Outreach por email o teléfono.
- CRM y seguimiento de resultados.
- Cobertura completa de todas las ciudades DFW.

## Respuestas para preguntas probables

**¿Esto consigue contratos automáticamente?**  
No. Encuentra y prioriza señales para que el equipo comercial investigue antes y mejor.

**¿Los datos son inventados?**  
No. Cada fila procede de una fuente municipal y conserva un enlace de evidencia.

**¿Por qué un score?**  
Para revisar primero proyectos nuevos, recientes y de tamaño atractivo, en vez de leer cientos de permisos sin orden.

**¿Por qué no usar Apollo desde el inicio?**  
Primero necesitamos saber qué proyecto y qué empresa merecen contacto. Apollo sirve después para localizar a la persona adecuada.

**¿Cuál es la limitación principal?**  
Los municipios publican campos diferentes y no siempre identifican al builder o GC. Por eso toda señal requiere validación antes de contactar.

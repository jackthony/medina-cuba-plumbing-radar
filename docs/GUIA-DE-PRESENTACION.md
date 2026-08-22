# Guía sencilla para presentar el DFW Project Radar

## Explicación de 30 segundos

> Construimos un radar que revisa permisos públicos de construcción en Fort Worth y Frisco. El sistema identifica proyectos recientes, les asigna una prioridad de 0 a 100 y muestra qué builders o developers tienen más actividad. La idea es que Medina Cuba Plumbing encuentre oportunidades antes de buscar contactos y pueda concentrar su tiempo comercial en proyectos con mejor probabilidad de necesitar plumbing.

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

Explicar que la tabla de empresas agrupa varios permisos de una misma organización. Una empresa con muchos proyectos nuevos puede ser más valiosa que un permiso aislado.

### 3. Mostrar Frisco

Abrir un proyecto como Fields, Silverleaf o The Link at PGA. Enseñar el nombre, dirección, tipo, superficie y el enlace al permiso municipal.

### 4. Mostrar un score

“El score no adivina quién nos contratará. Solo prioriza usando reglas visibles: ubicación DFW, construcción nueva, fecha reciente, tamaño y disponibilidad de una empresa investigable.”

### 5. Cerrar con el siguiente paso

“Ahora debemos validar las primeras diez empresas, encontrar al estimator, project manager o purchasing manager y medir cuántas señales se convierten en conversaciones, estimates y bids.”

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


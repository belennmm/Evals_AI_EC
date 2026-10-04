# Agent Parachute S.A.

Proyecto de Parachute S.A. Combina un sistema RAG de preguntas frecuentes con herramientas de clima y seguridad, y tres arquitecturas multiagente para comparar distintas formas de coordinar la atención y las reservas.

El proyecto utiliza Groq mediante una API compatible con OpenAI y el modelo `openai/gpt-oss-120b`.

## VIDEO

Video demostrativo: [https://youtu.be/WpdA-NCLGgw](https://youtu.be/WpdA-NCLGgw)


### Archivos de reporte

Archivos generados por Promptfoo son [reporte HTML](reports/promptfoo_report.html) y [resultados JSON](reports/promptfoo_results.json). 

```powershell
npx --yes promptfoo@latest eval --no-cache --output reports/promptfoo_report.html reports/promptfoo_results.json
```


## Tecnologías

- Python 3.12
- Docker / Docker Compose
- PostgreSQL
- pgvector
- sentence-transformers
- OpenAI Python SDK
- OpenAI Agents SDK (`openai-agents`)
- Groq como proveedor compatible con OpenAI
- Open-Meteo
- psycopg2
- python-dotenv
- requests
- pytest
- Promptfoo

Modelo de lenguaje utilizado: `openai/gpt-oss-120b`

Modelo de embeddings utilizado: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`

Dimensión de los embeddings: `384`

## Estructura del proyecto

```text
.
├── centralized/                 # Arquitectura con Manager central
├── decentralized/               # Arquitectura basada en handoffs
├── hierarchical/                # Arquitectura con supervisores
├── Evals/
│   ├── faq_tests.yaml            # Evals FAQ
│   └── booking_tests.yaml        # Evals Booking
├── providers/
│   ├── __init__.py
│   └── promptfoo_provider.py     # Adaptador Python para Promptfoo
├── reports/
│   ├── promptfoo_report.html     # Reporte oficial HTML
│   └── promptfoo_results.json    # Resultados oficiales JSON
├── promptfooconfig.yaml
├── shared/
│   ├── model_config.py          # Configuración reutilizable de Groq + Agents SDK
│   ├── safety_tool.py           # Reglas de seguridad del salto
│   └── weather_tool.py          # Consulta y validación de Open-Meteo
├── Corpus_FAQs_Parachute_SA_2026.txt
├── knowledge_tool.py            # Búsqueda vectorial sobre FAQs
├── Parachute_Agent.py           # Agente RAG original
├── load_embeddings.py           # Carga de corpus y embeddings
├── init.sql                     # Inicialización de PostgreSQL/pgvector
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── test_agents_sdk.py
├── test_centralized.py
├── test_decentralized.py
├── test_hierarchical.py
└── test_shared_tools.py
```

## Sistema RAG de preguntas frecuentes

El sistema RAG original responde usando únicamente la información almacenada a partir de `Corpus_FAQs_Parachute_SA_2026.txt`.

```text
Usuario
   ↓
Pregunta
   ↓
Parachute_Agent.py
   ↓
Groq mediante API compatible con OpenAI
   ↓
Tool call: buscar_en_base_conocimiento
   ↓
knowledge_tool.py
   ↓
sentence-transformers
   ↓
Embedding de la consulta
   ↓
PostgreSQL + pgvector
   ↓
TOP 3 FAQs más similares
   ↓
Resultado de la herramienta
   ↓
Groq
   ↓
Respuesta final
```

`knowledge_tool.py` genera el embedding de la consulta y recupera hasta tres FAQs mediante distancia coseno con `pgvector`. El agente responde con información respaldada por las FAQs; si no hay información suficiente, indica esa limitación.

## Herramientas compartidas

### Clima

`shared/weather_tool.py` consulta Open-Meteo para la ubicación de Parachute S.A.:

```text
Latitud:  14.013722
Longitud: -90.771611
```

La fecha debe estar en formato `YYYY-MM-DD`, no puede estar en el pasado y el pronóstico está limitado a 16 días. Para cada fecha devuelve:

- temperatura promedio (`temperatura_2m`)
- precipitación acumulada (`precipitacion`)
- cobertura máxima de nubes (`cobertura_nubes`)
- velocidad máxima del viento (`velocidad_viento`)
- ráfagas máximas (`rachas_viento`)

### Seguridad

`shared/safety_tool.py` usa los datos anteriores y clasifica el salto como `IDEAL`, `MARGINAL` o `PROHIBIDO`.

| Condición | IDEAL | MARGINAL | PROHIBIDO |
|---|---:|---:|---:|
| Viento | Menor de 20 km/h | 20–28 km/h | Mayor de 28 km/h |
| Ráfagas | Hasta 35 km/h | Hasta 35 km/h | Mayor de 35 km/h |
| Precipitación | 0 mm | 0 mm | Mayor de 0 mm |
| Nubes | Menor de 30% | 30–75% | Mayor de 75% |

La temperatura es informativa y no tiene un umbral de seguridad. El estado `MARGINAL` permite únicamente tándem experimentado; `PROHIBIDO` no permite reservar el salto.

## OpenAI Agents SDK + Groq

La configuración reutilizable está en `shared/model_config.py`. Esta crea un `AsyncOpenAI` con la URL compatible de Groq y devuelve un `OpenAIChatCompletionsModel` para `openai/gpt-oss-120b`.

El proyecto utiliza:

- `Agent`
- `Runner`
- `AsyncOpenAI`
- `OpenAIChatCompletionsModel`
- tracing desactivado

Los agentes de clima y seguridad usan schemas estructurados para sus argumentos. Esto permite que el modelo entregue `fecha` y los campos climáticos requeridos, en lugar de un único argumento genérico.

## Arquitectura centralizada

Los archivos están en `centralized/`.

El `Parachute Manager` conserva siempre el control de la conversación y utiliza agentes especializados como herramientas mediante `as_tool()`:

- FAQ Agent
- Weather Agent
- Safety Agent
- Booking Agent

```text
Usuario
   ↓
Manager
   ├── FAQ Agent
   └── Weather Agent → Safety Agent → Booking Agent
```

Para una reserva, el Manager consulta el clima, solicita la evaluación de seguridad y solo llama al Booking Agent si `puede_saltar` es verdadero. Ante un error de clima o un resultado `PROHIBIDO`, no se realiza la reserva.

## Arquitectura jerárquica

Los archivos están en `hierarchical/`.

```text
Main Supervisor
├── Information Supervisor
│   └── FAQ Agent
└── Booking Supervisor
    ├── Weather Agent
    ├── Safety Agent
    └── Booking Agent
```

El Main Supervisor clasifica la solicitud. Las consultas informativas se delegan al Information Supervisor y las reservas al Booking Supervisor, que coordina el flujo de clima, seguridad y reserva.

## Arquitectura descentralizada

Los archivos están en `decentralized/`.

No existe un Manager central permanente. Los agentes transfieren el control mediante handoffs reales:

```text
FAQ:
Entry / Router → FAQ Agent

Reserva:
Entry / Router → Weather Agent → Safety Agent → Booking Agent
```

Una FAQ se transfiere directamente al FAQ Agent, sin recorrer agentes innecesarios. Para reservas, Weather Agent transfiere a Safety Agent y este transfiere a Booking Agent solo cuando corresponde. Los handoffs usan un `input_type` estructurado con un resumen breve, para generar schemas compatibles con Groq y Chat Completions.

## ¿Por qué existen tres arquitecturas?

Las tres resuelven el mismo caso, pero distribuyen la coordinación de forma distinta:

| Arquitectura | Coordinación | Uso principal |
|---|---|---|
| Centralizada | Un Manager toma todas las decisiones y llama especialistas como tools. | Control único del flujo. |
| Jerárquica | Un supervisor principal delega a supervisores especializados. | Separación por dominios y niveles. |
| Descentralizada | Cada agente transfiere el control al siguiente mediante handoffs. | Delegación directa sin coordinador permanente. |

La finalidad de mantener las tres es comparar sus diferencias técnicas; este README no establece una como la mejor.

Para esta hoja de trabajo de evaluación se seleccionó la arquitectura **CENTRALIZADA** como sistema bajo evaluación. Las otras arquitecturas se conservan para comparación.

## Calendarización local

El Booking Agent implementa una calendarización sencilla en memoria. No modifica PostgreSQL.

- Guarda únicamente fechas en una lista local mientras el proceso está activo.
- Rechaza una reserva si la evaluación indica que no se puede saltar.
- Evita duplicar una fecha ya reservada durante esa misma ejecución.
- Confirma una reserva `MARGINAL` con la nota de “solo tándem experimentado”.
- No guarda usuarios, horarios, capacidad, pagos ni reservas entre ejecuciones.

## Infraestructura y Docker

PostgreSQL con `pgvector` se ejecuta en Docker. La aplicación también se ejecuta dentro de Docker para usar una versión controlada de Python y dependencias.

El servicio `postgres` expone el puerto local `5433` y el servicio `app` se conecta internamente a PostgreSQL por el puerto `5432`.

## Instalación

Se requiere:

- Docker Desktop
- Git
- Una API key de Groq

Clona o descarga el repositorio y abre una terminal en la carpeta del proyecto.

### Variables de entorno

Crea el archivo `.env` a partir de `.env.example`:

```powershell
Copy-Item .env.example .env
```

Configura al menos:

```text
GROQ_API_KEY=tu_api_key_de_groq
DB_HOST=localhost
DB_PORT=5433
DB_NAME=parachute_rag
DB_USER=parachute_user
DB_PASSWORD=parachute_secure_password
```

Estos valores corresponden a la ejecución local desde Windows. Dentro de Docker, el servicio de aplicación utiliza `DB_HOST=postgres` y el puerto interno `5432`.


### Construcción y base de datos

Levanta PostgreSQL:

```powershell
docker compose up -d postgres
```

Verifica que el contenedor esté activo:

```powershell
docker compose ps
```

Construye la imagen de la aplicación:

```powershell
docker compose build app
```

## Carga de embeddings

El archivo `load_embeddings.py`:

1. Lee `Corpus_FAQs_Parachute_SA_2026.txt`.
2. Extrae las FAQs.
3. Genera embeddings locales con `sentence-transformers`.
4. Inserta FAQs y embeddings en PostgreSQL.
5. Verifica los registros almacenados.

Para ejecutarlo:

```powershell
docker compose run --rm app python load_embeddings.py
```

La carga esperada debe detectar:

```text
120 FAQs
120 registros insertados
120 FAQs con embeddings
```

Los embeddings se generan a partir de la pregunta de cada FAQ; la respuesta completa se conserva en PostgreSQL para responder al usuario.


## Ejecución de las arquitecturas multiagente

Las tres interfaces son interactivas. Escribe una consulta y usa `salir`, `exit` o `quit` para terminar.

### Centralizada

```powershell
docker compose run --rm app python -m centralized.manager_agent
```

### Jerárquica

```powershell
docker compose run --rm app python -m hierarchical.main_supervisor
```

### Descentralizada

```powershell
docker compose run --rm app python -m decentralized.entry_agent
```

Ejemplos sencillos de consultas:

```text
¿Cuál es el peso máximo permitido?
¿Cómo puedo llegar al evento?
Quiero agendar un salto para 2026-09-23
¿Se puede saltar el 2026-09-23?
```

La fecha solicitada debe estar dentro de los próximos 16 días para que Open-Meteo pueda proporcionar el pronóstico.

## Evaluación con Promptfoo

La hoja de evaluación utiliza el flujo real `Promptfoo → providers/promptfoo_provider.py → centralized/manager_agent.py → agentes especializados`. El adaptador devuelve la respuesta final y metadata estructurada; no sustituye el sistema con respuestas simuladas.

La suite contiene cinco casos FAQ y tres Booking. Combina `contains`, `regex`, `factuality`, latencia y tool execution. Factuality se aplica a cuatro FAQ y al rechazo de reserva por seguridad, mediante el grader `groq:openai/gpt-oss-120b`, con la misma variable `GROQ_API_KEY`. Los límites de latencia son 45 000 ms para FAQ y 70 000 ms para Booking.

Promptfoo tiene además un timeout de ejecución de 120 000 ms por caso para registrar como error una llamada externa que no termine. Este timeout no sustituye ni eleva las assertions de latencia. Durante el cierre se interrumpieron dos intentos con siete resultados guardados y el caso meteorológico pendiente; los reportes corresponden únicamente a la última ejecución completa.

### Casos evaluados

FAQ cubre peso máximo de 100 kg, caída libre de 35 a 45 segundos, prohibición de cámara personal, recargo de Q250 entre 90 y 100 kg, y una consulta sobre perros sin información suficiente.

Booking cubre la reserva del `2026-10-10` a las `10:00` bloqueada por seguridad, una solicitud sin fecha y la fecha inexistente `2026-02-30`. Las fechas explícitas evitan ambigüedades como “mañana”, pero no congelan el pronóstico.

Tool execution usa assertions JavaScript de Promptfoo sobre `context.providerResponse.metadata.tool_calls`. Se exige `faq_agent` en peso y caída libre, y `weather_agent` y `safety_agent` en la reserva bloqueada. No se exige `booking_agent` cuando seguridad bloquea el flujo; tampoco debe invocarse al faltar una fecha o ser inválida. No se comparan IDs dinámicos.

### Ejecución local en Windows

Se requiere Node.js/npm, el entorno Python 3.12 con `requirements.txt`, PostgreSQL disponible en `localhost:5433`, el corpus cargado y `.env` configurado. `npx` descarga Promptfoo en su caché si es necesario; no requiere instalación global.

```powershell
$env:PROMPTFOO_PYTHON = (Join-Path (Get-Location) 'venv\Scripts\python.exe')
$env:PYTHONIOENCODING = 'utf-8'

npx --yes promptfoo@latest eval --no-cache
```

### Resultado final registrado

Última ejecución completa: `eval-v6Z-2026-10-03T06:12:00`, con **7 passed, 1 failed y 0 errors**, duración de **1 min 29 s** y **3 652 tokens de grading** (2 118 de entrada y 1 534 de salida). Los cinco FAQ, la reserva bloqueada y la solicitud sin fecha pasaron.

La fecha inválida respondió `ERROR: Fecha no válida.`. Falló la regex del test porque no contempla exactamente la variante `no válida`; el sistema sí rechazó la fecha. Se conserva la assertion y se documenta este pendiente de revisión, sin cambiar agentes ni tests para ocultar el fallo. El comando terminó con código 1 por ese test fallido.

### Limitaciones de la evaluación

- El clima puede cambiar: una fecha fija puede producir otro pronóstico y, con el tiempo, quedar en el pasado o fuera de los 16 días permitidos.
- No se obtuvo una reserva exitosa durante los evals realizados; las fechas futuras probadas fueron bloqueadas por seguridad.
- No se evaluaron duplicados de forma confiable: las reservas viven en memoria y Promptfoo puede utilizar distintos procesos.
- Booking conserva fechas durante el proceso, no horarios ni reservas persistentes entre ejecuciones.
- `tool_calls` refleja principalmente llamadas del manager a agentes; no expone todas las herramientas internas ni garantiza por sí solo que cada llamada haya terminado correctamente.
- Factuality utiliza un LLM grader y puede variar o emitir juicios discutibles; las assertions determinísticas complementan esa revisión.
- Una ejecución exitosa representa los casos observados y no garantiza todos los flujos posibles.

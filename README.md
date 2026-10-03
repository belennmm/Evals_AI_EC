# Agent Parachute S.A.

Proyecto de Parachute S.A. Combina un sistema RAG de preguntas frecuentes con herramientas de clima y seguridad, y tres arquitecturas multiagente para comparar distintas formas de coordinar la atención y las reservas.

El proyecto utiliza Groq mediante una API compatible con OpenAI y el modelo `openai/gpt-oss-120b`.

## VIDEO

Video demostrativo: [https://youtu.be/WpdA-NCLGgw](https://youtu.be/WpdA-NCLGgw)

## PREGUNTAS
1. ¿Qué arquitectura/arquitecturas resuelven mejor este problema? ¿Por qué?

Considero que la arquitectura centralizada es la que mejor resuelve este problema para este punto. El problema y su solución tienen tareas bien definidas, como responder preguntas frecuentes, consultar el clima, evaluar la seguridad y realizar una reserva. En la arquitectura centralizada, un solo manager mantiene el control y decide qué agente debe utilizar, lo que hace que el flujo sea más sencillo de mantener. 

En cambio, si el sistema creciera y se agregaran más funciones, yo optaría por la arquitectura jerárquica. Su separación entre un supervisor de información y otro de reservas permite organizar mejor las responsabilidades. La arquitectura descentralizada funciona bien con handoffs, pero su flujo sí es más complejo de controlar porque el control de la conversación va pasando entre agentes.

Por ende, yo elegiría la arquitectura centralizada, mientras que la jerárquica sería una buena alternativa si el sistema aumentara.

2. ¿Considera que es necesario utilizar un sistema multiagente en este caso? ¿Por qué?

No creo que un sistema multiagente sea necesario para resolver este problema en su escala actual. Las funciones del sistema podrían implementarse con un solo agente que utilice herramientas para consultar las FAQs, obtener el clima, evaluar las condiciones y registrar una reserva; esto sin complicar el mantenimiento. 

Tener un multiagente sí es ventajoso porque cada agente puede encargarse de una responsabilidad específica; pero esto lo implementaría en un futuro si hay más tareas o si se tiene un volumen más grance. Para esta etapa se pudieron reutilizar las mismas herramientas de clima y seguridad en las tres arquitecturas, en lugar de volver a implementar esas reglas.

Para esta versión se puede usar un agente sin problema. Si Parachute S.A. continúa agregando servicios y reglas, sí sería bueno cambiarlo a multiagente ya que permitiría mantener el sistema mejor organizado y distribuir las responsabilidades entre agentes.


## Tecnologías

- Python 3.11
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

Modelo de lenguaje utilizado: `openai/gpt-oss-120b`

Modelo de embeddings utilizado: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`

Dimensión de los embeddings: `384`

## Estructura del proyecto

```text
.
├── centralized/                 # Arquitectura con Manager central
├── decentralized/               # Arquitectura basada en handoffs
├── hierarchical/                # Arquitectura con supervisores
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
DB_PORT=5432
DB_NAME=parachute_rag
DB_USER=parachute_user
DB_PASSWORD=parachute_secure_password
```


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

## Consideraciones

El corpus original de Parachute S.A. contiene respuestas completas y otras más genéricas. El agente RAG no completa información faltante utilizando conocimiento externo.

Cuando una FAQ relevante no contiene el dato solicitado, el agente indica que la información específica no está disponible en la base de conocimiento. Esto permite mantener respuestas respaldadas por el corpus proporcionado.

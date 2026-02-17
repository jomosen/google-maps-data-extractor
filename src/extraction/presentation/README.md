# Extraction API Server

Backend API para el Bounded Context de Extraction.

## Iniciar el servidor

```bash
# Desde la raíz del proyecto
cd src/extraction/presentation

# Ejecutar con Python
python api_server.py

# O con uvicorn directamente
uvicorn api_server:app --reload --host 0.0.0.0 --port 8000
```

## Endpoints

- **GET /** - Health check
- **GET /api/health** - Detailed health status
- **WebSocket /ws/extraction/stream** - Real-time extraction streaming

## WebSocket Protocol

### Conexión
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/extraction/stream');
```

### Mensajes Recibidos

**Conexión establecida:**
```json
{
  "type": "connection",
  "message": "Connected to extraction stream",
  "status": "ready"
}
```

**Estado del bot:**
```json
{
  "type": "bot_status",
  "bot_id": "01JCXA...",
  "status": "initializing|idle|processing",
  "task_id": "01JCXB...",
  "message": "Bot #1 ready"
}
```

**Screenshot del bot:**
```json
{
  "type": "bot_snapshot",
  "bot_id": "01JCXA...",
  "task_id": "01JCXB...",
  "screenshot": "data:image/png;base64,...",
  "current_url": "https://google.com/maps/...",
  "timestamp": "2026-02-17T10:30:00"
}
```

**Error del bot:**
```json
{
  "type": "bot_error",
  "bot_id": "01JCXA...",
  "error": "Navigation timeout"
}
```

## Testing

### Desde el frontend (React):
```bash
cd ui
npm run dev
# Abrir http://localhost:5174
# Crear campaña y hacer "Start Extraction"
```

### Con wscat (CLI):
```bash
npm install -g wscat
wscat -c ws://localhost:8000/ws/extraction/stream
```

## Architecture

```
src/extraction/
├── presentation/          # ← HTTP/WebSocket layer
│   ├── api_server.py     # FastAPI app
│   └── websocket/
│       └── extraction_handler.py
│
├── application/
│   └── services/
│       └── bot_orchestrator.py
│
├── domain/
│   └── entities/
│       └── bot.py        # Ephemeral bot entity
│
└── infrastructure/
    └── browser/
        ├── playwright_driver.py
        └── bot_pool.py
```

# WebSocket Protocol - CQRS Pattern

## Endpoint
```
ws://localhost:8000/ws/extraction/stream
```

## Message Protocol

All messages follow this structure:
```json
{
    "type": "command" | "query" | "subscribe" | "auto_start",
    "command": "<command_name>",    // if type=command
    "query": "<query_name>",        // if type=query
    "data": { ... }                 // payload
}
```

---

## 1. Commands (Modify State)

Commands modify extraction state and return confirmation.

### Start Extraction
```json
// Client → Server
{
    "type": "command",
    "command": "start_extraction",
    "data": {
        "extraction_bots": 3,      // Number of bots for extraction (or "num_bots" for backward compatibility)
        "search_seed": "restaurants",
        "cities": [
            ["Madrid", 40.4168, -3.7038],
            ["Barcelona", 41.3851, 2.1734]
        ]
    }
}

// Server → Client
{
    "type": "command_result",
    "command": "start_extraction",
    "success": true,
    "extraction_id": "uuid-123",
    "num_tasks": 2,
    "num_bots": 3,
    "message": "Extraction started successfully"
}
```

### Pause Extraction (TODO)
```json
{
    "type": "command",
    "command": "pause_extraction",
    "data": {
        "extraction_id": "uuid-123"
    }
}
```

### Cancel Extraction (TODO)
```json
{
    "type": "command",
    "command": "cancel_extraction",
    "data": {
        "extraction_id": "uuid-123"
    }
}
```

---

## 2. Queries (Read-Only)

Queries only read state without modifying it.

### Get Status
```json
// Client → Server
{
    "type": "query",
    "query": "get_status",
    "data": {
        "extraction_id": "uuid-123"
    }
}

// Server → Client
{
    "type": "query_result",
    "query": "get_status",
    "success": true,
    "data": {
        "extraction_id": "uuid-123",
        "status": "running",
        "bots_active": 3,
        "tasks_completed": 1,
        "tasks_pending": 1,
        "tasks_failed": 0
    }
}
```

### Get Statistics
```json
{
    "type": "query",
    "query": "get_statistics",
    "data": {
        "extraction_id": "uuid-123"
    }
}

// Response
{
    "type": "query_result",
    "query": "get_statistics",
    "success": true,
    "data": {
        "total_places_extracted": 150,
        "average_time_per_task": 45.2,
        "success_rate": 0.95,
        "total_screenshots": 300
    }
}
```

### Get Bot Info
```json
{
    "type": "query",
    "query": "get_bot_info",
    "data": {}
}

// Response
{
    "type": "query_result",
    "query": "get_bot_info",
    "success": true,
    "data": {
        "bots": [
            {"bot_id": "1", "status": "processing", "uptime_seconds": 120},
            {"bot_id": "2", "status": "idle", "uptime_seconds": 118}
        ]
    }
}
```

---

## 3. Event Streaming (Real-time Push)

Subscribe to receive real-time events.

### Subscribe to Events
```json
// Client → Server
{
    "type": "subscribe"
}

// Server → Client (confirmation)
{
    "type": "stream_started",
    "message": "Event streaming active"
}
```

### Bot Events (Pushed by Server)

**Bot Initialized:**
```json
{
    "type": "bot_status",
    "data": {
        "bot_id": "1",
        "status": "idle",
        "message": "Bot initialized"
    }
}
```

**Bot Snapshot (Screenshot):**
```json
{
    "type": "bot_snapshot",
    "data": {
        "bot_id": "1",
        "status": "processing",
        "screenshot": "base64_encoded_image...",
        "current_url": "https://google.com/maps/...",
        "task_id": "task-123"
    }
}
```

**Task Assigned:**
```json
{
    "type": "bot_status",
    "data": {
        "bot_id": "1",
        "status": "processing",
        "task_id": "task-123",
        "message": "Task assigned"
    }
}
```

**Task Completed:**
```json
{
    "type": "bot_status",
    "data": {
        "bot_id": "1",
        "status": "idle",
        "task_id": "task-123",
        "message": "Task completed"
    }
}
```

**Bot Error:**
```json
{
    "type": "bot_error",
    "data": {
        "bot_id": "1",
        "error": "Navigation timeout"
    }
}
```

---

## 4. Auto-Start Mode (Legacy)

For backward compatibility, supports automatic start.

```json
// Client → Server
{
    "type": "auto_start",
    "data": {
        "num_bots": 3,
        "search_seed": "restaurants"
    }
}

// Automatically:
// 1. Starts event streaming
// 2. Starts extraction
// 3. Returns result
```

---

## Example Flow: Manual Control

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/extraction/stream');

// 1. Subscribe to events first
ws.send(JSON.stringify({
    type: 'subscribe'
}));

// 2. Start extraction
ws.send(JSON.stringify({
    type: 'command',
    command: 'start_extraction',
    data: {
        num_bots: 3,
        search_seed: 'restaurants'
    }
}));

// 3. Listen for events
ws.onmessage = (event) => {
    const message = JSON.parse(event.data);
    
    if (message.type === 'bot_snapshot') {
        // Update UI with screenshot
        updateBotDisplay(message.data);
    }
    else if (message.type === 'command_result') {
        console.log('Command result:', message);
    }
};

// 4. Query status periodically
setInterval(() => {
    ws.send(JSON.stringify({
        type: 'query',
        query: 'get_status',
        data: { extraction_id: 'uuid-123' }
    }));
}, 5000);
```

---

## Error Handling

All errors follow this format:
```json
{
    "type": "error",
    "message": "Error description"
}
```

Commands and queries also return errors:
```json
{
    "type": "command_result",
    "command": "start_extraction",
    "success": false,
    "error": "Detailed error message"
}
```

# Google Maps Data Extractor

## Descripcion del Proyecto

**Google Maps Data Extractor** es una aplicacion profesional de scraping y extraccion de datos de Google Maps que permite obtener informacion detallada de lugares (negocios, restaurantes, hoteles, etc.) de forma masiva y automatizada.

El proyecto está diseñado siguiendo los principios de **Clean Architecture**, **Domain-Driven Design (DDD)**, **Arquitectura Hexagonal (Ports & Adapters)**, **SOLID**, **CQRS** y **Event-Driven Architecture**, garantizando separación de responsabilidades, testabilidad y mantenibilidad.

---

## Technology Stack

### Backend
- **Python 3.10+** — Core language with modern type hints
- **FastAPI** — High-performance async web framework
- **WebSocket** — Real-time bidirectional communication
- **SQLAlchemy 2.0** — Modern ORM with `Mapped` type hints
- **SQLite** — Lightweight, zero-config database
- **Playwright** — Browser automation for scraping
- **structlog** — Structured logging (JSON for production)
- **asyncio** — Async/await concurrency

### Frontend
- **React 18** — Modern UI library with hooks
- **Vite** — Lightning-fast build tool and dev server
- **Tailwind CSS 3.4** — Utility-first styling
- **Zustand** — Lightweight state management
- **Lucide React** — Beautiful icon library
- **Framer Motion** — Smooth animations

### Architecture Patterns
- **DDD** — Domain-Driven Design with bounded contexts
- **Hexagonal Architecture** — Ports & Adapters (Alistair Cockburn)
- **CQRS** — Command Query Responsibility Segregation
- **Event Bus** — Pub/Sub for decoupling
- **Repository Pattern** — Data access abstraction
- **Unit of Work** — Transaction management
- **DTO + Mappers** — Anti-Corruption Layer
- **SRP** — Single Responsibility Principle (SOLID)

---

# Project details

Architecture: DDD with Hexagonal Architecture
Python Version: 3.10+ (uses `typing_extensions` for compatibility)
Patterns Used:
- CQRS (Commands/Queries with separate handlers)
- Event-Driven Architecture (Event Bus for domain events)
- Value Objects for all domain primitives (frozen dataclasses)
- ULIDs for entity IDs
- Unit of Work pattern for transaction management
- Repository pattern with SQLAlchemy implementation
- DTO + Mappers for presentation layer (Anti-Corruption Layer)

Folder Structure:
```
src/
├── extraction/                         # Bounded Context (DDD)
│   ├── application/
│   │   ├── commands/                   ✅ Implemented
│   │   ├── services/                   ✅ Implemented (BotPoolManager, TaskQueue, BotOrchestrator)
│   │   └── queries/                    ⬚ TODO (Future)
│   ├── domain/
│   │   ├── entities/                   ✅ Implemented
│   │   ├── enums/                      ✅ Implemented
│   │   ├── events/                     ✅ Implemented (Bot events, Task events)
│   │   ├── exceptions/                 ✅ Implemented
│   │   ├── interfaces/                 ✅ Implemented
│   │   └── value_objects/              ✅ Implemented
│   ├── infrastructure/
│   │   ├── browser/                    ✅ Implemented (Playwright integration)
│   │   ├── http/                       ✅ Implemented
│   │   └── persistence/
│   │       ├── models/                 ✅ Implemented
│   │       ├── repositories/           ✅ Implemented
│   │       └── unit_of_work.py         ✅ Implemented
│   └── presentation/
│       ├── adapters/                   ✅ Implemented (WebSocket notification adapter)
│       ├── api_server.py               ✅ Implemented (FastAPI)
│       ├── dto/                        ✅ Implemented (DTOs + Mappers)
│       └── websocket/
│           ├── handlers/               ✅ Implemented (CommandHandler, QueryHandler, EventStreamHandler)
│           ├── extraction_handler.py   ✅ Implemented
│           └── PROTOCOL.md             ✅ Documented (CQRS WebSocket protocol)
│
├── shared/                             # Cross-cutting concerns
│   ├── events/
│   │   └── event_bus.py                ✅ Implemented (Pub/Sub pattern)
│   └── logging/
│       └── config.py                   ✅ Implemented (structlog dev/prod)
│
├── licensing/                          # Integration module (NOT a BC)
│   ├── domain/
│   │   ├── interfaces/                 ✅ Skeleton
│   │   └── value_objects/              ✅ Skeleton
│   └── infrastructure/
│       ├── http/                       ⬚ TODO (Future)
│       └── mock/                       ✅ Implemented
│
├── app/                                # Desktop application (Flet) [DEPRECATED]
│   └── ...                             ⚠️ Being replaced by app_webview + UI
│
├── app_webview/                        # WebView backend [TRANSITION]
│   └── ...                             ⚠️ Transitioning to React frontend
│
└── ui/                                 # React frontend (Vite) [CURRENT]
    ├── src/
    │   ├── App.jsx                     ✅ Implemented
    │   ├── components/                 ✅ Implemented
    │   └── services/                   ✅ Implemented
    └── package.json                    ✅ Configured (React + Tailwind + Zustand)
```

# Principles for AI code generation

| # | Principle | What It Means |
| :--- | :--- | :--- |
| **1** | **Business logic lives in the domain** | Rules go in Entities and Value Objects, not views or handlers. |
| **2** | **Code reflects ubiquitous language** | Use business terms (`booking.cancel()`), not technical terms (`booking.status = 3`). |
| **3** | **Aggregates protect invariants** | Child entities are modified through the aggregate root, never directly. |
| **4** | **Domain is framework-agnostic** | No FastAPI or SQLAlchemy imports in domain code—pure Python only. |
| **5** | **Repositories abstract persistence** | Domain defines interfaces, infrastructure implements them. |
| **6** | **Commands return void** | Commands change state; queries read state. Don't mix them. |
| **7** | **Value objects are immutable** | No setters. Any "change" creates a new instance. Use `@dataclass(frozen=True)`. |

---

## Domain Model

### Extraction Bounded Context

#### Aggregate Roots

- **Campaign** — The main aggregate root. Orchestrates the entire extraction process.
- **ExtractedPlace** — Independent aggregate root representing a place obtained from Google Maps.

#### Entities

| Entity | Belongs to (Aggregate Root) |
| :--- | :--- |
| `PlaceExtractionTask` | `Campaign` |
| `ExtractedPlaceReview` | `ExtractedPlace` |

`WebsitePlaceEnrichmentTask` is an independent entity with a `place_id` reference (not a Campaign child).

All child entities are accessed and modified exclusively through their aggregate root, never directly.

---

## Structured Logging

The project uses **structlog** for structured logging, located in `shared/logging/` as a cross-cutting concern.

- **Development**: Human-readable colored console output
- **Production**: JSON format for log aggregation systems (ELK, CloudWatch, etc.)

### Configuration

Call `configure_logging()` once at application startup:

```python
from shared.logging import configure_logging

# In main.py or FastAPI lifespan
configure_logging(environment="development")  # or "production"
```

### Usage

```python
from shared.logging import get_logger

logger = get_logger(__name__)

class BotPoolManager:
    async def initialize_pool(self, num_bots: int) -> None:
        logger.info(
            "initializing_bot_pool",
            num_bots=num_bots,
        )
```

### Context Binding (for WebSocket sessions)

```python
from shared.logging import bind_context, clear_context

# In WebSocket handler
async def handle_connection(websocket: WebSocket):
    session_id = str(uuid.uuid4())
    bind_context(session_id=session_id, client_ip=websocket.client.host)
    
    try:
        # All subsequent logs include session_id and client_ip
        logger.info("connection_established")
        await process_messages(websocket)
    finally:
        clear_context()
```

### Log Levels

| Level | Use Case |
| :--- | :--- |
| `logger.debug()` | Detailed diagnostic information |
| `logger.info()` | State changes, completed operations |
| `logger.warning()` | Unexpected but recoverable situations |
| `logger.error()` | Failures requiring attention |

### Guidelines

1. **Domain layer does not log** — Emit domain events instead
2. **Log at boundaries** — Application services, adapters, WebSocket handlers
3. **Include context** — Always add `bot_id`, `task_id`, `session_id` when available
4. **Use semantic event names** — `bot_initialized`, `task_completed`, not generic messages

---

## Event Bus Pattern

The project uses a **lightweight Event Bus** (`shared/events/event_bus.py`) for decoupling domain events from side effects.

### Architecture

```
Domain Layer (emits events) → Event Bus → Application Layer (subscribes)
                                ↓
                         Infrastructure Layer (notifications, logging)
```

### Usage

**Publishing events:**
```python
from shared.events import EventBus

# In application service
async def start_extraction(self):
    # ... business logic ...
    
    event = BotInitializedEvent(
        bot_id="bot-1",
        timestamp=datetime.now(),
        status=BotStatus.READY
    )
    await EventBus.publish(event)
```

**Subscribing to events:**
```python
from shared.events import EventBus

# In adapters or other services
async def notify_websocket(event: BotSnapshotCapturedEvent):
    await websocket.send_json(event.to_dict())

# Register subscriber
EventBus.subscribe(BotSnapshotCapturedEvent, notify_websocket)
```

### Key Features

- **Async/await support** — Non-blocking event handling
- **Type-safe subscriptions** — Subscribe to specific event types
- **Error isolation** — Failed handlers don't break other subscribers
- **Decoupling** — Domain doesn't know about WebSocket, logging, etc.

---

## CQRS Pattern (WebSocket)

The WebSocket layer implements **CQRS (Command Query Responsibility Segregation)** with three distinct handler types.

### Architecture

```
WebSocket Connection
    │
    ├── CommandHandler    → Modifies state (start_extraction, pause, cancel)
    ├── QueryHandler      → Reads state (get_status, get_statistics)
    └── EventStreamHandler → Real-time events (bot snapshots, task updates)
```

### Protocol

See [extraction/presentation/websocket/PROTOCOL.md](src/extraction/presentation/websocket/PROTOCOL.md) for full protocol documentation.

**Auto-start mode (default):**
```
Client connects → Server auto-starts extraction → Events stream continuously
```

**Manual mode (future):**
```json
{
    "type": "command",
    "command": "start_extraction",
    "data": {
        "num_bots": 3,
        "search_seed": "restaurants",
        "cities": [["Madrid", 40.4168, -3.7038]]
    }
}
```

### Handlers

| Handler | Responsibility | Blocking |
| :--- | :--- | :--- |
| `CommandHandler` | Start/pause/cancel extraction | Yes (when starting) |
| `QueryHandler` | Read-only queries (status, stats) | No |
| `EventStreamHandler` | Forward domain events to WebSocket | No |

### Auto-Start Implementation

The current implementation auto-starts extraction on WebSocket connection:

```python
async def handle(self, websocket: WebSocket):
    await websocket.accept()
    await self._auto_start_extraction(websocket)  # Immediate start
```

This simplifies initial usage. CQRS handlers are available for future manual control.

---

## Frontend Architecture (React + Vite)

The UI follows a **clean architecture** similar to the backend, with clear separation of concerns.

### Structure

```
ui/src/
├── domain/                     # Domain layer (business logic, entities)
├── infrastructure/             # External services (API clients, WebSocket)
├── presentation/               # UI components and views
│   ├── components/             # Reusable components
│   └── views/                  # Page-level views
├── store/                      # Zustand state management
│   └── appStore.js             # Global application state
├── App.jsx                     # Root component
└── main.jsx                    # Entry point
```

### State Management (Zustand)

Lightweight state management without Redux boilerplate:

```javascript
import { useAppStore } from './store/appStore';

function ExtractionView() {
    const { bots, places, addBot } = useAppStore();
    
    // Bots and places are reactive
    return (
        <div>
            {bots.map(bot => <BotCard key={bot.id} bot={bot} />)}
        </div>
    );
}
```

### WebSocket Integration

Real-time communication with backend:

```javascript
// In infrastructure/
const ws = new WebSocket('ws://localhost:8000/ws/extraction/stream');

ws.onmessage = (event) => {
    const message = JSON.parse(event.data);
    
    switch (message.type) {
        case 'bot_snapshot':
            useAppStore.getState().updateBot(message.data);
            break;
        case 'place_extracted':
            useAppStore.getState().addPlace(message.data);
            break;
    }
};
```

### Key Features

| Feature | Technology | Description |
| :--- | :--- | :--- |
| **Real-time updates** | WebSocket | Bot snapshots, place extraction events |
| **Smooth animations** | Framer Motion | Bot status transitions, list animations |
| **State management** | Zustand | Lightweight, no boilerplate |
| **Styling** | Tailwind CSS | Utility-first, responsive design |
| **Icons** | Lucide React | Consistent icon system |
| **Dev Server** | Vite | HMR, instant feedback |

### Component Architecture

**Presentation Layer:**
- `views/DashboardView.jsx` — Campaign management, statistics
- `views/ExtractionView.jsx` — Real-time extraction monitoring
- `components/BotCard.jsx` — Bot status + screenshot
- `components/PlaceCard.jsx` — Extracted place preview
- `components/ProgressBar.jsx` — Task progress visualization

**Infrastructure Layer:**
- `api/WebSocketClient.js` — WebSocket connection management
- `api/ApiClient.js` — REST API calls (campaigns, exports)

**Store:**
- `appStore.js` — Global state (bots, places, tasks, UI state)

### Styling Approach

Tailwind CSS with custom theme:

```jsx
<div className="bg-gray-900 text-white min-h-screen p-6">
    <h1 className="text-3xl font-bold mb-6">Extraction Dashboard</h1>
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {/* Bot cards */}
    </div>
</div>
```

### Development Workflow

1. **Backend running:** `python run_server.py` (port 8000)
2. **Frontend running:** `npm run dev` (port 5174)
3. **Auto-reload:** Both backend and frontend support hot reload
4. **WebSocket:** Automatically connects on page load

---

## Implementation Status

### ✅ Completed

| Layer | Component | Description |
| :--- | :--- | :--- |
| **Domain** | Entities | `Campaign`, `ExtractedPlace`, `PlaceExtractionTask`, `ExtractedPlaceReview`, `WebsitePlaceEnrichmentTask` |
| **Domain** | Value Objects | IDs (ULID-based), `CampaignConfig`, `CampaignGeonameSelectionParams`, `Geoname`, `EnrichmentPoolConfig`, `BotSnapshot`, etc. |
| **Domain** | Enums | `CampaignStatus`, `TaskStatus`, `EnrichmentStatus`, `CampaignScope`, `CampaignDepthLevel`, `EnrichmentType`, `BotStatus` |
| **Domain** | Events | `BotInitializedEvent`, `BotSnapshotCapturedEvent`, `BotTaskAssignedEvent`, `BotTaskCompletedEvent`, `BotErrorEvent`, `BotClosedEvent`, `TaskStartedEvent`, `PlaceExtractedEvent`, `TaskCompletedEvent`, `TaskFailedEvent` |
| **Domain** | Interfaces | `CampaignRepository`, `ExtractedPlaceRepository`, `PlaceExtractionTaskRepository`, `WebsitePlaceEnrichmentTaskRepository`, `GeonameQueryService`, `AbstractUnitOfWork` |
| **Application** | Commands | `CreateCampaignCommand`, `StartCampaignCommand` with handlers |
| **Application** | Services | `BotPoolManager` (SRP: bot lifecycle), `TaskQueue` (SRP: task distribution), `BotOrchestrator` (SRP: extraction coordination) |
| **Infrastructure** | Browser | Playwright integration with `BotPool`, `PlaywrightBot` |
| **Infrastructure** | HTTP | `HttpGeonameQueryService` (adapter for geonames microservice) |
| **Infrastructure** | ORM Models | `CampaignModel`, `PlaceExtractionTaskModel`, `ExtractedPlaceModel`, `ExtractedPlaceReviewModel`, `WebsitePlaceEnrichmentTaskModel` (SQLAlchemy 2.0) |
| **Infrastructure** | Repositories | `SqlAlchemyCampaignRepository`, `SqlAlchemyExtractedPlaceRepository`, `SqlAlchemyPlaceExtractionTaskRepository`, `SqlAlchemyWebsitePlaceEnrichmentTaskRepository` |
| **Infrastructure** | Unit of Work | `SqlAlchemyUnitOfWork` with session management |
| **Presentation** | API Server | FastAPI with WebSocket support |
| **Presentation** | WebSocket | CQRS handlers (Command, Query, EventStream) |
| **Presentation** | DTOs | `BotSnapshotDTO` with mappers (Anti-Corruption Layer) |
| **Presentation** | Adapters | `WebSocketNotificationAdapter` (domain → WebSocket) |
| **Shared** | Event Bus | Pub/Sub pattern with async handlers |
| **Shared** | Logging | structlog with dev (colored) / prod (JSON) modes, contextual binding |
| **Licensing** | Interfaces | `LicenseValidator` port (validate, activate, deactivate) |
| **Licensing** | Value Objects | `LicenseStatus` (valid, tier, expires_at, features) |
| **Licensing** | Mock | `MockLicenseValidator` for development/testing |
| **UI** | Frontend | React + Vite + Tailwind + Zustand (state management) |
| **UI** | Components | Dashboard, Campaign creation, Real-time extraction view |

### ⬚ TODO / Future

| Layer | Component | Description |
| :--- | :--- | :--- |
| Application | Queries | Read-side query handlers (CQRS) - Currently using mock data |
| Presentation | Commands | `pause_extraction`, `cancel_extraction` - Marked TODO in CommandHandler |
| Licensing | HTTP Client | `HttpLicenseClient` implementation with offline grace period |
| Backend | Licensing API | Separate project: FastAPI + Stripe/Paddle integration |
| Application | Resume Campaign | Load pending tasks from DB to resume an interrupted campaign |

### ⚠️ Design Notes

**`PlaceExtractionTask.event_bus` injection on resume:**

`PlaceExtractionTask` holds an optional `event_bus` field (default `None`). When tasks are created fresh via `PlaceExtractionTask.create(..., event_bus=event_bus)`, domain events (`TaskStartedEvent`, `TaskCompletedEvent`, `TaskFailedEvent`) are published normally.

When tasks are loaded from the DB via `model_to_task()` (e.g., to resume a campaign), `event_bus` is `None` and state-change events are silently skipped. This is currently harmless because the execution pipeline always creates tasks fresh. **When resume is implemented**, `model_to_task` must accept an `event_bus` parameter and inject it:

```python
def model_to_task(
    model: PlaceExtractionTaskModel,
    event_bus: Optional[EventBus] = None,
) -> PlaceExtractionTask:
    return PlaceExtractionTask(..., event_bus=event_bus)
```

---

## Getting Started

### Prerequisites

- **Python 3.10+**
- **Node.js 18+** (for React frontend)
- **Git**

### Installation

**1. Clone the repository:**
```bash
git clone https://github.com/your-username/google-maps-data-extractor.git
cd google-maps-data-extractor
```

**2. Create Python virtual environment:**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

**3. Install Python dependencies:**
```bash
pip install -r requirements.txt
```

**4. Install Playwright browsers:**
```bash
python -m playwright install chromium
```

**5. Install frontend dependencies:**
```bash
cd ui
npm install
```

### Running the Application

**Terminal 1 - Backend (FastAPI + WebSocket):**
```bash
# From project root
cd src/extraction/presentation
python run_server.py
```

Backend will run on: `http://localhost:8000`

**Terminal 2 - Frontend (React + Vite):**
```bash
# From project root
cd ui
npm run dev
```

Frontend will run on: `http://localhost:5174`

**Open browser:** Navigate to `http://localhost:5174`

### Development Mode

The application runs in development mode by default with:
- **Colored console logs** (structlog)
- **Auto-reload** (FastAPI with uvicorn `--reload`)
- **Hot Module Replacement** (Vite HMR)
- **React DevTools** support

---

## Tests

### Structure

```
tests/
└── extraction/
    ├── conftest.py              # Fixtures (SQLite in-memory, UoW)
    ├── application/
    │   └── commands/
    └── infrastructure/
        └── persistence/
```

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run specific test file
pytest tests/extraction/infrastructure/persistence/test_campaign_repository.py

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

### Fixtures

Tests use SQLite in-memory for fast, isolated integration tests:

```python
@pytest.fixture
def uow(session_factory):
    """Create a Unit of Work with in-memory SQLite."""
    return SqlAlchemyUnitOfWork(session_factory)
```

---

## Database Schema

### Tables

| Table | Type | Description |
| :--- | :--- | :--- |
| `campaigns` | Aggregate Root | Campaign metadata and configuration |
| `place_extraction_tasks` | Entity | Tasks for extracting places (1:N with campaigns) |
| `extracted_places` | Aggregate Root | Extracted place data from Google Maps |
| `extracted_place_reviews` | Entity | Reviews for extracted places (1:N with places) |
| `website_enrichment_tasks` | Entity | Tasks for website enrichment (independent) |

### Relationships

```
campaigns (1) ─────< (N) place_extraction_tasks
                    
extracted_places (1) ─────< (N) extracted_place_reviews

website_enrichment_tasks → (place_id reference, not FK)
```

---

## Persistence

### ORM Models

SQLAlchemy 2.0 style with `Mapped` and `mapped_column`:

| Model | Table | Type |
| :--- | :--- | :--- |
| `CampaignModel` | `campaigns` | Aggregate Root |
| `PlaceExtractionTaskModel` | `place_extraction_tasks` | Child Entity |
| `ExtractedPlaceModel` | `extracted_places` | Aggregate Root |
| `ExtractedPlaceReviewModel` | `extracted_place_reviews` | Child Entity |
| `WebsitePlaceEnrichmentTaskModel` | `website_enrichment_tasks` | Independent Entity |

### Unit of Work Usage

```python
from extraction.infrastructure.persistence import create_unit_of_work

uow = create_unit_of_work("sqlite:///data.db")

with uow:
    campaign = Campaign.create(title="Test", config=config)
    uow.campaign_repository.save(campaign)
    uow.commit()
```

### Database Support

SQLite is the primary database for the desktop application:

| Database | Use Case |
| :--- | :--- |
| SQLite | Desktop app (production) |
| SQLite (in-memory) | Integration tests |

---

## Application Services (SRP Refactoring)

The extraction process is orchestrated by **three single-responsibility services**:

### BotPoolManager

**Responsibility:** Bot lifecycle management

```python
from extraction.application.services import BotPoolManager

manager = BotPoolManager(event_bus)

# Initialize bots
await manager.initialize_pool(num_bots=3)

# Get available bot
bot = await manager.get_available_bot()

# Release bot back to pool
await manager.release_bot(bot_id)

# Cleanup
await manager.cleanup()
```

**Key methods:**
- `initialize_pool(num_bots)` — Creates bot pool
- `get_available_bot()` — Returns ready bot (waits if none available)
- `release_bot(bot_id)` — Returns bot to available pool
- `cleanup()` — Closes all browsers

### TaskQueue

**Responsibility:** Task distribution (thread-safe)

```python
from extraction.application.services import TaskQueue

queue = TaskQueue()

# Load tasks
tasks = [task1, task2, task3, ...]
queue.enqueue_many(tasks)

# Workers claim tasks
task_id = await queue.dequeue()  # Returns None when empty

# Check completion
if queue.is_empty():
    print("All tasks completed")
```

**Key methods:**
- `enqueue_many(tasks)` — Bulk load tasks
- `dequeue()` — Claim next task (thread-safe)
- `is_empty()` — Check if all tasks claimed

### BotOrchestrator

**Responsibility:** Extraction coordination

```python
from extraction.application.services import BotOrchestrator

orchestrator = BotOrchestrator(bot_pool, task_queue, event_bus)

# Run extraction (blocks until complete)
await orchestrator.run()
```

**Workflow:**
1. Claims bot from pool
2. Claims task from queue
3. Extracts place
4. Captures screenshot
5. Publishes domain events
6. Releases bot
7. Repeats until queue empty

### Why This Design?

| Before | After |
| :--- | :--- |
| Monolithic `Bot` class | Three focused services |
| Mixed responsibilities | Single Responsibility Principle |
| Hard to test | Easy to mock individual services |
| Tight coupling | Loose coupling via Event Bus |

---

## DTOs and Mappers (Presentation Layer)

The presentation layer uses **DTOs (Data Transfer Objects)** to decouple domain models from WebSocket messages.

### Architecture

```
Domain Layer (bytes, enums) → Mapper → DTO (strings, JSON-serializable)
```

### Example: BotSnapshotDTO

**Domain model:**
```python
@dataclass(frozen=True)
class BotSnapshot:
    bot_id: str
    status: BotStatus  # Enum
    screenshot_bytes: bytes  # Raw binary
    timestamp: datetime
```

**DTO:**
```python
@dataclass(frozen=True)
class BotSnapshotDTO:
    bot_id: str
    status: str  # String, not enum
    screenshot_base64: str  # Base64 encoded
    timestamp: str  # ISO format
    
    def to_dict(self) -> dict:
        """JSON-serializable representation"""
        return asdict(self)
```

**Mapper (Anti-Corruption Layer):**
```python
from extraction.presentation.dto import bot_snapshot_to_dto

# Convert domain → DTO
snapshot = BotSnapshot(...)  # from domain
dto = bot_snapshot_to_dto(snapshot)
await websocket.send_json(dto.to_dict())
```

### Why DTOs?

| Concern | Solution |
| :--- | :--- |
| Domain uses bytes | DTO uses base64 strings (JSON-compatible) |
| Domain uses enums | DTO uses strings |
| Domain uses datetime | DTO uses ISO 8601 strings |
| Backward compatibility | Change DTO without touching domain |

---

## Concurrency Model

### Why Queue-Based Task Distribution?

SQLite is single-writer, but the real bottleneck in scraping is HTTP latency (~3s per request), not database writes (~5ms). This makes SQLite perfectly viable for concurrent scraping.

```
Operation Timings:
HTTP ████████████████████████████████████████████ 3000ms (99%)
Parse ▌ 30ms
SQLite │ 5ms
```

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      MAIN THREAD                             │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  TaskQueue [Task1, Task2, Task3, ... TaskN]         │    │
│  └─────────────────────────────────────────────────────┘    │
│                          │                                   │
│         ┌────────────────┼────────────────┐                 │
│         ▼                ▼                ▼                 │
│    ┌─────────┐      ┌─────────┐      ┌─────────┐           │
│    │  Bot 1  │      │  Bot 2  │      │  Bot 3  │           │
│    │ HTTP    │      │ HTTP    │      │ HTTP    │ ← parallel │
│    │ Parse   │      │ Parse   │      │ Parse   │           │
│    └────┬────┘      └────┬────┘      └────┬────┘           │
│         │                │                │                 │
│         └────────────────┼────────────────┘                 │
│                          ▼                                   │
│                   ┌─────────────┐                           │
│                   │   SQLite    │  ← serialized writes      │
│                   └─────────────┘                           │
└─────────────────────────────────────────────────────────────┘
```

### Key Benefits

| Aspect | Benefit |
| :--- | :--- |
| **Thread-safe claiming** | `asyncio.Queue` handles synchronization |
| **No DB locking needed** | Tasks distributed before workers start |
| **SQLite compatible** | Single-writer limitation irrelevant |
| **Simple & debuggable** | No race conditions to debug |

---

## Tests

### Structure

```
tests/
└── extraction/
    ├── conftest.py              # Fixtures (SQLite in-memory, UoW)
    └── infrastructure/
        └── persistence/
            └── test_campaign_repository.py
```

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run specific test file
pytest tests/extraction/infrastructure/persistence/test_campaign_repository.py
```

### Fixtures

Tests use SQLite in-memory for fast, isolated integration tests:

```python
@pytest.fixture
def uow(session_factory):
    """Create a Unit of Work with in-memory SQLite."""
    return SqlAlchemyUnitOfWork(session_factory)
```

---

## HTTP Adapters

### GeonameQueryService

Adapter for the geonames microservice:

```python
from extraction.infrastructure.http import HttpGeonameQueryService

geoname_service = HttpGeonameQueryService(base_url="http://localhost:8000")

# Get admin divisions (ADM1, ADM2, ADM3)
geonames = geoname_service.find_admin_geonames({
    "countryCode": "ES",
    "featureCode": "ADM1",
})

# Get cities
cities = geoname_service.find_city_geonames({
    "countryCode": "ES",
    "minPopulation": 50000,
})
```

---

## Product Architecture

### Desktop App + Licensing API

The product follows a **local-first architecture** with remote license validation:

```
┌────────────────────────────────────────────────┐
│              DESKTOP APP (Client)               │
├────────────────────────────────────────────────┤
│  Scraper → SQLite → Export (CSV/Excel/JSON)    │
│                                                 │
│  On startup: POST /api/license/validate        │
└─────────────────────┬──────────────────────────┘
                      │ HTTPS
                      ▼
┌────────────────────────────────────────────────┐
│              LICENSING API (VPS)                │
├────────────────────────────────────────────────┤
│  • /api/license/validate                        │
│  • /api/license/activate                        │
│  • /api/license/deactivate                      │
│  • Stripe/Paddle integration                   │
└────────────────────────────────────────────────┘
```

### Why This Architecture?

| Decision | Rationale |
| :--- | :--- |
| **Scraper runs on client** | Leverage residential IP to avoid Google bans |
| **Data stored locally** | Zero latency, works offline, no server storage costs |
| **License validation via API** | Anti-piracy, subscription management |
| **SQLite for client** | No database server needed, single-file portability |

### Licensing Integration

The `licensing/` module is **NOT a Bounded Context** — it's a port/adapter integration to communicate with the external Licensing API microservice. The actual Licensing BC lives on the VPS.

```python
from licensing.domain.interfaces import LicenseValidator
from licensing.infrastructure.http import HttpLicenseClient
from licensing.infrastructure.mock import MockLicenseValidator

# Production
validator = HttpLicenseClient(base_url="https://api.myapp.com")

# Development/Testing
validator = MockLicenseValidator()

# Validate license
status = validator.validate("LICENSE-KEY-HERE")
if status.is_active:
    # Allow app usage
    pass
```

### LicenseStatus Value Object

```python
@dataclass(frozen=True)
class LicenseStatus:
    valid: bool
    tier: str | None = None           # "basic", "pro", "enterprise"
    expires_at: datetime | None = None
    max_devices: int | None = None
    features: tuple[str, ...] = ()    # ("export_csv", "export_excel", "api_access")

    @property
    def is_active(self) -> bool:
        return self.valid and not self.is_expired
```

### Mock for Development

Use `MockLicenseValidator` during development:

- `VALID-*` → Returns valid license (tier: pro, 30 days)
- `EXPIRED-*` → Returns expired license
- Any other prefix → Returns invalid

---

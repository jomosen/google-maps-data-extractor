# Integración de Tauri - Próximos Pasos

## 📋 Configuración de Tauri

### 1. Instalar Tauri CLI

```bash
cd ui
npm install -D @tauri-apps/cli
```

### 2. Inicializar Tauri

```bash
npx tauri init
```

Responde las siguientes preguntas:
- **App name**: google-maps-extractor
- **Window title**: Google Maps Data Extractor
- **Web assets location**: ../dist
- **Dev server URL**: http://localhost:5173
- **Dev command**: npm run dev
- **Build command**: npm run build

Esto creará la carpeta `src-tauri/` con la configuración.

### 3. Actualizar package.json

Añade estos scripts:

```json
{
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "tauri": "tauri",
    "tauri:dev": "tauri dev",
    "tauri:build": "tauri build"
  }
}
```

### 4. Configurar tauri.conf.json

```json
{
  "build": {
    "beforeDevCommand": "npm run dev",
    "beforeBuildCommand": "npm run build",
    "devPath": "http://localhost:5173",
    "distDir": "../dist"
  },
  "package": {
    "productName": "Google Maps Data Extractor",
    "version": "0.1.0"
  },
  "tauri": {
    "allowlist": {
      "all": false,
      "shell": {
        "all": false,
        "open": true
      },
      "window": {
        "all": false,
        "close": true,
        "hide": true,
        "show": true,
        "maximize": true,
        "minimize": true,
        "unmaximize": true,
        "unminimize": true,
        "startDragging": true
      }
    },
    "bundle": {
      "active": true,
      "category": "DeveloperTool",
      "copyright": "",
      "identifier": "com.googlemaps.extractor",
      "longDescription": "",
      "shortDescription": "",
      "targets": "all"
    },
    "windows": [
      {
        "fullscreen": false,
        "height": 800,
        "resizable": true,
        "title": "Google Maps Data Extractor",
        "width": 1400,
        "minWidth": 1024,
        "minHeight": 768
      }
    ]
  }
}
```

## 🔌 Conectar con Backend Python

### Opción 1: Comunicación via Tauri Commands

Crea comandos Tauri en Rust que invoquen el backend Python:

```rust
// src-tauri/src/main.rs
#[tauri::command]
fn start_extraction(campaign_id: String) -> Result<String, String> {
    // Llamar al backend Python
    // Puede usar python_bridge o ejecutar scripts
    Ok("Started".to_string())
}

fn main() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![start_extraction])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
```

En el frontend:

```javascript
import { invoke } from '@tauri-apps/api/tauri';

// Reemplazar MockExtractionService
async function startExtraction(campaignId) {
    const result = await invoke('start_extraction', { campaignId });
    return result;
}
```

### Opción 2: Backend Python como Servidor Local

1. Inicia el backend Python en `localhost:8000`
2. Reemplaza MockExtractionService con fetch/WebSocket:

```javascript
// src/infrastructure/RealExtractionService.js
class RealExtractionService {
    async createCampaign(data) {
        const response = await fetch('http://localhost:8000/campaigns', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        return response.json();
    }

    subscribeToExtraction(campaignId, callback) {
        const ws = new WebSocket(`ws://localhost:8000/campaigns/${campaignId}/stream`);
        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            callback(data);
        };
        return () => ws.close();
    }
}
```

### Opción 3: Empaquetar Python con Tauri

Incluye el intérprete de Python en el bundle:

1. **pyinstaller**: Compila el backend a ejecutable
2. **Tauri sidecar**: Incluye el ejecutable en el bundle
3. **Comunicación**: Stdio o HTTP local

## 📡 Actualizar Store para Backend Real

```javascript
// src/store/appStore.js
import { realExtractionService } from '../infrastructure/RealExtractionService';

export const useAppStore = create((set, get) => ({
  // ... estado actual
  
  createCampaign: async (campaignData) => {
    // Llamada real al backend
    const campaign = await realExtractionService.createCampaign(campaignData);
    set({ campaigns: [campaign, ...get().campaigns] });
    return campaign;
  },

  startExtraction: async (campaignId) => {
    // Suscribirse a WebSocket o Tauri event
    const unsubscribe = realExtractionService.subscribeToExtraction(
      campaignId,
      (data) => {
        set({
          activeCampaign: data.campaign,
          bots: data.bots,
          places: data.places
        });
      }
    );
    
    set({ currentView: 'monitor' });
    return unsubscribe;
  }
}));
```

## 🚀 Ejecutar con Tauri

```bash
# Modo desarrollo (Hot reload)
npm run tauri:dev

# Build producción
npm run tauri:build
```

## 📦 Distribución

Los binarios se generan en:
- Windows: `src-tauri/target/release/bundle/msi/`
- macOS: `src-tauri/target/release/bundle/dmg/`
- Linux: `src-tauri/target/release/bundle/appimage/`

## ⚠️ Consideraciones

1. **Seguridad**: Valida todas las entradas del frontend
2. **Permisos**: Minimiza los permisos de Tauri allowlist
3. **Backend**: Asegura que el backend Python esté corriendo
4. **Logs**: Implementa logging para debugging
5. **Updates**: Configura auto-updates con Tauri updater

## 🔄 Migración del Mock

1. Mantén MockExtractionService para desarrollo
2. Usa variable de entorno para elegir adaptador:

```javascript
// src/infrastructure/index.js
const isDev = import.meta.env.DEV;
const useMock = import.meta.env.VITE_USE_MOCK === 'true';

export const extractionService = (isDev && useMock)
  ? mockExtractionService
  : realExtractionService;
```

3. En `.env`:
```
VITE_USE_MOCK=true  # Usar mock
# VITE_USE_MOCK=false  # Usar backend real
```

## 📚 Referencias

- [Tauri Docs](https://tauri.app/)
- [Tauri + Vite](https://tauri.app/v1/guides/getting-started/setup/vite)
- [Calling Python from Rust](https://pyo3.rs/)
- [WebSocket en Tauri](https://tauri.app/v1/guides/features/websocket)

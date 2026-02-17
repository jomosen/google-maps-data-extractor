# Google Maps Data Extractor - UI PoC

## Descripción

Interfaz de usuario construida con **Vite + React + Tailwind CSS** para la aplicación de extracción de datos de Google Maps. Este PoC implementa tres vistas principales con una arquitectura limpia y separación de responsabilidades.

## Características Implementadas

### 🎨 Vista 1: Dashboard Principal
- Header con estado de licencia (mock del BC Licensing)
- 4 KPI Cards: Total Extracted, Success Rate, Active Bots, Proxy Health
- Tabla de campañas recientes
- Empty state con botón "Create First Campaign"

### 🧙 Vista 2: Wizard de Creación
- Formulario de campaña con validación
- Select de Activity con búsqueda
- Geographic Picker jerárquico con `react-select`:
  - Country (single select)
  - Admin 1 / States (multi-select dependiente)
  - Cities (multi-select dependiente)
- Resumen de campaña antes de iniciar

### 📊 Vista 3: Monitor de Extracción
- Layout split-view con panel colapsable
- Panel izquierdo:
  - Progreso circular y contador
  - Tabla en tiempo real de lugares extraídos
  - Toggle para colapsar/expandir
- Panel derecho:
  - Sistema de pestañas para cada bot
  - Visualización del navegador (simulado)
  - Overlay con información del bot

## Arquitectura

```
ui/src/
├── domain/              # Interfaces y tipos del dominio
│   ├── Campaign.js
│   ├── Place.js
│   ├── Bot.js
│   └── License.js
├── infrastructure/      # Adaptadores y mocks
│   ├── MockExtractionService.js
│   └── mockData.js
├── presentation/        # Componentes React
│   ├── components/
│   │   ├── Button.jsx
│   │   ├── Card.jsx
│   │   ├── Input.jsx
│   │   └── Select2.jsx
│   └── views/
│       ├── DashboardView.jsx
│       ├── CreateCampaignView.jsx
│       └── MonitorView.jsx
└── store/              # Estado global (Zustand)
    └── appStore.js
```

## Tecnologías

- ⚡ **Vite** - Build tool
- ⚛️ **React 19** - Framework UI
- 🎨 **Tailwind CSS** - Estilos
- 🎭 **Framer Motion** - Animaciones
- 🎯 **Zustand** - State management
- 🔽 **react-select** - Select avanzado
- 🎨 **Lucide React** - Iconos

## Instalación y Ejecución

```bash
# Instalar dependencias
npm install

# Ejecutar en modo desarrollo
npm run dev

# Build para producción
npm run build
```

## Simulación de Backend (Mock)

El `MockExtractionService` simula el comportamiento del backend:

- ✅ Genera lugares cada 2-3 segundos
- ✅ Actualiza el progreso de bots
- ✅ Simula capturas de pantalla de navegadores
- ✅ Notifica cambios a través de un sistema de suscripción

## Flujo de Usuario

1. **Dashboard** → Ver campañas y KPIs
2. **Create Campaign** → Configurar nueva extracción
3. **Monitor** → Ver extracción en tiempo real
4. **Dashboard** → Ver resultados completados

## Principios de Diseño

- 🎯 **Fachada Pura**: Sin lógica de negocio en la UI
- 🏗️ **Arquitectura Hexagonal**: Preparada para adaptadores reales
- 🌑 **Dark Mode**: Estética minimalista profesional
- ⚡ **Performance**: Animaciones optimizadas
- 📱 **Responsive**: Diseño adaptable

## Próximos Pasos (Backend Integration)

1. Reemplazar `MockExtractionService` con adaptador WebSocket/API
2. Conectar con BC Extraction y BC Licensing
3. Implementar autenticación
4. Añadir Tauri para aplicación desktop

## Notas

- El mock incluye datos de prueba para USA, México, España, Francia y Alemania
- Las capturas de pantalla de bots se generan dinámicamente con Canvas
- El sistema está listo para conectarse con el backend Python existente en `/src`

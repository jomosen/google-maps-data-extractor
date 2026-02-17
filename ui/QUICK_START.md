# Guía Rápida de Uso - PoC UI

## 🚀 Inicio Rápido

```bash
cd ui
npm install  # Solo la primera vez
npm run dev  # Iniciar servidor de desarrollo
```

Abre tu navegador en: `http://localhost:5173`

## 📖 Cómo Usar el PoC

### 1. Dashboard (Vista Inicial)
Al iniciar verás:
- **KPI Cards** con métricas simuladas
- **Tabla de campañas** con 2 campañas de ejemplo ya completadas
- Botón **"Create Campaign"** para crear nueva campaña

### 2. Crear una Campaña
1. Haz clic en **"Create Campaign"**
2. Ingresa un título (ej: "NYC Cafés")
3. Selecciona una actividad (ej: "Café")
4. Selecciona geografía:
   - **Country**: Elige un país
   - **States/Regions**: Se habilitará automáticamente, selecciona uno o más
   - **Cities**: Se habilitará según las regiones, selecciona una o más
5. Verás un resumen de la campaña
6. Haz clic en **"Create and Start Extraction"**

### 3. Monitor de Extracción
- **Panel Izquierdo**: 
  - Ver progreso circular (0-100%)
  - Lista de lugares extraídos en tiempo real
  - Información detallada de cada lugar
- **Panel Derecho**:
  - Pestañas de bots (Bot #1, #2, #3)
  - Visualización del navegador simulado
  - Estado y progreso de cada bot
- **Toggle**: Botón entre paneles para colapsar/expandir

### 4. Ver Extracción en Tiempo Real
- Los lugares aparecen cada 2-3 segundos
- Los bots actualizan sus "pantallas" cada segundo
- El progreso se actualiza automáticamente
- La extracción se completa al llegar a 50 lugares

## 🎯 Funcionalidades a Probar

### Geographic Picker Jerárquico
- Prueba cambiar de país → las regiones se actualizan
- Selecciona múltiples regiones → las ciudades se actualizan
- Multi-selección con chips visuales

### Animaciones
- Hover sobre KPI cards
- Transición entre vistas
- Aparición de lugares extraídos
- Colapsar/expandir panel

### Datos de Prueba Disponibles
- **USA**: California, New York, Texas, Florida
- **México**: CDMX, Jalisco, Nuevo León  
- **España**: Madrid, Barcelona, Valencia
- **Francia** y **Alemania**: Datos básicos

## 🎨 Características Visuales

- **Dark Mode** profesional
- **Animaciones fluidas** con Framer Motion
- **Componentes interactivos** con feedback visual
- **Diseño responsivo**

## ⚙️ Personalización

### Modificar Datos Mock
- `src/infrastructure/mockData.js` - Añadir países, regiones, ciudades
- `src/infrastructure/MockExtractionService.js` - Ajustar velocidad de extracción

### Cambiar Colores
- `tailwind.config.js` - Personalizar paleta de colores
- `src/index.css` - Estilos globales

## 🐛 Solución de Problemas

### El servidor no inicia
```bash
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### Los estilos no se aplican
- Verifica que Tailwind esté instalado: `npm list tailwindcss`
- Reinicia el servidor: Ctrl+C y `npm run dev`

### No aparecen datos mock
- Abre DevTools (F12) → Console
- Verifica que no haya errores de JavaScript

## 📝 Notas Técnicas

- **Estado Global**: Zustand (`src/store/appStore.js`)
- **Simulación**: MockExtractionService con setInterval
- **Canvas**: Los "screenshots" de bots se generan dinámicamente
- **React 19**: Usando las últimas características

## 🔄 Próxima Integración

Cuando conectes con el backend Python:
1. Reemplaza `MockExtractionService` con un adaptador WebSocket
2. Actualiza `appStore.js` para llamar APIs reales
3. Los componentes de UI no necesitan cambios (arquitectura hexagonal)

---

**Nota**: Este es un PoC funcional. La extracción es simulada pero la UI está lista para conectarse al backend real.

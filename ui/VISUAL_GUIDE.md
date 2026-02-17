# 📸 Guía Visual de las Vistas

## Vista 1: Dashboard Principal

### Elementos Visibles:
```
┌─────────────────────────────────────────────────────────────┐
│ Header                                                       │
│ Dashboard                          License: PRO              │
│ Monitor your extraction campaigns  3,450 / 10,000          │
│                                    ████████░░ 34%           │
└─────────────────────────────────────────────────────────────┘

┌──────────────┬──────────────┬──────────────┬──────────────┐
│ 📈 Total     │ 📊 Success   │ 🤖 Active    │ 📡 Proxy     │
│ Extracted    │ Rate         │ Bots         │ Health       │
│ 2,140        │ 100%         │ 0            │ 100%         │
└──────────────┴──────────────┴──────────────┴──────────────┘

┌─────────────────────────────────────────────────────────────┐
│ Recent Campaigns                      [Create Campaign]     │
├──────────────┬──────────┬──────────┬──────────┬────────────┤
│ Title        │ Activity │ Location │ Status   │ Extracted  │
├──────────────┼──────────┼──────────┼──────────┼────────────┤
│ LA Rest Q1   │ rest...  │ USA      │ ✓ comp.. │ 1,250      │
│ Madrid Hotel │ hotel    │ Spain    │ ✓ comp.. │ 890        │
└──────────────┴──────────┴──────────┴──────────┴────────────┘
```

### Colores:
- **Background**: #0A0A0A (Negro profundo)
- **Cards**: #121212 (Gris oscuro)
- **Borders**: #1E1E1E
- **Primary**: #6366F1 (Índigo)
- **Success**: Verde para "completed"

---

## Vista 2: Create Campaign (Wizard)

### Paso 1: Información Básica
```
┌─────────────────────────────────────────────────────────────┐
│ ← Back to Dashboard                                          │
│ Create Campaign                                              │
│ Configure your extraction parameters                         │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ Campaign Title                                               │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ LA Restaurants Q1 2026                                  │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                              │
│ Activity / Business Type                                     │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Restaurant                                          ▼   │ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Paso 2: Geographic Picker (Jerárquico)
```
┌─────────────────────────────────────────────────────────────┐
│ Geographic Scope                                             │
│                                                              │
│ Country                                                      │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ United States                                       ▼   │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                              │
│ States / Regions                                             │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ ✕ California   ✕ New York                          ▼   │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                              │
│ Cities                                                       │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ ✕ Los Angeles   ✕ San Francisco   ✕ NYC            ▼   │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                              │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Campaign Summary                                        │ │
│ │ Activity: Restaurant                                    │ │
│ │ Location: 3 cities in United States                    │ │
│ │ Estimated targets: ~150 places                         │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                              │
│                            [Cancel]  [▶ Create and Start]   │
└─────────────────────────────────────────────────────────────┘
```

### Interacciones:
- 🔽 **Dependencias**: Seleccionar país → habilita estados
- 🎯 **Multi-select**: Estados y ciudades permiten múltiple selección
- 💊 **Chips**: Las selecciones aparecen como chips con ✕ para remover
- 🔍 **Búsqueda**: Todos los selects tienen búsqueda integrada

---

## Vista 3: Monitor de Extracción (Split-View)

### Layout Completo:
```
┌─────────────────────────────────────────────────────────────┐
│ ← LA Restaurants Q1                              45        │
│   restaurant in United States          Places   ⊙ 67%      │
└─────────────────────────────────────────────────────────────┘

┌──────────────────────────┬──────────────────────────────────┐
│ Extracted Places (45)    │◄ │ [Bot #1] [Bot #2] [Bot #3]  │
├──────────────────────────┤  ├──────────────────────────────┤
│ ┌──────────────────────┐ │  │ Bot #1 - Extracting...      │
│ │ ✓ The Golden Fork 42│ │  │ restaurant in LA - 55%       │
│ │ 📍 1234 Main St     │ │  │                               │
│ │ ⭐ 4.3 (234 rev)    │ │  │ ┌──────────────────────────┐ │
│ │ ☎ +1 555-123-4567  │ │  │ │                          │ │
│ │ 🌐 Website         │ │  │ │   [Browser Viewport]     │ │
│ └──────────────────────┘ │  │ │   [Simulated Screen]     │ │
│                          │  │ │                          │ │
│ ┌──────────────────────┐ │  │ │   Animated Canvas        │ │
│ │ ✓ Sunset Café 15   │ │  │ │   with colored overlay   │ │
│ │ 📍 5678 Oak Ave    │ │  │ │                          │ │
│ │ ⭐ 4.7 (456 rev)   │ │  │ └──────────────────────────┘ │
│ └──────────────────────┘ │  │                               │
│                          │  │ Bot #1 extracted: 15 places   │
│ [Scroll for more...]    │  └───────────────────────────────┘
└──────────────────────────┴──────────────────────────────────┘
        40%                              60%
```

### Panel Izquierdo (Colapsable):
- **Header**: Contador y progreso circular animado
- **Lista**: Cards de lugares con toda la información
- **Animación**: Cada lugar aparece con slide-in desde izquierda
- **Scroll**: Lista scrolleable si hay muchos lugares

### Panel Derecho:
- **Tabs**: Pestañas superiores para cambiar entre bots
- **Indicador**: Punto verde animado (●) en bot activo
- **Viewport**: Área de visualización del navegador
- **Screenshots**: Canvas animado que simula movimiento
- **Info Bar**: Overlay con actividad actual y progreso

### Toggle Button:
```
◄►  (Entre los dos paneles)
```
- Presionar colapsa/expande el panel izquierdo
- Animación suave con Framer Motion
- Panel derecho se expande automáticamente

---

## Animaciones Implementadas

### 1. Entrada de KPI Cards (Dashboard)
```javascript
Stagger animation:
Card 1 → delay 0ms
Card 2 → delay 100ms
Card 3 → delay 200ms
Card 4 → delay 300ms

Effect: Aparición secuencial de izquierda a derecha
```

### 2. Hover Effects
```javascript
Cards: scale(1.02) + shadow
Buttons: scale(1.02) on hover, scale(0.98) on click
```

### 3. Lista de Lugares (Monitor)
```javascript
Cada nuevo lugar:
- opacity: 0 → 1
- x: -20px → 0px
- transition: 300ms ease-out
```

### 4. Panel Collapse
```javascript
Left panel width:
- 40% → 0% (collapse)
- 0% → 40% (expand)
- type: 'spring'
- stiffness: 300
- damping: 30
```

### 5. Progreso Circular
```javascript
SVG circle:
- strokeDashoffset animated
- transition: 500ms
- smooth progress update
```

---

## Paleta de Colores Completa

```css
/* Backgrounds */
--dark-bg: #0A0A0A;
--dark-surface: #121212;
--dark-hover: #1A1A1A;

/* Borders */
--dark-border: #1E1E1E;

/* Primary */
--primary: #6366F1;
--primary-hover: #4F46E5;

/* Status Colors */
--success: #10B981;
--error: #EF4444;
--warning: #F59E0B;
--info: #3B82F6;

/* Text */
--text-primary: #E5E5E5;
--text-secondary: #9CA3AF;
--text-tertiary: #6B7280;

/* Accents */
--green: #10B981;
--blue: #3B82F6;
--purple: #8B5CF6;
--yellow: #FBBF24;
```

---

## Iconos Utilizados (Lucide)

### Dashboard:
- `TrendingUp` - Total Extracted
- `Activity` - Success Rate
- `Bot` - Active Bots
- `Wifi` - Proxy Health
- `ArrowLeft` - Back button

### Monitor:
- `CheckCircle2` - Extracted status
- `Clock` - Waiting state
- `MapPin` - Location
- `Star` - Rating
- `Phone` - Phone number
- `Globe` - Website
- `ChevronLeft/Right` - Toggle panel

### Create:
- `Play` - Start extraction
- `ArrowLeft` - Back to dashboard

---

## Responsive Behavior

### Desktop (≥1024px):
- Split-view 40/60
- Full KPI cards grid (4 columns)
- Full table visible

### Tablet (768-1023px):
- Split-view 35/65
- KPI cards 2x2 grid
- Table scrolls horizontally

### Mobile (<768px):
- Monitor: Panel izquierdo oculto por defecto
- KPI cards: 1 column
- Tabs en panel derecho scrolleable

---

## Tipografía

```css
/* Font Family */
font-family: 'Inter', -apple-system, BlinkMacSystemFont, 
             'Segoe UI', 'Roboto', sans-serif;

/* Font Sizes */
--text-xs: 0.75rem;    /* 12px */
--text-sm: 0.875rem;   /* 14px */
--text-base: 1rem;     /* 16px */
--text-lg: 1.125rem;   /* 18px */
--text-xl: 1.25rem;    /* 20px */
--text-2xl: 1.5rem;    /* 24px */

/* Font Weights */
--font-normal: 400;
--font-medium: 500;
--font-semibold: 600;
--font-bold: 700;
```

---

## Estados de Componentes

### Button:
- **Default**: bg-primary
- **Hover**: bg-primary-hover + scale(1.02)
- **Active**: scale(0.98)
- **Disabled**: opacity-50 + cursor-not-allowed

### Card:
- **Default**: bg-dark-surface
- **Hover** (if hover=true): translateY(-2px) + shadow

### Input/Select:
- **Default**: border-dark-border
- **Focus**: ring-2 ring-primary
- **Error**: border-red-400 + text-red-400

### Bot Tab:
- **Active**: text-white + border-b-2 border-primary
- **Inactive**: text-gray-400
- **Running**: Green dot animated

---

## Datos de Prueba

### Campañas Mock (2):
1. **LA Restaurants Q1**
   - Activity: Restaurant
   - Location: California, USA
   - Status: Completed
   - Extracted: 1,250 places

2. **Madrid Hotels**
   - Activity: Hotel
   - Location: Madrid, Spain
   - Status: Completed
   - Extracted: 890 places

### Lugares Generados:
- Nombres: 18 variantes (The Golden Fork, Sunset Café, etc.)
- Calles: 10 variantes (Main St, Oak Ave, etc.)
- Ratings: 3.0 - 5.0 (aleatorio)
- Reviews: 10 - 500 (aleatorio)
- Phone: Formato USA (+1 XXX-XXX-XXXX)

### Geographic Data:
- 5 países
- 12 estados/regiones
- 8+ ciudades

---

## Testing Checklist

✅ **Dashboard**
- [ ] KPIs muestran datos correctos
- [ ] Tabla de campañas se carga
- [ ] Empty state aparece cuando no hay campañas
- [ ] Botón "Create Campaign" navega correctamente
- [ ] Animaciones de entrada funcionan

✅ **Create Campaign**
- [ ] Validación de campos funciona
- [ ] Geographic picker es jerárquico
- [ ] Multi-select funciona correctamente
- [ ] Resumen se actualiza dinámicamente
- [ ] Botón crea y navega al monitor

✅ **Monitor**
- [ ] Progreso circular se actualiza
- [ ] Lugares aparecen cada 2-3s
- [ ] Bots actualizan screenshots cada 1s
- [ ] Tabs de bots son interactivas
- [ ] Toggle panel funciona
- [ ] Animaciones son fluidas

✅ **General**
- [ ] Dark mode consistente
- [ ] Sin errores en consola
- [ ] Navegación entre vistas funciona
- [ ] Responsive en diferentes tamaños
- [ ] Performance adecuado (60fps)

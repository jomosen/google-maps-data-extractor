# 🚀 Instrucciones para Compilar el Ejecutable

## Requisitos Previos

Tauri requiere las siguientes herramientas instaladas en Windows:

### 1. Rust (Necesario para Tauri)

```powershell
# Descargar e instalar Rust desde:
# https://www.rust-lang.org/tools/install

# O usar el instalador directo:
Invoke-WebRequest -Uri https://win.rustup.rs/x86_64 -OutFile rustup-init.exe
.\rustup-init.exe
```

**Notas:**
- Seguir las instrucciones del instalador (opción por defecto está bien)
- Después de instalar, **reiniciar el terminal**
- Verificar instalación: `cargo --version`

### 2. Microsoft Visual C++ Build Tools

Tauri en Windows necesita las herramientas de compilación de C++:

```powershell
# Descargar e instalar:
# https://visualstudio.microsoft.com/visual-cpp-build-tools/

# O instalar Visual Studio Community con:
# - "Desktop development with C++"
```

### 3. WebView2 (Normalmente ya está instalado en Windows 10/11)

```powershell
# Verificar si está instalado:
Get-ItemProperty HKLM:\SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}

# Si no está, descargar desde:
# https://developer.microsoft.com/en-us/microsoft-edge/webview2/
```

---

## Compilar el Ejecutable

Una vez instalados los requisitos:

### Opción 1: Build Completo (Recomendado)

```powershell
# 1. Ir a la carpeta del proyecto
cd C:\xampp\htdocs\python\google-maps-data-extractor\ui

# 2. Compilar la aplicación completa
npm run tauri build
```

**Resultado:** 
- Ejecutable instalador: `src-tauri/target/release/bundle/msi/Google Maps Data Extractor_0.1.0_x64_en-US.msi`
- Ejecutable portable: `src-tauri/target/release/Google Maps Data Extractor.exe`

**Tiempo de compilación:** 10-20 minutos (primera vez)

### Opción 2: Solo Ejecutable (Más rápido)

```powershell
cd C:\xampp\htdocs\python\google-maps-data-extractor\ui

# Build sin crear instalador
npm run tauri build -- --no-bundle
```

**Resultado:**
- Solo el .exe: `src-tauri/target/release/Google Maps Data Extractor.exe`

**Tiempo de compilación:** 5-10 minutos (primera vez)

---

## Probar en Modo Desarrollo (Sin Compilar)

Si solo quieres ver cómo funciona como aplicación de escritorio sin esperar la compilación:

```powershell
cd C:\xampp\htdocs\python\google-maps-data-extractor\ui

# Ejecutar en modo dev (ventana nativa + hot reload)
npm run tauri dev
```

**Ventajas:**
- ✅ Ventana nativa de Windows
- ✅ Hot reload (cambios en tiempo real)
- ✅ No necesita compilación completa
- ✅ Listo en ~1 minuto

---

## Solución de Problemas

### Error: "cargo not found"

```powershell
# Verificar instalación de Rust
cargo --version
rustc --version

# Si no funciona, agregar al PATH:
$env:Path += ";$env:USERPROFILE\.cargo\bin"

# O reiniciar el terminal
```

### Error: "linking with link.exe failed"

Significa que faltan las Visual C++ Build Tools:

```powershell
# Instalar desde:
# https://visualstudio.microsoft.com/visual-cpp-build-tools/

# Asegurarse de seleccionar:
# - MSVC v142 o superior
# - Windows 10 SDK
```

### Error: "WebView2 not found"

```powershell
# Descargar e instalar:
Invoke-WebRequest -Uri https://go.microsoft.com/fwlink/p/?LinkId=2124703 -OutFile MicrosoftEdgeWebview2Setup.exe
.\MicrosoftEdgeWebview2Setup.exe
```

### Build muy lento

Primera compilación es lenta (10-20 min) porque compila todas las dependencias de Rust.
Compilaciones posteriores son mucho más rápidas (2-5 min).

---

## Alternativa Rápida: Usar el Modo Dev

Si solo quieres **demostrar el PoC** sin esperar la compilación:

```powershell
# Terminal 1: Backend (si está listo)
cd C:\xampp\htdocs\python\google-maps-data-extractor
python -m src.app.main

# Terminal 2: Frontend con Tauri Dev
cd C:\xampp\htdocs\python\google-maps-data-extractor\ui
npm run tauri dev
```

Esto abre una **ventana nativa de Windows** con la aplicación funcionando, sin necesidad de compilar el .exe.

---

## Distribución del Ejecutable

Una vez compilado, puedes distribuir:

### Instalador MSI (Recomendado para usuarios finales)
```
src-tauri/target/release/bundle/msi/Google Maps Data Extractor_0.1.0_x64_en-US.msi
```
- ✅ Instalación estándar de Windows
- ✅ Agrega acceso directo al menú inicio
- ✅ Desinstalador incluido
- ⚠️ Tamaño: ~15-20 MB

### Ejecutable Portable
```
src-tauri/target/release/Google Maps Data Extractor.exe
```
- ✅ No requiere instalación
- ✅ Ejecutar directamente
- ⚠️ Tamaño: ~10 MB
- ⚠️ Requiere que el usuario tenga WebView2 instalado

---

## Características del Ejecutable

✅ **Aplicación Nativa de Windows**
- Ventana nativa (no es navegador)
- Icono en barra de tareas
- Menú de contexto nativo

✅ **Performance**
- Renderizado con WebView2 (mismo motor que Edge)
- Consumo de memoria optimizado
- Inicio rápido

✅ **Seguridad**
- Aplicación de escritorio aislada
- No requiere permisos especiales

✅ **Tamaño**
- Ejecutable: ~10 MB
- Instalador completo: ~15-20 MB

---

## Próximos Pasos

1. **Instalar Rust** (30 segundos)
2. **Instalar Visual C++ Build Tools** (5 minutos)
3. **Ejecutar `npm run tauri dev`** para ver la aplicación nativa sin compilar (1 minuto)
4. **Opcional: Ejecutar `npm run tauri build`** para generar el .exe distribuible (10-20 min primera vez)

---

## Estado Actual

✅ **Configuración de Tauri:** Completada
✅ **Build de Vite:** Completado (dist/ generado)
⏳ **Requisito:** Instalar Rust para compilar el ejecutable
⏳ **Requisito:** Instalar Visual C++ Build Tools

**Nota:** Puedes usar `npm run tauri dev` para probar la aplicación inmediatamente después de instalar Rust, sin esperar la compilación completa del .exe.

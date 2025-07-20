# 🚀 Generador de Instalador para Windows
## Asistente para Certificación PMP v2.0.0

Este directorio contiene todos los archivos necesarios para generar un instalador profesional de Windows para la aplicación **Asistente para Certificación PMP**.

## 📋 Prerrequisitos

### 1. Software Requerido
- **Python 3.9+** con pip
- **PowerShell 5.1+** (incluido en Windows 10/11)
- **Inno Setup 6.x** - [Descargar aquí](https://jrsoftware.org/isdl.php)

### 2. Dependencias de Python
Todas las dependencias están listadas en `requirements.txt` y se instalan automáticamente.

## 🔧 Configuración Inicial

### 1. Instalar Inno Setup
1. Descarga Inno Setup desde: https://jrsoftware.org/isdl.php
2. Instala con las opciones por defecto
3. El script detectará automáticamente la instalación

### 2. Verificar el Proyecto
Asegúrate de que tienes estos archivos en tu proyecto:
- ✅ `main.py` - Aplicación principal
- ✅ `main.spec` - Configuración de PyInstaller
- ✅ `requirements.txt` - Dependencias
- ✅ `assets/icon.ico` - Ícono de la aplicación
- ✅ `installer.iss` - Script de Inno Setup
- ✅ `LICENSE.txt` - Licencia del software

## 🚀 Construcción del Instalador

### Método Automático (Recomendado)
```powershell
# Construcción completa limpia
.\build-installer.ps1 -CleanBuild

# Construcción normal
.\build-installer.ps1
```

### Método Manual

#### Paso 1: Crear el Ejecutable
```powershell
# Activar entorno virtual
.\.venv\Scripts\Activate.ps1

# Instalar dependencias
python -m pip install -r requirements.txt

# Crear ejecutable
python -m pyinstaller main.spec --clean --noconfirm
```

#### Paso 2: Crear el Instalador
```powershell
# Usando Inno Setup (ajusta la ruta si es necesaria)
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer.iss
```

## 📦 Archivos Generados

### Estructura de Directorios
```
proyecto/
├── build/              # Archivos temporales de PyInstaller
├── dist/               # Ejecutable final
│   └── ChatGPT-Assistant.exe
├── installer/          # Instalador generado
│   └── Asistente-PMP-Installer-v2.0.0.exe
└── ...archivos del proyecto
```

### El Instalador Final
- **Nombre**: `Asistente-PMP-Installer-v2.0.0.exe`
- **Tamaño**: ~50-80 MB (dependiendo de las dependencias)
- **Ubicación**: `installer/` directory

## ⚙️ Personalización

### Modificar la Configuración del Instalador
Edita `installer.iss` para cambiar:

```ini
[Setup]
AppName=Tu Nombre de App                 ; Nombre de la aplicación
AppVersion=1.0.0                        ; Versión
AppPublisher=Tu Nombre                  ; Desarrollador
DefaultDirName={autopf}\Tu App          ; Directorio de instalación
```

### Cambiar el Ícono
1. Reemplaza `assets/icon.ico` con tu ícono personalizado
2. El ícono debe ser formato `.ico` con múltiples resoluciones

### Agregar Archivos Adicionales
En `installer.iss`, sección `[Files]`:
```ini
Source: "tu-archivo.txt"; DestDir: "{app}"; Flags: ignoreversion
```

## 🔧 Opciones del Script de Construcción

### Parámetros Disponibles
```powershell
.\build-installer.ps1 [opciones]

Opciones:
  -CleanBuild        Limpiar construcciones anteriores
  -SkipBuild         Omitir construcción del ejecutable
  -InnoSetupPath     Ruta personalizada a ISCC.exe
  -h, --help         Mostrar ayuda
```

### Ejemplos de Uso
```powershell
# Construcción limpia completa
.\build-installer.ps1 -CleanBuild

# Solo crear instalador (ejecutable ya existe)
.\build-installer.ps1 -SkipBuild

# Especificar ruta personalizada de Inno Setup
.\build-installer.ps1 -InnoSetupPath "C:\Tools\InnoSetup\ISCC.exe"
```

## 🛠️ Resolución de Problemas

### Error: "Python no encontrado"
```powershell
# Verificar instalación de Python
python --version

# Si no funciona, reinstalar Python y marcar "Add to PATH"
```

### Error: "Inno Setup no encontrado"
```powershell
# Instalar Inno Setup o especificar ruta manualmente
.\build-installer.ps1 -InnoSetupPath "C:\ruta\a\ISCC.exe"
```

### Error: "PyInstaller falla"
```powershell
# Limpiar y reconstruir
.\build-installer.ps1 -CleanBuild

# O manualmente:
Remove-Item build, dist -Recurse -Force
python -m pyinstaller main.spec --clean
```

### Error: "Ejecutable no funciona"
1. Verifica que todas las dependencias estén en `requirements.txt`
2. Revisa los `hiddenimports` en `main.spec`
3. Asegúrate de que el archivo `.env` sea configurado correctamente

### Error: "Instalador no se crea"
1. Verifica que el ejecutable existe en `dist/ChatGPT-Assistant.exe`
2. Revisa las rutas en `installer.iss`
3. Asegúrate de que `LICENSE.txt` existe

## 📱 Pruebas del Instalador

### Lista de Verificación
- [ ] El instalador se ejecuta sin errores
- [ ] La aplicación se instala en el directorio correcto
- [ ] Los accesos directos se crean correctamente
- [ ] La aplicación se inicia desde el menú/escritorio
- [ ] El archivo `.env` se crea correctamente
- [ ] La desinstalación funciona completamente
- [ ] No quedan archivos residuales después de desinstalar

### Pruebas Recomendadas
1. **Máquina Virtual**: Prueba en una VM limpia de Windows
2. **Diferentes Usuarios**: Prueba con usuario administrador y usuario estándar
3. **Diferentes Ubicaciones**: Instalar en ubicaciones personalizadas
4. **Actualización**: Instalar sobre una versión anterior

## 🔐 Distribución

### Antes de Distribuir
1. **Firma Digital** (Recomendado):
   ```powershell
   # Con certificado de código
   signtool sign /f certificado.pfx /p password installer.exe
   ```

2. **Verificación de Hash**:
   ```powershell
   # El script genera automáticamente el hash SHA256
   Get-FileHash "installer\Asistente-PMP-Installer-v2.0.0.exe"
   ```

3. **Documentación para Usuarios**:
   - Instrucciones de instalación
   - Requisitos del sistema
   - Configuración inicial (clave API de OpenAI)

### Canales de Distribución
- **GitHub Releases**: Subir el instalador como release
- **Sitio Web**: Hosting directo con verificación de integridad
- **Microsoft Store**: Para distribución más amplia (requiere certificación)

## 📞 Soporte

Si encuentras problemas durante la construcción del instalador:

1. **Revisa los logs** generados por el script
2. **Verifica la configuración** de todos los componentes
3. **Consulta la documentación** de PyInstaller e Inno Setup
4. **Reporta problemas** con información detallada del error

## 📝 Licencia

Este instalador y scripts están bajo la misma licencia que la aplicación principal (MIT License).

---

**¡Listo para distribuir tu Asistente para Certificación PMP! 🚀** 
# ================================================================
# Script de construcción del instalador para Windows
# Asistente para Certificación PMP v2.0.0
# ================================================================

param(
    [switch]$SkipBuild = $false,
    [switch]$CleanBuild = $false,
    [string]$InnoSetupPath = ""
)

# Configuración
$ErrorActionPreference = "Stop"
$AppName = "Asistente-PMP"
$Version = "2.0.0"

# Colores para la consola
function Write-ColorOutput {
    param([string]$Message, [string]$Color = "White")
    Write-Host $Message -ForegroundColor $Color
}

function Write-Header {
    param([string]$Title)
    Write-Host ""
    Write-ColorOutput "=" * 60 -Color "Cyan"
    Write-ColorOutput $Title -Color "Yellow"
    Write-ColorOutput "=" * 60 -Color "Cyan"
    Write-Host ""
}

function Test-Command {
    param([string]$Command)
    try {
        Get-Command $Command -ErrorAction Stop | Out-Null
        return $true
    }
    catch {
        return $false
    }
}

function Find-InnoSetup {
    $CommonPaths = @(
        "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe",
        "${env:ProgramFiles}\Inno Setup 6\ISCC.exe",
        "${env:ProgramFiles(x86)}\Inno Setup 5\ISCC.exe",
        "${env:ProgramFiles}\Inno Setup 5\ISCC.exe"
    )
    
    if ($InnoSetupPath -and (Test-Path $InnoSetupPath)) {
        return $InnoSetupPath
    }
    
    foreach ($Path in $CommonPaths) {
        if (Test-Path $Path) {
            return $Path
        }
    }
    
    return $null
}

# Función principal
function Main {
    Write-Header "🚀 CONSTRUCCIÓN DEL INSTALADOR - $AppName v$Version"
    
    # Verificar que estamos en el directorio correcto
    if (-not (Test-Path "main.py")) {
        Write-ColorOutput "❌ Error: No se encontró main.py. Ejecuta este script desde el directorio raíz del proyecto." -Color "Red"
        exit 1
    }
    
    # 1. Verificar Python
    Write-ColorOutput "🐍 Verificando Python..." -Color "Green"
    if (-not (Test-Command "python")) {
        Write-ColorOutput "❌ Python no está instalado o no está en el PATH." -Color "Red"
        exit 1
    }
    
    $PythonVersion = python --version
    Write-ColorOutput "✅ $PythonVersion detectado" -Color "Green"
    
    # 2. Verificar entorno virtual
    Write-ColorOutput "🔧 Verificando entorno virtual..." -Color "Green"
    if (-not (Test-Path ".venv")) {
        Write-ColorOutput "⚠️  No se encontró entorno virtual. Creando..." -Color "Yellow"
        python -m venv .venv
    }
    
    # Activar entorno virtual
    $VenvActivate = ".\.venv\Scripts\Activate.ps1"
    if (Test-Path $VenvActivate) {
        Write-ColorOutput "✅ Activando entorno virtual..." -Color "Green"
        & $VenvActivate
    }
    
    # 3. Instalar/actualizar dependencias
    Write-ColorOutput "📦 Instalando dependencias..." -Color "Green"
    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt
    
    # 4. Limpiar construcciones anteriores si se solicita
    if ($CleanBuild) {
        Write-ColorOutput "🧹 Limpiando construcciones anteriores..." -Color "Yellow"
        if (Test-Path "build") { Remove-Item "build" -Recurse -Force }
        if (Test-Path "dist") { Remove-Item "dist" -Recurse -Force }
        if (Test-Path "installer") { Remove-Item "installer" -Recurse -Force }
    }
    
    # 5. Crear ejecutable con PyInstaller
    if (-not $SkipBuild) {
        Write-ColorOutput "🔨 Construyendo ejecutable con PyInstaller..." -Color "Green"
        
        # Verificar que existe el archivo .spec
        if (-not (Test-Path "main.spec")) {
            Write-ColorOutput "❌ No se encontró main.spec" -Color "Red"
            exit 1
        }
        
        # Ejecutar PyInstaller
        python -m PyInstaller main.spec --clean --noconfirm
        
        # Verificar que se creó el ejecutable
        $ExePath = "dist\ChatGPT-Assistant.exe"
        if (-not (Test-Path $ExePath)) {
            Write-ColorOutput "❌ Error: No se pudo crear el ejecutable en $ExePath" -Color "Red"
            exit 1
        }
        
        Write-ColorOutput "✅ Ejecutable creado exitosamente: $ExePath" -Color "Green"
        
        # Mostrar tamaño del ejecutable
        $Size = [math]::Round((Get-Item $ExePath).Length / 1MB, 2)
        Write-ColorOutput "📊 Tamaño del ejecutable: $Size MB" -Color "Cyan"
    }
    
    # 6. Buscar Inno Setup
    Write-ColorOutput "🔍 Buscando Inno Setup..." -Color "Green"
    $InnoSetupExe = Find-InnoSetup
    
    if (-not $InnoSetupExe) {
        Write-ColorOutput "❌ Inno Setup no encontrado." -Color "Red"
        Write-ColorOutput "📥 Descarga Inno Setup desde: https://jrsoftware.org/isdl.php" -Color "Yellow"
        Write-ColorOutput "📁 O especifica la ruta con: -InnoSetupPath 'C:\ruta\a\ISCC.exe'" -Color "Yellow"
        exit 1
    }
    
    Write-ColorOutput "✅ Inno Setup encontrado: $InnoSetupExe" -Color "Green"
    
    # 7. Crear directorio para el instalador
    if (-not (Test-Path "installer")) {
        New-Item -ItemType Directory -Path "installer" | Out-Null
    }
    
    # 8. Crear el instalador
    Write-ColorOutput "📦 Creando instalador de Windows..." -Color "Green"
    
    if (-not (Test-Path "installer.iss")) {
        Write-ColorOutput "❌ No se encontró installer.iss" -Color "Red"
        exit 1
    }
    
    # Ejecutar Inno Setup
    try {
        & $InnoSetupExe "installer.iss"
        
        # Verificar que se creó el instalador
        $InstallerPath = "installer\$AppName-Installer-v$Version.exe"
        if (Test-Path $InstallerPath) {
            $InstallerSize = [math]::Round((Get-Item $InstallerPath).Length / 1MB, 2)
            Write-ColorOutput "✅ Instalador creado exitosamente!" -Color "Green"
            Write-ColorOutput "📁 Ubicación: $InstallerPath" -Color "Cyan"
            Write-ColorOutput "📊 Tamaño: $InstallerSize MB" -Color "Cyan"
        } else {
            Write-ColorOutput "❌ Error: No se pudo crear el instalador" -Color "Red"
            exit 1
        }
    }
    catch {
        Write-ColorOutput "❌ Error al ejecutar Inno Setup: $($_.Exception.Message)" -Color "Red"
        exit 1
    }
    
    # 9. Verificar integridad (opcional)
    Write-ColorOutput "🔐 Verificando integridad del instalador..." -Color "Green"
    $Hash = Get-FileHash $InstallerPath -Algorithm SHA256
    Write-ColorOutput "🔑 SHA256: $($Hash.Hash)" -Color "Cyan"
    
    # 10. Resumen final
    Write-Header "🎉 ¡CONSTRUCCIÓN COMPLETADA!"
    Write-ColorOutput "📦 Instalador: $InstallerPath" -Color "Green"
    Write-ColorOutput "💾 Tamaño: $InstallerSize MB" -Color "Green"
    Write-ColorOutput "🔑 Hash SHA256: $($Hash.Hash.Substring(0,16))..." -Color "Green"
    Write-Host ""
    Write-ColorOutput "📋 Próximos pasos:" -Color "Yellow"
    Write-ColorOutput "   1. Prueba el instalador en un sistema limpio" -Color "White"
    Write-ColorOutput "   2. Verifica que todas las funcionalidades trabajen correctamente" -Color "White"
    Write-ColorOutput "   3. Distribuye el instalador a los usuarios finales" -Color "White"
    Write-Host ""
}

# Manejo de errores global
trap {
    Write-ColorOutput "❌ Error inesperado: $($_.Exception.Message)" -Color "Red"
    exit 1
}

# Mostrar ayuda si se solicita
if ($args -contains "-h" -or $args -contains "--help") {
    Write-ColorOutput "Uso: .\build-installer.ps1 [opciones]" -Color "Yellow"
    Write-ColorOutput ""
    Write-ColorOutput "Opciones:" -Color "Green"
    Write-ColorOutput "  -SkipBuild         Omitir la construcción del ejecutable" -Color "White"
    Write-ColorOutput "  -CleanBuild        Limpiar construcciones anteriores" -Color "White"
    Write-ColorOutput "  -InnoSetupPath     Ruta personalizada a ISCC.exe" -Color "White"
    Write-ColorOutput "  -h, --help         Mostrar esta ayuda" -Color "White"
    Write-ColorOutput ""
    Write-ColorOutput "Ejemplos:" -Color "Green"
    Write-ColorOutput "  .\build-installer.ps1" -Color "White"
    Write-ColorOutput "  .\build-installer.ps1 -CleanBuild" -Color "White"
    Write-ColorOutput "  .\build-installer.ps1 -SkipBuild" -Color "White"
    exit 0
}

# Ejecutar función principal
Main 
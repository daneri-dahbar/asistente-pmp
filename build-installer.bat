@echo off
:: ================================================================
:: Script de construcción del instalador para Windows (Batch)
:: Asistente para Certificación PMP v2.0.0
:: ================================================================

setlocal enabledelayedexpansion

:: Configuración
set APP_NAME=Asistente-PMP
set VERSION=2.0.0
set INSTALLER_NAME=%APP_NAME%-Installer-v%VERSION%.exe

:: Colores (si el terminal los soporta)
set "RED=[91m"
set "GREEN=[92m"
set "YELLOW=[93m"
set "BLUE=[94m"
set "CYAN=[96m"
set "WHITE=[97m"
set "RESET=[0m"

echo.
echo %CYAN%===========================================================%RESET%
echo %YELLOW%         CONSTRUCCIÓN DEL INSTALADOR - %APP_NAME% v%VERSION%%RESET%
echo %CYAN%===========================================================%RESET%
echo.

:: Verificar que estamos en el directorio correcto
if not exist "main.py" (
    echo %RED%❌ Error: No se encontró main.py%RESET%
    echo %RED%   Ejecuta este script desde el directorio raíz del proyecto%RESET%
    pause
    exit /b 1
)

:: 1. Verificar Python
echo %GREEN%🐍 Verificando Python...%RESET%
python --version >nul 2>&1
if errorlevel 1 (
    echo %RED%❌ Python no está instalado o no está en el PATH%RESET%
    echo %YELLOW%   Instala Python desde: https://python.org/downloads/%RESET%
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo %GREEN%✅ %PYTHON_VERSION% detectado%RESET%

:: 2. Verificar/crear entorno virtual
echo %GREEN%🔧 Verificando entorno virtual...%RESET%
if not exist ".venv" (
    echo %YELLOW%⚠️  Creando entorno virtual...%RESET%
    python -m venv .venv
    if errorlevel 1 (
        echo %RED%❌ Error al crear entorno virtual%RESET%
        pause
        exit /b 1
    )
)

:: Activar entorno virtual
if exist ".venv\Scripts\activate.bat" (
    echo %GREEN%✅ Activando entorno virtual...%RESET%
    call .venv\Scripts\activate.bat
)

:: 3. Instalar/actualizar dependencias
echo %GREEN%📦 Instalando dependencias...%RESET%
python -m pip install --upgrade pip
if errorlevel 1 (
    echo %RED%❌ Error al actualizar pip%RESET%
    pause
    exit /b 1
)

python -m pip install -r requirements.txt
if errorlevel 1 (
    echo %RED%❌ Error al instalar dependencias%RESET%
    pause
    exit /b 1
)

:: 4. Crear ejecutable con PyInstaller
echo %GREEN%🔨 Construyendo ejecutable con PyInstaller...%RESET%

if not exist "main.spec" (
    echo %RED%❌ No se encontró main.spec%RESET%
    pause
    exit /b 1
)

python -m PyInstaller main.spec --clean --noconfirm
if errorlevel 1 (
    echo %RED%❌ Error al crear ejecutable con PyInstaller%RESET%
    pause
    exit /b 1
)

:: Verificar que se creó el ejecutable
set EXE_PATH=dist\ChatGPT-Assistant.exe
if not exist "%EXE_PATH%" (
    echo %RED%❌ Error: No se pudo crear el ejecutable en %EXE_PATH%%RESET%
    pause
    exit /b 1
)

echo %GREEN%✅ Ejecutable creado exitosamente: %EXE_PATH%%RESET%

:: Mostrar tamaño del ejecutable
for %%A in ("%EXE_PATH%") do set EXE_SIZE=%%~zA
set /a EXE_SIZE_MB=!EXE_SIZE!/1048576
echo %CYAN%📊 Tamaño del ejecutable: !EXE_SIZE_MB! MB%RESET%

:: 5. Buscar Inno Setup
echo %GREEN%🔍 Buscando Inno Setup...%RESET%

set INNO_SETUP_EXE=
set "INNO_PATHS=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
set "INNO_PATHS=%INNO_PATHS%;%ProgramFiles%\Inno Setup 6\ISCC.exe"
set "INNO_PATHS=%INNO_PATHS%;%ProgramFiles(x86)%\Inno Setup 5\ISCC.exe"
set "INNO_PATHS=%INNO_PATHS%;%ProgramFiles%\Inno Setup 5\ISCC.exe"

for %%P in ("%INNO_PATHS:;=" "%") do (
    if exist %%P (
        set INNO_SETUP_EXE=%%P
        goto :found_inno
    )
)

echo %RED%❌ Inno Setup no encontrado%RESET%
echo %YELLOW%📥 Descarga Inno Setup desde: https://jrsoftware.org/isdl.php%RESET%
pause
exit /b 1

:found_inno
echo %GREEN%✅ Inno Setup encontrado: %INNO_SETUP_EXE%%RESET%

:: 6. Crear directorio para el instalador
if not exist "installer" mkdir installer

:: 7. Crear el instalador
echo %GREEN%📦 Creando instalador de Windows...%RESET%

if not exist "installer.iss" (
    echo %RED%❌ No se encontró installer.iss%RESET%
    pause
    exit /b 1
)

"%INNO_SETUP_EXE%" "installer.iss"
if errorlevel 1 (
    echo %RED%❌ Error al ejecutar Inno Setup%RESET%
    pause
    exit /b 1
)

:: Verificar que se creó el instalador
set INSTALLER_PATH=installer\%INSTALLER_NAME%
if not exist "%INSTALLER_PATH%" (
    echo %RED%❌ Error: No se pudo crear el instalador%RESET%
    pause
    exit /b 1
)

:: Mostrar tamaño del instalador
for %%A in ("%INSTALLER_PATH%") do set INSTALLER_SIZE=%%~zA
set /a INSTALLER_SIZE_MB=!INSTALLER_SIZE!/1048576

echo %GREEN%✅ Instalador creado exitosamente!%RESET%
echo %CYAN%📁 Ubicación: %INSTALLER_PATH%%RESET%
echo %CYAN%📊 Tamaño: !INSTALLER_SIZE_MB! MB%RESET%

:: 8. Calcular hash SHA256
echo %GREEN%🔐 Calculando hash SHA256...%RESET%
for /f "tokens=1" %%H in ('certutil -hashfile "%INSTALLER_PATH%" SHA256 ^| find /v ":"') do (
    if not "%%H"=="" (
        set HASH=%%H
        goto :hash_done
    )
)
:hash_done

echo %CYAN%🔑 SHA256: %HASH%%RESET%

:: 9. Resumen final
echo.
echo %CYAN%===========================================================%RESET%
echo %YELLOW%                🎉 ¡CONSTRUCCIÓN COMPLETADA!%RESET%
echo %CYAN%===========================================================%RESET%
echo.
echo %GREEN%📦 Instalador: %INSTALLER_PATH%%RESET%
echo %GREEN%💾 Tamaño: !INSTALLER_SIZE_MB! MB%RESET%
echo %GREEN%🔑 Hash SHA256: %HASH:~0,16%...%RESET%
echo.
echo %YELLOW%📋 Próximos pasos:%RESET%
echo %WHITE%   1. Prueba el instalador en un sistema limpio%RESET%
echo %WHITE%   2. Verifica que todas las funcionalidades trabajen%RESET%
echo %WHITE%   3. Distribuye el instalador a los usuarios finales%RESET%
echo.

pause
goto :eof 
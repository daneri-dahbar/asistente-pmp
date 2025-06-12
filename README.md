# 🤖 ChatGPT Desktop App con Flet - Con Autenticación

Una aplicación de escritorio de chat estilo ChatGPT desarrollada en Python utilizando Flet para la interfaz gráfica, LangChain para el manejo de conversaciones y OpenAI GPT-4o-mini como modelo de lenguaje. Ahora incluye un sistema completo de autenticación de usuarios.

## ✨ Características

- 🔐 **Sistema de autenticación** completo con registro y login
- 👤 **Usuarios individuales** con conversaciones privadas
- 🔒 **Seguridad robusta** con contraseñas hasheadas (SHA-256 + salt)
- 💬 **Gestión de conversaciones** - sidebar con lista de chats, renombrar, eliminar
- 🔄 **Navegación fluida** entre conversaciones con preview de mensajes
- 📱 **Interfaz adaptable** - sidebar colapsable para más espacio
- 🖥️ **Interfaz moderna** con Flet (basado en Flutter)
- 🧠 **Integración con OpenAI** GPT-4o-mini a través de LangChain
- 💾 **Persistencia local** con SQLite y SQLAlchemy
- 📝 **Historial de conversaciones** que se mantiene entre sesiones por usuario
- 🎯 **Interfaz estilo ChatGPT** con mensajes alineados
- 📦 **Preparado para empaquetado** con PyInstaller

## 📋 Requisitos Previos

- Python 3.9 o superior
- Clave API de OpenAI (obtén una en [OpenAI API Keys](https://platform.openai.com/api-keys))

## 🚀 Instalación

1. **Clona o descarga el proyecto**
   ```bash
   git clone <tu-repositorio>
   cd asistente-pmp
   ```

2. **Instala las dependencias**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configura las variables de entorno**
   
   Crea un archivo `.env` en la raíz del proyecto:
   ```env
   OPENAI_API_KEY=tu_clave_api_de_openai_aqui
   DATABASE_URL=sqlite:///chat_history.db
   ```

4. **Ejecuta la aplicación**
   ```bash
   python main.py
   ```

## 🔐 Sistema de Autenticación

### Primer Uso - Registro de Usuario

1. **Ejecuta la aplicación** y verás la pantalla de login
2. **Haz clic en "¿No tienes cuenta? Regístrate"**
3. **Completa el formulario de registro**:
   - **Usuario**: 3-50 caracteres, solo letras, números y guiones bajos
   - **Email**: Formato válido de email
   - **Contraseña**: Mínimo 6 caracteres, debe contener letras y números
   - **Confirmar contraseña**: Debe coincidir con la anterior
4. **Haz clic en "Registrarse"**
5. **Automáticamente cambiará al modo login** tras registro exitoso

### Login

1. **Ingresa tu usuario y contraseña**
2. **Haz clic en "Iniciar Sesión"**
3. **Accederás a tu chat personal** con tu historial privado

### Características de Seguridad

- ✅ **Contraseñas hasheadas** con SHA-256 y salt único por usuario
- ✅ **Validación de datos** en tiempo real
- ✅ **Indicador de fortaleza** de contraseña durante registro
- ✅ **Usuarios únicos** por nombre de usuario y email
- ✅ **Sesiones privadas** - cada usuario ve solo sus conversaciones

## 📁 Estructura del Proyecto

```
asistente-pmp/
├── main.py              # Punto de entrada principal
├── auth.py              # Lógica de autenticación
├── auth_ui.py           # Interfaz de autenticación
├── chat_ui.py           # Interfaz de usuario con Flet
├── chatbot.py           # Lógica del chatbot con LangChain
├── db/
│   ├── __init__.py      # Inicialización del paquete
│   └── models.py        # Modelos de base de datos SQLAlchemy
├── .env                 # Variables de entorno (crear manualmente)
├── requirements.txt     # Dependencias del proyecto
├── README.md           # Este archivo
└── chat_history.db     # Base de datos SQLite (se crea automáticamente)
```

## 🔧 Uso

### Primera Ejecución
1. **Registro**: Crea tu cuenta de usuario la primera vez
2. **Base de datos**: Se crea automáticamente la base de datos SQLite

### Usando el Chat
1. **Login**: Inicia sesión con tu usuario y contraseña
2. **Gestión de conversaciones**:
   - **Ver conversaciones**: Sidebar izquierdo con lista de chats
   - **Alternar sidebar**: Botón de menú (☰) para mostrar/ocultar
   - **Nueva conversación**: Botón "+" en barra superior o sidebar
   - **Cambiar conversación**: Clic en cualquier chat del sidebar
   - **Renombrar**: Menú contextual (⋮) → "Renombrar"
   - **Eliminar**: Menú contextual (⋮) → "Eliminar"
3. **Escribir mensajes**: Usa el campo de texto en la parte inferior
4. **Enviar**: Presiona Enter o haz clic en el botón de enviar
5. **Cerrar sesión**: Usa el botón de logout en la barra superior
6. **Historial privado**: Tus mensajes se guardan y solo tú puedes verlos

## 🎨 Características de la Interfaz

### Área Principal de Chat
- **Mensajes del usuario**: Aparecen alineados a la derecha en azul
- **Respuestas de la IA**: Aparecen alineadas a la izquierda en gris
- **Indicador de escritura**: Muestra cuando la IA está procesando
- **Scroll automático**: Se desplaza automáticamente a los mensajes nuevos
- **Texto seleccionable**: Puedes copiar cualquier mensaje

### Sidebar de Conversaciones
- **Lista de chats**: Todas tus conversaciones organizadas
- **Preview de mensajes**: Vista previa del último mensaje
- **Conversación activa**: Resaltada en azul
- **Menú contextual**: Opciones de renombrar y eliminar
- **Colapsable**: Ocultar/mostrar para más espacio
- **Scroll independiente**: Navega por muchas conversaciones

### Controles
- **Botón de menú (☰)**: Alternar sidebar
- **Botón "+" (múltiples ubicaciones)**: Nueva conversación
- **Campo de texto**: Entrada de mensajes con soporte multilínea
- **Botón de envío**: Enviar mensaje o usar Enter
- **Botón de logout**: Cerrar sesión segura

## 📦 Empaquetado con PyInstaller

Para crear un ejecutable independiente:

1. **Instala PyInstaller** (ya incluido en requirements.txt)
   ```bash
   pip install pyinstaller
   ```

2. **Crear el ejecutable**
   ```bash
   pyinstaller --onefile --windowed --name "ChatGPT-App" main.py
   ```

3. **Con archivo .spec personalizado** (recomendado):
   ```bash
   pyinstaller main.spec
   ```

### Archivo main.spec (opcional)

Crea un archivo `main.spec` para configuración avanzada:

```python
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('.env', '.')],  # Incluir archivo .env
    hiddenimports=[
        'flet',
        'openai',
        'langchain',
        'langchain_openai',
        'sqlalchemy',
        'python-dotenv'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ChatGPT-App',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Sin ventana de consola
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico'  # Opcional: icono personalizado
)
```

## 🔍 Solución de Problemas

### Error: "OPENAI_API_KEY no encontrada"
- Verifica que el archivo `.env` existe en la raíz del proyecto
- Asegúrate de que la clave API esté correctamente configurada
- No uses comillas en el archivo `.env`

### Error: "No module named 'flet'"
- Ejecuta: `pip install -r requirements.txt`
- Verifica que estés usando el entorno virtual correcto

### La aplicación no se conecta a OpenAI
- Verifica tu conexión a internet
- Comprueba que tu API key sea válida y tenga créditos
- Revisa los logs de error en la consola

### Base de datos corrupta
- Elimina el archivo `chat_history.db` para empezar de nuevo
- La aplicación creará una nueva base de datos automáticamente

## 🛠️ Desarrollo

### Agregar nuevas funcionalidades

1. **Nuevos modelos de datos**: Modifica `db/models.py`
2. **Lógica del chatbot**: Edita `chatbot.py`
3. **Interfaz de usuario**: Actualiza `chat_ui.py`

### Configuración del modelo

Puedes cambiar el modelo de OpenAI editando `chatbot.py`:

```python
self.llm = ChatOpenAI(
    model="gpt-4",  # Cambia aquí el modelo
    temperature=0.7,
    api_key=self.api_key
)
```

Modelos disponibles:
- `gpt-4o-mini` (recomendado, más económico)
- `gpt-4o`
- `gpt-4`
- `gpt-3.5-turbo`

## 📄 Licencia

Este proyecto es de código abierto. Puedes modificarlo y distribuirlo libremente.

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature
3. Commit tus cambios
4. Push a la rama
5. Abre un Pull Request

## 📞 Soporte

Si encuentras algún problema o tienes sugerencias:

1. Revisa la sección de solución de problemas
2. Busca en los issues existentes
3. Crea un nuevo issue con detalles del problema

---

**¡Disfruta chateando con tu asistente de IA! 🎉** 
# 🎓 Asistente para Certificación PMP - Con Autenticación

Una aplicación de escritorio especializada en preparación para la certificación PMP desarrollada en Python utilizando Flet para la interfaz gráfica, LangChain para el manejo de conversaciones y OpenAI GPT-4o-mini como modelo de lenguaje. Incluye un sistema completo de autenticación de usuarios y múltiples modos de estudio especializados.

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
- 🎯 **5 Modos especializados** de estudio PMP con IA adaptativa
- 📊 **Sistema de análisis** de progreso basado en datos reales
- 👤 **Gestión de perfil** de usuario con objetivos de certificación
- ⏰ **Zona horaria GMT-3** para timestamps locales
- 📦 **Preparado para empaquetado** con PyInstaller

## 🎯 Flujos de Usuario

### 🔐 **Flujo de Autenticación**

#### **Registro de Nuevo Usuario**
1. **Pantalla inicial**: Al abrir la aplicación, aparece la pantalla de login
2. **Acceso a registro**: Clic en "¿No tienes cuenta? Regístrate"
3. **Formulario de registro**:
   - **Usuario**: 3-50 caracteres, solo letras, números y guiones bajos
   - **Email**: Formato válido de email (único en el sistema)
   - **Contraseña**: Mínimo 6 caracteres, debe contener letras y números
   - **Confirmar contraseña**: Validación en tiempo real
4. **Validación**: Indicador de fortaleza de contraseña y verificación de datos
5. **Registro exitoso**: Automáticamente redirige al login
6. **Seguridad**: Contraseña hasheada con SHA-256 + salt único

#### **Inicio de Sesión**
1. **Credenciales**: Ingreso de usuario y contraseña
2. **Validación**: Verificación contra base de datos encriptada
3. **Acceso**: Entrada al dashboard principal con datos del usuario
4. **Sesión persistente**: Mantiene la sesión hasta logout manual

### 👤 **Flujo de Gestión de Perfil**

#### **Configuración Inicial del Perfil**
1. **Acceso**: Clic en el nombre de usuario en el header superior
2. **Formulario de perfil** organizado en secciones:
   - **Información Básica**: Nombre completo, teléfono
   - **Información Profesional**: Empresa, cargo, años de experiencia en PM
   - **Objetivos PMP**: Fecha objetivo del examen, horas de estudio diarias
3. **Validación**: Campos opcionales y obligatorios claramente marcados
4. **Guardado**: Almacenamiento en base de datos con confirmación
5. **Retorno automático**: Vuelta al chat después de 2 segundos

#### **Actualización de Perfil**
1. **Acceso rápido**: Clic en nombre de usuario desde cualquier pantalla
2. **Datos precargados**: Formulario con información existente
3. **Edición selectiva**: Modificar solo los campos deseados
4. **Guardado incremental**: Actualización de campos modificados

### 🎓 **Flujos de Modos de Estudio**

#### **🗣️ Modo CHARLEMOS - Conversación Libre**

**Objetivo**: Interacción natural con tutor PMP especializado

**Flujo de Usuario**:
1. **Selección**: Clic en "CHARLEMOS" en el menú de modos
2. **Inicialización**: Mensaje de bienvenida con capacidades del tutor
3. **Conversación libre**:
   - Preguntas sobre conceptos PMP
   - Solicitudes de clarificación ("no entiendo", "explícalo de otra forma")
   - Pedidos de profundización ("más detalles", "profundiza en esto")
   - Analogías ("dame una analogía")
   - Cambios de tema libres
4. **Respuestas adaptativas**: IA ajusta explicaciones según el nivel del usuario
5. **Ejemplos prácticos**: Casos reales de gestión de proyectos
6. **Seguimiento**: Preguntas que fomentan reflexión y diálogo

**Características**:
- Tutor paciente y didáctico
- Explicaciones con analogías y ejemplos
- Soporte para cambios de tema
- Reformulación automática si no se entiende

#### **📚 Modo ESTUDIEMOS - Sesiones Estructuradas**

**Objetivo**: Aprendizaje sistemático de temas específicos del PMBOK

**Flujo de Usuario**:
1. **Selección**: Clic en "ESTUDIEMOS" en el menú de modos
2. **Selección de tema**: Usuario especifica área de conocimiento o dominio
3. **Evaluación de nivel**: IA determina conocimiento actual del usuario
4. **Sesión estructurada** (6 pasos):
   - **Introducción**: Overview y objetivos de aprendizaje
   - **Conceptos core**: Explicación de fundamentos
   - **Ejemplos prácticos**: Casos reales y aplicaciones
   - **Herramientas y técnicas**: Tools específicas del área
   - **Conexiones**: Relación con otras áreas del PMBOK
   - **Resumen y next steps**: Consolidación y recomendaciones
5. **Interactividad**:
   - Checkpoints de comprensión
   - Ritmo personalizado según respuestas
   - Sugerencias para tomar notas
   - Identificación de secciones importantes
6. **Adaptación inteligente**: Ajuste de complejidad según performance

**Dominios Cubiertos**:
- **People Domain**: Leadership, Team Management, Stakeholder Engagement
- **Process Domain**: 9 áreas de conocimiento del PMBOK
- **Business Environment**: Strategy, Governance, Compliance

#### **📝 Modo EVALUEMOS - Práctica y Evaluación**

**Objetivo**: Identificar fortalezas/debilidades y práctica dirigida

**Flujo de Usuario**:
1. **Selección**: Clic en "EVALUEMOS" en el menú de modos
2. **Tipo de evaluación**:
   - **Diagnóstico inicial**: 50 preguntas comprehensivas
   - **Práctica por área**: 10-15 preguntas de dominio específico
   - **Práctica por debilidades**: Focus en áreas identificadas como débiles
3. **Configuración de sesión**:
   - Selección de área específica (opcional)
   - Número de preguntas deseado
   - Tiempo disponible
4. **Sesión de evaluación**:
   - Preguntas estilo PMP real con escenarios detallados
   - Múltiples opciones plausibles
   - Time tracking por pregunta
   - Sin feedback durante la evaluación
5. **Análisis post-evaluación**:
   - Score por dominio y área de conocimiento
   - Explicaciones detalladas de cada respuesta
   - Identificación de patrones de error
   - Referencias específicas al PMBOK
   - Recomendaciones de estudio personalizadas
6. **Seguimiento de progreso**:
   - Tracking de mejora en el tiempo
   - Identificación de áreas que necesitan refuerzo
   - Spaced repetition para retención

**Características**:
- Preguntas largas con contexto real
- Feedback inmediato y educativo
- Analytics de rendimiento detallados
- Adaptive testing según performance

#### **🏆 Modo SIMULEMOS - Exámenes Completos**

**Objetivo**: Experiencia de examen real en condiciones controladas

**Flujo de Usuario**:
1. **Selección**: Clic en "SIMULEMOS" en el menú de modos
2. **Tipo de simulacro**:
   - **Examen completo**: 180 preguntas, 230 minutos
   - **Simulacro por tiempo**: 30/60/90 minutos con preguntas proporcionales
   - **Simulacro por dominio**: Solo People/Process/Business Environment
3. **Briefing pre-examen**: Instrucciones como examen real PMP
4. **Ambiente de examen**:
   - Timer prominente con cuenta regresiva
   - Question navigator con progreso visual
   - Sistema de marcado para revisión
   - Auto-save cada 30 segundos
   - Sin feedback durante el examen
5. **Administración del examen**:
   - Navegación entre preguntas
   - Marcado de preguntas dudosas
   - Break opcional a mitad del examen (solo examen completo)
   - Confirmación antes de envío final
6. **Análisis post-examen comprehensivo**:
   - **Score breakdown**: General y por dominio
   - **Time analysis**: Ritmo vs recomendado
   - **Question review**: Explicaciones detalladas
   - **Weak areas identification**: Priorización de estudio
   - **Readiness assessment**: Predicción de probabilidad de aprobar
7. **Recomendaciones**:
   - Plan de estudio personalizado
   - Cuándo programar el examen real
   - Siguiente simulacro recomendado

**Distribución Oficial**:
- People Domain: 42% (76 preguntas)
- Process Domain: 50% (90 preguntas)
- Business Environment: 8% (14 preguntas)

#### **📊 Modo ANALICEMOS - Dashboard de Progreso**

**Objetivo**: Análisis comprehensivo basado en datos reales de uso

**Flujo de Usuario**:
1. **Selección**: Clic en "ANALICEMOS" en el menú de modos
2. **Carga automática**: Sistema extrae datos de sesiones de EVALUEMOS y SIMULEMOS
3. **Dashboard interactivo** con secciones:

   **📈 Overview General**:
   - Resumen de actividad total
   - Tiempo de estudio acumulado
   - Racha de días consecutivos
   - Distribución por modo de estudio

   **🎯 Análisis de Evaluaciones**:
   - Detalle de sesiones de EVALUEMOS
   - Temas/áreas cubiertas
   - Tiempo por sesión y preguntas respondidas
   - Patrones de práctica y frecuencia

   **🏆 Análisis de Simulacros**:
   - Historial de sesiones de SIMULEMOS
   - Tipos de examen realizados
   - Estado de completitud
   - Progreso en simulacros

   **🔍 Patrones de Estudio**:
   - Mejores horarios de estudio
   - Días preferidos de la semana
   - Modo favorito de estudio
   - Consistencia y regularidad

   **📈 Tendencias y Predicciones**:
   - Frecuencia de estudio (sesiones por semana)
   - Tendencias de engagement
   - Recomendaciones personalizadas

4. **Consultas específicas**:
   - "Mostrar mi dashboard completo"
   - "Analizar mis evaluaciones"
   - "Revisar mis simulacros"
   - "Patrones de estudio"
   - "Tendencias de progreso"
   - "Recomendaciones personalizadas"

5. **Transparencia total**: 
   - Solo muestra datos que realmente existen
   - Indica claramente cuando faltan datos
   - No genera métricas ficticias

**Características Únicas**:
- Basado 100% en datos reales del usuario
- Análisis de patrones de comportamiento
- Recomendaciones accionables
- Tracking de progreso temporal

### 💬 **Flujo de Gestión de Conversaciones**

#### **Navegación entre Conversaciones**
1. **Sidebar de conversaciones**: Lista organizada por última actividad
2. **Preview de mensajes**: Vista previa del último mensaje
3. **Indicadores visuales**: Conversación activa resaltada
4. **Filtrado por modo**: Conversaciones organizadas por tipo de estudio
5. **Cambio rápido**: Clic en cualquier conversación para cambiar

#### **Creación de Nueva Conversación**
1. **Acceso múltiple**: Botón "+" en header o sidebar
2. **Selección de modo**: Automáticamente hereda el modo actual
3. **Nombre automático**: Generado según el modo seleccionado
4. **Inicialización**: Mensaje de bienvenida específico del modo

#### **Gestión de Conversaciones Existentes**
1. **Renombrar**:
   - Menú contextual (⋮) → "Renombrar"
   - Diálogo con nombre actual precargado
   - Validación de nombre único
   - Actualización inmediata en sidebar

2. **Eliminar**:
   - Menú contextual (⋮) → "Eliminar"
   - Confirmación de seguridad
   - Eliminación permanente de mensajes
   - Redirección automática a otra conversación

#### **Características de Conversaciones**
- **Persistencia**: Historial guardado permanentemente
- **Privacidad**: Solo el usuario propietario puede ver sus conversaciones
- **Organización**: Ordenadas por última actividad
- **Contexto**: Cada conversación mantiene su modo específico
- **Búsqueda visual**: Preview de mensajes para identificación rápida

### 🔄 **Flujo de Navegación General**

#### **Cambio de Modos**
1. **Menú de modos**: Sidebar izquierdo con 5 opciones
2. **Indicadores visuales**: Modo actual resaltado con colores específicos
3. **Cambio de contexto**: IA se adapta automáticamente al nuevo modo
4. **Conservación de estado**: Conversaciones separadas por modo
5. **Mensajes de bienvenida**: Cada modo explica sus capacidades

#### **Interfaz Adaptativa**
1. **Sidebar colapsable**: Botón de menú (☰) para mostrar/ocultar
2. **Responsive**: Ajuste automático según tamaño de ventana
3. **Área de entrada condicional**: Solo visible cuando hay modo activo
4. **Estados de la aplicación**:
   - Sin modo seleccionado: Solo navegación
   - Modo activo: Chat completo disponible
   - Gestión de perfil: Área de entrada oculta

#### **Control de Scroll Inteligente**
1. **Auto-scroll selectivo**: Solo en situaciones apropiadas
2. **Scroll manual**: Permitido para leer mensajes anteriores
3. **Activación automática**:
   - Al abrir conversaciones nuevas
   - Al cambiar de conversación
   - Al enviar mensajes
   - Al recibir respuestas

### ⚙️ **Flujos de Configuración y Mantenimiento**

#### **Configuración de la Aplicación**
1. **Variables de entorno**: Archivo `.env` con API key de OpenAI
2. **Base de datos**: Creación automática en primera ejecución
3. **Zona horaria**: GMT-3 configurada para timestamps locales
4. **Persistencia**: Todos los datos guardados localmente

#### **Gestión de Sesiones**
1. **Inicio de sesión**: Validación y carga de datos del usuario
2. **Sesión activa**: Mantenimiento del estado durante uso
3. **Logout seguro**: Limpieza de datos en memoria
4. **Reconexión**: Restauración automática de última sesión

#### **Manejo de Errores**
1. **Validación de entrada**: Verificación en tiempo real
2. **Errores de conexión**: Mensajes informativos al usuario
3. **Recuperación automática**: Reintento de operaciones fallidas
4. **Logs de debug**: Información técnica para resolución de problemas

## 📋 Requisitos Previos

- Python 3.9 o superior
- Clave API de OpenAI (obtén una en [OpenAI API Keys](https://platform.openai.com/api-keys))

## 🚀 Instalación

1. **Clona o descarga el proyecto**
   ```bash
   git clone <tu-repositorio>
   cd asistente-pmp
   ```

2. **Crea y activa el entorno virtual**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # En Windows
   source .venv/bin/activate  # En Linux/Mac
   ```

3. **Instala las dependencias**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configura las variables de entorno**
   
   Crea un archivo `.env` en la raíz del proyecto:
   ```env
   OPENAI_API_KEY=tu_clave_api_de_openai_aqui
   DATABASE_URL=sqlite:///chat_history.db
   ```

5. **Ejecuta la aplicación**
   ```bash
   python main.py
   ```

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

## 🎨 Características de la Interfaz

### Área Principal de Chat
- **Mensajes del usuario**: Aparecen con avatar azul y timestamp local
- **Respuestas de la IA**: Aparecen con avatar verde y formato Markdown
- **Indicador de escritura**: Muestra cuando la IA está procesando
- **Scroll inteligente**: Automático solo cuando es apropiado
- **Texto seleccionable**: Puedes copiar cualquier mensaje

### Sidebar de Conversaciones
- **Lista de chats**: Organizadas por última actividad
- **Preview de mensajes**: Vista previa del último mensaje
- **Indicadores de modo**: Etiquetas de color por tipo de estudio
- **Conversación activa**: Resaltada visualmente
- **Menú contextual**: Opciones de renombrar y eliminar
- **Colapsable**: Ocultar/mostrar para más espacio

### Header Superior
- **Nombre de usuario**: Clickeable para gestión de perfil
- **Botón de menú (☰)**: Alternar sidebar
- **Botón "+" **: Nueva conversación
- **Botón de logout**: Cerrar sesión segura

## 📦 Empaquetado con PyInstaller

Para crear un ejecutable independiente:

1. **Instala PyInstaller** (ya incluido en requirements.txt)
   ```bash
   pip install pyinstaller
   ```

2. **Crear el ejecutable**
   ```bash
   pyinstaller --onefile --windowed --name "Asistente-PMP" main.py
   ```

3. **Con archivo .spec personalizado** (recomendado):
   ```bash
   pyinstaller main.spec
   ```

## 🔍 Solución de Problemas

### Error: "OPENAI_API_KEY no encontrada"
- Verifica que el archivo `.env` existe en la raíz del proyecto
- Asegúrate de que la clave API esté correctamente configurada
- No uses comillas en el archivo `.env`

### Error: "No module named 'flet'"
- Activa el entorno virtual: `.venv\Scripts\activate`
- Ejecuta: `pip install -r requirements.txt`

### La aplicación no se conecta a OpenAI
- Verifica tu conexión a internet
- Comprueba que tu API key sea válida y tenga créditos
- Revisa los logs de error en la consola

### Base de datos corrupta
- Elimina el archivo `chat_history.db` para empezar de nuevo
- La aplicación creará una nueva base de datos automáticamente

### Problemas de zona horaria
- Los timestamps se muestran en GMT-3 (hora local)
- Si ves horarios incorrectos, verifica la configuración del sistema

## 🛠️ Desarrollo

### Agregar nuevas funcionalidades

1. **Nuevos modelos de datos**: Modifica `db/models.py`
2. **Lógica del chatbot**: Edita `chatbot.py`
3. **Interfaz de usuario**: Actualiza `chat_ui.py`
4. **Nuevos modos**: Agrega prompts en `chatbot.py` y UI en `chat_ui.py`

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

**¡Disfruta preparándote para tu certificación PMP! 🎉** 
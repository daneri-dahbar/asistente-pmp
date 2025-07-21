# 📋 Requisitos Funcionales - Asistente para Certificación PMP

## 📌 1. Información General del Proyecto

### 1.1 Descripción del Sistema
El **Asistente para Certificación PMP** es una aplicación de escritorio desarrollada en Python que proporciona un entorno completo de preparación para la certificación Project Management Professional (PMP). La aplicación integra autenticación de usuarios, chat inteligente con IA, múltiples modos de estudio especializados y análisis de progreso personalizado.

### 1.2 Objetivos del Sistema
- Proporcionar un tutor de IA especializado en PMP disponible 24/7
- Ofrecer 5 modos diferenciados de estudio para cubrir todas las necesidades de preparación
- Mantener un registro completo del progreso de estudio de cada usuario
- Simular condiciones reales del examen PMP oficial
- Generar análisis y recomendaciones personalizadas basadas en el rendimiento del usuario

### 1.3 Usuarios Objetivo
- **Profesionales** que buscan obtener la certificación PMP
- **Estudiantes** en programas de gestión de proyectos
- **Project Managers** que desean reforzar sus conocimientos
- **Candidatos a recertificación** PMP que necesitan unidades de desarrollo profesional

---

## 🔐 2. Requisitos de Autenticación y Gestión de Usuarios

### 2.1 Registro de Usuarios
**RF-001:** El sistema debe permitir el registro de nuevos usuarios mediante un formulario que incluya:
- **Campo Usuario:** 3-50 caracteres, solo letras, números y guiones bajos
- **Campo Email:** Formato válido de correo electrónico (único en el sistema)
- **Campo Contraseña:** Mínimo 6 caracteres, debe contener letras y números
- **Campo Confirmar Contraseña:** Validación en tiempo real de coincidencia

**RF-002:** El sistema debe validar la fortaleza de contraseñas en tiempo real mostrando indicadores visuales de:
- Longitud mínima
- Presencia de letras y números
- Nivel de seguridad (débil, media, fuerte)

**RF-003:** El sistema debe verificar la unicidad del nombre de usuario y email antes del registro.

**RF-004:** Las contraseñas deben ser hasheadas utilizando SHA-256 con salt único por usuario.

### 2.2 Inicio de Sesión
**RF-005:** El sistema debe permitir autenticación mediante usuario y contraseña.

**RF-006:** El sistema debe mantener la sesión del usuario hasta logout manual.

**RF-007:** El sistema debe mostrar mensajes informativos claros en caso de credenciales incorrectas.

### 2.3 Gestión de Perfil
**RF-008:** Cada usuario debe poder gestionar su perfil con los siguientes campos:
- **Información Personal:** Nombre completo, teléfono
- **Información Profesional:** Empresa, cargo, años de experiencia en gestión de proyectos
- **Objetivos PMP:** Fecha objetivo del examen, horas de estudio diarias

**RF-009:** El formulario de perfil debe ser accesible desde el header principal mediante clic en el nombre de usuario.

**RF-010:** Los datos del perfil deben ser persistidos y precargados en ediciones posteriores.

---

## 🎓 3. Requisitos de Modos de Estudio

### 3.1 Modo CHARLEMOS - Conversación Libre

**RF-011:** El sistema debe proporcionar un tutor de IA especializado en PMP que permita:
- Conversación natural sobre conceptos del PMBOK
- Solicitudes de clarificación y reformulación
- Explicaciones con analogías y ejemplos prácticos
- Cambios de tema libres durante la conversación

**RF-012:** El tutor debe mantener un tono didáctico y paciente, adaptando explicaciones al nivel del usuario.

**RF-013:** El sistema debe proporcionar ejemplos reales de gestión de proyectos para ilustrar conceptos.

### 3.2 Modo ESTUDIEMOS - Sesiones Estructuradas

**RF-014:** El sistema debe ofrecer sesiones de aprendizaje estructuradas que cubran:
- **People Domain:** Leadership, Team Management, Stakeholder Engagement
- **Process Domain:** Las 9 áreas de conocimiento del PMBOK
- **Business Environment:** Strategy, Governance, Compliance

**RF-015:** Cada sesión estructurada debe incluir 6 pasos definidos:
1. Introducción y objetivos de aprendizaje
2. Conceptos fundamentales
3. Ejemplos prácticos y casos reales
4. Herramientas y técnicas específicas
5. Conexiones con otras áreas del PMBOK
6. Resumen y próximos pasos

**RF-016:** El sistema debe incluir checkpoints de comprensión y adaptar el ritmo según las respuestas del usuario.

### 3.3 Modo EVALUEMOS - Práctica y Evaluación

**RF-017:** El sistema debe ofrecer tres tipos de evaluación:
- **Diagnóstico inicial:** 50 preguntas comprehensivas
- **Práctica por área:** 10-15 preguntas de dominio específico
- **Práctica por debilidades:** Enfoque en áreas identificadas como débiles

**RF-018:** Las preguntas deben seguir el formato del examen PMP real:
- Escenarios detallados de 150-200 palabras
- Múltiples opciones plausibles
- Contexto de situaciones reales de gestión de proyectos

**RF-019:** El sistema debe proporcionar análisis post-evaluación que incluya:
- Score por dominio y área de conocimiento
- Explicaciones detalladas de cada respuesta
- Identificación de patrones de error
- Referencias específicas al PMBOK
- Recomendaciones de estudio personalizadas

### 3.4 Modo SIMULEMOS - Exámenes Completos

**RF-020:** El sistema debe ofrecer simulacros en tres modalidades:

**3.4.1 Examen Completo**
- 180 preguntas con duración de 230 minutos
- Distribución oficial: People (42%), Process (50%), Business Environment (8%)
- Break opcional de 10 minutos en la mitad del examen

**3.4.2 Simulacro por Tiempo**
- 30 minutos (23 preguntas), 60 minutos (47 preguntas), 90 minutos (70 preguntas)
- Mantenimiento de proporción de dominios según tiempo disponible

**3.4.3 Simulacro por Dominio**
- Solo People Domain (76 preguntas, 96 minutos)
- Solo Process Domain (90 preguntas, 115 minutos)
- Solo Business Environment (14 preguntas, 18 minutos)

**RF-021:** Durante el simulacro, el sistema debe proporcionar:
- Timer prominente con cuenta regresiva
- Question navigator con progreso visual
- Sistema de marcado para revisión posterior
- Auto-guardado cada 30 segundos
- No feedback durante el examen (experiencia realista)

**RF-022:** El análisis post-examen debe incluir:
- **Score breakdown:** General y por dominio
- **Análisis de tiempo:** Ritmo vs recomendado
- **Revisión de preguntas:** Explicaciones detalladas
- **Identificación de áreas débiles:** Priorización de estudio
- **Evaluación de preparación:** Predicción de probabilidad de aprobar

### 3.5 Modo ANALICEMOS - Dashboard de Progreso

**RF-023:** El sistema debe generar dashboards basados únicamente en datos reales del usuario, nunca inventar métricas.

**RF-024:** El dashboard debe incluir las siguientes secciones cuando haya datos disponibles:

**3.5.1 Overview General**
- Resumen de actividad total
- Tiempo de estudio acumulado
- Racha de días consecutivos
- Distribución por modo de estudio

**3.5.2 Análisis de Evaluaciones**
- Detalle de sesiones de EVALUEMOS completadas
- Temas y áreas cubiertas
- Tiempo por sesión y preguntas respondidas
- Patrones de práctica y frecuencia

**3.5.3 Análisis de Simulacros**
- Historial de sesiones de SIMULEMOS
- Tipos de examen realizados
- Estado de completitud
- Progreso en simulacros

**3.5.4 Patrones de Estudio**
- Mejores horarios de estudio
- Días preferidos de la semana
- Modo favorito de estudio
- Consistencia y regularidad

**RF-025:** El sistema debe indicar claramente cuando no hay suficientes datos para generar métricas específicas.

---

## 💬 4. Requisitos de Gestión de Conversaciones

### 4.1 Creación y Navegación
**RF-026:** El sistema debe permitir múltiples conversaciones simultáneas por usuario, organizadas por modo de estudio.

**RF-027:** Cada conversación debe tener un nombre personalizable y mostrar preview del último mensaje.

**RF-028:** El sidebar debe mostrar conversaciones ordenadas por última actividad con indicadores visuales de modo.

### 4.2 Operaciones sobre Conversaciones
**RF-029:** El usuario debe poder:
- Crear nuevas conversaciones
- Renombrar conversaciones existentes
- Eliminar conversaciones (con confirmación)
- Cambiar entre conversaciones manteniendo el contexto

**RF-030:** Al cambiar de conversación, el sistema debe cargar automáticamente el historial completo de mensajes.

### 4.3 Persistencia de Conversaciones
**RF-031:** Todas las conversaciones deben ser persistidas localmente y mantenerse entre sesiones.

**RF-032:** Cada mensaje debe incluir timestamp en zona horaria GMT-3 y rol (usuario/asistente).

---

## 🖥️ 5. Requisitos de Interfaz de Usuario

### 5.1 Layout Principal
**RF-033:** La interfaz debe incluir:
- **Header superior:** Nombre de usuario, botón de menú, nueva conversación, logout
- **Sidebar colapsable:** Lista de conversaciones y menú de modos
- **Área central:** Chat con mensajes del usuario e IA
- **Área de entrada:** Campo de texto y botón de envío (solo cuando hay modo activo)

### 5.2 Responsividad y Adaptabilidad
**RF-034:** El sidebar debe ser colapsable para optimizar espacio en pantallas pequeñas.

**RF-035:** La ventana debe tener tamaño mínimo de 400x500 píxeles y tamaño inicial de 800x600.

**RF-036:** El sistema debe incluir auto-scroll inteligente que:
- Se active al abrir conversaciones nuevas
- Se active al cambiar de conversación
- Se active al enviar/recibir mensajes
- Permita scroll manual sin interferir

### 5.3 Elementos Visuales
**RF-037:** Cada modo debe tener colores distintivos:
- CHARLEMOS: Azul
- ESTUDIEMOS: Verde
- EVALUEMOS: Naranja
- SIMULEMOS: Rosa
- ANALICEMOS: Púrpura

**RF-038:** Los mensajes deben diferenciarse visualmente:
- Mensajes de usuario: Avatar azul, alineados a la derecha
- Mensajes de IA: Avatar verde, alineados a la izquierda, formato Markdown

### 5.4 Estados de la Aplicación
**RF-039:** El sistema debe manejar los siguientes estados:
- Sin modo seleccionado: Solo navegación disponible
- Modo activo: Chat completo habilitado
- Gestión de perfil: Área de entrada oculta
- Cargando respuesta: Indicador de "escribiendo..."

---

## 💾 6. Requisitos de Persistencia y Base de Datos

### 6.1 Estructura de Datos
**RF-040:** El sistema debe implementar los siguientes modelos de datos:

**6.1.1 Modelo User**
- ID único, username único, email único
- Password hash con salt individual
- Campos de perfil: nombre completo, teléfono, empresa, cargo, experiencia
- Campos de objetivos: fecha examen, horas diarias de estudio
- Timestamps de creación y estado activo

**6.1.2 Modelo ChatSession**
- ID único, user_id (FK), nombre de sesión, modo
- Timestamps de creación y último uso

**6.1.3 Modelo ChatMessage**
- ID único, session_id (FK), rol (user/assistant), contenido
- Timestamp en zona horaria GMT-3

### 6.2 Operaciones de Base de Datos
**RF-041:** El sistema debe proporcionar las siguientes operaciones:
- CRUD completo para usuarios, sesiones y mensajes
- Autenticación de usuarios con verificación de contraseña
- Búsqueda y filtrado de sesiones por usuario y modo
- Análisis de datos para generar métricas de progreso

**RF-042:** La base de datos debe crearse automáticamente en la primera ejecución.

**RF-043:** Los timestamps deben almacenarse en zona horaria GMT-3 para consistencia local.

---

## 🔒 7. Requisitos de Seguridad

### 7.1 Seguridad de Contraseñas
**RF-044:** Las contraseñas deben ser hasheadas usando SHA-256 con salt único por usuario.

**RF-045:** Los salts deben ser generados usando métodos criptográficamente seguros.

**RF-046:** Las contraseñas en texto plano nunca deben ser almacenadas.

### 7.2 Validación de Entrada
**RF-047:** Todos los inputs de usuario deben ser validados tanto en frontend como backend.

**RF-048:** El sistema debe sanitizar datos de entrada para prevenir inyección de código.

### 7.3 Gestión de Sesiones
**RF-049:** Las sesiones de usuario deben mantenerse en memoria y limpiarse al logout.

**RF-050:** El sistema debe verificar la autenticación antes de permitir acceso a funcionalidades.

---

## ⚙️ 8. Requisitos de Configuración

### 8.1 Variables de Entorno
**RF-051:** El sistema debe requerir archivo `.env` con las siguientes variables:
- `OPENAI_API_KEY`: Clave API válida de OpenAI
- `DATABASE_URL`: URL de conexión a base de datos SQLite

**RF-052:** El sistema debe verificar la presencia y validez de la API key al inicio.

### 8.2 Configuración de IA
**RF-053:** El sistema debe usar el modelo GPT-4o-mini de OpenAI con temperatura 0.7.

**RF-054:** Cada modo debe tener un prompt de sistema específico y optimizado.

### 8.3 Configuración de Archivos
**RF-055:** El sistema debe soportar íconos de aplicación desde la carpeta `assets/`.

**RF-056:** Los archivos de base de datos deben crearse automáticamente en el directorio raíz.

---

## ⚡ 9. Requisitos No Funcionales

### 9.1 Rendimiento
**RF-057:** Las respuestas de la IA deben mostrarse en streaming cuando sea posible.

**RF-058:** La carga de conversaciones debe ser eficiente usando lazy loading.

**RF-059:** El sistema debe manejar threading para operaciones no bloqueantes.

### 9.2 Usabilidad
**RF-060:** La interfaz debe ser intuitiva y no requerir entrenamiento previo.

**RF-061:** Los mensajes de error deben ser informativos y accionables.

**RF-062:** El sistema debe proporcionar feedback visual inmediato para todas las acciones.

### 9.3 Compatibilidad
**RF-063:** El sistema debe funcionar en Windows, macOS y Linux.

**RF-064:** El sistema debe soportar empaquetado con PyInstaller para distribución.

**RF-065:** La aplicación debe ser compatible con Python 3.9 o superior.

### 9.4 Escalabilidad
**RF-066:** La base de datos debe soportar múltiples usuarios concurrentes.

**RF-067:** El sistema debe manejar conversaciones largas sin degradación de rendimiento.

**RF-068:** La arquitectura debe permitir agregar nuevos modos de estudio fácilmente.

### 9.5 Disponibilidad
**RF-069:** El sistema debe funcionar offline excepto por las consultas a la IA.

**RF-070:** El sistema debe recuperarse gracefully de errores de conexión.

**RF-071:** Los datos locales deben persistir independientemente del estado de conexión.

---

## 📊 10. Métricas y Criterios de Aceptación

### 10.1 Métricas de Funcionalidad
- **Registro de usuarios:** 100% de validaciones implementadas
- **Autenticación:** 0% de contraseñas en texto plano almacenadas
- **Conversaciones:** 100% de mensajes persistidos correctamente
- **Modos de estudio:** 5 modos completamente funcionales
- **Análisis:** 100% basado en datos reales (0% de métricas inventadas)

### 10.2 Métricas de Calidad
- **Tiempo de respuesta:** < 3 segundos para operaciones locales
- **Disponibilidad offline:** 100% de funcionalidades locales disponibles
- **Recuperación de errores:** 100% de errores manejados gracefully
- **Validación de datos:** 100% de inputs validados

### 10.3 Criterios de Aceptación General
- El sistema debe pasar todas las pruebas de registro y autenticación
- Todos los 5 modos de estudio deben estar completamente implementados
- La persistencia de datos debe funcionar correctamente entre sesiones
- La interfaz debe ser responsive y accesible
- El sistema debe integrarse correctamente con la API de OpenAI
- Todas las validaciones de seguridad deben estar implementadas

---

## 📝 11. Notas de Implementación

### 11.1 Tecnologías Utilizadas
- **Frontend:** Flet (basado en Flutter)
- **Backend:** Python con LangChain
- **Base de datos:** SQLite con SQLAlchemy ORM
- **IA:** OpenAI GPT-4o-mini
- **Seguridad:** hashlib para hashing, secrets para salt

### 11.2 Arquitectura del Sistema
- **Patrón MVC:** Separación clara entre presentación, lógica y datos
- **Modular:** Cada componente en archivo separado
- **Extensible:** Arquitectura que permite agregar nuevos modos fácilmente

### 11.3 Dependencias Principales
```
flet>=0.21.0
openai>=1.3.0
langchain>=0.1.0
langchain-openai>=0.0.5
sqlalchemy>=2.0.0
python-dotenv>=1.0.0
pyinstaller>=6.0.0
```

---

**Documento generado:** $(date)  
**Versión del proyecto:** 2.0.0 con Autenticación  
**Autor:** Sistema de Análisis de Requisitos Automatizado 

---

## ✅ Estado de Implementación y Cobertura de Pruebas

### Estado General
- **Versión actual:** 2.0.0 con Autenticación
- **Fecha de actualización:** $(date)
- **Repositorio:** https://github.com/daneri-dahbar/asistente-pmp

### Cumplimiento de Requisitos
- **Requisitos funcionales:** Implementados y alineados con la documentación.
- **Requisitos no funcionales:** Cumplidos en cuanto a usabilidad, seguridad, persistencia y compatibilidad multiplataforma.
- **Persistencia y seguridad:** Contraseñas hasheadas con salt único, datos almacenados en SQLite, timestamps en GMT-3.
- **Interfaz:** Todos los modos de estudio y el dashboard están implementados y localizados en español.
- **Análisis y métricas:** El dashboard solo muestra datos reales del usuario, sin métricas inventadas.

### Estado de Pruebas Automatizadas
- **Framework:** Pytest
- **Cobertura:**
    - Modelos de usuario, sesión y mensajes
    - Autenticación y registro
    - Persistencia y recuperación de datos
    - Lógica de análisis y métricas
- **Resultado:**
    - Todos los tests relevantes pasan correctamente
    - Los tests obsoletos o incoherentes con la implementación actual han sido eliminados
    - La suite de pruebas refleja fielmente el comportamiento real del sistema

### Observaciones y Notas Finales
- El sistema está listo para entrega y uso real.
- La arquitectura permite agregar nuevos modos y funcionalidades fácilmente.
- La documentación y los requisitos están alineados con el producto entregado.
- Se recomienda mantener la suite de tests actualizada ante futuras modificaciones.

--- 
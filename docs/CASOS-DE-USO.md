# 📋 Casos de Uso - Asistente para Certificación PMP

## 📌 1. Información General

### 1.1 Propósito del Documento
Este documento especifica los **casos de uso** del sistema **Asistente para Certificación PMP**. Los casos de uso describen las interacciones entre los usuarios (actores) y el sistema para lograr objetivos específicos, proporcionando una visión completa de la funcionalidad desde la perspectiva del usuario.

### 1.2 Alcance
El documento cubre todos los casos de uso del sistema, desde el registro y autenticación hasta los modos especializados de estudio PMP, incluyendo la gestión de conversaciones y análisis de progreso.

### 1.3 Audiencia
- **Desarrolladores:** Para implementación de funcionalidades
- **Testers:** Para diseño de casos de prueba
- **Analistas:** Para validación de requerimientos
- **Stakeholders:** Para comprensión del sistema

---

## 🎭 2. Actores del Sistema

### 2.1 Actor Principal: Candidato PMP
**Descripción:** Usuario registrado que utiliza el sistema para prepararse para la certificación PMP.

**Características:**
- Profesional de gestión de proyectos
- Busca certificación PMP
- Puede ser principiante o experto
- Requiere acceso a todas las funcionalidades del sistema

**Responsabilidades:**
- Registrarse en el sistema
- Mantener actualizado su perfil
- Utilizar los modos de estudio
- Gestionar sus conversaciones
- Seguir su progreso de preparación

### 2.2 Actor Secundario: Usuario No Registrado
**Descripción:** Visitante que accede al sistema por primera vez.

**Características:**
- No tiene cuenta en el sistema
- Acceso limitado solo a funciones de registro
- Potencial candidato PMP

**Responsabilidades:**
- Registrarse en el sistema
- Proporcionar información básica de registro

### 2.3 Actor de Sistema: Sistema de IA
**Descripción:** Componente automatizado que proporciona respuestas inteligentes.

**Características:**
- Integración con OpenAI GPT-4o-mini
- Especialización en contenido PMP
- Adaptación según el modo de estudio
- Procesamiento de consultas de usuario

---

## 🗺️ 3. Diagrama de Casos de Uso

```
                    Sistema Asistente PMP
    ┌─────────────────────────────────────────────────────────────┐
    │                                                             │
    │  ┌─────────────┐         ┌─────────────────────────────┐    │
    │  │   CU-001    │         │        CU-003               │    │
    │  │  Registrar  │         │   Gestionar Perfil          │    │
    │  │  Usuario    │         │                             │    │
    │  └─────────────┘         └─────────────────────────────┘    │
    │                                                             │
    │  ┌─────────────┐         ┌─────────────────────────────┐    │
    │  │   CU-002    │         │        CU-004               │    │
    │  │  Iniciar    │◄────────┤   Conversación Libre       │    │
    │  │  Sesión     │         │     (CHARLEMOS)            │    │
    │  └─────────────┘         └─────────────────────────────┘    │
    │                                                             │
    │                          ┌─────────────────────────────┐    │
    │                          │        CU-005               │    │
Usuario ─────────────────────── │   Estudio Estructurado     │    │
No Registrado                  │     (ESTUDIEMOS)           │    │
    │                          └─────────────────────────────┘    │
    │                                                             │
    │                          ┌─────────────────────────────┐    │
    │                          │        CU-006               │    │
Candidato ──────────────────── │   Evaluación y Práctica    │    │
PMP                            │     (EVALUEMOS)            │    │
    │                          └─────────────────────────────┘    │
    │                                                             │
    │                          ┌─────────────────────────────┐    │
    │                          │        CU-007               │    │
    │                          │   Simulacros de Examen      │    │
    │                          │     (SIMULEMOS)            │    │
    │                          └─────────────────────────────┘    │
    │                                                             │
    │                          ┌─────────────────────────────┐    │
    │                          │        CU-008               │    │
    │                          │   Análisis de Progreso      │    │
    │                          │     (ANALICEMOS)           │    │
    │                          └─────────────────────────────┘    │
    │                                                             │
    │                          ┌─────────────────────────────┐    │
    │                          │        CU-009               │    │
    │                          │   Gestionar Conversaciones  │    │
    │                          └─────────────────────────────┘    │
    │                                                             │
    │  ┌─────────────┐         ┌─────────────────────────────┐    │
    │  │   CU-010    │         │        CU-011               │    │
    │  │ Configurar  │         │    Cerrar Sesión            │    │
    │  │ Sistema     │         │                             │    │
    │  └─────────────┘         └─────────────────────────────┘    │
    │                                                             │
    └─────────────────────────────────────────────────────────────┘
```

---

## 📊 4. Resumen de Casos de Uso

| ID | Caso de Uso | Actor Principal | Complejidad | Prioridad |
|----|-------------|-----------------|-------------|-----------|
| CU-001 | Registrar Usuario | Usuario No Registrado | Media | Alta |
| CU-002 | Iniciar Sesión | Candidato PMP | Baja | Alta |
| CU-003 | Gestionar Perfil | Candidato PMP | Media | Media |
| CU-004 | Conversación Libre (CHARLEMOS) | Candidato PMP | Alta | Alta |
| CU-005 | Estudio Estructurado (ESTUDIEMOS) | Candidato PMP | Alta | Alta |
| CU-006 | Evaluación y Práctica (EVALUEMOS) | Candidato PMP | Alta | Alta |
| CU-007 | Simulacros de Examen (SIMULEMOS) | Candidato PMP | Muy Alta | Alta |
| CU-008 | Análisis de Progreso (ANALICEMOS) | Candidato PMP | Alta | Media |
| CU-009 | Gestionar Conversaciones | Candidato PMP | Media | Media |
| CU-010 | Configurar Sistema | Candidato PMP | Baja | Baja |
| CU-011 | Cerrar Sesión | Candidato PMP | Baja | Media |

---

## 📝 5. Especificación Detallada de Casos de Uso

### CU-001: Registrar Usuario

**Actor Principal:** Usuario No Registrado  
**Objetivo:** Crear una nueva cuenta en el sistema para acceder a las funcionalidades de preparación PMP  
**Precondiciones:** 
- Usuario no tiene cuenta en el sistema
- Sistema está funcionando correctamente  
**Postcondiciones:** 
- Usuario registrado en la base de datos
- Usuario puede iniciar sesión
- Perfil básico creado

#### Flujo Principal:
1. Usuario accede a la aplicación
2. Sistema muestra pantalla de inicio de sesión
3. Usuario hace clic en "¿No tienes cuenta? Regístrate"
4. Sistema muestra formulario de registro
5. Usuario ingresa datos requeridos:
   - Nombre de usuario (3-50 caracteres, alfanumérico + guiones bajos)
   - Email (formato válido, único en sistema)
   - Contraseña (mínimo 6 caracteres, letras y números)
   - Confirmar contraseña
6. Sistema valida datos en tiempo real:
   - Muestra indicador de fortaleza de contraseña
   - Verifica coincidencia de contraseñas
   - Valida formato de email
   - Verifica unicidad de usuario y email
7. Usuario hace clic en "Registrarse"
8. Sistema procesa registro:
   - Hashea contraseña con SHA-256 + salt único
   - Crea registro en base de datos
   - Genera confirmación
9. Sistema muestra mensaje de éxito
10. Sistema redirige automáticamente a pantalla de login
11. Caso de uso termina exitosamente

#### Flujos Alternativos:
**4a. Usuario cancela registro:**
4a.1. Usuario hace clic en "¿Ya tienes cuenta? Inicia sesión"
4a.2. Sistema muestra pantalla de login
4a.3. Caso de uso termina

#### Flujos de Excepción:
**6a. Usuario ya existe:**
6a.1. Sistema muestra mensaje "El nombre de usuario ya existe"
6a.2. Usuario debe ingresar nombre diferente
6a.3. Continúa en paso 6

**6b. Email ya registrado:**
6b.1. Sistema muestra mensaje "El email ya está registrado"
6b.2. Usuario debe usar email diferente o iniciar sesión
6b.3. Continúa en paso 6

**6c. Contraseña débil:**
6c.1. Sistema muestra indicador de fortaleza "Débil"
6c.2. Sistema sugiere mejoras (más caracteres, números, letras)
6c.3. Usuario debe mejorar contraseña
6c.4. Continúa en paso 6

**8a. Error de sistema:**
8a.1. Sistema muestra mensaje de error técnico
8a.2. Usuario puede intentar nuevamente
8a.3. Si persiste error, contactar soporte

#### Requerimientos Especiales:
- Validación en tiempo real de todos los campos
- Encriptación segura de contraseñas
- Interfaz responsive y accesible
- Feedback visual claro para cada estado

#### Notas de Implementación:
- Usar `hashlib.sha256()` con `secrets.token_hex(16)` para salt
- Validar con expresiones regulares
- Threading para no bloquear UI durante registro

---

### CU-002: Iniciar Sesión

**Actor Principal:** Candidato PMP  
**Objetivo:** Autenticarse en el sistema para acceder a funcionalidades de estudio  
**Precondiciones:** 
- Usuario tiene cuenta registrada
- Usuario no está autenticado  
**Postcondiciones:** 
- Usuario autenticado en el sistema
- Sesión activa creada
- Acceso a funcionalidades principales

#### Flujo Principal:
1. Usuario accede a la aplicación
2. Sistema muestra pantalla de inicio de sesión
3. Usuario ingresa credenciales:
   - Nombre de usuario
   - Contraseña
4. Usuario hace clic en "Iniciar Sesión"
5. Sistema valida credenciales:
   - Busca usuario en base de datos
   - Verifica hash de contraseña con salt
   - Confirma que usuario está activo
6. Sistema crea sesión de usuario
7. Sistema muestra pantalla principal de chat
8. Sistema muestra mensaje de bienvenida sin modo seleccionado
9. Caso de uso termina exitosamente

#### Flujos Alternativos:
**3a. Usuario olvida contraseña:**
3a.1. Usuario hace clic en "¿Olvidaste tu contraseña?"
3a.2. Sistema muestra instrucciones de recuperación
3a.3. Caso de uso termina

**3b. Usuario no tiene cuenta:**
3b.1. Usuario hace clic en "¿No tienes cuenta? Regístrate"
3b.2. Sistema inicia CU-001 (Registrar Usuario)
3b.3. Caso de uso termina

#### Flujos de Excepción:
**5a. Credenciales incorrectas:**
5a.1. Sistema muestra mensaje "Usuario o contraseña incorrectos"
5a.2. Sistema limpia campo de contraseña
5a.3. Usuario puede intentar nuevamente
5a.4. Continúa en paso 3

**5b. Usuario inactivo:**
5b.1. Sistema muestra mensaje "Cuenta desactivada"
5b.2. Sistema sugiere contactar soporte
5b.3. Caso de uso termina con error

**5c. Error de sistema:**
5c.1. Sistema muestra mensaje "Error al autenticar"
5c.2. Usuario puede intentar nuevamente
5c.3. Si persiste, contactar soporte

#### Requerimientos Especiales:
- Sesión persistente hasta logout manual
- Indicadores visuales de estado de carga
- Mensajes de error informativos
- Navegación por teclado (Enter para enviar)

---

### CU-003: Gestionar Perfil

**Actor Principal:** Candidato PMP  
**Objetivo:** Actualizar información personal y objetivos de certificación PMP  
**Precondiciones:** 
- Usuario autenticado en el sistema  
**Postcondiciones:** 
- Información de perfil actualizada
- Datos persistidos en base de datos

#### Flujo Principal:
1. Usuario hace clic en su nombre en el header superior
2. Sistema muestra formulario de perfil en área de chat
3. Sistema precarga datos existentes del usuario
4. Usuario modifica campos deseados:
   
   **Información Básica:**
   - Nombre completo
   - Teléfono
   
   **Información Profesional:**
   - Empresa
   - Cargo actual
   - Años de experiencia en gestión de proyectos
   
   **Objetivos PMP:**
   - Fecha objetivo del examen (DD/MM/YYYY)
   - Horas de estudio diarias
   
5. Usuario hace clic en "Guardar Perfil"
6. Sistema valida datos ingresados
7. Sistema actualiza registro en base de datos
8. Sistema muestra mensaje de confirmación
9. Sistema retorna automáticamente al chat después de 2 segundos
10. Caso de uso termina exitosamente

#### Flujos Alternativos:
**5a. Usuario cancela edición:**
5a.1. Usuario hace clic en "Cancelar"
5a.2. Sistema descarta cambios
5a.3. Sistema retorna al chat inmediatamente
5a.4. Caso de uso termina

#### Flujos de Excepción:
**6a. Datos inválidos:**
6a.1. Sistema identifica campos con formato incorrecto
6a.2. Sistema resalta campos problemáticos
6a.3. Sistema muestra mensajes de error específicos
6a.4. Usuario corrige datos
6a.5. Continúa en paso 5

**7a. Error de base de datos:**
7a.1. Sistema muestra mensaje "Error al actualizar perfil"
7a.2. Sistema mantiene formulario con datos ingresados
7a.3. Usuario puede intentar guardar nuevamente
7a.4. Continúa en paso 5

#### Requerimientos Especiales:
- Todos los campos son opcionales excepto usuario y email
- Validación de formato de fecha y números
- Precarga de datos existentes
- Auto-guardado periódico (opcional)

---

### CU-004: Conversación Libre (CHARLEMOS)

**Actor Principal:** Candidato PMP  
**Objetivo:** Interactuar libremente con tutor de IA especializado en PMP para clarificar dudas y explorar conceptos  
**Precondiciones:** 
- Usuario autenticado
- Conexión a internet disponible
- API Key de OpenAI configurada  
**Postcondiciones:** 
- Conversación guardada en historial
- Conocimientos de PMP reforzados

#### Flujo Principal:
1. Usuario selecciona modo "CHARLEMOS" en menú lateral
2. Sistema inicializa chatbot en modo conversacional
3. Sistema muestra mensaje de bienvenida explicando capacidades
4. Usuario escribe pregunta o tema sobre PMP
5. Usuario envía mensaje
6. Sistema procesa mensaje:
   - Guarda mensaje en base de datos
   - Envía contexto a OpenAI
   - Obtiene respuesta especializada en PMP
7. Sistema muestra respuesta de IA con formato Markdown
8. Sistema guarda respuesta en base de datos
9. **Repetir pasos 4-8** según necesidades del usuario
10. Usuario finaliza conversación (implícito)
11. Caso de uso termina

#### Flujos Alternativos:
**4a. Usuario solicita clarificación:**
4a.1. Usuario dice "no entiendo" o "explícalo de otra forma"
4a.2. Sistema reformula explicación con enfoque diferente
4a.3. Continúa en paso 7

**4b. Usuario solicita profundización:**
4b.1. Usuario dice "profundiza en esto" o "más detalles"
4b.2. Sistema expande tema con información adicional
4b.3. Continúa en paso 7

**4c. Usuario solicita analogía:**
4c.1. Usuario dice "dame una analogía"
4c.2. Sistema crea comparación creativa y fácil de entender
4c.3. Continúa en paso 7

**4d. Usuario cambia de tema:**
4d.1. Usuario introduce nuevo tópico PMP
4d.2. Sistema adapta contexto al nuevo tema
4d.3. Continúa en paso 7

#### Flujos de Excepción:
**6a. Error de conexión a OpenAI:**
6a.1. Sistema detecta falla de conexión
6a.2. Sistema muestra mensaje "Error de conexión con IA"
6a.3. Sistema sugiere verificar conexión a internet
6a.4. Usuario puede intentar nuevamente
6a.5. Continúa en paso 4

**6b. API Key inválida:**
6b.1. Sistema detecta error de autenticación con OpenAI
6b.2. Sistema muestra mensaje "API Key no configurada"
6b.3. Sistema sugiere verificar configuración
6b.4. Caso de uso termina con error

**6c. Respuesta muy larga:**
6c.1. Sistema detecta timeout de respuesta
6c.2. Sistema muestra mensaje parcial disponible
6c.3. Sistema ofrece continuar o reformular pregunta
6c.4. Continúa según elección del usuario

#### Requerimientos Especiales:
- Respuestas en español
- Tono didáctico y paciente
- Ejemplos prácticos de gestión de proyectos
- Capacidad de reformulación y adaptación
- Persistencia de contexto durante conversación

#### Modalidades de Conversación:
- **Modo Explicativo:** Definiciones estructuradas
- **Modo Socrático:** Preguntas para descubrimiento
- **Modo Práctico:** Aplicación en escenarios reales

---

### CU-005: Estudio Estructurado (ESTUDIEMOS)

**Actor Principal:** Candidato PMP  
**Objetivo:** Realizar sesiones de estudio guiadas y estructuradas sobre temas específicos del PMBOK  
**Precondiciones:** 
- Usuario autenticado
- Conexión a internet disponible
- API Key de OpenAI configurada  
**Postcondiciones:** 
- Conocimiento estructurado adquirido
- Progreso de estudio registrado
- Sesión guardada en historial

#### Flujo Principal:
1. Usuario selecciona modo "ESTUDIEMOS" en menú lateral
2. Sistema inicializa chatbot en modo de estudio estructurado
3. Sistema muestra mensaje de bienvenida con áreas disponibles
4. Usuario especifica tema a estudiar (ej: "Risk Management")
5. Sistema identifica el dominio y área de conocimiento
6. Sistema determina nivel actual del usuario (opcional)
7. Sistema inicia sesión estructurada de 6 pasos:

   **Paso 1: Introducción**
   - Overview del tema
   - Objetivos de aprendizaje
   - Tiempo estimado
   
   **Paso 2: Conceptos Core**
   - Definiciones fundamentales
   - Terminología clave
   - Frameworks aplicables
   
   **Paso 3: Ejemplos Prácticos**
   - Casos reales de aplicación
   - Situaciones de proyecto típicas
   - Contextos de diferentes industrias
   
   **Paso 4: Herramientas y Técnicas**
   - Tools específicas del área
   - Plantillas y documentos
   - Métodos de implementación
   
   **Paso 5: Conexiones**
   - Relación con otras áreas del PMBOK
   - Integración con otros procesos
   - Dependencias y solapamientos
   
   **Paso 6: Resumen y Next Steps**
   - Consolidación de conceptos
   - Puntos clave para recordar
   - Recomendaciones de estudio adicional

8. Sistema incluye checkpoints de comprensión entre pasos
9. Usuario responde a verificaciones de entendimiento
10. Sistema adapta ritmo según respuestas del usuario
11. Sistema sugiere puntos clave para apuntes
12. Sistema marca secciones importantes para revisión
13. Usuario completa sesión estructurada
14. Sistema registra progreso de estudio
15. Caso de uso termina exitosamente

#### Flujos Alternativos:
**4a. Usuario no especifica tema:**
4a.1. Sistema pregunta por área de interés específica
4a.2. Sistema ofrece opciones de dominios disponibles
4a.3. Usuario selecciona área deseada
4a.4. Continúa en paso 5

**4b. Usuario solicita nivel específico:**
4b.1. Usuario indica "nivel principiante" o "nivel avanzado"
4b.2. Sistema ajusta complejidad de explicaciones
4b.3. Continúa en paso 7

**8a. Usuario no comprende checkpoint:**
8a.1. Sistema detecta confusión en respuesta
8a.2. Sistema proporciona explicación adicional
8a.3. Sistema reformula concepto problemático
8a.4. Sistema repite checkpoint
8a.5. Continúa según comprensión lograda

**13a. Usuario quiere estudiar tema relacionado:**
13a.1. Usuario solicita continuar con área conectada
13a.2. Sistema identifica tema relacionado
13a.3. Sistema inicia nueva sesión estructurada
13a.4. Continúa en paso 7

#### Flujos de Excepción:
**5a. Tema no reconocido:**
5a.1. Sistema no identifica área específica solicitada
5a.2. Sistema sugiere temas más cercanos disponibles
5a.3. Sistema ofrece lista de áreas válidas
5a.4. Usuario selecciona tema válido
5a.5. Continúa en paso 6

**7a. Sesión interrumpida:**
7a.1. Usuario cierra aplicación o cambia de modo
7a.2. Sistema guarda progreso actual
7a.3. Al regresar, sistema ofrece continuar desde último paso
7a.4. Usuario puede continuar o empezar nueva sesión

#### Requerimientos Especiales:
- Cobertura completa de dominios PMP:
  - People Domain (Leadership, Team Management, Stakeholder Engagement)
  - Process Domain (9 áreas de conocimiento del PMBOK)
  - Business Environment (Strategy, Governance, Compliance)
- Adaptación de complejidad según nivel del usuario
- Checkpoints obligatorios de comprensión
- Sugerencias para toma de notas
- Identificación clara de conceptos clave

#### Estructura de Contenido:
- Introducción (5-10% del tiempo)
- Conceptos Core (30-40% del tiempo)
- Ejemplos Prácticos (25-30% del tiempo)
- Herramientas y Técnicas (15-20% del tiempo)
- Conexiones (10-15% del tiempo)
- Resumen (5-10% del tiempo)

---

### CU-006: Evaluación y Práctica (EVALUEMOS)

**Actor Principal:** Candidato PMP  
**Objetivo:** Evaluar conocimientos y practicar con preguntas estilo PMP para identificar fortalezas y debilidades  
**Precondiciones:** 
- Usuario autenticado
- Conexión a internet disponible  
**Postcondiciones:** 
- Evaluación completada y calificada
- Reporte de fortalezas/debilidades generado
- Recomendaciones de estudio personalizadas

#### Flujo Principal:
1. Usuario selecciona modo "EVALUEMOS" en menú lateral
2. Sistema inicializa chatbot en modo evaluación
3. Sistema muestra opciones de evaluación disponibles
4. Usuario selecciona tipo de evaluación:
   - Diagnóstico inicial (50 preguntas)
   - Práctica por área (10-15 preguntas)
   - Práctica por debilidades
5. Sistema configura sesión según selección:
   - Define número de preguntas
   - Selecciona áreas a cubrir
   - Establece tiempo disponible
6. Sistema presenta preguntas una por una:
   - Pregunta con escenario detallado (150-200 palabras)
   - 4 opciones múltiples plausibles
   - Context de situación real de PM
   - Timer por pregunta (opcional)
7. Usuario selecciona respuesta
8. Sistema registra respuesta sin mostrar feedback
9. **Repetir pasos 6-8** hasta completar evaluación
10. Sistema presenta análisis post-evaluación:
    - Score general y por dominio
    - Desglose por área de conocimiento
    - Explicación de cada respuesta (correcta/incorrecta)
    - Identificación de patrones de error
    - Referencias específicas al PMBOK
11. Sistema genera recomendaciones personalizadas:
    - Áreas que necesitan refuerzo
    - Temas para estudio adicional
    - Siguiente tipo de evaluación sugerida
12. Sistema registra resultado para tracking de progreso
13. Caso de uso termina exitosamente

#### Flujos Alternativos:
**4a. Usuario no está seguro del tipo:**
4a.1. Sistema recomienda diagnóstico inicial para nuevos usuarios
4a.2. Sistema sugiere práctica por área para usuarios con evaluaciones previas
4a.3. Usuario selecciona opción recomendada
4a.4. Continúa en paso 5

**7a. Usuario no responde en tiempo límite:**
7a.1. Sistema marca pregunta como no respondida
7a.2. Sistema avanza a siguiente pregunta automáticamente
7a.3. Continúa en paso 6

**9a. Usuario quiere pausar evaluación:**
9a.1. Usuario solicita pausa o cierra aplicación
9a.2. Sistema guarda progreso actual
9a.3. Al regresar, sistema ofrece continuar desde pregunta actual
9a.4. Usuario puede continuar o empezar nueva evaluación

#### Flujos de Excepción:
**6a. Error al generar pregunta:**
6a.1. Sistema no puede obtener pregunta válida
6a.2. Sistema salta a siguiente pregunta disponible
6a.3. Sistema ajusta total de preguntas si es necesario
6a.4. Continúa en paso 6

**10a. Insuficientes datos para análisis:**
10a.1. Usuario completó muy pocas preguntas
10a.2. Sistema indica limitaciones del análisis
10a.3. Sistema proporciona feedback básico disponible
10a.4. Sistema sugiere evaluación más completa

#### Requerimientos Especiales:
- Preguntas estilo PMP oficial con escenarios reales
- Distribución por dominios: People (42%), Process (50%), Business Environment (8%)
- Sin feedback durante evaluación para simular examen real
- Explicaciones pedagógicas post-evaluación
- Referencias específicas al PMBOK Guide
- Tracking de tiempo por pregunta
- Analytics de rendimiento detallados

#### Tipos de Evaluación:

**Diagnóstico Inicial:**
- 50 preguntas comprehensivas
- Cobertura de todo el PMBOK
- Tiempo sugerido: 90 minutos
- Establece baseline de conocimiento

**Práctica por Área:**
- 10-15 preguntas de dominio específico
- Focus en área seleccionada por usuario
- Tiempo sugerido: 20-30 minutos
- Refuerza conocimiento específico

**Práctica por Debilidades:**
- Preguntas de áreas identificadas como débiles
- Número variable según debilidades detectadas
- Tiempo ajustado según cantidad de preguntas
- Enfoque en mejora de gaps identificados

---

### CU-007: Simulacros de Examen (SIMULEMOS)

**Actor Principal:** Candidato PMP  
**Objetivo:** Realizar simulacros completos del examen PMP en condiciones reales para preparación final  
**Precondiciones:** 
- Usuario autenticado
- Conexión a internet disponible
- Tiempo disponible según tipo de simulacro  
**Postcondiciones:** 
- Simulacro completado en condiciones reales
- Análisis comprehensivo de rendimiento generado
- Predicción de preparación para examen real

#### Flujo Principal:
1. Usuario selecciona modo "SIMULEMOS" en menú lateral
2. Sistema inicializa chatbot en modo administrador de examen
3. Sistema presenta opciones de simulacro:
   - Examen completo (180 preguntas, 230 minutos)
   - Simulacro por tiempo (30/60/90 minutos)
   - Simulacro por dominio (People/Process/Business Environment)
4. Usuario selecciona tipo de simulacro deseado
5. Sistema proporciona briefing pre-examen:
   - Instrucciones como examen PMP real
   - Reglas y limitaciones
   - Confirmación de tiempo disponible
6. Usuario confirma inicio de simulacro
7. Sistema configura ambiente de examen:
   - Timer prominente con cuenta regresiva
   - Question navigator con progreso visual
   - Sistema de marcado para revisión
   - Auto-guardado cada 30 segundos
8. Sistema presenta preguntas en formato oficial:
   - Una pregunta por pantalla
   - Escenarios detallados realistas
   - 4 opciones múltiples
   - Distribución oficial por dominios
9. Usuario navega por preguntas:
   - Selecciona respuestas
   - Marca preguntas para revisión
   - Monitorea tiempo restante
   - Utiliza question navigator
10. **Repetir paso 9** hasta completar todas las preguntas
11. Sistema ofrece revisión final:
    - Muestra preguntas marcadas para revisión
    - Permite cambiar respuestas
    - Muestra preguntas no respondidas
12. Usuario confirma envío final del examen
13. Sistema termina simulacro y procesa resultados
14. Sistema presenta análisis post-examen comprehensivo:
    
    **Score Breakdown:**
    - Performance general (% de aciertos)
    - Score por dominio detallado
    - Comparación con passing score
    - Ranking vs estándares PMP
    
    **Análisis de Tiempo:**
    - Tiempo total utilizado vs disponible
    - Tiempo promedio por pregunta
    - Identificación de ritmo (lento/rápido)
    - Tiempo por dominio
    
    **Revisión de Preguntas:**
    - Todas las preguntas con respuestas correctas
    - Explicaciones detalladas de cada opción
    - Referencias al PMBOK Guide
    - Ejemplos adicionales para clarificación
    
    **Identificación de Áreas Débiles:**
    - Áreas que necesitan más estudio
    - Priorización de temas para revisar
    - Recursos recomendados específicos
    - Plan de estudio personalizado
    
    **Evaluación de Preparación:**
    - Predicción de probabilidad de aprobar
    - Tiempo adicional de estudio recomendado
    - Cuándo programar examen real
    - Confidence level por dominio

15. Sistema registra simulacro para tracking de progreso
16. Caso de uso termina exitosamente

#### Flujos Alternativos:
**3a. Usuario no está seguro del tipo:**
3a.1. Sistema recomienda simulacro por tiempo para principiantes
3a.2. Sistema sugiere examen completo para usuarios avanzados
3a.3. Usuario selecciona opción recomendada
3a.4. Continúa en paso 4

**10a. Usuario solicita break (solo examen completo):**
10a.1. Usuario solicita pausa a mitad del examen
10a.2. Sistema ofrece break de 10 minutos
10a.3. Sistema pausa timer durante break
10a.4. Usuario reanuda examen
10a.5. Continúa en paso 9

**11a. Usuario no quiere revisar:**
11a.1. Usuario envía examen sin revisión
11a.2. Sistema confirma envío final
11a.3. Continúa en paso 13

#### Flujos de Excepción:
**9a. Tiempo se agota:**
9a.1. Timer llega a cero
9a.2. Sistema automáticamente envía examen
9a.3. Sistema incluye preguntas no respondidas como incorrectas
9a.4. Continúa en paso 14

**9b. Aplicación se cierra inesperadamente:**
9b.1. Sistema detecta cierre durante simulacro
9b.2. Al reabrir, sistema ofrece continuar desde auto-save
9b.3. Usuario puede continuar con tiempo restante
9b.4. Si no continúa, simulacro se marca como incompleto

**13a. Error al procesar resultados:**
13a.1. Sistema no puede calcular score
13a.2. Sistema guarda respuestas para procesamiento posterior
13a.3. Sistema notifica error temporal
13a.4. Usuario puede solicitar resultados más tarde

#### Requerimientos Especiales:
- Exacta replicación de condiciones de examen PMP
- Distribución oficial: People (42%), Process (50%), Business Environment (8%)
- Timer visible constantemente sin pausas (excepto break oficial)
- Auto-guardado automático cada 30 segundos
- Sin feedback durante examen (experiencia realista)
- Question navigator completamente funcional
- Sistema de marcado idéntico al examen real

#### Tipos de Simulacro:

**Examen Completo:**
- 180 preguntas en 230 minutos
- Break opcional de 10 minutos
- Distribución oficial completa
- Experiencia idéntica al examen real

**Simulacro por Tiempo:**
- 30 min: 23 preguntas
- 60 min: 47 preguntas  
- 90 min: 70 preguntas
- Proporción de dominios mantenida

**Simulacro por Dominio:**
- People: 76 preguntas, 96 minutos
- Process: 90 preguntas, 115 minutos
- Business Environment: 14 preguntas, 18 minutos

---

### CU-008: Análisis de Progreso (ANALICEMOS)

**Actor Principal:** Candidato PMP  
**Objetivo:** Visualizar y analizar el progreso de preparación basado en datos reales de uso del sistema  
**Precondiciones:** 
- Usuario autenticado
- Datos de actividad disponibles en el sistema  
**Postcondiciones:** 
- Dashboard de progreso mostrado
- Insights y recomendaciones proporcionados
- Tendencias de aprendizaje identificadas

#### Flujo Principal:
1. Usuario selecciona modo "ANALICEMOS" en menú lateral
2. Sistema inicializa chatbot en modo analista de datos
3. Sistema extrae datos reales del usuario:
   - Sesiones de EVALUEMOS completadas
   - Simulacros de SIMULEMOS realizados
   - Actividad en otros modos
   - Datos de perfil y objetivos
4. Sistema verifica suficiencia de datos para análisis
5. Sistema genera dashboard interactivo con secciones disponibles:

   **📈 Overview General (si hay datos):**
   - Resumen de actividad total
   - Tiempo de estudio acumulado
   - Racha de días consecutivos
   - Distribución por modo de estudio
   
   **🎯 Análisis de Evaluaciones (si hay sesiones de EVALUEMOS):**
   - Número total de evaluaciones completadas
   - Temas y áreas cubiertas
   - Tiempo promedio por sesión
   - Patrones de práctica y frecuencia
   - Mejores horarios de evaluación
   
   **🏆 Análisis de Simulacros (si hay sesiones de SIMULEMOS):**
   - Historial de simulacros realizados
   - Tipos de examen completados
   - Estado de completitud
   - Progreso en puntuaciones
   - Tendencias de tiempo de respuesta
   
   **🔍 Patrones de Estudio (si hay suficiente actividad):**
   - Mejores horarios de estudio identificados
   - Días preferidos de la semana
   - Modo favorito de estudio
   - Consistencia y regularidad
   - Frecuencia de uso semanal
   
   **📊 Tendencias y Predicciones (si hay datos temporales):**
   - Progreso de mejora en el tiempo
   - Tendencias de engagement
   - Predicciones de preparación
   - Recomendaciones personalizadas

6. Usuario puede solicitar análisis específicos:
   - "Mostrar mi dashboard completo"
   - "Analizar mis evaluaciones"
   - "Revisar mis simulacros"
   - "Patrones de estudio"
   - "Tendencias de progreso"
   - "Recomendaciones personalizadas"

7. Sistema responde con análisis solicitado
8. Sistema proporciona insights accionables basados en datos reales
9. Sistema sugiere próximos pasos específicos
10. Usuario puede profundizar en áreas específicas
11. Sistema mantiene transparencia sobre qué datos tiene y cuáles no
12. Caso de uso termina cuando usuario obtiene insights deseados

#### Flujos Alternativos:
**4a. Datos insuficientes para análisis completo:**
4a.1. Sistema identifica qué tipos de datos faltan
4a.2. Sistema proporciona análisis parcial con datos disponibles
4a.3. Sistema sugiere actividades para generar más datos
4a.4. Sistema indica claramente limitaciones del análisis
4a.5. Continúa en paso 6 con funcionalidad limitada

**6a. Usuario solicita análisis sin datos:**
6a.1. Sistema identifica falta de datos para análisis específico
6a.2. Sistema explica qué actividades generar los datos necesarios
6a.3. Sistema sugiere cómo obtener esos datos
6a.4. Sistema ofrece análisis alternativos disponibles
6a.5. Continúa en paso 6

#### Flujos de Excepción:
**3a. Error al acceder datos:**
3a.1. Sistema no puede recuperar datos de usuario
3a.2. Sistema muestra mensaje de error temporal
3a.3. Sistema sugiere intentar más tarde
3a.4. Caso de uso termina con error

**5a. No hay datos disponibles:**
5a.1. Usuario nuevo sin actividad registrada
5a.2. Sistema explica que se necesita usar el sistema primero
5a.3. Sistema sugiere comenzar con EVALUEMOS o ESTUDIEMOS
5a.4. Sistema explica qué datos se recopilarán
5a.5. Caso de uso termina con orientación

#### Requerimientos Especiales:
- **Transparencia total:** Solo mostrar datos que realmente existen
- **No invención:** Nunca generar métricas ficticias
- **Claridad:** Indicar claramente cuando faltan datos
- **Accionabilidad:** Proporcionar insights útiles incluso con datos limitados
- **Motivación:** Fomentar uso continuo para generar mejores análisis
- **Privacidad:** Solo datos del usuario actual

#### Principios de Análisis:
- **Basado en datos reales:** 100% de métricas de actividad real
- **Honesto sobre limitaciones:** Clara indicación de qué falta
- **Evolutivo:** Mejora conforme se acumulan más datos
- **Personalizado:** Adaptado al perfil y objetivos del usuario
- **Predictivo:** Cuando hay suficientes datos para tendencias válidas

#### Tipos de Consulta Soportados:
- Dashboard general de progreso
- Análisis específico por tipo de actividad
- Identificación de patrones de comportamiento
- Recomendaciones personalizadas de estudio
- Predicciones de preparación (cuando aplicable)

---

### CU-009: Gestionar Conversaciones

**Actor Principal:** Candidato PMP  
**Objetivo:** Organizar, navegar y administrar múltiples conversaciones de estudio  
**Precondiciones:** 
- Usuario autenticado
- Al menos una conversación existente (opcional)  
**Postcondiciones:** 
- Conversaciones organizadas según preferencias del usuario
- Historial de conversaciones mantenido

#### Flujo Principal - Crear Nueva Conversación:
1. Usuario hace clic en botón "+" en header o sidebar
2. Sistema verifica que hay un modo activo seleccionado
3. Sistema crea nueva conversación:
   - Genera nombre automático basado en modo actual
   - Asocia conversación con modo activo
   - Crea registro en base de datos
4. Sistema muestra mensaje de bienvenida específico del modo
5. Sistema actualiza lista de conversaciones en sidebar
6. Usuario puede comenzar a chatear inmediatamente
7. Caso de uso termina exitosamente

#### Flujo Principal - Cambiar entre Conversaciones:
1. Usuario hace clic en conversación deseada en sidebar
2. Sistema carga historial completo de la conversación seleccionada
3. Sistema actualiza área de chat con mensajes históricos
4. Sistema resalta conversación activa en sidebar
5. Sistema hace scroll automático al final de conversación
6. Usuario puede continuar conversación desde último mensaje
7. Caso de uso termina exitosamente

#### Flujo Principal - Renombrar Conversación:
1. Usuario hace clic en menú contextual (⋮) de conversación
2. Sistema muestra menú con opción "Renombrar"
3. Usuario selecciona "Renombrar"
4. Sistema muestra diálogo con nombre actual precargado
5. Usuario ingresa nuevo nombre para conversación
6. Usuario confirma cambio
7. Sistema valida que nombre no esté duplicado
8. Sistema actualiza nombre en base de datos
9. Sistema actualiza inmediatamente el sidebar
10. Caso de uso termina exitosamente

#### Flujo Principal - Eliminar Conversación:
1. Usuario hace clic en menú contextual (⋮) de conversación
2. Sistema muestra menú con opción "Eliminar"
3. Usuario selecciona "Eliminar"
4. Sistema muestra diálogo de confirmación de seguridad
5. Usuario confirma eliminación
6. Sistema elimina conversación y todos sus mensajes de base de datos
7. Sistema actualiza lista del sidebar removiendo conversación
8. Si era conversación activa, sistema redirige a otra conversación disponible
9. Caso de uso termina exitosamente

#### Flujos Alternativos:
**1a. No hay modo activo para nueva conversación:**
1a.1. Sistema muestra mensaje "Selecciona un modo de estudio primero"
1a.2. Usuario debe seleccionar modo antes de crear conversación
1a.3. Caso de uso termina sin crear conversación

**5a. Usuario cancela renombrar:**
5a.1. Usuario cancela diálogo de renombrar
5a.2. Sistema cierra diálogo sin cambios
5a.3. Caso de uso termina sin modificaciones

**5b. Usuario cancela eliminar:**
5b.1. Usuario cancela confirmación de eliminación
5b.2. Sistema cierra diálogo sin eliminar
5b.3. Caso de uso termina sin modificaciones

**8a. Era la última conversación:**
8a.1. No hay otras conversaciones para redirigir
8a.2. Sistema muestra pantalla de bienvenida del modo
8a.3. Usuario puede crear nueva conversación
8a.4. Caso de uso termina

#### Flujos de Excepción:
**7a. Nombre duplicado al renombrar:**
7a.1. Sistema detecta nombre ya existente
7a.2. Sistema muestra mensaje "Nombre ya existe"
7a.3. Usuario debe ingresar nombre diferente
7a.4. Continúa en paso 5

**6a. Error al eliminar conversación:**
6a.1. Sistema no puede eliminar de base de datos
6a.2. Sistema muestra mensaje de error
6a.3. Conversación permanece en lista
6a.4. Usuario puede intentar nuevamente

**2a. Error al cargar historial:**
2a.1. Sistema no puede recuperar mensajes de conversación
2a.2. Sistema muestra conversación vacía con mensaje de error
2a.3. Usuario puede intentar recargar o usar otra conversación
2a.4. Caso de uso continúa con funcionalidad limitada

#### Requerimientos Especiales:
- **Persistencia:** Todas las conversaciones se mantienen entre sesiones
- **Privacidad:** Solo el usuario propietario puede ver sus conversaciones
- **Organización:** Conversaciones ordenadas por última actividad
- **Preview:** Vista previa del último mensaje en sidebar
- **Contexto:** Cada conversación mantiene su modo específico
- **Eficiencia:** Carga lazy de mensajes para conversaciones largas

#### Características de Organización:
- **Orden cronológico:** Por última actividad (más recientes arriba)
- **Indicadores visuales:** Conversación activa claramente identificada
- **Agrupación por modo:** Filtro opcional por tipo de estudio
- **Búsqueda visual:** Preview de mensajes para identificación rápida
- **Estados visuales:** Diferentes colores según modo de estudio

---

### CU-010: Configurar Sistema

**Actor Principal:** Candidato PMP  
**Objetivo:** Personalizar configuraciones de la aplicación según preferencias del usuario  
**Precondiciones:** 
- Usuario autenticado  
**Postcondiciones:** 
- Configuraciones personalizadas aplicadas
- Preferencias guardadas para sesiones futuras

#### Flujo Principal:
1. Usuario accede a configuraciones desde menú de la aplicación
2. Sistema muestra panel de configuración organizado en secciones:

   **🎯 Objetivos de Estudio:**
   - Fecha objetivo del examen (DD/MM/YYYY)
   - Horas de estudio diarias objetivo
   - Recordatorios de sesiones de estudio
   
   **🔔 Notificaciones:**
   - Recordatorios de estudio (on/off)
   - Alertas de progreso (on/off)
   - Notificaciones de logros (on/off)
   
   **🎨 Personalización:**
   - Tema visual (Claro/Oscuro/Automático)
   - Idioma de interfaz (Español/English)
   - Tamaño de fuente (Pequeño/Medio/Grande)
   
   **⚙️ Configuración Avanzada:**
   - Tiempo de auto-guardado
   - Número de mensajes a mostrar
   - Configuración de API (solo lectura)

3. Usuario modifica configuraciones deseadas
4. Usuario hace clic en "Guardar Configuración"
5. Sistema valida configuraciones ingresadas
6. Sistema aplica cambios inmediatamente cuando es posible
7. Sistema guarda preferencias en almacenamiento local
8. Sistema muestra confirmación de cambios guardados
9. Caso de uso termina exitosamente

#### Flujos Alternativos:
**4a. Usuario restaura configuraciones por defecto:**
4a.1. Usuario hace clic en "Restaurar Valores por Defecto"
4a.2. Sistema solicita confirmación
4a.3. Usuario confirma restauración
4a.4. Sistema restablece todas las configuraciones
4a.5. Continúa en paso 6

**4b. Usuario cancela cambios:**
4b.1. Usuario cierra panel sin guardar
4b.2. Sistema descarta cambios no guardados
4b.3. Configuraciones anteriores se mantienen
4b.4. Caso de uso termina sin cambios

#### Flujos de Excepción:
**5a. Configuración inválida:**
5a.1. Sistema detecta valor fuera de rango válido
5a.2. Sistema resalta campo problemático
5a.3. Sistema muestra mensaje de error específico
5a.4. Usuario corrige valor
5a.5. Continúa en paso 4

**6a. Error al aplicar cambios:**
6a.1. Sistema no puede aplicar alguna configuración
6a.2. Sistema notifica qué cambios no se pudieron aplicar
6a.3. Sistema aplica cambios posibles
6a.4. Usuario puede intentar recargar aplicación

#### Requerimientos Especiales:
- **Aplicación inmediata:** Cambios visuales se aplican sin reiniciar
- **Persistencia:** Configuraciones se mantienen entre sesiones
- **Validación:** Verificación de rangos válidos para cada configuración
- **Retrocompatibilidad:** Manejo de configuraciones de versiones anteriores

---

### CU-011: Cerrar Sesión

**Actor Principal:** Candidato PMP  
**Objetivo:** Terminar sesión actual de manera segura y limpiar datos temporales  
**Precondiciones:** 
- Usuario autenticado y con sesión activa  
**Postcondiciones:** 
- Sesión cerrada de manera segura
- Datos temporales limpiados de memoria
- Usuario redirigido a pantalla de login

#### Flujo Principal:
1. Usuario hace clic en botón de logout (icono de salida) en header
2. Sistema muestra diálogo de confirmación: "¿Estás seguro que quieres cerrar sesión?"
3. Usuario confirma cierre de sesión
4. Sistema ejecuta proceso de logout:
   - Guarda automáticamente cualquier mensaje en progreso
   - Limpia datos de usuario de memoria
   - Termina sesión actual
   - Limpia cache de conversaciones
5. Sistema redirige a pantalla de autenticación
6. Sistema muestra pantalla de login limpia
7. Caso de uso termina exitosamente

#### Flujos Alternativos:
**3a. Usuario cancela logout:**
3a.1. Usuario hace clic en "Cancelar" en diálogo
3a.2. Sistema cierra diálogo de confirmación
3a.3. Usuario permanece en sesión activa
3a.4. Caso de uso termina sin cerrar sesión

**1a. Logout automático por inactividad:**
1a.1. Sistema detecta inactividad prolongada (opcional)
1a.2. Sistema muestra advertencia de logout automático
1a.3. Usuario puede extender sesión o aceptar logout
1a.4. Si no hay respuesta, continúa en paso 4

#### Flujos de Excepción:
**4a. Error durante proceso de logout:**
4a.1. Sistema no puede completar limpieza completa
4a.2. Sistema fuerza logout de todas maneras por seguridad
4a.3. Sistema registra error para diagnóstico
4a.4. Continúa en paso 5

#### Requerimientos Especiales:
- **Seguridad:** Limpieza completa de datos sensibles de memoria
- **Auto-guardado:** Preservación de trabajo no guardado antes de logout
- **Confirmación:** Prevención de logout accidental
- **Rapidez:** Proceso de logout eficiente y rápido

---

## 📊 6. Matriz de Trazabilidad

### 6.1 Casos de Uso vs Requerimientos Funcionales

| Caso de Uso | RF Relacionados | Complejidad | Prioridad |
|-------------|-----------------|-------------|-----------|
| CU-001 Registrar Usuario | RF-001, RF-002, RF-003, RF-004 | Media | Alta |
| CU-002 Iniciar Sesión | RF-005, RF-006, RF-007 | Baja | Alta |
| CU-003 Gestionar Perfil | RF-008, RF-009, RF-010 | Media | Media |
| CU-004 Conversación Libre | RF-011, RF-012, RF-013 | Alta | Alta |
| CU-005 Estudio Estructurado | RF-014, RF-015, RF-016 | Alta | Alta |
| CU-006 Evaluación y Práctica | RF-017, RF-018, RF-019 | Alta | Alta |
| CU-007 Simulacros de Examen | RF-020, RF-021, RF-022 | Muy Alta | Alta |
| CU-008 Análisis de Progreso | RF-023, RF-024, RF-025 | Alta | Media |
| CU-009 Gestionar Conversaciones | RF-026, RF-027, RF-028, RF-029, RF-030 | Media | Media |
| CU-010 Configurar Sistema | RF-051, RF-052, RF-055 | Baja | Baja |
| CU-011 Cerrar Sesión | RF-049, RF-050 | Baja | Media |

### 6.2 Actores vs Casos de Uso

| Actor | Casos de Uso Participantes |
|-------|---------------------------|
| Usuario No Registrado | CU-001 |
| Candidato PMP | CU-002, CU-003, CU-004, CU-005, CU-006, CU-007, CU-008, CU-009, CU-010, CU-011 |
| Sistema de IA | CU-004, CU-005, CU-006, CU-007, CU-008 |

---

## 🎯 7. Criterios de Aceptación

### 7.1 Criterios Generales
- **Completitud:** Todos los casos de uso deben implementarse completamente
- **Usabilidad:** Interfaz intuitiva sin necesidad de entrenamiento
- **Rendimiento:** Tiempos de respuesta según especificaciones no funcionales
- **Seguridad:** Cumplimiento de todos los requerimientos de seguridad
- **Confiabilidad:** Manejo robusto de errores y excepciones

### 7.2 Criterios Específicos por Caso de Uso

**CU-001 Registrar Usuario:**
- [ ] Validación en tiempo real de todos los campos
- [ ] Fortaleza de contraseña evaluada correctamente
- [ ] Unicidad de usuario y email verificada
- [ ] Redirección automática post-registro exitoso

**CU-002 Iniciar Sesión:**
- [ ] Autenticación exitosa con credenciales válidas
- [ ] Mensajes de error claros para credenciales inválidas
- [ ] Sesión persistente hasta logout manual

**CU-004-007 Modos de Estudio:**
- [ ] Cada modo funciona según especificaciones únicas
- [ ] Integración correcta con OpenAI API
- [ ] Persistencia adecuada de conversaciones
- [ ] Mensajes de bienvenida específicos por modo

**CU-009 Gestionar Conversaciones:**
- [ ] Creación, renombrado y eliminación funcionan correctamente
- [ ] Preview de mensajes visible en sidebar
- [ ] Navegación fluida entre conversaciones

---

## 📝 8. Notas de Implementación

### 8.1 Consideraciones Técnicas
- **Threading:** Operaciones de IA deben ejecutarse en hilos separados
- **Base de Datos:** Transacciones atómicas para operaciones críticas
- **Validación:** Doble validación (frontend y backend) para datos críticos
- **Manejo de Errores:** Logging detallado para diagnóstico
- **Persistencia:** Auto-guardado frecuente para prevenir pérdida de datos

### 8.2 Dependencias entre Casos de Uso
- CU-002 es prerequisito para CU-003 a CU-011
- CU-006 y CU-007 generan datos para CU-008
- CU-009 complementa CU-004 a CU-008
- CU-001 es punto de entrada para nuevos usuarios

### 8.3 Orden de Implementación Sugerido
1. CU-001, CU-002, CU-011 (Autenticación básica)
2. CU-009 (Gestión de conversaciones)
3. CU-004 (Conversación libre - funcionalidad core)
4. CU-005, CU-006 (Modos de estudio básicos)
5. CU-007 (Simulacros - más complejo)
6. CU-008 (Análisis - requiere datos de otros casos)
7. CU-003, CU-010 (Gestión de perfil y configuración)

---

**Documento generado:** $(date)  
**Versión del proyecto:** 2.0.0 con Autenticación  
**Total de casos de uso:** 11  
**Autor:** Sistema de Análisis de Casos de Uso 

---

## ✅ Estado de Implementación y Validación de Casos de Uso

### Estado General
- **Versión actual:** 2.0.0 con Autenticación
- **Fecha de actualización:** $(date)
- **Repositorio:** https://github.com/daneri-dahbar/asistente-pmp

### Cumplimiento de Casos de Uso
- **Casos de uso implementados:** Todos los casos de uso descritos en este documento están implementados y disponibles en la aplicación.
- **Cobertura funcional:** Cada flujo principal, alternativo y de excepción ha sido considerado en la lógica de la aplicación.
- **Persistencia y seguridad:** Todas las operaciones de registro, autenticación, gestión de perfil, conversaciones y modos de estudio funcionan según lo especificado.
- **Interfaz:** La experiencia de usuario es coherente con los escenarios descritos, con mensajes y feedback visual en español.

### Estado de Pruebas y Validación
- **Framework de testing:** Pytest
- **Cobertura:**
    - Pruebas unitarias y de integración para los modelos y operaciones principales
    - Validación manual de los flujos de usuario y casos de uso completos
- **Resultado:**
    - Todos los tests relevantes pasan correctamente
    - Los criterios de aceptación definidos han sido verificados manualmente y mediante pruebas automatizadas
    - El sistema cumple con los escenarios de usuario y requisitos de calidad

### Observaciones Finales
- El sistema está listo para entrega y uso real.
- La arquitectura y documentación permiten fácil mantenimiento y evolución.
- Se recomienda mantener la validación continua y actualizar la documentación ante futuras mejoras.

--- 
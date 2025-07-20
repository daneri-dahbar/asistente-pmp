# ⚡ Requerimientos No Funcionales - Asistente para Certificación PMP

## 📌 1. Información General

### 1.1 Propósito del Documento
Este documento especifica los **requerimientos no funcionales** del sistema **Asistente para Certificación PMP**. Los requerimientos no funcionales definen **cómo debe comportarse el sistema** en términos de rendimiento, seguridad, usabilidad, confiabilidad y otros atributos de calidad, complementando los requerimientos funcionales que definen **qué hace el sistema**.

### 1.2 Alcance
Los requerimientos no funcionales cubren todos los aspectos de calidad del sistema, desde el rendimiento de la interfaz hasta la seguridad de los datos, garantizando una experiencia de usuario óptima y un sistema robusto y escalable.

### 1.3 Clasificación de Requerimientos
Los requerimientos se clasifican según la norma ISO/IEC 25010 en las siguientes categorías:
- **Rendimiento y Eficiencia**
- **Confiabilidad y Disponibilidad** 
- **Seguridad**
- **Usabilidad**
- **Compatibilidad y Portabilidad**
- **Escalabilidad y Mantenibilidad**

---

## 🚀 2. Rendimiento y Eficiencia

### 2.1 Tiempos de Respuesta

**RNF-001: Tiempo de Inicio de Aplicación**
- **Descripción:** La aplicación debe iniciar en un tiempo razonable
- **Criterio:** < 5 segundos desde ejecución hasta interfaz funcional
- **Medición:** Tiempo desde `python main.py` hasta ventana completamente cargada
- **Prioridad:** Alta
- **Implementación:** Lazy loading de componentes, inicialización asíncrona

**RNF-002: Respuesta de Interfaz Local**
- **Descripción:** Las operaciones de interfaz deben ser inmediatas
- **Criterio:** < 200ms para navegación, cambio de modos, apertura de conversaciones
- **Medición:** Tiempo entre clic del usuario y respuesta visual
- **Prioridad:** Alta
- **Implementación:** Threading para operaciones no bloqueantes

**RNF-003: Tiempo de Respuesta de IA**
- **Descripción:** Las respuestas del chatbot deben llegar en tiempo razonable
- **Criterio:** < 10 segundos para respuestas simples, < 30 segundos para análisis complejos
- **Medición:** Tiempo desde envío de mensaje hasta inicio de respuesta
- **Prioridad:** Media
- **Dependencia:** Latencia de red y API de OpenAI

### 2.2 Gestión de Memoria

**RNF-004: Uso de Memoria Base**
- **Descripción:** La aplicación debe funcionar en sistemas con recursos limitados
- **Criterio:** < 200MB RAM en estado idle, < 500MB durante uso activo
- **Medición:** Monitor de memoria del sistema operativo
- **Prioridad:** Media
- **Implementación:** Garbage collection automático, liberación de recursos

**RNF-005: Gestión de Conversaciones Largas**
- **Descripción:** El sistema debe manejar conversaciones extensas sin degradación
- **Criterio:** Sin pérdida de rendimiento hasta 1000 mensajes por conversación
- **Medición:** Tiempo de carga y scrolling en conversaciones largas
- **Prioridad:** Media
- **Implementación:** Paginación de mensajes, lazy loading del historial

### 2.3 Operaciones de Base de Datos

**RNF-006: Consultas de Base de Datos**
- **Descripción:** Las operaciones de base de datos deben ser eficientes
- **Criterio:** < 100ms para consultas simples, < 500ms para análisis complejos
- **Medición:** Tiempo de ejecución de queries SQLite
- **Prioridad:** Alta
- **Implementación:** Índices optimizados, consultas preparadas

**RNF-007: Crecimiento de Base de Datos**
- **Descripción:** La base de datos debe manejar el crecimiento de datos
- **Criterio:** Soporte hasta 100MB de datos por usuario sin degradación
- **Medición:** Tamaño de archivo SQLite y tiempo de consultas
- **Prioridad:** Media
- **Implementación:** Optimización de esquemas, limpieza automática

### 2.4 Threading y Concurrencia

**RNF-008: Operaciones No Bloqueantes**
- **Descripción:** Las operaciones largas no deben bloquear la interfaz
- **Criterio:** UI responsive durante carga de IA, guardado de datos, análisis
- **Medición:** Capacidad de interactuar con UI durante operaciones
- **Prioridad:** Alta
- **Implementación:** `threading.Thread(daemon=True)` para operaciones asíncronas

---

## 🛡️ 3. Confiabilidad y Disponibilidad

### 3.1 Manejo de Errores

**RNF-009: Recuperación de Errores de IA**
- **Descripción:** El sistema debe manejar fallos de la API de OpenAI
- **Criterio:** Mensaje informativo al usuario, no crash de aplicación
- **Medición:** Comportamiento ante desconexión de internet o error de API
- **Prioridad:** Alta
- **Implementación:** Try-catch blocks, mensajes de error amigables

**RNF-010: Manejo de Errores de Base de Datos**
- **Descripción:** Errores de SQLite no deben causar pérdida de datos
- **Criterio:** Recuperación automática, backup de datos críticos
- **Medición:** Comportamiento ante corrupción de DB o disco lleno
- **Prioridad:** Alta
- **Implementación:** Transacciones atómicas, validación de integridad

**RNF-011: Graceful Degradation**
- **Descripción:** Funcionalidades deben degradar elegantemente ante problemas
- **Criterio:** Sistema usable aunque algunos componentes fallen
- **Medición:** Funcionalidad disponible en modo offline o con errores parciales
- **Prioridad:** Media
- **Implementación:** Verificación de componentes, modos de emergencia

### 3.2 Persistencia de Datos

**RNF-012: Auto-guardado**
- **Descripción:** Los datos deben guardarse automáticamente
- **Criterio:** Persistencia inmediata de mensajes, perfil, configuraciones
- **Medición:** Recuperación de datos tras cierre inesperado
- **Prioridad:** Alta
- **Implementación:** Commit automático en SQLite, transacciones inmediatas

**RNF-013: Integridad de Datos**
- **Descripción:** Los datos deben mantenerse íntegros
- **Criterio:** 0% de pérdida de datos en operaciones normales
- **Medición:** Verificación de consistencia tras múltiples operaciones
- **Prioridad:** Crítica
- **Implementación:** Constraints de base de datos, validación de entrada

### 3.3 Disponibilidad del Sistema

**RNF-014: Funcionamiento Offline**
- **Descripción:** El sistema debe funcionar sin conexión a internet
- **Criterio:** Todas las funciones excepto IA disponibles offline
- **Medición:** Funcionalidad con red desconectada
- **Prioridad:** Media
- **Implementación:** Base de datos local, verificación de conectividad

**RNF-015: Tiempo de Actividad**
- **Descripción:** La aplicación debe ser estable durante uso prolongado
- **Criterio:** > 8 horas de uso continuo sin degradación
- **Medición:** Sesiones largas de uso, monitoring de memoria
- **Prioridad:** Media
- **Implementación:** Limpieza de memoria, gestión de recursos

---

## 🔒 4. Seguridad

### 4.1 Seguridad de Autenticación

**RNF-016: Hashing de Contraseñas**
- **Descripción:** Las contraseñas deben estar fuertemente protegidas
- **Criterio:** SHA-256 + salt único por usuario, 0% texto plano
- **Medición:** Inspección de base de datos, validación de algoritmos
- **Prioridad:** Crítica
- **Implementación:** `hashlib.sha256()`, `secrets.token_hex(16)`

**RNF-017: Generación de Salt**
- **Descripción:** Los salts deben ser criptográficamente seguros
- **Criterio:** Aleatoriedad criptográfica, 32 caracteres hexadecimales
- **Medición:** Análisis de entropía, unicidad de salts
- **Prioridad:** Crítica
- **Implementación:** `secrets` module para generación segura

**RNF-018: Validación de Contraseñas**
- **Descripción:** Las contraseñas deben cumplir políticas de seguridad
- **Criterio:** Mínimo 6 caracteres, letras y números obligatorios
- **Medición:** Validación en tiempo real, rechazo de contraseñas débiles
- **Prioridad:** Alta
- **Implementación:** Expresiones regulares, validación en frontend y backend

### 4.2 Protección de Datos

**RNF-019: Sanitización de Entrada**
- **Descripción:** Todos los inputs deben ser validados y sanitizados
- **Criterio:** 100% de inputs validados, prevención de inyección
- **Medición:** Testing de inyección SQL, XSS, validación de tipos
- **Prioridad:** Alta
- **Implementación:** SQLAlchemy ORM, validación de tipos de datos

**RNF-020: Gestión de API Keys**
- **Descripción:** Las claves API deben estar protegidas
- **Criterio:** Almacenamiento en variables de entorno, no en código
- **Medición:** Inspección de código fuente, verificación de .env
- **Prioridad:** Crítica
- **Implementación:** `python-dotenv`, validación de presencia

### 4.3 Gestión de Sesiones

**RNF-021: Limpieza de Sesiones**
- **Descripción:** Las sesiones deben limpiarse adecuadamente
- **Criterio:** Datos de usuario eliminados de memoria al logout
- **Medición:** Monitoring de memoria tras logout
- **Prioridad:** Alta
- **Implementación:** Limpieza explícita de variables, garbage collection

---

## 🎨 5. Usabilidad

### 5.1 Interfaz de Usuario

**RNF-022: Responsive Design**
- **Descripción:** La interfaz debe adaptarse a diferentes tamaños
- **Criterio:** Funcional desde 400x500 hasta pantallas grandes
- **Medición:** Testing en diferentes resoluciones
- **Prioridad:** Alta
- **Implementación:** Sidebar colapsable, layout adaptativo

**RNF-023: Feedback Visual**
- **Descripción:** Todas las acciones deben tener respuesta visual
- **Criterio:** Indicadores de loading, confirmación de acciones
- **Medición:** Verificación visual de cada interacción
- **Prioridad:** Alta
- **Implementación:** SnackBars, spinners, cambios de color

**RNF-024: Accesibilidad**
- **Descripción:** La interfaz debe ser accesible
- **Criterio:** Contraste adecuado, navegación por teclado
- **Medición:** Herramientas de accesibilidad, testing manual
- **Prioridad:** Media
- **Implementación:** Colores contrastantes, tooltips informativos

### 5.2 Experiencia de Usuario

**RNF-025: Curva de Aprendizaje**
- **Descripción:** La aplicación debe ser intuitiva
- **Criterio:** Usuario nuevo productivo en < 5 minutos
- **Medición:** Testing con usuarios reales, tiempo de primera acción
- **Prioridad:** Alta
- **Implementación:** Mensajes de bienvenida, navegación clara

**RNF-026: Consistencia Visual**
- **Descripción:** El diseño debe ser consistente en toda la aplicación
- **Criterio:** Mismos patrones de color, tipografía, espaciado
- **Medición:** Auditoría visual de pantallas
- **Prioridad:** Media
- **Implementación:** Sistema de colores definido, componentes reutilizables

### 5.3 Manejo de Errores para Usuario

**RNF-027: Mensajes de Error Informativos**
- **Descripción:** Los errores deben ser comprensibles para el usuario
- **Criterio:** Lenguaje claro, acciones correctivas sugeridas
- **Medición:** Revisión de todos los mensajes de error
- **Prioridad:** Alta
- **Implementación:** Mensajes en español, contexto específico

---

## 🔧 6. Compatibilidad y Portabilidad

### 6.1 Compatibilidad de Plataforma

**RNF-028: Sistemas Operativos**
- **Descripción:** La aplicación debe funcionar en múltiples SO
- **Criterio:** Windows 10+, macOS 10.15+, Ubuntu 20.04+
- **Medición:** Testing en cada plataforma objetivo
- **Prioridad:** Alta
- **Implementación:** Python multiplataforma, Flet framework

**RNF-029: Versiones de Python**
- **Descripción:** Compatibilidad con versiones recientes de Python
- **Criterio:** Python 3.9+ (verificación automática en startup)
- **Medición:** Testing con diferentes versiones de Python
- **Prioridad:** Crítica
- **Implementación:** Verificación en `setup.py` y `main.py`

### 6.2 Empaquetado y Distribución

**RNF-030: Ejecutable Standalone**
- **Descripción:** Debe poder distribuirse como ejecutable
- **Criterio:** PyInstaller genera .exe funcional con todas las dependencias
- **Medición:** Ejecución en sistema sin Python instalado
- **Prioridad:** Alta
- **Implementación:** Configuración PyInstaller, inclusion de assets

**RNF-031: Instalador**
- **Descripción:** Disponibilidad de instalador para Windows
- **Criterio:** Inno Setup genera instalador .exe con shortcuts
- **Medición:** Instalación y desinstalación limpia
- **Prioridad:** Media
- **Implementación:** Script `installer.iss`, iconos incluidos

### 6.3 Dependencias

**RNF-032: Gestión de Dependencias**
- **Descripción:** Control claro de versiones de dependencias
- **Criterio:** `requirements.txt` con versiones específicas
- **Medición:** Instalación limpia en entorno nuevo
- **Prioridad:** Alta
- **Implementación:** Versionado semántico, testing de compatibilidad

---

## 📈 7. Escalabilidad y Mantenibilidad

### 7.1 Escalabilidad de Datos

**RNF-033: Capacidad de Usuarios**
- **Descripción:** El sistema debe soportar múltiples usuarios
- **Criterio:** > 100 usuarios registrados sin degradación
- **Medición:** Carga de base de datos con múltiples usuarios
- **Prioridad:** Media
- **Implementación:** Índices en base de datos, optimización de consultas

**RNF-034: Volumen de Conversaciones**
- **Descripción:** Soporte para gran cantidad de conversaciones por usuario
- **Criterio:** > 500 conversaciones por usuario, > 10,000 mensajes totales
- **Medición:** Performance con datasets grandes
- **Prioridad:** Media
- **Implementación:** Paginación, lazy loading, archivado automático

### 7.2 Arquitectura y Código

**RNF-035: Modularidad**
- **Descripción:** El código debe estar bien organizado y modular
- **Criterio:** Separación clara de responsabilidades, bajo acoplamiento
- **Medición:** Análisis de dependencias entre módulos
- **Prioridad:** Media
- **Implementación:** Patrón MVC, archivos separados por funcionalidad

**RNF-036: Extensibilidad**
- **Descripción:** Debe ser fácil agregar nuevos modos de estudio
- **Criterio:** Nuevo modo implementable en < 2 horas
- **Medición:** Tiempo de implementación de feature nuevo
- **Prioridad:** Media
- **Implementación:** Arquitectura basada en plugins, configuración centralizada

### 7.3 Documentación y Mantenimiento

**RNF-037: Documentación del Código**
- **Descripción:** El código debe estar adecuadamente documentado
- **Criterio:** Docstrings en todas las funciones públicas
- **Medición:** Cobertura de documentación > 80%
- **Prioridad:** Media
- **Implementación:** Estándares de documentación Python, comentarios explicativos

**RNF-038: Configuración Centralizada**
- **Descripción:** Configuraciones deben estar centralizadas
- **Criterio:** Archivo `.env` para configuración, constantes en archivos dedicados
- **Medición:** Facilidad de cambio de configuración
- **Prioridad:** Media
- **Implementación:** `python-dotenv`, configuración por ambiente

---

## 🌐 8. Requerimientos de Red y Conectividad

### 8.1 Gestión de Conectividad

**RNF-039: Detección de Conectividad**
- **Descripción:** El sistema debe detectar el estado de conexión
- **Criterio:** Indicador visual de estado online/offline
- **Medición:** Comportamiento al desconectar/reconectar red
- **Prioridad:** Media
- **Implementación:** Verificación periódica de conexión, feedback visual

**RNF-040: Timeout de Requests**
- **Descripción:** Las llamadas a API deben tener timeout apropiado
- **Criterio:** Timeout de 30 segundos para OpenAI API
- **Medición:** Comportamiento ante conexión lenta
- **Prioridad:** Alta
- **Implementación:** Configuración de timeout en LangChain

### 8.2 Eficiencia de Red

**RNF-041: Compresión de Datos**
- **Descripción:** Minimizar el uso de ancho de banda
- **Criterio:** Requests optimizados, sin datos innecesarios
- **Medición:** Análisis de tráfico de red
- **Prioridad:** Baja
- **Implementación:** Configuración de compression en requests

---

## 💾 9. Requerimientos de Almacenamiento

### 9.1 Gestión de Archivos

**RNF-042: Ubicación de Datos**
- **Descripción:** Los datos deben almacenarse en ubicación apropiada
- **Criterio:** Base de datos en directorio de aplicación, configuración en .env
- **Medición:** Verificación de creación de archivos
- **Prioridad:** Alta
- **Implementación:** Rutas relativas, creación automática de directorios

**RNF-043: Limpieza de Datos**
- **Descripción:** El sistema debe gestionar el crecimiento de datos
- **Criterio:** Opción de limpiar conversaciones antiguas (>6 meses)
- **Medición:** Herramientas de mantenimiento disponibles
- **Prioridad:** Baja
- **Implementación:** Scripts de limpieza, archivado automático

### 9.2 Backup y Recuperación

**RNF-044: Backup de Datos**
- **Descripción:** Los usuarios deben poder respaldar sus datos
- **Criterio:** Archivo SQLite copiable, importación/exportación disponible
- **Medición:** Capacidad de restaurar datos desde backup
- **Prioridad:** Media
- **Implementación:** Documentación de backup, herramientas de exportación

---

## ⚙️ 10. Requerimientos de Configuración

### 10.1 Configuración de Usuario

**RNF-045: Personalización**
- **Descripción:** Los usuarios deben poder personalizar la experiencia
- **Criterio:** Temas (claro/oscuro), tamaño de fuente, colores
- **Medición:** Persistencia de preferencias entre sesiones
- **Prioridad:** Baja
- **Implementación:** Sistema de configuración, storage local

**RNF-046: Configuración de IA**
- **Descripción:** Parámetros de IA deben ser configurables
- **Criterio:** Modelo, temperatura, max_tokens en archivo de configuración
- **Medición:** Cambio efectivo de comportamiento al modificar configuración
- **Prioridad:** Baja
- **Implementación:** Variables de entorno, configuración por modo

### 10.2 Configuración del Sistema

**RNF-047: Variables de Entorno**
- **Descripción:** Configuración sensible debe estar en variables de entorno
- **Criterio:** API keys, URLs, configuración de DB en .env
- **Medición:** Verificación de no hardcoding de valores sensibles
- **Prioridad:** Crítica
- **Implementación:** `python-dotenv`, validación de configuración

---

## 📊 11. Métricas y Monitoreo

### 11.1 Métricas de Rendimiento

**RNF-048: Logging de Performance**
- **Descripción:** El sistema debe registrar métricas de rendimiento
- **Criterio:** Tiempo de respuesta, uso de memoria, errores de API
- **Medición:** Logs estructurados, métricas exportables
- **Prioridad:** Baja
- **Implementación:** Python logging, métricas personalizadas

**RNF-049: Monitoring de Recursos**
- **Descripción:** Monitoreo de uso de recursos del sistema
- **Criterio:** Alertas ante uso excesivo de memoria o CPU
- **Medición:** Herramientas de sistema operativo
- **Prioridad:** Baja
- **Implementación:** Integración con herramientas de OS

### 11.2 Calidad de Servicio

**RNF-050: SLA de Disponibilidad**
- **Descripción:** El sistema debe mantener alta disponibilidad
- **Criterio:** > 99% uptime durante uso normal (8 horas/día)
- **Medición:** Registro de crashes y tiempo de inactividad
- **Prioridad:** Media
- **Implementación:** Manejo robusto de errores, testing exhaustivo

---

## 🎯 12. Criterios de Aceptación y Testing

### 12.1 Testing de Rendimiento

**Criterios de Aceptación:**
- [ ] Inicio de aplicación < 5 segundos
- [ ] Respuesta de UI < 200ms
- [ ] Respuesta de IA < 30 segundos
- [ ] Uso de memoria < 500MB en uso activo
- [ ] Base de datos soporta > 10,000 mensajes sin degradación

### 12.2 Testing de Confiabilidad

**Criterios de Aceptación:**
- [ ] 0% pérdida de datos en condiciones normales
- [ ] Recuperación automática de errores de red
- [ ] Manejo graceful de todos los errores identificados
- [ ] Funcionamiento > 8 horas continuas sin degradación
- [ ] Funcionalidad offline disponible

### 12.3 Testing de Seguridad

**Criterios de Aceptación:**
- [ ] 0% contraseñas en texto plano en base de datos
- [ ] Salts únicos para cada usuario
- [ ] Validación efectiva de todos los inputs
- [ ] API keys nunca hardcodeadas en código
- [ ] Limpieza efectiva de sesiones al logout

### 12.4 Testing de Usabilidad

**Criterios de Aceptación:**
- [ ] Usuario nuevo productivo < 5 minutos
- [ ] Interfaz funcional en resoluciones 400x500+
- [ ] Feedback visual para todas las acciones
- [ ] Mensajes de error comprensibles
- [ ] Navegación intuitiva sin entrenamiento

### 12.5 Testing de Compatibilidad

**Criterios de Aceptación:**
- [ ] Funcionamiento en Windows 10+, macOS 10.15+, Ubuntu 20.04+
- [ ] Compatibilidad con Python 3.9+
- [ ] Ejecutable standalone funcional
- [ ] Instalador Windows operativo
- [ ] Todas las dependencias resueltas correctamente

---

## 📋 13. Matriz de Prioridades

### 13.1 Requerimientos Críticos (Implementación Obligatoria)
- **RNF-013:** Integridad de Datos
- **RNF-016:** Hashing de Contraseñas
- **RNF-017:** Generación de Salt Seguro
- **RNF-020:** Gestión de API Keys
- **RNF-029:** Compatibilidad Python 3.9+
- **RNF-047:** Variables de Entorno

### 13.2 Requerimientos Altos (Alta Prioridad)
- **RNF-001, 002:** Tiempos de Respuesta
- **RNF-006:** Consultas de Base de Datos
- **RNF-008:** Operaciones No Bloqueantes
- **RNF-009, 010:** Manejo de Errores
- **RNF-012:** Auto-guardado
- **RNF-018:** Validación de Contraseñas
- **RNF-019:** Sanitización de Entrada
- **RNF-021:** Limpieza de Sesiones
- **RNF-022, 023:** Interfaz Responsive
- **RNF-025:** Curva de Aprendizaje
- **RNF-027:** Mensajes de Error Informativos
- **RNF-028:** Compatibilidad Multi-Plataforma
- **RNF-030:** Ejecutable Standalone
- **RNF-032:** Gestión de Dependencias
- **RNF-040:** Timeout de Requests
- **RNF-042:** Ubicación de Datos

### 13.3 Requerimientos Medios
- Todos los demás RNF no clasificados como críticos o altos

### 13.4 Requerimientos Bajos (Deseables)
- **RNF-041:** Compresión de Datos
- **RNF-043:** Limpieza de Datos
- **RNF-045:** Personalización
- **RNF-046:** Configuración de IA
- **RNF-048, 049:** Logging y Monitoring

---

## 🔍 14. Herramientas y Metodologías de Validación

### 14.1 Herramientas de Testing
- **Rendimiento:** `time`, `memory_profiler`, `cProfile`
- **Base de Datos:** SQLite Browser, consultas de análisis
- **Seguridad:** Auditoría manual de código, testing de penetración básico
- **Usabilidad:** Testing con usuarios reales, métricas de tiempo
- **Compatibilidad:** VMs con diferentes sistemas operativos

### 14.2 Metodologías de Validación
- **Testing Continuo:** Validación en cada build
- **Testing de Carga:** Simulación de uso intensivo
- **Testing de Estrés:** Condiciones extremas de uso
- **Testing de Regresión:** Verificación tras cambios
- **Testing de Aceptación:** Validación con criterios definidos

---

## 📝 15. Notas de Implementación

### 15.1 Tecnologías Clave
- **Framework UI:** Flet (Flutter-based) para rendimiento nativo
- **Threading:** Python `threading` para operaciones asíncronas
- **Base de Datos:** SQLite con SQLAlchemy para performance y confiabilidad
- **Seguridad:** `hashlib` + `secrets` para protección de contraseñas
- **Configuración:** `python-dotenv` para gestión de variables de entorno

### 15.2 Patrones de Diseño Aplicados
- **Patrón Observer:** Para actualizaciones de UI
- **Patrón Strategy:** Para diferentes modos de estudio
- **Patrón Factory:** Para creación de componentes de UI
- **Patrón Singleton:** Para gestión de base de datos

### 15.3 Consideraciones de Arquitectura
- **Separación de Responsabilidades:** UI, Lógica de Negocio, Datos
- **Inversión de Dependencias:** Interfaces claras entre capas
- **Principio de Responsabilidad Única:** Cada clase con propósito específico
- **Principio Abierto/Cerrado:** Extensible para nuevos modos sin modificación

---

**Documento generado:** $(date)  
**Versión del proyecto:** 2.0.0 con Autenticación  
**Total de requerimientos no funcionales:** 50  
**Autor:** Sistema de Análisis de Requerimientos No Funcionales 
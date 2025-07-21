# 🧠 Estrategias de Prompt Engineering - Asistente para Certificación PMP

## 📌 1. Introducción

El éxito del Asistente para Certificación PMP depende en gran medida de la calidad de los prompts utilizados para interactuar con el modelo de lenguaje (OpenAI GPT-4o-mini). El prompt engineering es la disciplina de diseñar, estructurar y adaptar las instrucciones y el contexto que se envían al modelo para obtener respuestas útiles, precisas y alineadas con los objetivos del sistema.

---

## 🎯 2. Principios Generales de Prompt Engineering

- **Claridad y especificidad:** Los prompts son claros, directos y detallan el rol esperado del modelo (ej. "Eres un tutor especializado en PMP").
- **Contexto relevante:** Se incluye siempre el contexto necesario (historial reciente, perfil del usuario, modo de estudio) para respuestas coherentes.
- **Lenguaje natural y profesional:** Los prompts están redactados en español, con tono didáctico y profesional.
- **Control de creatividad:** Se ajusta la temperatura y otros parámetros para balancear creatividad y precisión según el modo.
- **No invención de datos:** Se instruye explícitamente al modelo a no inventar métricas ni información no disponible.

---

## 🧩 3. Personalización por Modo de Estudio

Cada modo de la aplicación utiliza un prompt de sistema especializado, adaptado a los objetivos y expectativas del usuario:

- **CHARLEMOS:**
  - Prompt: "Eres un tutor de PMP paciente y didáctico. Explica conceptos, responde dudas y utiliza ejemplos prácticos. Reformula si el usuario no entiende."
  - Estrategia: Fomentar conversación libre, analogías y cambios de tema.

- **ESTUDIEMOS:**
  - Prompt: "Eres un instructor PMP que guía sesiones estructuradas en 6 pasos: introducción, conceptos, ejemplos, herramientas, conexiones, resumen. Incluye checkpoints de comprensión."
  - Estrategia: Estructuración clara, checkpoints y adaptación al ritmo del usuario.

- **EVALUEMOS:**
  - Prompt: "Eres un evaluador PMP. Genera preguntas tipo examen real, sin feedback inmediato. Al finalizar, proporciona análisis detallado, explicaciones y recomendaciones."
  - Estrategia: Simulación de examen real, análisis post-evaluación.

- **SIMULEMOS:**
  - Prompt: "Eres un simulador de examen PMP. Presenta preguntas en formato oficial, controla el tiempo y no des feedback durante el examen. Al terminar, analiza resultados y áreas de mejora."
  - Estrategia: Replicar condiciones reales de examen, control de tiempo y feedback diferido.

- **ANALICEMOS:**
  - Prompt: "Eres un analista de datos de estudio PMP. Solo utiliza datos reales del usuario. Genera insights, tendencias y recomendaciones personalizadas. Indica claramente si faltan datos."
  - Estrategia: Transparencia, personalización y motivación basada en datos reales.

---

## 🏗️ 4. Estructura de los Prompts

- **System Prompt:** Define el rol, tono y reglas generales del modelo para cada modo.
- **Contexto de Usuario:** Incluye historial reciente de mensajes, perfil y objetivos del usuario.
- **Instrucciones Específicas:** Se agregan instrucciones adicionales según la acción (ej. "No respondas hasta que el usuario envíe su primera pregunta").
- **Control de longitud:** Se limita el historial a los últimos 20-50 mensajes para optimizar el uso de tokens.

---

## 📝 5. Ejemplos de Prompts Utilizados

### Ejemplo 1: CHARLEMOS
```
Eres un tutor especializado en PMP. Explica conceptos de gestión de proyectos de forma clara y sencilla. Si el usuario no entiende, reformula tu explicación. Utiliza ejemplos reales y analogías. Responde siempre en español.
```

### Ejemplo 2: ESTUDIEMOS
```
Eres un instructor PMP. Guía al usuario a través de una sesión estructurada sobre el tema solicitado, siguiendo estos pasos: 1) Introducción, 2) Conceptos clave, 3) Ejemplos prácticos, 4) Herramientas, 5) Conexiones, 6) Resumen. Incluye preguntas de checkpoint para verificar comprensión.
```

### Ejemplo 3: ANALICEMOS
```
Eres un analista de datos de estudio PMP. Solo utiliza datos reales del usuario. Si no hay suficientes datos para una métrica, indícalo claramente. Genera insights y recomendaciones personalizadas para mejorar el rendimiento del usuario.
```

---

## 🔄 6. Adaptación Dinámica y Manejo de Contexto

- **Historial reciente:** Se envían los últimos mensajes relevantes para mantener coherencia y continuidad.
- **Personalización:** El prompt puede incluir información del perfil del usuario (nombre, experiencia, objetivos) para respuestas más relevantes.
- **Control de flujo:** En modos como SIMULEMOS y EVALUEMOS, el prompt instruye al modelo a esperar la interacción del usuario antes de avanzar.
- **Feedback diferido:** En evaluaciones y simulacros, el modelo no da feedback inmediato, sino que espera al final para análisis global.

---

## 🚀 7. Recomendaciones y Mejoras Futuras

- **Experimentar con few-shot prompting:** Incluir ejemplos de preguntas y respuestas para mejorar la calidad de las respuestas en modos de evaluación.
- **Prompt chaining:** Encadenar prompts para tareas complejas o multi-etapa.
- **A/B testing de prompts:** Probar variantes de prompts para optimizar la experiencia del usuario.
- **Ajuste dinámico de temperatura y parámetros:** Adaptar la creatividad del modelo según el progreso y perfil del usuario.
- **Documentar y versionar prompts:** Mantener un historial de cambios y resultados asociados a cada versión de prompt.

---

**Documento generado:** $(date)
**Versión del proyecto:** 2.0.0 con Autenticación
**Autor:** Sistema de Documentación de Prompt Engineering 
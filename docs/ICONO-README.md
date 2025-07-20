# 🎨 Guía para Cambiar el Ícono de la Aplicación

## 📁 Archivos Necesarios

Para cambiar el ícono de tu aplicación Asistente para Certificación PMP, necesitas preparar los siguientes archivos:

### 1. Para la Ventana de la Aplicación
- **Archivo**: `assets/icon.png`
- **Formato**: PNG recomendado
- **Tamaño**: 64x64 píxeles o superior
- **Uso**: Se muestra en la barra de título de la ventana

### 2. Para el Ejecutable (Windows)
- **Archivo**: `assets/icon.ico`
- **Formato**: ICO (ícono de Windows)
- **Tamaños**: Múltiples tamaños en un solo archivo (16x16, 32x32, 48x48, 256x256)
- **Uso**: Ícono del archivo .exe en Windows

## 🔧 Pasos para Implementar

### Paso 1: Preparar tus Archivos de Ícono

1. **Obtén tu ícono base** (puede ser PNG, JPG, SVG)
2. **Crea el archivo PNG**:
   - Redimensiona a 64x64 píxeles mínimo
   - Guarda como `icon.png`
3. **Crea el archivo ICO**:
   - Usa herramientas online como [favicon.io](https://favicon.io) o [converticon.com](https://converticon.com)
   - O usa software como GIMP, Photoshop, o IcoFX
   - Guarda como `icon.ico`

### Paso 2: Colocar los Archivos

```
asistente-pmp/
├── assets/
│   ├── icon.png    ← Ícono para la ventana
│   └── icon.ico    ← Ícono para el ejecutable
└── ...
```

### Paso 3: Verificar la Implementación

El código ya está configurado para:
- ✅ Usar `assets/icon.png` como ícono de ventana
- ✅ Usar `assets/icon.ico` para el ejecutable
- ✅ Verificar que los archivos existan antes de aplicarlos

## 🛠️ Herramientas Recomendadas

### Conversión Online (Gratis)
- [favicon.io](https://favicon.io) - Convierte PNG a ICO
- [converticon.com](https://converticon.com) - Múltiples formatos
- [icogenerator.com](https://icogenerator.com) - Genera múltiples tamaños

### Software de Escritorio
- **GIMP** (Gratis) - Con plugin ICO
- **IcoFX** (Pago) - Especializado en íconos
- **Photoshop** (Pago) - Con plugin ICO

## 🚀 Compilar con el Nuevo Ícono

Una vez que tengas tus archivos de ícono en la carpeta `assets/`:

```bash
# Compilar el ejecutable
pyinstaller main.spec
```

El ejecutable resultante tendrá tu ícono personalizado.

## 📋 Checklist

- [ ] Crear/obtener imagen del ícono
- [ ] Generar `assets/icon.png` (64x64 o superior)
- [ ] Generar `assets/icon.ico` (múltiples tamaños)
- [ ] Colocar archivos en la carpeta `assets/`
- [ ] Probar la aplicación: `python main.py`
- [ ] Compilar ejecutable: `pyinstaller main.spec`
- [ ] Verificar que el ejecutable tenga el ícono correcto

## ❓ Resolución de Problemas

### El ícono no aparece en la ventana
- Verifica que `assets/icon.png` existe
- Verifica que el archivo no esté corrupto
- Reinicia la aplicación

### El ejecutable no tiene ícono
- Verifica que `assets/icon.ico` existe y es válido
- Recompila con `pyinstaller main.spec`
- En Windows, puede tardar unos momentos en actualizar el ícono

### Formatos alternativos
- **PNG**: Funciona para ventana, no para ejecutable Windows
- **JPG**: Funciona para ventana, no recomendado
- **ICO**: Solo para ejecutable Windows
- **ICNS**: Para macOS (si planeas compilar en Mac)

## 🎨 Consejos de Diseño

- **Simplicidad**: Los íconos pequeños deben ser simples y reconocibles
- **Contraste**: Usa colores que contrasten bien con fondos claros y oscuros
- **Consistencia**: Mantén el estilo consistente con la aplicación
- **Escalabilidad**: El diseño debe verse bien en diferentes tamaños 
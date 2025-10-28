# 📄 Generador de Catálogo PDF Automático

Herramienta Python para generar catálogos PDF profesionales a partir de datos en Google Sheets, con descarga automática de imágenes, diseño personalizado y gestión de errores.

## ✨ Características

- 📊 **Importación desde Google Sheets**: Lee datos directamente desde hojas de cálculo de Google
- 🖼️ **Descarga automática de imágenes**: Procesa imágenes de productos con reintentos y manejo de errores
- 🎨 **Diseño profesional**: Header y footer personalizables en cada página
- 📑 **Organización por categorías**: Agrupa productos automáticamente
- 💰 **Precios con descuentos**: Muestra precio actual y precio anterior tachado
- 📈 **Barra de progreso**: Seguimiento visual del procesamiento
- ⚠️ **Reporte de errores**: Identifica imágenes AVIF no soportadas y URLs con error 404

## 🛠️ Requisitos

### Dependencias

```bash
pip install pandas requests reportlab tqdm
```

### Versiones recomendadas
- Python 3.7+
- pandas >= 1.3.0
- reportlab >= 3.6.0
- requests >= 2.26.0
- tqdm >= 4.62.0

## 📋 Estructura del CSV

El archivo CSV debe contener las siguientes columnas:

| Columna | Tipo | Descripción | Obligatorio |
|---------|------|-------------|-------------|
| `CATEGORIA` | Texto | Categoría del producto | Sí |
| `NOMBRE` | Texto | Nombre del producto | Sí |
| `PRECIO` | Número | Precio actual | Sí |
| `PRECIO ANTES` | Número | Precio anterior (opcional) | No |
| `IMAGEN` | URL | URL de la imagen del producto | No |
| `SKU` | Texto | Código SKU | No |
| `ATRIBUTOS` | Texto | Características del producto | No |
| `DESCRIPCION` | Texto | Descripción detallada | No |

### Ejemplo de datos

```csv
CATEGORIA,NOMBRE,PRECIO,PRECIO ANTES,IMAGEN,SKU,ATRIBUTOS,DESCRIPCION
Electrónica,Laptop HP,2500.00,3000.00,https://ejemplo.com/laptop.jpg,LP-001,Intel i7 - 16GB RAM,Laptop profesional para trabajo
Hogar,Licuadora,150.00,,https://ejemplo.com/licuadora.jpg,LC-002,600W - 5 velocidades,Licuadora de alta potencia
```

## 🚀 Configuración

### 1. Preparar archivos de imagen

Crea una carpeta con las imágenes de header y footer:

```
C:\Users\user\Downloads\CATALOGO\IMG\
├── header.png
└── footer.png
```

### 2. Configurar URL del Google Sheet

Reemplaza en el código:

```python
csv_url = 'https://docs.google.com/spreadsheets/d/TU_ID_DE_HOJA/export?format=csv'
```

**Para obtener la URL:**
1. Abre tu Google Sheet
2. Ve a Archivo > Compartir > Publicar en la web
3. Selecciona la hoja específica
4. Elige formato CSV
5. Copia el enlace generado

### 3. Configurar rutas de salida

Modifica las rutas según tu sistema:

```python
output_path = r'C:\Users\user\Downloads\catalogo.pdf'
```

## 📖 Uso

### Ejecución básica

```bash
python generador_catalogo.py
```

### Flujo de trabajo

1. **Descarga datos**: El script descarga el CSV desde Google Sheets
2. **Procesa imágenes**: Descarga cada imagen con reintentos automáticos
3. **Genera páginas**: Crea el diseño con 3 productos por página
4. **Agrega header/footer**: Inserta imágenes personalizadas
5. **Exporta PDF**: Guarda el catálogo final

## 🎨 Personalización

### Modificar colores de precio

```python
COLOR_MAP = {
    'rojo': colors.red,
    'azul': colors.blue,
    'verde': colors.green,
}
```

### Ajustar tamaño de imágenes

```python
imagen.drawHeight = 210  # Altura en puntos
imagen.drawWidth = 210   # Ancho en puntos
```

### Cambiar productos por página

Busca esta línea y modifica el número:

```python
if current_page_items >= 3:  # Cambiar 3 por el número deseado
    elements.append(PageBreak())
```

### Ajustar estilos de texto

```python
titulo_estilo = ParagraphStyle(
    name='Titulo',
    fontSize=18,        # Tamaño de fuente
    leading=20,         # Espaciado de línea
    fontName="Helvetica-Bold"
)
```

## 🔧 Características técnicas

### Manejo de imágenes

- **Reintentos**: 3 intentos por imagen con espera entre intentos
- **Timeout**: 30 segundos por descarga
- **Formatos soportados**: JPG, PNG (AVIF no soportado, se registra)
- **Headers personalizados**: User-Agent para evitar bloqueos

### Gestión de errores

El script genera reportes de:
- ✅ Imágenes descargadas correctamente
- ⚠️ Imágenes AVIF no procesadas
- ❌ URLs con error 404
- 📊 Productos procesados vs total

### Optimizaciones

- Caché de imágenes de header/footer
- Procesamiento por lotes con barra de progreso
- Ajuste automático de texto para evitar desbordamiento

## 📊 Salida del script

```
Descargando datos del CSV...
CSV descargado exitosamente. 45 productos encontrados.

Procesando 45 productos en total...
Descargando imágenes y procesando productos...
Progreso total: 100%|████████████████| 45/45 [01:23<00:00, 1.85s/producto]

Construyendo PDF final...
PDF creado exitosamente en: C:\Users\user\Downloads\catalogo.pdf

Imágenes AVIF no procesadas:
- producto-123
Total de imágenes AVIF no procesadas: 1

Imágenes no encontradas (Error 404):
- imagen-vieja
Total de imágenes no encontradas: 2

Total de productos procesados: 45
```

## 🐛 Solución de problemas

### Error: "No se pudieron cargar las imágenes del header y footer"

**Solución**: Verifica que las rutas de las imágenes sean correctas:

```python
self.footer_path = r'C:\Users\user\Downloads\CATALOGO\IMG\footer.png'
self.header_path = r'C:\Users\user\Downloads\CATALOGO\IMG\header.png'
```

### Error: Timeout al descargar imágenes

**Solución**: Aumenta el timeout:

```python
def descargar_imagen(url, pbar=None, max_retries=3, timeout=60):  # 60 segundos
```

### Imágenes no se muestran en el PDF

**Causas posibles**:
- URLs inválidas o imágenes protegidas
- Formato AVIF (no soportado)
- Problemas de red

**Solución**: Revisa el reporte de errores al final de la ejecución

### PDF vacío o incompleto

**Solución**: Verifica que el CSV tenga datos y las columnas correctas

## 📝 Ejemplo completo

```python
# 1. Preparar Google Sheet con datos
# 2. Configurar rutas
output_path = r'C:\Users\tu_usuario\Desktop\catalogo.pdf'
csv_url = 'https://docs.google.com/spreadsheets/d/ABC123/export?format=csv'

# 3. Ejecutar script
python generador_catalogo.py

# 4. Resultado: catalogo.pdf con diseño profesional
```

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/NuevaCaracteristica`)
3. Commit tus cambios (`git commit -m 'Añadir nueva característica'`)
4. Push a la rama (`git push origin feature/NuevaCaracteristica`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto es de código abierto y está disponible bajo la licencia MIT.

## 🔗 Recursos adicionales

- [Documentación de ReportLab](https://www.reportlab.com/docs/reportlab-userguide.pdf)
- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [Google Sheets API](https://developers.google.com/sheets/api)

## 📧 Contacto

Para preguntas o sugerencias, abre un issue en GitHub.

---

**Nota**: Este script está diseñado para Windows. Para Linux/Mac, ajusta las rutas usando `/` en lugar de `\`.
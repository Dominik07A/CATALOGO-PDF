import pandas as pd
import requests
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image, KeepInFrame
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.platypus.frames import Frame
from reportlab.platypus.doctemplate import PageTemplate
from reportlab.pdfgen import canvas
from tqdm import tqdm
import time

COLOR_MAP = {
    'rojo': colors.red,
    'azul': colors.blue,
    'verde': colors.green,
}

output_path = r'C:\Users\user\Downloads\catalogo.pdf'

def procesar_atributos(atributos_texto):
    if pd.isna(atributos_texto) or str(atributos_texto).strip() == '':
        return None
    
    elementos = []
    elementos.append(Paragraph(f"<b>{atributos_texto}</b>", datos_estilo))
    return elementos

print("Descargando datos del CSV...")
csv_url = 'https://docs.google.com/spreadsheets/d/TU_ID_DE_HOJA/export?format=csv'
data = pd.read_csv(csv_url)
print(f"CSV descargado exitosamente. {len(data)} productos encontrados.")

def descargar_imagen(url, pbar=None, max_retries=3, timeout=30, avif_errors=None, error_404_list=None):
    """
    Función mejorada para descargar imágenes con mejor manejo de errores y headers
    """
    if pd.isna(url) or str(url).strip() == '':
        if pbar:
            pbar.update(1)
        return None

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive'
    }

    # Si es una imagen AVIF, registrarla y saltar el proceso
    if url.lower().endswith('.avif'):
        if avif_errors is not None:
            avif_errors.append(url)
        if pbar:
            pbar.update(1)
        return None

    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
            
            if response.status_code == 200:
                imagen = Image(BytesIO(response.content))
                imagen.drawHeight = 210
                imagen.drawWidth = 210
                if pbar:
                    pbar.update(1)
                return imagen
            
            elif response.status_code == 404:
                if attempt == max_retries - 1:  # Solo registrar después del último intento
                    if error_404_list is not None:
                        error_404_list.append(url)
            
            time.sleep(1)
            
        except Exception:
            if attempt < max_retries - 1:
                time.sleep(1)
            continue
    
    if pbar:
        pbar.update(1)
    return None

def procesar_atributos(atributos_texto):
    if pd.isna(atributos_texto) or str(atributos_texto).strip() == '':
        return None
    
    elementos = []
    elementos.append(Paragraph(f"<b>{atributos_texto}</b>", datos_estilo))
    return elementos


class PDFWithHeaderAndFooter(SimpleDocTemplate):
    def __init__(self, *args, **kwargs):
        kwargs['pageCompression'] = 0
        SimpleDocTemplate.__init__(self, *args, **kwargs)
        self.footer_path = r'C:\Users\user\Downloads\CATALOGO\IMG\footer.png'
        self.header_path = r'C:\Users\user\Downloads\CATALOGO\IMG\header.png'
        self._header_image = None
        self._footer_image = None
        
    def handle_pageBegin(self):
        self._handle_pageBegin()
        
    def _load_images(self):
        try:
            print("Cargando imágenes de header y footer...")
            if self._footer_image is None:
                self._footer_image = Image(self.footer_path)
                footer_scale = 0.25
                self._footer_image.drawWidth = self._footer_image.imageWidth * footer_scale
                self._footer_image.drawHeight = self._footer_image.imageHeight * footer_scale

            if self._header_image is None:
                self._header_image = Image(self.header_path)
                header_scale = 0.25
                self._header_image.drawWidth = self._header_image.imageWidth * header_scale
                self._header_image.drawHeight = self._header_image.imageHeight * header_scale
                
            print("Imágenes de header y footer cargadas exitosamente.")
            return True
        except Exception as e:
            print(f"Error al cargar las imágenes: {str(e)}")
            return False
    
    def build(self, flowables):
        if not self._load_images():
            raise Exception("No se pudieron cargar las imágenes del header y footer")
        
        def draw_header_and_footer(canvas, doc):
            canvas.saveState()
            
            footer_offset = -37
            footer_y_position = doc.bottomMargin - 72
            if self._footer_image:
                self._footer_image.drawOn(canvas, doc.leftMargin + footer_offset, footer_y_position)
            
            header_offset = -37
            header_y_position = doc.height - self._header_image.drawHeight + 82
            if self._header_image:
                self._header_image.drawOn(canvas, doc.leftMargin + header_offset, header_y_position)
            
            canvas.restoreState()
        
        frame = Frame(
            self.leftMargin,
            self.bottomMargin,
            self.width,
            self.height - 50,
            leftPadding=0,
            rightPadding=0,
            topPadding=0,
            bottomPadding=0,
            showBoundary=0,
        )
        
        template = PageTemplate('normal', [frame], onPage=draw_header_and_footer)
        self.addPageTemplates([template])
        
        print("Generando páginas del PDF...")
        for flow in flowables:
            if isinstance(flow, PageBreak):
                continue
        
        SimpleDocTemplate.build(self, flowables)

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        pass

print("Iniciando generación del PDF...")
doc = PDFWithHeaderAndFooter(output_path, pagesize=letter, leftMargin=30, rightMargin=30, topMargin=5)
elements = []
avif_errors = []  # Agregar esta línea
error_404_list = []  # Lista para almacenar URLs con error 404

# Estilo para categoría visible (primera página)
categoria_estilo = ParagraphStyle(
    name='Categoria',
    fontSize=56,
    leading=58,
    spaceAfter=6,
    fontName="Helvetica-Bold",
    textColor=colors.white,
    leftIndent=-22,
)

# Estilo para categoría invisible (páginas siguientes)
categoria_estilo_invisible = ParagraphStyle(
    name='CategoriaInvisible',
    fontSize=56,
    leading=58,
    spaceAfter=6,
    fontName="Helvetica-Bold",
    leftIndent=-22,
    textColor=colors.Color(1, 1, 1, alpha=0)  # Color completamente transparente
)

titulo_estilo = ParagraphStyle(
    name='Titulo',
    fontSize=18,
    leading=20,
    spaceAfter=6,
    fontName="Helvetica-Bold"
)

descripcion_estilo = ParagraphStyle(
    name='Descripcion',
    fontSize=10,
    leading=12,
    wordWrap='CJK',
    alignment=TA_JUSTIFY
)

datos_estilo = ParagraphStyle(
    name='Datos',
    fontSize=10,
    leading=12
)

precio_estilo = ParagraphStyle(
    name='Precio',
    fontSize=20,
    leading=22,
    fontName="Helvetica-Bold",
    textColor=colors.white,
    spaceAfter=8,
)

precio_anterior_estilo = ParagraphStyle(
    name='PrecioAnterior',
    fontSize=20,
    leading=22,
    fontName="Helvetica-Bold",
    textColor=colors.red,
    spaceAfter=8,
)

ancho_precio = 110
ancho_linea = 150

linea_divisoria = TableStyle([
    ('LINEABOVE', (0,0), (-1,0), 1, colors.black),
    ('TOPPADDING', (0,0), (-1,0), 5),
    ('BOTTOMPADDING', (0,0), (-1,0), 5),
])

data = data.replace('', pd.NA)
grouped_by_category = data.groupby('CATEGORIA')
total_productos = len(data)
productos_procesados = 0

print(f"\nProcesando {total_productos} productos en total...")
print("Descargando imágenes y procesando productos...")

# Crear barra de progreso para la descarga de imágenes
with tqdm(total=total_productos, desc="Progreso total", unit="producto", ncols=100) as pbar:
    for idx, (category, group) in enumerate(grouped_by_category):
        if idx > 0:
            elements.append(PageBreak())
        
        current_page_items = 0
        primera_pagina_categoria = True
        
        for index, row in group.iterrows():
            # Agregar título de categoría al inicio de cada página
            if current_page_items == 0:
                elements.append(Spacer(1, -43))
                if pd.notna(category):
                    # Usar siempre el mismo estilo para todas las páginas
                    category_title = Paragraph(f"<b>{category}</b>", categoria_estilo)
                    elements.append(category_title)
                    elements.append(Spacer(1, 4))
            
            if current_page_items >= 3:
                elements.append(PageBreak())
                current_page_items = 0
                primera_pagina_categoria = False
                # Agregar título de categoría después del salto de página
                elements.append(Spacer(1, -43))
                if pd.notna(category):
                    category_title = Paragraph(f"<b>{category}</b>", categoria_estilo)
                    elements.append(category_title)
                    elements.append(Spacer(1, 4))
            
            imagen = descargar_imagen(row.get('IMAGEN'), pbar, avif_errors=avif_errors, error_404_list=error_404_list)
            if imagen:
                imagen_element = imagen
            else:
                imagen_element = Paragraph("", datos_estilo)

            columna_derecha = []
            
            if pd.notna(row.get('NOMBRE')):
                titulo = Paragraph(str(row['NOMBRE']), titulo_estilo)
                columna_derecha.extend([titulo, Spacer(1, 8)])

            if pd.notna(row.get('PRECIO')):
                precio_actual = f'S/{row["PRECIO"]:.2f}'
                precio_tabla_contenido = [[Paragraph(precio_actual, precio_estilo)]]
                anchos_columna = [ancho_precio]
                
                if pd.notna(row.get('PRECIO ANTES')):
                    precio_anterior = f'<strike>S/{row["PRECIO ANTES"]:.2f}</strike>'
                    precio_tabla_contenido[0].append(Paragraph(precio_anterior, precio_anterior_estilo))
                    anchos_columna.append(105)

                precio = Table(
                    precio_tabla_contenido,
                    colWidths=anchos_columna,
                    rowHeights=[30],
                )

                precio.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (0, 0), colors.red),
                    ('BACKGROUND', (1, 0), (1, 0), None),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 10),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                ]))
                
                columna_derecha.extend([precio, Spacer(1, 12)])

            linea = Table([['']],colWidths=[ancho_linea], rowHeights=[2])
            linea.setStyle(linea_divisoria)
            columna_derecha.extend([linea, Spacer(1, 3)])

            if pd.notna(row.get('CATEGORIA')):
                categoria = Paragraph(f"<b>Categoría:</b> {row['CATEGORIA']}", datos_estilo)
                columna_derecha.append(categoria)
            
            if pd.notna(row.get('SKU')):
                sku = Paragraph(f"<b>SKU:</b> {row['SKU']}", datos_estilo)
                columna_derecha.append(sku)
            
            atributos_elementos = procesar_atributos(row.get('ATRIBUTOS'))
            if atributos_elementos:
                columna_derecha.extend(atributos_elementos)
                
            columna_derecha.extend([Spacer(1, 5), linea, Spacer(1, 6)])

            if pd.notna(row.get('DESCRIPCION')):
                descripcion_texto = str(row['DESCRIPCION'])
                palabras = descripcion_texto.split()
                nueva_descripcion = []
                linea_actual = []
                
                for palabra in palabras:
                    linea_actual.append(palabra)
                    if len(' '.join(linea_actual)) > 70:
                        nueva_descripcion.append(' '.join(linea_actual[:-1]))
                        linea_actual = [palabra]
                if linea_actual:
                    nueva_descripcion.append(' '.join(linea_actual))
                    
                descripcion = Paragraph('<br/>'.join(nueva_descripcion), descripcion_estilo)
                columna_derecha.append(descripcion)

            data_tabla = [[imagen_element, columna_derecha]]
            tabla = Table(data_tabla, colWidths=[200, 400])
            
            tabla.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 5),
                ('LEFTPADDING', (1, 0), (1, -1), 45),
                ('RIGHTPADDING', (0, 0), (0, 0), 0),
                ('RIGHTPADDING', (1, 0), (1, 0), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ]))
            
            elements.append(tabla)
            
            if current_page_items < 2:
                elements.append(Spacer(1, 5))
            
            current_page_items += 1
            productos_procesados += 1

print("\nConstruyendo PDF final...")
doc.build(elements)
print(f"\nPDF creado exitosamente en: {output_path}")
if avif_errors:
    print("\nImágenes AVIF no procesadas:")
    for url in avif_errors:
        nombre_producto = url.split('/')[-1].replace('.avif', '').replace('ImageToStl.com_', '')
        print(f"- {nombre_producto}")
    print(f"\nTotal de imágenes AVIF no procesadas: {len(avif_errors)}")
if error_404_list:
    print("\nImágenes no encontradas (Error 404):")
    for url in error_404_list:
        nombre_producto = url.split('/')[-1].replace('.jpg', '').replace('.png', '').replace('-300x300', '')
        print(f"- {nombre_producto}")
    print(f"\nTotal de imágenes no encontradas: {len(error_404_list)}")

print(f"Total de productos procesados: {productos_procesados}")
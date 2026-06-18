import os
import logging
import traceback
from datetime import datetime
from PIL import Image as PILImage
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                 Table, TableStyle, Image as RLImage)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from utils.paths import get_user_data_dir


# bueno, esta función hace el PDF con los resultados del paciente
def generar_reporte(paciente_id, datos_paciente, resultado, carpeta=None):
    """
    bueno, genera el reporte en PDF con los datos del paciente y los resultados del análisis.
    retorna la ruta del PDF o None si algo salió mal.
    """
    carpeta = carpeta or os.path.join(get_user_data_dir(), "reportes")
    os.makedirs(carpeta, exist_ok=True)

    # bueno, el nombre del PDF lleva el DNI y la hora para que no se repita
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    dni = datos_paciente.get('dni', 'paciente') or 'paciente'
    nombre_archivo = f"reporte_{dni}_{timestamp}.pdf"
    ruta_pdf = os.path.join(carpeta, nombre_archivo)

    try:
        doc = SimpleDocTemplate(
            ruta_pdf,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )

        styles = getSampleStyleSheet()
        story = []

        # bueno, estilos para que se vea bonito
        estilo_titulo = ParagraphStyle(
            "titulo",
            parent=styles["Normal"],
            fontSize=14,
            fontName="Helvetica-Bold",
            alignment=TA_CENTER,
            spaceAfter=6
        )
        estilo_fecha = ParagraphStyle(
            "fecha",
            parent=styles["Normal"],
            fontSize=10,
            fontName="Helvetica",
            alignment=TA_RIGHT,
            spaceAfter=12
        )
        estilo_seccion = ParagraphStyle(
            "seccion",
            parent=styles["Normal"],
            fontSize=11,
            fontName="Helvetica-Bold",
            textColor=colors.HexColor("#2563eb"),
            spaceAfter=6
        )
        estilo_normal = ParagraphStyle(
            "normal_custom",
            parent=styles["Normal"],
            fontSize=10,
            fontName="Helvetica",
            spaceAfter=4
        )
        estilo_resultado = ParagraphStyle(
            "resultado",
            parent=styles["Normal"],
            fontSize=10,
            fontName="Helvetica-Bold",
            textColor=colors.HexColor("#ef4444"),
            spaceAfter=4
        )
        estilo_anexo = ParagraphStyle(
            "anexo",
            parent=styles["Normal"],
            fontSize=12,
            fontName="Helvetica-Bold",
            alignment=TA_CENTER,
            spaceBefore=12,
            spaceAfter=10
        )

        # bueno, título del reporte
        story.append(Paragraph("Detección de prueba de Bacilos", estilo_titulo))
        story.append(Spacer(1, 0.2*cm))

        # bueno, fecha de hoy
        fecha_hoy = datetime.now().strftime("%d/%m/%Y")
        story.append(Paragraph(fecha_hoy, estilo_fecha))

        # bueno, línea separadora
        story.append(Table([[""]], colWidths=[17*cm],
                           style=TableStyle([
                               ("LINEBELOW", (0, 0), (-1, -1), 0.5,
                                colors.HexColor("#cbd5e1"))
                           ])))
        story.append(Spacer(1, 0.4*cm))

        # bueno, datos del paciente
        nombre_completo = (
            f"{datos_paciente.get('nombre', '')} "
            f"{datos_paciente.get('apellido_paterno', '')} "
            f"{datos_paciente.get('apellido_materno', '')}"
        ).strip()

        story.append(Paragraph("Paciente", estilo_seccion))
        story.append(Paragraph(nombre_completo, estilo_normal))
        story.append(Spacer(1, 0.2*cm))

        # bueno, tabla con los datos del paciente
        datos_tabla = [
            ["DNI:", datos_paciente.get("dni", ""),
             "Edad:", datos_paciente.get("edad", "")],
            ["Sexo:", datos_paciente.get("sexo", ""),
             "Fecha de nacimiento:", datos_paciente.get("fecha_nacimiento", "")],
            ["Domicilio:", datos_paciente.get("domicilio", ""), "", ""],
            ["Médico solicitante:", datos_paciente.get("medico_solicitante", ""),
             "N° muestra:", datos_paciente.get("numero_muestra", "")],
            ["Fecha del análisis:", datos_paciente.get("fecha_analisis", ""), "", ""],
        ]

        tabla_paciente = Table(datos_tabla, colWidths=[3.5*cm, 5*cm, 4*cm, 4.5*cm])
        tabla_paciente.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#333333")),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(tabla_paciente)
        story.append(Spacer(1, 0.4*cm))

        # bueno, otra línea separadora
        story.append(Table([[""]], colWidths=[17*cm],
                           style=TableStyle([
                               ("LINEBELOW", (0, 0), (-1, -1), 0.5,
                                colors.HexColor("#cbd5e1"))
                           ])))
        story.append(Spacer(1, 0.4*cm))

        # bueno, resultados del análisis
        story.append(Paragraph("Resultados del análisis", estilo_seccion))

        total = resultado.get("total_bacilos", 0)
        promedio = resultado.get("promedio", 0)
        diagnostico = resultado.get("diagnostico", "")

        story.append(Paragraph(
            f"<b>Número total de bacilos en 20 campos:</b> {total}", estilo_normal))
        story.append(Paragraph(
            f"<b>Promedio por campo:</b> {promedio}", estilo_normal))
        story.append(Paragraph(
            f"<b>Diagnóstico final:</b> {diagnostico}", estilo_resultado))

        story.append(Spacer(1, 0.4*cm))

        # bueno, otra línea separadora
        story.append(Table([[""]], colWidths=[17*cm],
                           style=TableStyle([
                               ("LINEBELOW", (0, 0), (-1, -1), 0.5,
                                colors.HexColor("#cbd5e1"))
                           ])))

        # bueno, anexo con las fotos procesadas
        story.append(Paragraph("Anexo — Imágenes procesadas", estilo_anexo))

        imagenes = resultado.get("imagenes_procesadas", [])
        if imagenes:
            ancho_img = 7.5*cm
            alto_img = 6.0*cm
            cols = 2
            filas_imgs = []
            fila_actual = []

            for i, ruta in enumerate(imagenes):
                img_obj = None
                if os.path.exists(ruta):
                    try:
                        # bueno, revisamos que la foto esté bien antes de ponerla en el PDF
                        with PILImage.open(ruta) as pil_img:
                            pil_img.verify()
                        img_obj = RLImage(ruta, width=ancho_img, height=alto_img)
                    except Exception as img_err:
                        logging.getLogger(__name__).warning("No se pudo poner la foto %s: %s", ruta, img_err)
                        img_obj = Paragraph(f"Campo {i+1}", estilo_normal)
                else:
                    img_obj = Paragraph(f"Campo {i+1}", estilo_normal)

                celda = [img_obj, Paragraph(f"Campo {i+1}",
                                             ParagraphStyle("pie", fontSize=7,
                                                            alignment=TA_CENTER))]
                fila_actual.append(celda)

                if len(fila_actual) == cols:
                    filas_imgs.append(fila_actual)
                    fila_actual = []

            # bueno, si la última fila no está completa, la rellenamos
            while len(fila_actual) > 0 and len(fila_actual) < cols:
                fila_actual.append([Spacer(1, 1)])
            if fila_actual:
                filas_imgs.append(fila_actual)

            for fila in filas_imgs:
                tabla_imgs = Table([fila],
                                   colWidths=[8.5*cm] * cols)
                tabla_imgs.setStyle(TableStyle([
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                ]))
                story.append(tabla_imgs)

        # bueno, armamos el PDF
        doc.build(story)
        logging.getLogger(__name__).info("PDF generado correctamente: %s", ruta_pdf)
        return ruta_pdf

    except Exception as e:
        logging.getLogger(__name__).exception("Error al generar reporte")
        return None

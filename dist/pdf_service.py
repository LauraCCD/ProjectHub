from datetime import datetime
from typing import Any, Dict, List
import os

class PDFService:
    def __init__(self):
        pass

    def exportar(self, module_name: str, data: List[Dict[str, Any]], user_name: str) -> str:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"REPORTE_{module_name.upper()}_{timestamp}.pdf"
        import tkinter.filedialog as fd
        filepath = fd.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfile=filename,
            title="Guardar reporte PDF"
        )
        if not filepath:
            return filename  # usuario canceló
        
        doc = SimpleDocTemplate(filepath, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []

        # Título
        elements.append(Paragraph(f"Reporte de {module_name}", styles["Title"]))
        elements.append(Paragraph(f"Generado por: {user_name}", styles["Normal"]))
        elements.append(Paragraph(f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", styles["Normal"]))
        elements.append(Spacer(1, 20))

        if data:
            headers = list(data[0].keys())
            table_data = [headers]
            for item in data:
                table_data.append([str(item[h]) for h in headers])

            table = Table(table_data, repeatRows=1)
            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4ecca3")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 10),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f0f0f0")]),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("FONTSIZE", (0, 1), (-1, -1), 9),
                ("PADDING", (0, 0), (-1, -1), 6),
            ]))
            elements.append(table)
        else:
            elements.append(Paragraph("No hay datos para mostrar.", styles["Normal"]))

        doc.build(elements)
        return filepath
# coding: utf-8
"""
Export Service Module

Provides data export functionality in multiple formats:
- CSV export for spreadsheet analysis
- Excel export with formatting
- PDF reports with charts and tables
"""
from datetime import date
from typing import Dict, Any, List
from io import BytesIO, StringIO
import csv

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from loguru import logger


class ExportService:
    """Service for exporting analytics data in various formats"""

    @staticmethod
    def export_to_csv(data: List[Dict[str, Any]], filename: str = "export.csv") -> BytesIO:
        """
        Export data to CSV format

        Args:
            data: List of dictionaries to export
            filename: Name for the CSV file

        Returns:
            BytesIO object containing CSV data
        """
        logger.info(f"Exporting to CSV: {filename}")

        if not data:
            logger.warning("No data to export")
            data = [{"message": "No data available"}]

        output = StringIO()

        # Get all unique keys from all dictionaries
        all_keys = set()
        for item in data:
            all_keys.update(item.keys())

        fieldnames = sorted(all_keys)

        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

        # Convert to BytesIO
        bytes_output = BytesIO()
        bytes_output.write(output.getvalue().encode('utf-8-sig'))  # UTF-8 with BOM for Excel compatibility
        bytes_output.seek(0)

        return bytes_output

    @staticmethod
    def export_to_excel(data: List[Dict[str, Any]], sheet_name: str = "Data", filename: str = "export.xlsx") -> BytesIO:
        """
        Export data to Excel format with formatting

        Args:
            data: List of dictionaries to export
            sheet_name: Name for the Excel sheet
            filename: Name for the Excel file

        Returns:
            BytesIO object containing Excel data
        """
        logger.info(f"Exporting to Excel: {filename}")

        if not data:
            logger.warning("No data to export")
            data = [{"message": "No data available"}]

        # Create DataFrame
        df = pd.DataFrame(data)

        # Create Excel file in memory
        output = BytesIO()

        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=False)

            # Get workbook and worksheet
            workbook = writer.book
            worksheet = writer.sheets[sheet_name]

            # Format header row
            for cell in worksheet[1]:
                cell.font = cell.font.copy(bold=True)
                cell.fill = cell.fill.copy(fgColor="CCCCCC")

            # Auto-adjust column widths
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width

        output.seek(0)
        return output

    @staticmethod
    def export_to_pdf(
        title: str,
        data: List[Dict[str, Any]],
        summary: Dict[str, Any] = None,
        filename: str = "report.pdf"
    ) -> BytesIO:
        """
        Export data to PDF format with formatting

        Args:
            title: Report title
            data: List of dictionaries to export as table
            summary: Optional summary statistics to display at top
            filename: Name for the PDF file

        Returns:
            BytesIO object containing PDF data
        """
        logger.info(f"Exporting to PDF: {filename}")

        output = BytesIO()
        doc = SimpleDocTemplate(output, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()

        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1F2937'),
            spaceAfter=30,
            alignment=TA_CENTER
        )

        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#374151'),
            spaceAfter=12,
            spaceBefore=12
        )

        # Title
        elements.append(Paragraph(title, title_style))
        elements.append(Spacer(1, 0.2*inch))

        # Date range
        date_text = f"Generado: {date.today().strftime('%d/%m/%Y')}"
        elements.append(Paragraph(date_text, styles['Normal']))
        elements.append(Spacer(1, 0.3*inch))

        # Summary section
        if summary:
            elements.append(Paragraph("Resumen", heading_style))

            summary_data = [[key, str(value)] for key, value in summary.items()]
            summary_table = Table(summary_data, colWidths=[3*inch, 3*inch])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F3F4F6')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1F2937')),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
            ]))
            elements.append(summary_table)
            elements.append(Spacer(1, 0.3*inch))

        # Data table
        if data:
            elements.append(Paragraph("Datos Detallados", heading_style))

            # Prepare table data
            if not data:
                data = [{"message": "No data available"}]

            # Get headers
            headers = list(data[0].keys())
            table_data = [headers]

            # Add data rows (limit to prevent huge PDFs)
            for item in data[:100]:  # Limit to 100 rows
                row = [str(item.get(key, '')) for key in headers]
                table_data.append(row)

            # Calculate column widths dynamically
            num_cols = len(headers)
            col_width = 6.5 * inch / num_cols
            col_widths = [col_width] * num_cols

            # Create table
            data_table = Table(table_data, colWidths=col_widths, repeatRows=1)
            data_table.setStyle(TableStyle([
                # Header style
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3B82F6')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),

                # Data style
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#1F2937')),
                ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),

                # Alternating row colors
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F9FAFB')])
            ]))

            elements.append(data_table)

            if len(data) > 100:
                elements.append(Spacer(1, 0.2*inch))
                elements.append(Paragraph(
                    f"Nota: Mostrando 100 de {len(data)} registros. Exporte a CSV/Excel para ver todos los datos.",
                    styles['Italic']
                ))

        # Build PDF
        doc.build(elements)
        output.seek(0)

        return output

    @staticmethod
    def export_centers_comparison(centers_data: Dict[str, Any], format: str = "csv") -> BytesIO:
        """
        Export centers comparison data

        Args:
            centers_data: Centers comparison data from analytics
            format: Export format (csv, excel, pdf)

        Returns:
            BytesIO object containing exported data
        """
        logger.info(f"Exporting centers comparison as {format}")

        # Flatten the data for export
        flat_data = []
        for center in centers_data.get("centers", []):
            flat_item = {
                "Centro": center["center_name"],
                "Codigo": center["center_code"],
                "Ciudad": center.get("city", ""),
                "Activo": "Si" if center["is_active"] else "No",
                "Total Ordenes": center["metrics"]["total_orders"],
                "Total Resultados": center["metrics"]["total_results"],
                "Total Mascotas": center["metrics"]["total_pets"],
                "Promedio Ordenes/Dia": center["metrics"]["avg_daily_orders"],
                "Dias Activos": center["metrics"]["active_days"],
                "Tasa Completacion %": center["performance"]["avg_completion_rate"],
                "Tiempo Procesamiento (min)": center["performance"]["avg_processing_minutes"],
                "Crecimiento %": center["growth_rate_percent"]
            }
            flat_data.append(flat_item)

        if format == "csv":
            return ExportService.export_to_csv(flat_data, "centros_comparacion.csv")
        elif format == "excel":
            return ExportService.export_to_excel(flat_data, "Comparacion de Centros", "centros_comparacion.xlsx")
        elif format == "pdf":
            summary = {
                "Total de Centros": centers_data.get("total_centers", 0),
                "Centros Activos": centers_data.get("active_centers", 0),
                "Periodo": f"{centers_data['period']['days']} dias"
            }
            return ExportService.export_to_pdf(
                "Comparacion de Centros Veterinarios",
                flat_data,
                summary,
                "centros_comparacion.pdf"
            )
        else:
            raise ValueError(f"Unsupported format: {format}")

    @staticmethod
    def export_top_tests(tests_data: Dict[str, Any], format: str = "csv") -> BytesIO:
        """
        Export top tests data

        Args:
            tests_data: Top tests data from analytics
            format: Export format (csv, excel, pdf)

        Returns:
            BytesIO object containing exported data
        """
        logger.info(f"Exporting top tests as {format}")

        # Flatten the data for export
        flat_data = []
        for test in tests_data.get("tests", []):
            flat_item = {
                "Codigo": test["code"],
                "Nombre": test["name"],
                "Total Solicitudes": test["total_count"],
                "Numero de Centros": test["num_centers"],
                "Promedio por Dia": test["avg_per_day"],
                "Crecimiento %": test["growth_rate_percent"]
            }
            flat_data.append(flat_item)

        if format == "csv":
            return ExportService.export_to_csv(flat_data, "top_pruebas.csv")
        elif format == "excel":
            return ExportService.export_to_excel(flat_data, "Top Pruebas", "top_pruebas.xlsx")
        elif format == "pdf":
            summary = {
                "Total de Pruebas": tests_data.get("total_tests", 0),
                "Periodo": f"{tests_data['period']['days']} dias"
            }
            return ExportService.export_to_pdf(
                "Pruebas Mas Solicitadas",
                flat_data,
                summary,
                "top_pruebas.pdf"
            )
        else:
            raise ValueError(f"Unsupported format: {format}")

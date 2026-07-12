"""
core/exporter.py

Módulo de exportación de resultados de diagnóstico.
Soporta formatos JSON y PDF.

El módulo intenta importar reportlab para PDF. Si no está disponible,
solo exporta JSON y avisa al usuario.
"""

from __future__ import annotations
import json
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .runner import DiagnosticResult

_REPORTLAB_AVAILABLE = False
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.units import inch
    _REPORTLAB_AVAILABLE = True
except ImportError:
    pass


def export_json(result: "DiagnosticResult", path: Path) -> bool:
    """Exporta el resultado del diagnóstico a formato JSON.
    
    Args:
        result: Resultado del diagnóstico (DiagnosticResult).
        path: Ruta del archivo de destino (.json).
    
    Returns:
        True si la exportación fue exitosa, False en caso contrario.
    """
    try:
        data = result.to_dict()
        if result.report:
            data["report"] = {
                "board": result.report.board,
                "chip": result.report.chip,
                "vcc_mv": result.report.vcc_mv,
                "led_ok": result.report.led_ok,
                "digital_results": result.report.digital_results,
                "adc_results": result.report.adc_results,
                "eeprom_ok": result.report.eeprom_ok,
                "ram_free": result.report.ram_free,
                "spi_ok": result.report.spi_ok,
                "i2c_devices": result.report.i2c_devices,
                "clock_drift_ms": result.report.clock_drift_ms,
                "done": result.report.done,
                "done_code": result.report.done_code,
            }
        data["exported_at"] = datetime.now().isoformat()

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error exportando JSON: {e}")
        return False


def export_pdf(result: "DiagnosticResult", path: Path) -> bool:
    """Exporta el resultado del diagnóstico a formato PDF con tabla de resultados.
    
    Args:
        result: Resultado del diagnóstico (DiagnosticResult).
        path: Ruta del archivo de destino (.pdf).
    
    Returns:
        True si la exportación fue exitosa, False en caso contrario.
    """
    if not _REPORTLAB_AVAILABLE:
        print(
            "reportlab no está instalado. No se puede exportar a PDF.\n"
            "Instálalo con: pip install reportlab"
        )
        return False

    try:
        doc = SimpleDocTemplate(
            str(path),
            pagesize=A4,
            rightMargin=0.75 * inch,
            leftMargin=0.75 * inch,
            topMargin=0.75 * inch,
            bottomMargin=0.75 * inch,
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "TitleStyle",
            parent=styles["Title"],
            fontSize=20,
            spaceAfter=12,
        )
        subtitle_style = ParagraphStyle(
            "SubtitleStyle",
            parent=styles["Normal"],
            fontSize=10,
            textColor=colors.grey,
            spaceAfter=20,
        )
        section_style = ParagraphStyle(
            "SectionStyle",
            parent=styles["Heading2"],
            fontSize=13,
            spaceBefore=12,
            spaceAfter=6,
            textColor=colors.HexColor("#333333"),
        )

        elements = []

        # Título
        elements.append(
            Paragraph("ArduCheck — Informe de Diagnóstico", title_style)
        )
        elements.append(
            Paragraph(
                f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  |  "
                f"Puerto: {result.port}",
                subtitle_style,
            )
        )

        # Veredicto
        verdict_color = {
            "GOOD": colors.HexColor("#0a8f3c"),
            "WARN": colors.HexColor("#cc8b00"),
            "FAIL": colors.HexColor("#c0182c"),
        }.get(result.verdict, colors.black)

        verdict_emoji = {"GOOD": "✅", "WARN": "⚠️", "FAIL": "❌"}.get(
            result.verdict, "❓"
        )
        verdict_text = f"{verdict_emoji} {result.verdict}  (score: {result.score}/100)"

        verdict_style = ParagraphStyle(
            "VerdictStyle",
            parent=styles["Normal"],
            fontSize=16,
            textColor=verdict_color,
            spaceAfter=10,
        )
        elements.append(Paragraph(verdict_text, verdict_style))
        elements.append(Spacer(1, 8))

        # Info general
        elements.append(Paragraph("Información General", section_style))
        info_data = [
            ["Placa", result.board],
            ["Chip", result.chip],
            ["Puerto", result.port],
        ]
        if result.report and result.report.vcc_mv:
            info_data.append(["Voltaje", f"{result.report.vcc_mv / 100:.2f} V"])

        info_table = Table(info_data, colWidths=[2 * inch, 4 * inch])
        info_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#e8f4f8")),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, colors.HexColor("#f9f9f9")]),
        ]))
        elements.append(info_table)
        elements.append(Spacer(1, 12))

        # Detalles
        if result.details:
            elements.append(Paragraph("✅ Detalles", section_style))
            for d in result.details:
                elements.append(Paragraph(f"• {d}", styles["Normal"]))

        if result.warnings:
            elements.append(Paragraph("⚠️ Advertencias", section_style))
            for w in result.warnings:
                elements.append(Paragraph(f"• {w}", styles["Normal"]))

        if result.errors:
            elements.append(Paragraph("❌ Errores", section_style))
            for e in result.errors:
                elements.append(Paragraph(f"• {e}", styles["Normal"]))

        # Pin table
        if result.report and result.report.digital_results:
            elements.append(Paragraph("Pines Digitales", section_style))
            pin_data = [["Pin", "Estado"]]
            for pin, ok in sorted(result.report.digital_results.items()):
                pin_data.append([str(pin), "✅ OK" if ok else "❌ FALLO"])

            pin_table = Table(pin_data, colWidths=[1.5 * inch, 4.5 * inch])
            ok_rows = [i for i, row in enumerate(pin_data) if row[0] != "Pin" and "OK" in row[1]]
            fail_rows = [i for i, row in enumerate(pin_data) if row[0] != "Pin" and "FALLO" in row[1]]

            ts = [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4a90d9")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
            for r in ok_rows:
                ts.append(("TEXTCOLOR", (1, r), (1, r), colors.HexColor("#0a8f3c")))
            for r in fail_rows:
                ts.append(("TEXTCOLOR", (1, r), (1, r), colors.HexColor("#c0182c")))

            pin_table.setStyle(TableStyle(ts))
            elements.append(pin_table)

        # Footer
        elements.append(Spacer(1, 20))
        footer_style = ParagraphStyle(
            "FooterStyle",
            parent=styles["Normal"],
            fontSize=8,
            textColor=colors.grey,
        )
        elements.append(
            Paragraph(
                "Generado por ArduCheck — Herramienta de diagnóstico para Arduino",
                footer_style,
            )
        )

        doc.build(elements)
        return True

    except Exception as e:
        print(f"Error exportando PDF: {e}")
        return False


def export_result(result: "DiagnosticResult", path: Path) -> bool:
    """Función de conveniencia: exporta en el formato que corresponda según la extensión.
    
    Args:
        result: Resultado del diagnóstico.
        path: Ruta del archivo. Se detecta el formato por la extensión (.json o .pdf).
    
    Returns:
        True si la exportación fue exitosa, False en caso contrario.
    """
    ext = path.suffix.lower()
    if ext == ".json":
        return export_json(result, path)
    elif ext == ".pdf":
        return export_pdf(result, path)
    else:
        # Default a JSON si no se reconoce la extensión
        return export_json(result, path)


if __name__ == "__main__":
    # Demo rápido
    from core.runner import DiagnosticResult

    demo = DiagnosticResult(
        port="COM3",
        board="Arduino Uno",
        chip="ATmega328P",
        verdict="GOOD",
        score=95,
        summary="[OK] GOOD - Arduino Uno (ATmega328P) score=95/100",
        details=["Voltaje de alimentación: 5.01 V", "LED integrado (pin 13): OK", "Pines digitales: 12/12 OK"],
        warnings=["Reloj con deriva de 12 ms/s"],
        errors=[],
    )

    print("Exportando demo a JSON...")
    ok = export_json(demo, Path("demo_report.json"))
    print(f"JSON: {'OK' if ok else 'FALLO'}")

    print("Exportando demo a PDF...")
    ok = export_pdf(demo, Path("demo_report.pdf"))
    print(f"PDF: {'OK' if ok else 'FALLO (reportlab no instalado)'}")

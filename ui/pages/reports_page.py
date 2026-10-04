"""
Reports page - generic port of the report views (sitem_report, shsn_report,
sale_report, pitem_report, phsn_report, purchase_report, quoteitem_report,
quote_report, quickquote_report): date-range filter, item search,
DataTables-style table with bold totals row and the same red DataTables
export button strip (Copy / JSON / Excel / CSV / PDF / Print / TXT / SQL /
Docx / PNG) the master pages use.
"""
import csv
import json
import os

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QTextDocument
from PyQt6.QtPrintSupport import QPrinter, QPrintPreviewDialog
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QHeaderView, QApplication, QFileDialog)

from database import db_manager
from ui import widgets as W
from utils.helpers import money

# Active breadcrumb item (last 'li' of the original 'ol.breadcrumb'), exactly
# as written in the report views under C4/app/views/report.
REPORT_CRUMB = {
    ("item", "tax"): "Sale Item Report",
    ("hsn", "tax"): "Sale HSN Report",
    ("summary", "tax"): "Sale Report",
    ("item", "purchase"): "Purchase Item Report",
    ("hsn", "purchase"): "Purchase HSN Report",
    ("summary", "purchase"): "Purchase Report",
    ("item", "quote"): "Quotation Item Report",
    ("summary", "quote"): "Quotation Report",
    ("quickquote", None): "Quick Quotation Report",
    ("item", "proforma"): "Proforma Item Report",
    ("summary", "proforma"): "Proforma Invoice Report",
}

# --------------------------------------------------------------------------- #
# Column widths for the Quotation-family reports.
#
# The generic report table lets every column fit its content
# ('ResizeToContents') with only the last section stretching, so the columns
# come out uneven and even re-flow when you page/filter.  For the three
# quotation reports we instead pin the narrow / numeric columns to stable
# widths and let just the text-heavy columns stretch - the same approach the
# master, accounts and ledger pages already use (_apply_column_widths).
#
# Keyed by (kind, doc) exactly as ReportPage receives them, so only these
# reports are affected; every other report keeps its previous behaviour.
#
# Column index -> meaning (for reference):
#
#   Quick Quote Report  ("quickquote", None)
#     0 Sr No    1 Quote ID   2 Product*   3 Mobile   4 Qty
#     5 Price    6 Subtotal   7 GST        8 Total    9 Date
#
#   Quote Item Report   ("item", "quote")
#     0 Sr No    1 Invoice    2 Client*    3 Date     4 Item*
#     5 Description*         6 HSN        7 Qty      8 Price
#     9 Subtotal 10 Tax Rate  11 Tax Amt  12 Total
#
#   Quote Report        ("summary", "quote")
#     0 Sr No    1 Invoice    2 Client*    3 Date
#     4 Items    5 Subtotal   6 Tax Rate   7 Tax Amt  8 Total
#
#   (*) = stretch column
# --------------------------------------------------------------------------- #
COLUMN_LAYOUT = {
    # Quick Quote Report - Product is the only free-flowing column.
    ("quickquote", None): (
        {0: 45,           # Sr No     - narrow
         1: 110,          # Quote ID
         3: 110,          # Mobile
         4: 55,           # Qty       - narrow
         5: 100,          # Price
         6: 110,          # Subtotal
         7: 90,           # GST
         8: 110,          # Total
         9: 100},         # Date
        [2]),             # Product stretches

    # Quote Item Report - Client / Item / Description stretch.
    ("item", "quote"): (
        {0: 45,           # Sr No     - narrow
         1: 120,          # Invoice
         3: 100,          # Date
         6: 90,           # HSN       - narrow
         7: 55,           # Qty       - narrow
         8: 100,          # Price
         9: 110,          # Subtotal
         10: 75,          # Tax Rate  - narrow
         11: 100,         # Tax Amt
         12: 110},        # Total
        [2, 4, 5]),       # Client, Item, Description stretch

    # Quote Report - Client stretches.
    ("summary", "quote"): (
        {0: 45,           # Sr No     - narrow
         1: 130,          # Invoice
         3: 110,          # Date
         4: 60,           # Items     - narrow
         5: 120,          # Subtotal
         6: 80,           # Tax Rate  - narrow
         7: 110,          # Tax Amt
         8: 120},         # Total
        [2]),             # Client stretches
}


def _apply_column_layout(table, fixed_cols, stretch_cols):
    """Pin report column widths so they no longer jump with the page content.

    Mirrors the `_apply_column_widths` helper used by the master / accounts /
    ledger pages: explicit widths for the fixed columns, remaining space split
    evenly between the stretch columns.
    """
    header = table.horizontalHeader()
    header.setStretchLastSection(False)
    header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
    for col, width in fixed_cols.items():
        header.setSectionResizeMode(col, QHeaderView.ResizeMode.Fixed)
        table.setColumnWidth(col, width)
    for col in stretch_cols:
        header.setSectionResizeMode(col, QHeaderView.ResizeMode.Stretch)


# --------------------------------------------------------------------------- #
# Centered red export button strip (DataTables "Buttons" style)
#
# The exact strip the master / accounts / ledger pages use, so every report
# page carries the same toolbar:
#     [ Copy ][ JSON ][ Excel ][ CSV ][ PDF ][ Print ][ TXT ][ SQL ][ Docx ][ PNG ]
# --------------------------------------------------------------------------- #
class ExportButtonStrip(QWidget):
    BUTTONS = (
        ("Copy",  "copy",  "\U0001F5D0"),
        ("JSON",  "json",  "{}"),
        ("Excel", "excel", "\U0001F4CA"),
        ("CSV",   "csv",   "\U0001F4C4"),
        ("PDF",   "pdf",   "\U0001F4C4"),
        ("Print", "print", "\U0001F5A8"),
        ("TXT",   "txt",   "\U0001F4C3"),
        ("SQL",   "sql",   "\U0001F5C4"),
        ("Docx",  "docx",  "\U0001F4DD"),
        ("PNG",   "png",   "\U0001F5BC"),
    )

    def __init__(self, parent=None, on_export=None, buttons=None):
        super().__init__(parent)
        self._on_export = on_export

        h = QHBoxLayout(self)
        h.setContentsMargins(0, 6, 0, 6)
        h.setSpacing(0)
        h.addStretch()

        specs = buttons if buttons is not None else self.BUTTONS
        last_idx = len(specs) - 1

        for i, (label, kind, icon) in enumerate(specs):
            b = QPushButton(f"  {icon}  {label}  ")
            b.setFixedHeight(30)
            b.setCursor(Qt.CursorShape.PointingHandCursor)

            tl = "4px" if i == 0 else "0px"
            tr = "4px" if i == last_idx else "0px"
            bl = "4px" if i == 0 else "0px"
            br = "4px" if i == last_idx else "0px"

            b.setStyleSheet(
                f"QPushButton {{"
                f"  background: #dd4b39;"
                f"  color: #ffffff;"
                f"  border: 1px solid #c23321;"
                f"  border-right: 1px solid #b7301f;"
                f"  border-top-left-radius: {tl};"
                f"  border-top-right-radius: {tr};"
                f"  border-bottom-left-radius: {bl};"
                f"  border-bottom-right-radius: {br};"
                f"  padding: 4px 12px;"
                f"  font-size: 12px;"
                f"  font-weight: 600;"
                f"}}"
                f"QPushButton:hover   {{ background: #d73925; }}"
                f"QPushButton:pressed {{ background: #c23321; }}")
            b.clicked.connect(lambda _, k=kind: self._fire(k))
            h.addWidget(b)

        h.addStretch()

    def _fire(self, kind):
        if self._on_export:
            self._on_export(kind)


# =========================================================================== #
# Generic multi-format export helper
# =========================================================================== #
def _generic_export(parent, kind, rows, columns, filename_stub,
                    sql_table, sql_cols):
    """Export `rows` in the format requested.

    columns : list of (key, header) tuples
    """
    if not rows:
        W.info(parent, "Nothing to export.")
        return

    keys = [k for k, _ in columns]
    headers = [h for _, h in columns]

    # ------------------------------------------------------------------ copy
    if kind == "copy":
        lines = ["\t".join(headers)]
        for r in rows:
            lines.append("\t".join(str(r.get(k, "")) for k in keys))
        QApplication.clipboard().setText("\n".join(lines))
        W.info(parent, f"Copied {len(rows)} rows to clipboard.")
        return

    # ------------------------------------------------------------------ print
    if kind == "print":
        html = [
            "<html><body style='font-family:Segoe UI;font-size:10pt;'>",
            "<table border='1' cellspacing='0' cellpadding='4'"
            " style='border-collapse:collapse;'>",
            "<tr style='background:#dd4b39;color:#fff;'>",
        ]
        html += [f"<th>{h}</th>" for h in headers]
        html.append("</tr>")
        for r in rows:
            html.append("<tr>")
            for k in keys:
                html.append(f"<td>{r.get(k, '')}</td>")
            html.append("</tr>")
        html.append("</table></body></html>")

        doc = QTextDocument()
        doc.setHtml("".join(html))
        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        dlg = QPrintPreviewDialog(printer, parent)
        dlg.setWindowTitle("Print")
        W.apply(dlg)                       # brand mark on the title bar
        dlg.paintRequested.connect(lambda p: doc.print(p))
        dlg.exec()
        return

    # ------------------------------------------------------------ file picker
    if kind == "csv":
        ext, filt = "csv", "CSV Files (*.csv)"
    elif kind == "txt":
        ext, filt = "txt", "Text Files (*.txt)"
    elif kind == "json":
        ext, filt = "json", "JSON Files (*.json)"
    elif kind == "sql":
        ext, filt = "sql", "SQL Files (*.sql)"
    elif kind == "excel":
        ext, filt = "csv", "Excel Files (*.csv)"
    elif kind == "docx":
        ext, filt = "html", "Word Documents (*.html)"
    elif kind == "pdf":
        ext, filt = "pdf", "PDF Files (*.pdf)"
    elif kind == "png":
        ext, filt = "png", "PNG Images (*.png)"
    else:
        W.info(parent, f"Export '{kind}' is not supported.")
        return

    default = os.path.join(os.path.expanduser("~"),
                           f"{filename_stub}.{ext}")
    fname, _ = QFileDialog.getSaveFileName(parent, f"Save {ext.upper()}",
                                           default, filt)
    if not fname:
        return
    if not fname.lower().endswith("." + ext):
        fname += "." + ext

    if kind in ("csv", "excel"):
        with open(fname, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(headers)
            for r in rows:
                w.writerow([r.get(k, "") for k in keys])
        W.info(parent, f"Saved to {fname}")

    elif kind == "txt":
        lines = ["\t".join(headers)]
        for r in rows:
            lines.append("\t".join(str(r.get(k, "")) for k in keys))
        with open(fname, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        W.info(parent, f"Saved to {fname}")

    elif kind == "json":
        data = [{k: r.get(k, "") for k in keys} for r in rows]
        with open(fname, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)
        W.info(parent, f"Saved to {fname}")

    elif kind == "sql":
        def esc(v):
            return ("NULL" if v is None
                    else "'" + str(v).replace("'", "''") + "'")
        lines = []
        for r in rows:
            vals = ", ".join(esc(r.get(k)) for k in sql_cols)
            lines.append(f"INSERT INTO {sql_table} "
                         f"({', '.join(sql_cols)}) VALUES ({vals});")
        with open(fname, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        W.info(parent, f"Saved to {fname}")

    elif kind == "docx":
        html = ["<html><body style='font-family:Calibri;font-size:11pt;'>"]
        html.append("<table border='1' cellspacing='0' cellpadding='4'"
                    " style='border-collapse:collapse;'>")
        html.append("<tr>")
        html += [f"<th>{h}</th>" for h in headers]
        html.append("</tr>")
        for r in rows:
            html.append("<tr>")
            for k in keys:
                html.append(f"<td>{r.get(k, '')}</td>")
            html.append("</tr>")
        html.append("</table></body></html>")
        with open(fname, "w", encoding="utf-8") as f:
            f.write("".join(html))
        W.info(parent, f"Saved to {fname}")

    elif kind == "pdf":
        from PyQt6.QtGui import QPageSize, QPageLayout
        from PyQt6.QtCore import QMarginsF
        html = ["<html><head><style>"
                "body{font-family:'Segoe UI';font-size:10pt;}"
                "table{border-collapse:collapse;width:100%;}"
                "th{background:#dd4b39;color:#fff;padding:6px;"
                "   border:1px solid #999;text-align:left;}"
                "td{padding:5px;border:1px solid #ccc;}"
                "</style></head><body>"]
        html.append("<table><tr>")
        html += [f"<th>{h}</th>" for h in headers]
        html.append("</tr>")
        for r in rows:
            html.append("<tr>")
            for k in keys:
                html.append(f"<td>{r.get(k, '')}</td>")
            html.append("</tr>")
        html.append("</table></body></html>")

        doc = QTextDocument()
        doc.setHtml("".join(html))

        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
        printer.setOutputFileName(fname)
        printer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
        printer.setPageMargins(QMarginsF(10, 10, 10, 10),
                               QPageLayout.Unit.Millimeter)
        doc.print(printer)
        W.info(parent, f"Saved to {fname}")

    elif kind == "png":
        from PyQt6.QtGui import QImage, QPainter, QColor
        html = ["<html><body style='background:#ffffff;"
                "font-family:Arial;font-size:11pt;color:#222;'>"]
        html.append("<table border='1' cellspacing='0' cellpadding='6'"
                    " style='border-collapse:collapse;'>")
        html.append("<tr style='background:#dd4b39;color:#fff;'>")
        html += [f"<th>{h}</th>" for h in headers]
        html.append("</tr>")
        for r in rows:
            html.append("<tr>")
            for k in keys:
                html.append(f"<td>{r.get(k, '')}</td>")
            html.append("</tr>")
        html.append("</table></body></html>")

        doc = QTextDocument()
        doc.setHtml("".join(html))
        doc.setTextWidth(1000)
        size = doc.size().toSize()
        size.setWidth(max(size.width() + 20, 800))
        size.setHeight(max(size.height() + 20, 200))

        img = QImage(size, QImage.Format.Format_ARGB32)
        img.fill(QColor("#ffffff"))
        painter = QPainter(img)
        doc.drawContents(painter)
        painter.end()
        img.save(fname, "PNG")
        W.info(parent, f"Saved to {fname}")


class ReportPage(QWidget):
    def __init__(self, main, kind, doc, title):
        super().__init__()
        self.main = main
        self.kind = kind          # item | hsn | summary | quickquote
        self.doc = doc
        self.title = title
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(W.PageHeader(title,
                                   breadcrumb=REPORT_CRUMB.get((kind, doc),
                                                               title)))
        box = W.Box(f"{title}", "danger")

        bar = QHBoxLayout()
        self.dates = W.DateRangeBar(on_change=self.refresh)
        bar.addWidget(self.dates)
        if kind == "item":
            from PyQt6.QtWidgets import QLineEdit
            self.item_edit = QLineEdit()
            self.item_edit.setPlaceholderText("Item name...")
            self.item_edit.setFixedWidth(200)
            self.item_edit.setClearButtonEnabled(True)
            self.item_edit.textChanged.connect(self.refresh)
            bar.addWidget(self.item_edit)
        bar.addStretch()
        box.addLayout(bar)

        # ---- export buttons (centered red strip - same as the master pages) --
        self.export_strip = ExportButtonStrip(self, on_export=self._on_export)
        box.add(self.export_strip)

        self.headers, self.columns, self.total_cols = self._spec()
        self.table = W.DataTable(self.headers)
        layout = COLUMN_LAYOUT.get((kind, doc))
        if layout:
            _apply_column_layout(self.table, layout[0], layout[1])
        box.add(self.table, 1)
        self.paginator = W.Paginator(on_change=self._render)
        box.add(self.paginator, 0)
        from PyQt6.QtWidgets import QLabel
        self.totals_label = QLabel("")
        self.totals_label.setStyleSheet("font-weight: 600; color: #444;")
        box.add(self.totals_label)
        lay.addWidget(box, 1)
        self._rows = []
        self.refresh()

    def _spec(self):
        if self.kind == "item":
            return (["Sr No", "Invoice", "Client", "Date", "Item",
                     "Description", "HSN", "Qty", "Price", "Subtotal",
                     "Tax Rate", "Tax Amt", "Total"],
                    ["invid", "c_name", "doc_date", "item_name", "item_desc",
                     "hsn", "quantity", "price", "subtotal", "taxrate",
                     "taxamount", "totalamount"],
                    [6, 8, 10, 11])
        if self.kind == "hsn":
            return (["Sr No", "HSN", "Total Qty", "Total Price", "Subtotal"],
                    ["hsn", "quantity", "price", "subtotal"],
                    [1, 2, 3])
        if self.kind == "quickquote":
            return (["Sr No", "Quote ID", "Product", "Mobile", "Qty", "Price",
                     "Subtotal", "GST", "Total", "Date"],
                    ["q_id", "product_name", "mob", "quantity", "price",
                     "subtotal", "gst", "total", "created"],
                    [5, 6, 7])
        return (["Sr No", "Invoice", "Client", "Date", "Items", "Subtotal",
                 "Tax Rate", "Tax Amt", "Total"],
                ["invid", "c_name", "doc_date", "totalitems", "subtotal",
                 "taxrate", "taxamount", "totalamount"],
                [4, 6, 7])

    def _data(self):
        start, end = self.dates.dates()
        if self.kind == "item":
            return db_manager.item_report(self.doc, start, end,
                                          self.item_edit.text().strip())
        if self.kind == "hsn":
            return db_manager.hsn_report(self.doc, start, end)
        if self.kind == "quickquote":
            return db_manager.quickquote_report(start, end)
        return db_manager.list_invoices(self.doc, start, end)

    def refresh(self):
        try:
            self._rows = self._data()
        except Exception as exc:
            W.error(self, f"Database error: {exc}")
            return
        self._render()

    def _render(self):
        rows = self._rows
        self.paginator._preserve_current = True
        self.paginator._refresh_total(len(rows))
        start, end = self.paginator.page_range()
        page_rows = rows[start:end]

        self.table.clear_rows()
        # sums per data column (visible page), keyed by column index
        sums = {c: 0.0 for c in self.total_cols}
        for i, r in enumerate(page_rows):
            cells = [start + i + 1]
            for c, col in enumerate(self.columns):
                v = r.get(col, "")
                if col in ("subtotal", "price", "taxamount", "totalamount",
                           "gst", "total"):
                    v = money(v)
                    if c in sums:
                        sums[c] += float(r[col] or 0)
                cells.append(v)
            self.table.add_row(cells)
        # totals row: header position 0 is the Sr No column, data starts at 1
        totals_row = [None]        # 'Total' label goes here
        for c in range(len(self.columns)):
            totals_row.append(money(sums[c]) if c in sums else "")
        self.table.apply_totals_row(totals_row)
        # footer: overall totals across all filtered rows
        ov = {c: sum(float(r.get(self.columns[c]) or 0) for r in rows)
              for c in self.total_cols}
        parts = ", ".join(f"{self.headers[c + 1]}: {money(ov[c])}"
                          for c in self.total_cols)
        self.totals_label.setText(f"{len(rows)} records  |  {parts}")

    def _on_export(self, kind):
        """Export the filtered report rows in the requested format.

        Mirrors the master pages' DataTables "Buttons" strip: every filtered
        row is exported (not just the visible page), using the report's own
        column headings.  'Sr No' is display-only, so - exactly like the
        master pages skip their Sr.No column - it is left out of the export.
        """
        columns = list(zip(self.columns, self.headers[1:]))
        stub = self.title.lower().replace(" ", "_")
        _generic_export(
            self, kind, self._rows, columns,
            filename_stub=stub,
            sql_table=stub,
            sql_cols=list(self.columns))
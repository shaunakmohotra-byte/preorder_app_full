import os
from flask import current_app
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.colors import grey
from datetime import datetime

def generate_invoice_pdf(order_id, user, order_items, total):
    invoices_dir = os.path.join(current_app.root_path, "invoices")
    os.makedirs(invoices_dir, exist_ok=True)

    file_path = os.path.join(invoices_dir, f"invoice_{order_id}.pdf")

    c = canvas.Canvas(file_path, pagesize=A4)
    width, height = A4

    # -------------------------------------------------
    # HEADER
    # -------------------------------------------------
    c.setFont("Helvetica-Bold", 20)
    c.drawString(2 * cm, height - 2 * cm, "CAFETERIA E-BILL")

    c.setFont("Helvetica", 10)
    c.drawRightString(width - 2 * cm, height - 2.2 * cm, "Invoice")
    c.drawRightString(width - 2 * cm, height - 2.8 * cm, f"Order ID: {order_id}")
    c.drawRightString(
        width - 2 * cm,
        height - 3.4 * cm,
        datetime.now().strftime("%d %b %Y, %I:%M %p")
    )

    # Divider
    c.setStrokeColor(grey)
    c.line(2 * cm, height - 4 * cm, width - 2 * cm, height - 4 * cm)

    # -------------------------------------------------
    # CUSTOMER DETAILS
    # -------------------------------------------------
    y = height - 5 * cm
    c.setFont("Helvetica-Bold", 11)
    c.drawString(2 * cm, y, "Billed To:")

    y -= 0.6 * cm
    c.setFont("Helvetica", 10)
    c.drawString(2 * cm, y, user.get("username", "User"))
    y -= 0.5 * cm
    c.drawString(2 * cm, y, user.get("email", ""))

    # -------------------------------------------------
    # TABLE HEADER
    # -------------------------------------------------
    y -= 1.2 * cm
    c.setFont("Helvetica-Bold", 11)
    c.drawString(2 * cm, y, "Item")
    c.drawRightString(13 * cm, y, "Qty")
    c.drawRightString(18 * cm, y, "Subtotal")

    c.line(2 * cm, y - 0.2 * cm, width - 2 * cm, y - 0.2 * cm)

    # -------------------------------------------------
    # TABLE ROWS
    # -------------------------------------------------
    c.setFont("Helvetica", 10)
    y -= 0.7 * cm

    for item in order_items:
        name = item.get("name", "")
        qty = item.get("qty", 0)

        c.drawString(2 * cm, y, name)
        c.drawRightString(13 * cm, y, str(qty))
        c.drawRightString(18 * cm, y, f"₹ {qty * 1}")  # subtotal visual
        y -= 0.6 * cm

        # Page break safety
        if y < 4 * cm:
            c.showPage()
            y = height - 3 * cm

    # -------------------------------------------------
    # TOTAL SECTION
    # -------------------------------------------------
    y -= 0.5 * cm
    c.line(10 * cm, y, width - 2 * cm, y)

    y -= 0.8 * cm
    c.setFont("Helvetica-Bold", 13)
    c.drawRightString(13 * cm, y, "TOTAL:")
    c.drawRightString(18 * cm, y, f"Rs.{total}")

    # -------------------------------------------------
    # FOOTER
    # -------------------------------------------------
    c.setFont("Helvetica-Oblique", 9)
    c.setFillColor(grey)
    c.drawCentredString(
        width / 2,
        2 * cm,
        "Thank you for your order! This is a system-generated receipt."
    )

    c.showPage()
    c.save()

    return file_path



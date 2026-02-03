import os
from flask import current_app
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor, grey, black, white
from datetime import datetime


def generate_invoice_pdf(order_id, user, order_items, total):
    invoices_dir = os.path.join(current_app.root_path, "invoices")
    os.makedirs(invoices_dir, exist_ok=True)

    file_path = os.path.join(invoices_dir, f"invoice_{order_id}.pdf")

    c = canvas.Canvas(file_path, pagesize=A4)
    width, height = A4

    # =================================================
    # HEADER BAND
    # =================================================
    header_color = HexColor("#1F2937")  # dark slate
    c.setFillColor(header_color)
    c.rect(0, height - 3.2 * cm, width, 4.0 * cm, fill=1, stroke=0)

    c.setFillColor(white)
    c.setFont("Times-Bold", 22)
    c.drawString(2 * cm, height - 2 * cm, "CAFETERIA E-BILL")

    c.setFont("Times-Roman", 10)
    c.drawRightString(width - 2 * cm, height - 2.1 * cm, "INVOICE")
    c.drawRightString(width - 2 * cm, height - 2.7 * cm, f"Order ID: {order_id}")
    c.drawRightString(
        width - 2 * cm,
        height - 3.3 * cm,
        datetime.now().strftime("%d %b %Y • %I:%M %p")
    )

    # =================================================
    # CUSTOMER DETAILS
    # =================================================
    y = height - 4.5 * cm
    c.setFillColor(black)

    c.setFont("Times-Bold", 12)
    c.drawString(2 * cm, y, "Billed To")

    y -= 0.6 * cm
    c.setFont("Times-Roman", 11)
    c.drawString(2 * cm, y, user.get("username", "User"))

    y -= 0.5 * cm
    c.setFont("Times-Roman", 10)
    c.drawString(2 * cm, y, user.get("email", ""))

    # =================================================
    # TABLE HEADER
    # =================================================
    y -= 1.4 * cm
    c.setFont("Times-Bold", 11)

    c.drawString(2 * cm, y, "Item")
    c.drawRightString(11 * cm, y, "Price")
    c.drawRightString(14 * cm, y, "Qty")
    c.drawRightString(18 * cm, y, "Amount")

    c.setStrokeColor(grey)
    c.line(2 * cm, y - 0.3 * cm, width - 2 * cm, y - 0.3 * cm)

    # =================================================
    # TABLE ROWS
    # =================================================
    c.setFont("Times-Roman", 10)
    y -= 0.8 * cm

    for item in order_items:
        name = item.get("name", "")
        qty = int(item.get("qty", 0))
        price = int(item.get("price", 0))
        subtotal = qty * price

        c.drawString(2 * cm, y, name)
        c.drawRightString(11 * cm, y, f"Rs {price}")
        c.drawRightString(14 * cm, y, str(qty))
        c.drawRightString(18 * cm, y, f"Rs {subtotal}")

        y -= 0.65 * cm

        if y < 4 * cm:
            c.showPage()
            y = height - 3 * cm
            c.setFont("Times-Roman", 10)

    # =================================================
    # TOTAL BOX
    # =================================================
    y -= 0.6 * cm
    c.setStrokeColor(black)
    c.line(11 * cm, y, width - 2 * cm, y)

    y -= 0.9 * cm
    c.setFont("Times-Bold", 14)
    c.drawRightString(14 * cm, y, "TOTAL PAYABLE")
    c.drawRightString(18 * cm, y, f"Rs {total}")

    # =================================================
    # FOOTER
    # =================================================
    c.setFont("Times-Italic", 9)
    c.setFillColor(grey)
    c.drawCentredString(
        width / 2,
        2 * cm,
        "This is a computer-generated invoice. No signature required."
    )

    c.showPage()
    c.save()

    return file_path

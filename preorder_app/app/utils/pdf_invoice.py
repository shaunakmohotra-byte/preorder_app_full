import os
from flask import current_app
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.colors import grey, black, HexColor, white
from datetime import datetime


def generate_invoice_pdf(order_id, user, order_items, total):
    invoices_dir = os.path.join(current_app.root_path, "invoices")
    os.makedirs(invoices_dir, exist_ok=True)

    file_path = os.path.join(invoices_dir, f"invoice_{order_id}.pdf")

    c = canvas.Canvas(file_path, pagesize=A4)
    width, height = A4

    # ===============================
    # COLORS
    # ===============================
    PRIMARY = HexColor("#1f3c88")      # Deep blue
    LIGHT_GREY = HexColor("#f2f2f2")   # Table background
    DARK_GREY = HexColor("#555555")

    y = height - 2 * cm

    # ===============================
    # HEADER BAND
    # ===============================
    c.setFillColor(PRIMARY)
    c.rect(0, height - 4 * cm, width, 4 * cm, fill=1)

    c.setFillColor(white)
    c.setFont("Times-Bold", 24)
    c.drawString(2 * cm, height - 2.5 * cm, "CAFETERIA E-BILL")

    c.setFont("Times-Roman", 11)
    c.drawString(2 * cm, height - 3.3 * cm, "Tagore International School – Cafeteria")

    c.drawRightString(
        width - 2 * cm,
        height - 2.5 * cm,
        f"Invoice No: {order_id}"
    )
    c.drawRightString(
        width - 2 * cm,
        height - 3.3 * cm,
        datetime.now().strftime("%d %b %Y, %I:%M %p")
    )

    # LOGO (optional)
    logo_path = os.path.join(current_app.root_path, "static", "logo.png")
    if os.path.exists(logo_path):
        c.drawImage(
            logo_path,
            width - 5 * cm,
            height - 3.8 * cm,
            width=2.8 * cm,
            height=2.8 * cm,
            preserveAspectRatio=True,
            mask='auto'
        )

    y = height - 5 * cm
    c.setFillColor(black)

    # ===============================
    # CUSTOMER DETAILS
    # ===============================
    c.setFont("Times-Bold", 12)
    c.drawString(2 * cm, y, "Billed To:")
    y -= 0.6 * cm

    c.setFont("Times-Roman", 11)
    c.drawString(2 * cm, y, user.get("username", "Student"))
    y -= 0.5 * cm
    c.drawString(2 * cm, y, user.get("email", ""))

    # ===============================
    # TABLE HEADER (COLORED)
    # ===============================
    y -= 1.5 * cm
    c.setFillColor(LIGHT_GREY)
    c.rect(2 * cm, y - 0.5 * cm, width - 4 * cm, 0.9 * cm, fill=1)

    c.setFillColor(PRIMARY)
    c.setFont("Times-Bold", 11)
    c.drawString(2.2 * cm, y, "Item")
    c.drawRightString(12 * cm, y, "Qty")
    c.drawRightString(15 * cm, y, "Price")
    c.drawRightString(18 * cm, y, "Subtotal")

    # ===============================
    # ORDER ITEMS
    # ===============================
    y -= 1 * cm
    c.setFont("Times-Roman", 11)
    c.setFillColor(black)

    for item in order_items:
        c.drawString(2.2 * cm, y, item["name"])
        c.drawRightString(12 * cm, y, str(item["qty"]))
        c.drawRightString(15 * cm, y, f"Rs {item['price']}")
        c.drawRightString(18 * cm, y, f"Rs {item['subtotal']}")
        y -= 0.7 * cm

        if y < 6 * cm:
            c.showPage()
            y = height - 3 * cm
            c.setFont("Times-Roman", 11)

    # ===============================
    # TOTAL BOX
    # ===============================
    y -= 0.5 * cm
    c.setFillColor(LIGHT_GREY)
    c.rect(11.5 * cm, y - 0.8 * cm, 6.5 * cm, 1.2 * cm, fill=1)

    c.setFillColor(PRIMARY)
    c.setFont("Times-Bold", 14)
    c.drawRightString(15 * cm, y, "TOTAL:")
    c.drawRightString(18 * cm, y, f"Rs {total}")

    # ===============================
    # PAYMENT INFO
    # ===============================
    y -= 2 * cm
    c.setFillColor(black)
    c.setFont("Times-Bold", 12)
    c.drawString(2 * cm, y, "Payment Information")

    y -= 0.7 * cm
    c.setFont("Times-Roman", 11)
    c.drawString(2 * cm, y, "Payment Mode: Mock Digital Payment")
    y -= 0.5 * cm
    c.drawString(2 * cm, y, "Payment Status: Successful")
    y -= 0.5 * cm
    c.drawString(2 * cm, y, "Transaction Type: Cafeteria Pre-Order")

    # ===============================
    # NOTES
    # ===============================
    y -= 1.6 * cm
    c.setFont("Times-Bold", 12)
    c.drawString(2 * cm, y, "Notes & Terms")

    y -= 0.7 * cm
    c.setFont("Times-Roman", 10)
    c.setFillColor(DARK_GREY)

    terms = [
        "• This receipt is system-generated and does not require a signature.",
        "• Items once ordered cannot be cancelled after preparation.",
        "• Payments shown here are part of a prototype cafeteria system.",
        "• Generated for academic and demonstration purposes only.",
    ]

    for t in terms:
        c.drawString(2 * cm, y, t)
        y -= 0.5 * cm

    # ===============================
    # FOOTER
    # ===============================
    c.setFont("Times-Italic", 9)
    c.setFillColor(grey)
    c.drawCentredString(
        width / 2,
        2 * cm,
        "Thank you for using the Cafeteria Pre-Order System"
    )

    c.showPage()
    c.save()

    return file_path

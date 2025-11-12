import qrcode
from io import BytesIO
import tempfile
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from django.http import HttpResponse

def generate_qr_code(data):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill='black', back_color='white')
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()

def create_pdf_with_qr(response, qr_code_data):
    c = canvas.Canvas(response, pagesize=letter)
    c.drawString(100, 750, "Voici votre code QR:")
    
    # Générer le code QR
    qr_code = generate_qr_code(qr_code_data)
    
    # Enregistrer le code QR dans un fichier temporaire
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_file:
        tmp_file.write(qr_code)
        tmp_file_path = tmp_file.name
    
    # Ajouter le code QR au PDF
    c.drawImage(tmp_file_path, 100, 600, 2*inch, 2*inch)
    
    c.showPage()
    c.save()

def generate_pdf_view(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="report.pdf"'
    
    qr_code_data = response
    create_pdf_with_qr(response, qr_code_data)
    
    return response

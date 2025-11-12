from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.pagesizes import A4

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
        self.setFont("Times-Italic", 10)
        self.drawRightString(200*mm, 10*mm, f"Page {self._pageNumber} sur {page_count}")

class CustomCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pages = []

    def showPage(self):
        self.pages.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        page_count = len(self.pages)
        for page in self.pages:
            self.__dict__.update(page)
            self.draw_header_footer(page_count)
            super().showPage()
        super().save()

    def draw_header_footer(self, page_count):
        width, height = A4
        self.setFont("Times-Italic", 10)
        # self.drawString(100, height - 20, "Ceci est un en-tête")
        self.drawString(200,30, "Contact : +243 999 917 125 / 999 917 112")
        self.drawString(160, 20, "Av. du Lac, Q. Ndendere, Commune d'Ibanda, Ville de Bukavu")
        self.drawRightString(width - 10, 20, f"{self._pageNumber}/{page_count}")
        # self.drawRightString(width - 20, 20, f"Page {self._pageNumber} sur {page_count}")
        # self.drawImage("media/images/Picture2.png", 100, height - 80, width=200, height=50) #Entete
        # self.drawImage("media/images/Picture2.png", 100, 20, width=200, height=50) #Footer

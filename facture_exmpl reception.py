import pdfkit

# directly from url
# pdfkit.from_url("https://google.com", "C:\\Users\\MICHKA\\Desktop\DJ\\rivisoft\\google.pdf", verbose=True)
# print("="*50)

# from file
pdfkit.from_file("C:\\Users\\MICHKA\\Desktop\\DJ\\rivisoft\\exempleFctReception.html", "C:\\Users\\MICHKA\\Desktop\\DJ\\rivisoft\\exempleFctReception.pdf", verbose=True, options={"enable-local-file-access": True})
print("="*50)

import win32print
import win32api

# printer_name = win32print.GetDefaultPrinter()
# file_name = "facture.pdf"
# print(printer_name)

# try :
#     win32api.ShellExecute(
#         0,
#         "print",
#         file_name,
#         f'/d:"{printer_name}"',
#         ".",
#         0
#     )
# except Exception as e :
#     print(f"Erreur lors de l'impression {e}")



# -------------------------------------------------------------------------------------------- 2ème méthode 

# printers = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL,None,1)
# # for printer in printers:
# #     print(printer[2])
    
# file_path = 'C:\\Users\\MICHKA\\Desktop\\DJ\\rivisoft\\facture.pdf'
# printer_name = 'Microsoft Print to PDF'
# file_handle = open(file_path, "rb")
# printer_handle = win32print.OpenPrinter(printer_name)
# job_info = win32print.StartDocPrinter(printer_handle, 1, (file_path,None,'RAW'))
# win32print.StartPagePrinter(printer_handle)
# win32print.WritePrinter(printer_handle,file_handle.read())
# win32print.EndPagePrinter(printer_handle)
# win32print.EndDocPrinter(printer_handle)

# win32print.ClosePrinter(printer_handle)
# file_handle.close()

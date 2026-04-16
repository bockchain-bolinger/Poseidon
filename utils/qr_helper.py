import qrcode
from .ui_helpers import clear_screen

def show_qr_code(data):
    """Zeigt einen QR-Code im Terminal an (vereinfacht)."""
    qr = qrcode.QRCode()
    qr.add_data(data)
    qr.make()
    # Terminal-Darstellung mit ASCII
    qr.print_ascii(invert=True)
    print(f"\nDaten: {data}")
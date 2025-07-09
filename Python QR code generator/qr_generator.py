import qrcode
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
folder_path = os.path.join(script_dir, "Generated QR Codes")

if not os.path.exists(folder_path):
    os.makedirs(folder_path)

data = input("Enter the text or URL to generate QR code: ")
filename = input("Enter a name for your QR code file (without .png): ")
qr = qrcode.make(data)
file_path = os.path.join(folder_path, f"{filename}.png")
qr.save(file_path)
print(f"✅ QR Code saved at: {file_path}")
input("Press Enter to exit...")

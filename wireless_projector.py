import os
import sys
import json
import socket
import threading
import tempfile
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox
from flask import Flask, request
import requests

CONFIG_FILE = "projector_config.json"
PORT = 5000

# --- HELPER: GET LOCAL IP ---
def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

class UnifiedProjectorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Wireless Projector Hub")
        self.root.geometry("420x320")
        self.root.configure(bg="#1e1e1e")
        self.root.resizable(False, False)

        self.current_process = None
        self.load_or_setup()

    def load_or_setup(self):
        # Clear existing widgets if resetting
        for widget in self.root.winfo_children():
            widget.destroy()

        config = self.load_config()
        if not config:
            self.show_setup_screen()
        else:
            self.role = config.get("role")
            if self.role == "receiver":
                self.start_receiver_ui()
                self.start_flask_server()
            else:
                self.target_ip = config.get("target_ip", "192.168.1.50")
                self.start_sender_ui()

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    return json.load(f)
            except:
                pass
        return None

    def save_config(self, role, target_ip=""):
        config = {"role": role, "target_ip": target_ip}
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f)
        self.load_or_setup()

    # ==================== SETUP SCREEN ====================
    def show_setup_screen(self):
        tk.Label(self.root, text="Initial Device Setup", bg="#1e1e1e", fg="#ffffff", font=("Arial", 14, "bold")).pack(pady=20)
        tk.Label(self.root, text="Select what this computer will act as:", bg="#1e1e1e", fg="#b0b0b0", font=("Arial", 10)).pack(pady=5)

        btn_rcv = tk.Button(self.root, text="📺 Projector Receiver (PPC)", bg="#28a745", fg="white", font=("Arial", 11, "bold"), width=30, pady=8, command=lambda: self.save_config("receiver"))
        btn_rcv.pack(pady=10)

        self.ip_entry_frame = tk.Frame(self.root, bg="#1e1e1e")
        self.ip_entry_frame.pack(pady=10)

        tk.Label(self.ip_entry_frame, text="Target PPC IP (for Sender mode):", bg="#1e1e1e", fg="#b0b0b0", font=("Arial", 9)).pack(anchor="w")
        self.ip_input = tk.Entry(self.ip_entry_frame, font=("Arial", 11), width=25)
        self.ip_input.insert(0, get_local_ip())
        self.ip_input.pack(pady=5)

        btn_snd = tk.Button(self.root, text="💻 Main Controller (MPC)", bg="#007acc", fg="white", font=("Arial", 11, "bold"), width=30, pady=8, command=self.setup_sender_choice)
        btn_snd.pack(pady=5)

    def setup_sender_choice(self):
        ip = self.ip_input.get().strip()
        if not ip:
            messagebox.showerror("Error", "Please enter a valid IP address.")
            return
        self.save_config("sender", target_ip=ip)

    # ==================== RECEIVER MODE (PPC) ====================
    def start_receiver_ui(self):
        tk.Label(self.root, text="Projector Receiver Mode (PPC)", bg="#1e1e1e", fg="#28a745", font=("Arial", 13, "bold")).pack(pady=15)
        
        local_ip = get_local_ip()
        tk.Label(self.root, text=f"Listening on IP: {local_ip}", bg="#1e1e1e", fg="#ffffff", font=("Arial", 10)).pack(pady=5)

        self.rcv_status = tk.Label(self.root, text="Status: Waiting for incoming files...", bg="#1e1e1e", fg="#b0b0b0", font=("Arial", 10))
        self.rcv_status.pack(pady=20)

        tk.Button(self.root, text="⚙️ Change Role / Settings", bg="#444", fg="white", font=("Arial", 9), command=self.reset_config).pack(side="bottom", pady=15)

    def start_flask_server(self):
        app = Flask(__name__)

        @app.route('/project', methods=['POST'])
        def project():
            file = request.files.get('file')
            if not file:
                return "No file", 400

            filename = file.filename
            temp_path = os.path.join(tempfile.gettempdir(), filename)
            file.save(temp_path)

            # Close previous process if open
            if self.current_process and self.current_process.poll() is None:
                try:
                    self.current_process.terminate()
                except:
                    pass

            # Open natively in full screen
            def open_viewer():
                if os.name == 'nt':
                    self.current_process = subprocess.Popen(['start', '', temp_path], shell=True)
                else:
                    viewer = 'xdg-open' if os.name == 'posix' else 'open'
                    self.current_process = subprocess.Popen([viewer, temp_path])

            threading.Thread(target=open_viewer).start()
            
            # Update GUI status safely from thread
            self.root.after(0, lambda: self.rcv_status.config(text=f"Projecting: {filename}", fg="#00ff00"))
            return "OK", 200

        def run_server():
            app.run(host='0.0.0.0', port=PORT, threaded=True)

        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()

    # ==================== SENDER MODE (MPC) ====================
    def start_sender_ui(self):
        tk.Label(self.root, text="Main Controller Mode (MPC)", bg="#1e1e1e", fg="#007acc", font=("Arial", 13, "bold")).pack(pady=15)
        tk.Label(self.root, text=f"Target Projector IP: {self.target_ip}", bg="#1e1e1e", fg="#b0b0b0", font=("Arial", 9)).pack(pady=2)

        frame = tk.Frame(self.root, bg="#2d2d2d", bd=2, relief="groove")
        frame.pack(padx=20, pady=10, fill="both", expand=True)

        tk.Label(frame, text="Click below to select a file\nto beam to the projector instantly.", bg="#2d2d2d", fg="#cccccc", font=("Arial", 10)).pack(pady=10)

        tk.Button(frame, text="📂 Browse & Project File", bg="#007acc", fg="white", font=("Arial", 10, "bold"), padx=10, pady=6, command=self.browse_and_send).pack(pady=5)

        self.snd_status = tk.Label(self.root, text="Ready", bg="#1e1e1e", fg="#888888", font=("Arial", 9))
        self.snd_status.pack(side="bottom", pady=5)

        tk.Button(self.root, text="⚙️ Change Role / Settings", bg="#444", fg="white", font=("Arial", 9), command=self.reset_config).pack(side="bottom", pady=5)

    def browse_and_send(self):
        path = filedialog.askopenfilename()
        if path:
            threading.Thread(target=self.send_file, args=(path,), daemon=True).start()

    def send_file(self, file_path):
        filename = os.path.basename(file_path)
        self.root.after(0, lambda: self.snd_status.config(text=f"Sending: {filename}...", fg="#ffa500"))
        
        url = f"http://{self.target_ip}:{PORT}/project"
        try:
            with open(file_path, 'rb') as f:
                res = requests.post(url, files={'file': f}, timeout=10)
            if res.status_code == 200:
                self.root.after(0, lambda: self.snd_status.config(text=f"Successfully Projected: {filename}", fg="#00ff00"))
            else:
                self.root.after(0, lambda: self.snd_status.config(text="Error: Rejected by Projector PC.", fg="#ff4d4d"))
        except Exception as e:
            self.root.after(0, lambda: self.snd_status.config(text="Connection Failed!", fg="#ff4d4d"))
            messagebox.showerror("Connection Error", f"Could not reach Projector PC at {self.target_ip}\nDetails: {e}")

    def reset_config(self):
        if os.path.exists(CONFIG_FILE):
            os.remove(CONFIG_FILE)
        self.load_or_setup()

if __name__ == "__main__":
    root = tk.Tk()
    app = UnifiedProjectorApp(root)
    root.mainloop()

Wireless Projector Hub (MPC to PPC Streamer)
A lightweight, zero-friction local network utility built with Python and Tkinter that allows a Main PC (MPC) to instantly stream and project files onto a Projector PC (PPC) over Wi-Fi without cluttering disk storage or requiring manual approvals.

🌟 Overview
When working with a dual-computer setup where one computer is plugged into a projector (ppc) and the other is your main workstation (mpc), traditional file-sharing or casting tools can be slow or require multiple clicks.

Wireless Projector Hub solves this by providing a unified, single-application approach. During the initial setup, you designate the role of the computer (Receiver or Sender). Once configured, dropping or selecting a file on the Main PC instantly pushes it over the local network via an in-memory stream, firing up the native viewer in full-screen on the projector instantly.

🏗️ Architecture & Workflow
Unified Application: A single Python script handles both roles based on a saved local configuration file (projector_config.json).

Receiver Mode (ppc):

Runs a background Flask server on a local network port (5000).

Listens for incoming file payloads from the mpc.

Automatically closes any previously open file viewer and opens the new file natively in full-screen mode using the operating system's default viewer.

Sender Mode (mpc):

Provides a sleek Tkinter GUI.

Allows users to browse and send files securely over local Wi-Fi to the target Projector IP.

✨ Key Features
Unified Setup Wizard: Choose whether the machine acts as the Receiver or Sender on first launch.

Zero-Click Projection: Files sent from the Main PC automatically open on the projector screen with no confirmation prompts required.

Standalone Executable Support: Can be easily compiled into a single .exe file using PyInstaller for hassle-free deployment without needing Python installed on target machines.

Dynamic Settings: Easily switch roles or update target IP addresses using the built-in settings panel.

Cross-Platform Compatibility: Built with cross-platform modules (Tkinter, Flask, Subprocess).

🛠️ Tech Stack
Language: Python 3.x

GUI Framework: Tkinter (Built-in)

Networking / Server: Flask, Requests, Socket

Packaging: PyInstaller

🚀 Installation & Setup Guide
1. Prerequisites
Ensure Python is installed on your machines, then install the required dependencies:

Bash
pip install flask requests
2. Running the Application from Source
Clone or download the script (wireless_projector.py) onto both computers and run it:

Bash
python wireless_projector.py
On the Projector PC (ppc): Select 📺 Projector Receiver (PPC) during the setup screen.

On the Main PC (mpc): Enter the local IP address of your Projector PC and select 💻 Main Controller (MPC).

📦 Creating a Standalone .exe File
If you want to run the application without installing Python on your machines, you can compile it into a standalone executable using PyInstaller:

Install PyInstaller:

Bash
pip install pyinstaller
Build the executable (hidden console, single file):

Bash
pyinstaller --noconsole --onefile wireless_projector.py
Find your compiled app inside the dist folder (wireless_projector.exe). Copy it to both computers and create a desktop shortcut.

📖 How to Use
Launch wireless_projector.py (or the .exe) on both computers.

Complete the one-time configuration setup.

On your Main PC (mpc), click Browse & Project File.

Watch the file beam across your local Wi-Fi and display instantly on the projector screen!

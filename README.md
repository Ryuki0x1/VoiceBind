# VoiceClip

VoiceClip is a lightweight, fully local, offline voice-to-hotkey macro tool. It allows you to speak customizable voice commands (e.g., *"clip thirty"*, *"clip one minute"*, *"start recording"*) and maps them to keyboard shortcuts/macros (e.g., `Ctrl+Alt+Shift+1`) in real-time.

It runs locally with a clean web configuration UI and sits quietly in your system tray.

---

## Features

- **Offline Speech Recognition**: Powered by [Vosk](https://alphacephei.com/vosk/), ensuring complete privacy with zero cloud dependencies or API keys.
- **Dynamic Keybind Mappings**: Create custom voice commands and pair them with any hotkey (using standard modifiers like `ctrl`, `alt`, `shift`, `win`).
- **Modern Web Configuration UI**: A beautiful, local dashboard to adjust settings, view available microphones, manage hotkey mappings, and toggle preferences.
- **Accent/Language Support**: Switch between **US English** and **Indian English** pronunciation models. The application automatically downloads and configures the required models in the background.
- **Robust Rolling Recognition Buffer**: Uses an advanced rolling phrase buffer to accurately parse multi-word commands even when speech engine recognition is slightly delayed or out-of-order.
- **System Tray Integration**: Sits in the system tray (`pystray`) for unobtrusive background operation, with easy toggle for voice recognition and quick access to settings.

---

## Installation & Setup (Run from Source)

### Prerequisites
- Python 3.8 to 3.12 (Pydantic and Vosk support)
- Soundcard / Working Microphone

### Steps
1. **Clone the repository:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/VoiceClip.git
   cd VoiceClip
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Linux/macOS:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Download a speech model (Optional):**
   The application will prompt you or download the model automatically when launched, but you can also download a model manually:
   ```bash
   python download_model.py --language en-US
   ```

5. **Start the application:**
   ```bash
   python main.py
   ```
   *Note: This will launch the tray application and automatically open the settings dashboard at `http://127.0.0.1:5000`.*

---

## Building an Executable

If you want to package VoiceClip into a standalone `.exe` file for Windows:

1. **Install PyInstaller:**
   ```bash
   pip install pyinstaller
   ```

2. **Run the build script:**
   ```bash
   python build.py
   ```

3. **Deploying the executable:**
   - The compiled executable `VoiceClip.exe` will be located in the `dist/` directory.
   - **Crucial:** You must copy or move the `models/` directory next to the built executable so it can perform speech recognition offline. (Alternatively, run the executable and use the Settings web interface to download the models dynamically).

---

## Usage Guide

1. **Start the app**: Double-click `run.bat` or the compiled executable.
2. **Access configuration**: Right-click the microphone icon in your Windows System Tray and select **Settings**, or open `http://127.0.0.1:5000` in your web browser.
3. **Customize Keybinds**:
   - In the **Commands** tab, add or edit voice phrases and assign them hotkeys (e.g. `clip thirty` -> `ctrl+alt+shift+1`).
   - Click **Save & Apply** to apply mappings instantly.
4. **Choose Audio & Accents**:
   - In the **Audio** tab, choose your active microphone device and set the command cooldown window.
   - In the **General** tab, select **English (India)** if you want the engine optimized for Indian English speech patterns. The model will download automatically in the background.

---

## Security & Privacy

- **100% Local**: VoiceClip records audio and processes speech locally. Nothing is ever sent to external cloud APIs or remote servers.
- **Secure Flask Web Server**: The configuration server runs strictly on localhost (`127.0.0.1`), meaning it is inaccessible from outside your local computer.
- **No Admin Rights Needed**: The application runs completely in user space.

---

## License

This project is open-source and available under the [MIT License](LICENSE).

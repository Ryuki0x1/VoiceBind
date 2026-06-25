# VoiceBind

Voice-controlled hotkey launcher for Windows. Speak a phrase, trigger a hotkey.

## Features

- Speech-to-hotkey mapping via Vosk (offline, no internet needed)
- System tray integration — runs in background
- Customizable voice commands with hotkey capture
- Audio feedback on command trigger
- Minimize to tray or start with Windows

## Getting Started

1. Download the latest installer from [Releases](https://github.com/Ryuki0x1/VoiceBind/releases)
2. Run the installer
3. On first launch, the setup wizard will guide you through adding commands
4. Start speaking your phrases!

## Build from Source

Requires Python 3.10+.

```bash
git clone https://github.com/Ryuki0x1/VoiceBind.git
cd VoiceBind
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python build.py
```

The executable will be in `dist/VoiceClip.exe`. An Inno Setup installer can be built from `installer/VoiceClip.iss`.

## Usage

- Press your configured hotkey to start listening, speak a command phrase
- The associated keyboard shortcut is simulated
- Right-click the tray icon to open settings or quit

## License

MIT

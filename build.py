import PyInstaller.__main__
import vosk
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
MODELS_PATH = BASE_DIR / "models" / "vosk-model-small-en-us"
VOSK_DIR = Path(vosk.__file__).parent

sep = ";"

PyInstaller.__main__.run([
    'main.py',
    '--name=VoiceClip',
    '--windowed',
    '--onefile',
    '--noconfirm',
    '--clean',
    f'--add-data=assets{sep}assets',
    f'--add-data={MODELS_PATH}{sep}models/vosk-model-small-en-us',
    # Include Vosk native DLLs (loaded at runtime via cffi)
    f'--add-binary={VOSK_DIR / "libvosk.dll"}{sep}vosk',
    f'--add-binary={VOSK_DIR / "libgcc_s_seh-1.dll"}{sep}vosk',
    f'--add-binary={VOSK_DIR / "libstdc++-6.dll"}{sep}vosk',
    f'--add-binary={VOSK_DIR / "libwinpthread-1.dll"}{sep}vosk',
    '--hidden-import=pystray',
    '--hidden-import=keyboard',
    '--hidden-import=sounddevice',
    '--hidden-import=vosk',
    '--hidden-import=ttkbootstrap'
])

print("Build complete! Single executable: dist/VoiceClip.exe")

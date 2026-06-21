# Stussi Launcher

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?logo=python" alt="Python" />
  <img src="https://img.shields.io/badge/Qt-PySide6-darkblue?logo=qt" alt="PySide6" />
  <img src="https://img.shields.io/badge/Steam-Launcher-ff4d4d" alt="Steam Launcher" />
</p>

A modern and stylized launcher for your Steam library, designed to give a premium, racing-inspired experience while keeping the interface clean and practical.

## ✨ Features

- Browse installed Steam games directly from your library
- Search and sort games by name, size, or last played time
- Fullscreen and windowed modes
- Smooth animated cards and polished UI
- Custom startup sound and splash screen
- Support for high-resolution and ultra-wide displays
- Fast launch via Steam game URLs

## 🧩 About the project

Stussi Launcher is a Windows desktop application built with Python and PySide6. It reads Steam manifest files to detect installed games and presents them in an elegant visual interface.

The project is especially useful for users who want a more immersive launcher experience for their Steam collection.

## 🛠️ Requirements

- Python 3.10 or newer
- Steam installed and logged in
- Windows operating system

Install the dependencies:

```bash
pip install -r requirements.txt
```

## ▶️ How to run

From the project folder:

```bash
python main.py
```

## 📦 Build executable

If you want to generate a standalone Windows executable:

```bash
pyinstaller StussiLauncher.spec
```

The output will be created in the `dist/` folder.

## 📁 Project structure

```text
.
├── main.py               # Main application UI and logic
├── steam_utils.py        # Steam discovery and launch helpers
├── requirements.txt      # Python dependencies
├── StussiLauncher.spec   # PyInstaller build configuration
├── icon.ico              # App icon
├── somstussi.wav         # Startup sound
└── README.md             # Project documentation
```

## 🎨 UI notes

The launcher uses a dark racing-inspired visual theme with:

- navy and red accents
- rounded cards and subtle glow effects
- modern typography and animated overlays
- fullscreen-first presentation

## 🔎 Troubleshooting

- If no games appear, confirm that Steam is installed and that your library manifests exist.
- If the launcher does not launch correctly, ensure all dependencies are installed.
- For packaging issues, verify that the assets referenced by the spec file are present in the project folder.

## 📸 Screenshots

> Add screenshots here later to showcase the launcher interface.

## 🚀 Next steps

Possible improvements for future versions:

- game filtering by genres or tags
- recent games section
- custom themes
- support for launching external launch options
- automatic updates

---

If you want, I can also add a proper `LICENSE` file and a more advanced GitHub badge section.

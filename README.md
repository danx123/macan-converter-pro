# ♻️ Macan Converter Pro

Macan Converter Pro is a multi-conversion application for files, images, audio, and video.
Fast, modern, and easy to use.

Macan Converter Pro is a versatile PySide6-based converter application that supports a wide range of file formats:
- File Converter: PDF → Image (PNG/JPG), PNG → ICO with a choice of resolutions.

- Image Converter: Convert images between formats (JPEG, PNG, WEBP, BMP, GIF), with resolution and quality settings.
- Video Converter: Convert videos to various formats (MP4, MKV, AVI, MOV, WEBM, GIF) with support for resolutions up to 4K and quality.
- Video - Audio Converter
- Audio Converter: Convert audio to MP3, WAV, AAC, FLAC, OGG, WMA, and M4A with a choice of bitrates.

This application uses PyMuPDF, Pillow, and FFmpeg, with batch mode support to speed up the process.

---

## ✨ Key Features
- Modern interface based on PySide6.
- Fast conversion with a real-time progress bar.
- Multi-format conversion support (file, image, video, audio).
- Batch mode for converting multiple files at once.
- Quality and resolution optimization according to user needs.

---

## 📸 Screenshot
<img width="897" height="732" alt="Screenshot 2025-11-17 081839" src="https://github.com/user-attachments/assets/2306dc07-3777-459e-80ed-95e5128254cd" />




---
## 📜 Changelog v5.0.0
- ✨ New Features
Advanced Video Conversion: A new "Advanced Options" panel has been added, giving users granular control over:
Video Bitrate & FPS
Video Encoder (e.g., libx264, libx265, vp9)
Audio Encoder (e.g., aac, libmp3lame, ac3)
Audio Sample Rate, Bitrate, and Channels (Mono/Stereo)
Video Preset System:
Users can now save their custom advanced configurations as a named preset.
Saved presets can be easily loaded from a dropdown menu for future use.
The system automatically detects manual changes and switches to a "-- Custom --" state.
Dynamic Encoders: The Video Encoder list now intelligently updates based on the selected output container (e.g., MP4 and MKV will show different encoder options).

- 🖥️ UI/UX Improvements
Video Tab Redesign: The Video options panel has been completely rebuilt using a QSplitter.
Collapsible Panel: The "Advanced Options" checkbox now toggles the visibility of the new panel in a clean, expandable splitter layout, replacing the old layout.
Window & Layout:
The main window's default and minimum size has been increased to better accommodate the new options.
Minor stylesheet padding was adjusted for a tighter UI.

- ⚙️ Backend & Core
VideoConversionWorker: The worker class has been fundamentally upgraded to accept and process all new advanced parameters (is_advanced, v_bitrate, fps, v_encoder, etc.) and build the correct FFMPEG command.
Settings Persistence: The _save_settings and _load_settings functions now store all advanced video settings and saved user presets in QSettings, ensuring they persist between sessions.
Localization: All new UI elements and dialog boxes (e.g., "Save Preset") have been added to the multi-language dictionary for both Indonesian and English.
---

## ⚙️ Installation
1. Ensure Python 3.10+ is installed.
2. Install dependencies:


📦 Important Note
The source code shared in this repository is a framework/base project that serves as the foundation for the application.
For the full version with the latest features, please check the Releases section—ready-to-use binaries are available there.

📖 License
This project is released under the MIT license — free to use, modify, and distribute with proper credit.

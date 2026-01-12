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
<img width="905" height="733" alt="Screenshot 2025-12-30 181722" src="https://github.com/user-attachments/assets/e6ccca0e-2ba1-4b44-a45e-7d735901f25e" />
<img width="902" height="730" alt="Cuplikan layar 2026-01-12 210740" src="https://github.com/user-attachments/assets/53aee912-a4cf-4bb9-927d-715e41484dcb" />

---
## 📜 Changelog v6.2.0

## 🚀 New Features
- Custom Bitrate Support: Users can now manually define video bitrates (e.g., 5000k, 10M) in Advanced Mode. The system automatically validates and formats the input to ensure compatibility with the FFmpeg backend.
- CABAC Entropy Coding: Added support for CABAC (Context-adaptive binary arithmetic coding) parameters. This improves compression efficiency and video quality for H.264/AVC streams compared to CAVLC.
- Custom Parameter Injection: Introduced a dedicated "Custom Parameters" field. Advanced users can now pass direct CLI arguments to the FFmpeg process, allowing for specialized tuning not covered by the standard UI.
  
## 🛠️ Improvements & Fixes
- Optimized GPU Rendering (NVENC): * Refined the hardware acceleration pipeline for NVIDIA GPUs.
  - Fixed a critical bug where h264_nvenc would fail if the bitrate was set to "Auto" while in Advanced Mode.
  - Improved rate control management (-rc vbr) to ensure stable rendering when using custom bitrates on GPU.
- Parameter Validation: Implemented a sanitization layer to prevent conversion crashes caused by empty or malformed bitrate strings.
- Ref Frame Logic: Enhanced the handling of reference frames (-refs) to better align with hardware encoder limitations.
---

## ⚙️ Installation
1. Ensure Python 3.10+ is installed.
2. Install dependencies:


📦 Important Note
The source code shared in this repository is a framework/base project that serves as the foundation for the application.
For the full version with the latest features, please check the Releases section—ready-to-use binaries are available there.

📖 License
This project is released under the MIT license — free to use, modify, and distribute with proper credit.

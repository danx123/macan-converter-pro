# ♻️ Macan Converter Pro

Macan Converter Pro is a multi-conversion application for files, images, audio, and video.
Fast, modern, and easy to use.

Macan Converter Pro is a versatile PyQt6-based converter application that supports a wide range of file formats:
- File Converter: PDF → Image (PNG/JPG), PNG → ICO with a choice of resolutions.

- Image Converter: Convert images between formats (JPEG, PNG, WEBP, BMP, GIF), with resolution and quality settings.
- Video Converter: Convert videos to various formats (MP4, MKV, AVI, MOV, WEBM, GIF) with support for resolutions up to 4K and quality.
- Video - Audio Converter
- Audio Converter: Convert audio to MP3, WAV, AAC, FLAC, OGG, WMA, and M4A with a choice of bitrates.

This application uses PyMuPDF, Pillow, and FFmpeg, with batch mode support to speed up the process.

---

## ✨ Key Features
- Modern interface based on PyQt6.
- Fast conversion with a real-time progress bar.
- Multi-format conversion support (file, image, video, audio).
- Batch mode for converting multiple files at once.
- Quality and resolution optimization according to user needs.

---

## 📸 Screenshot
<img width="654" height="667" alt="Screenshot 2025-08-27 210353" src="https://github.com/user-attachments/assets/8a35bd2c-21a4-4a89-acf4-30020e377f2a" />
<img width="654" height="668" alt="Screenshot 2025-08-27 210408" src="https://github.com/user-attachments/assets/486b9b24-7363-4a8c-9acc-413dc2aec840" />
<img width="653" height="666" alt="Screenshot 2025-08-27 210425" src="https://github.com/user-attachments/assets/f6c45137-e70b-479d-bea5-aa65a7fe79ca" />

---
## 📜 Changelog v2.5.0
- Added conversion functions to the file converter tab, such as:
- Convert PDF files to .txt, .docx, and .xlsx
- Convert .docx to PDF
- Convert from Fambar to PDF

- Added a checkbox function: Shut down the PC after conversion is complete (in the video converter tab)
- Added a new tab called Video-Audio Converter (placed before the About tab)
- Added a function to convert video files to audio (complete) (in the Video-Audio Converter tab)

---

## ⚙️ Installation
1. Ensure Python 3.10+ is installed.
2. Install dependencies:

bash

pip install PyQt6 PyMuPDF Pillow

📦 Important Note
The source code shared in this repository is a framework/base project that serves as the foundation for the application.
For the full version with the latest features, please check the Releases section—ready-to-use binaries are available there.

📖 License
This project is released under the MIT license — free to use, modify, and distribute with proper credit.

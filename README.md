
# Photo Booth Workflow Manager

A desktop photo booth workflow application built with Python and PySide6 that automates photo ingestion, organization, editing, logo placement, and print session management for high-volume event photography workflows.

Designed to streamline real-world photography operations by handling folder management, live file watching, batch processing, non-destructive image editing, and GUI-based photo review.


<img width="894" height="711" alt="Screenshot 2026-05-27 at 6 23 18 PM" src="https://github.com/user-attachments/assets/6a85de75-a30c-4b74-ac4d-724190756a58" />

---

## Features

- Live folder watcher for automatic photo ingestion
- Session-based workspace and print organization
- Drag-and-drop photo importing
- Batch logo insertion with configurable placement
- Photo preview window with zoom and editing controls
- Brightness, contrast, gamma, and sharpness adjustments
- Selection management across photo/print workflows
- Archive system for raw and processed images
- GUI built with PySide6 (Qt for Python)
- Multi-threaded watcher system using `QThread`
- Print workflow management for event photography pipelines
- Quality-preserving image pipeline using Pillow (PIL)

---

## Tech Stack

### Languages
- Python

### GUI
- PySide6 (Qt)

### Image Processing
- Pillow (PIL)
- NumPy
- Torch / torchvision (orientation detection experiments)

### File System & Concurrency
- watchdog
- pathlib
- shutil
- QThread

---

## Project Structure

```bash
photo_app/
│
├── core/           # File management, watcher, editing logic
├── gui/            # PySide6 GUI components
├── processing/     # Image processing pipeline
├── data/           # Assets such as logos
├── workspace/      # Runtime photo workflow directories
└── main_gui.py     # Application entry point
````

---

## How to Run

### 1. Clone the repository

```bash
git clone https://github.com/InjuSmol/Photo-Editor.git
cd Photo-Editor
```

### 2. Create virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Launch the application

```bash
python3 main_gui.py
```

---
### Settings Page: 
<img width="696" height="552" alt="Screenshot 2026-05-27 at 6 18 33 PM" src="https://github.com/user-attachments/assets/7e9626bf-8698-4762-ba0c-fea6e1685b51" />

### Editor Page: 
<img width="896" height="712" alt="Screenshot 2026-05-27 at 6 21 33 PM" src="https://github.com/user-attachments/assets/0ae721c7-9b2b-40ba-b538-4b06081e9939" />
### Adjustments Applied: 
<img width="899" height="716" alt="Screenshot 2026-05-27 at 6 22 18 PM" src="https://github.com/user-attachments/assets/653b06e4-097d-4a9b-aafa-3f66df1c4f89" />
### Main Page: 
<img width="702" height="541" alt="Screenshot 2026-05-27 at 6 23 46 PM" src="https://github.com/user-attachments/assets/9a2cef95-85d6-4bd0-a4ad-5b099543e661" />

## Future Improvements

* AI-based blurry photo filtering
* Automatic face-aware cropping
* Non-destructive edit history
* RAW image support
* Export presets for print/social media
* Event-driven GUI updates via Qt signals
* Standalone desktop packaging with PyInstaller

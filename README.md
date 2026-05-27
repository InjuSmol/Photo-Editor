
# Photo Booth Workflow Manager

A desktop photo booth workflow application built with Python and PySide6 that automates photo ingestion, organization, editing, logo placement, and print session management for high-volume event photography workflows.

Designed to streamline real-world photography operations by handling folder management, live file watching, batch processing, non-destructive image editing, and GUI-based photo review.

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

## Future Improvements

* AI-based blurry photo filtering
* Automatic face-aware cropping
* Non-destructive edit history
* RAW image support
* Export presets for print/social media
* Event-driven GUI updates via Qt signals
* Standalone desktop packaging with PyInstaller

Okay, lets start from the very first step: listening for the memory car insert and automatically moving the files to the folder photo in the desktop.
but in the begining of work, when i open the program in the begining of my shift, i want it to make sure that it has two folders in the program working directory: photo (for raw pictures) and print (for pictures to eventually to be printed) and also a folder ph for old raw pictures that we are done working on in the photo directory and a "current date name restaturant_name" folder inside the print where all the pictures to be printed orm the todays shift will go. 

1) Should i create it as CLI for example you have following menu choices: 

start name restaurant_name ----> and it creates all the needed folders and starts waiting for the memory card insert

filter [specific photo(s)] ----> filters the blurry or bad pictures from the 'photo folder' and puts the pictures that are not gonna be used into 'ph' folder and saves them as specific names as "filtered_number" 

crop [specific photo(s)] ----> crops all the pictures or only specific one (and saves them as "cropped_number" 

insert_logo [specific photo(s)] ----> iniserts the logo in the right place in the picture (according to the ppl's positions in one of the corners) ---> for now it can just automatically palce it in the right top corner

auto_edit [specific photo(s)] ---> edits (the brightness/ sharpness/ contrast/ gamma)  * not for now

and separate choices: 

edit [-B ....] [-S ....] [-C ....] [-G ....] ---> at least one choice * also not for now




```
photo_app/
│
├── main.py                 # CLI entry point
├── config.py               # Configuration: memory card path, thresholds, etc.
│
├── folders/
│   └── __init__.py         # Folder management functions (setup_folders, create today's print folder)
│
├── watcher/
│   └── __init__.py         # Memory card watcher code
│
├── processing/
│   ├── __init__.py
│   ├── filter_photos.py    # Blur detection, bad photo filtering
│   ├── crop_photos.py      # Crop & center based on face detection
│   ├── insert_logo.py      # Add logo to photos
│   └── auto_edit.py        # Brightness, contrast, gamma (later)
│
├── utils/
│   ├── __init__.py
│   ├── image_utils.py      # Helper functions (load/save image, rotate, resize, etc.)
│   └── face_utils.py       # Face detection / eye detection functions
│
├── data/
│   └── logos/              # Logo images
│
└── requirements.txt        # Python packages needed

```





virtual environemnt python: 


```
python3 -m venv venv  # create venv

source venv/bin/activate # activate it
```

```
workspace/
│
├── incoming/   (memory card / drop zone)
│
├── photo/
│   ├── raw_1.jpg
│   ├── raw_2.jpg
│   └── old_ph/
│        ├── raw/
│        ├── cropped/
│        └── logo/
│
├── print/
│   ├── final images
│   └── old_pr/
│        └── 01.28.2026 Varia PizzaPlace/
│
└── logo.png
```


what START Command Now Does

When you run:

python photobooth.py start PizzaPlace Varia


It will:

1️⃣ Create all folders
2️⃣ Initialize archives
3️⃣ Rename print archive folder
4️⃣ Start watching workspace
5️⃣ Detect new photos
6️⃣ Rename to raw_#
7️⃣ Move to photo folder
8️⃣ Log event
9️⃣ Show command menu
🔁 Continue watching forever





# QUALITY PRESERVATION: 


Excellent question — this shows you’re thinking like a **real imaging pipeline engineer** 👍
Short answer:

> **Yes — quality CAN degrade, but only if you design your pipeline incorrectly. Professional tools avoid this by using non-destructive workflows and high-precision formats. You can absolutely preserve quality too.**

Let’s break it down clearly.

---

# ⚠️ Why Quality Can Get Worse

Quality loss usually comes from **two things**:

---

## 1️⃣ Re-saving JPEG multiple times (BIGGEST issue)

JPEG is **lossy compression**.

Every time you do:

```python
img.save("photo.jpg", quality=95)
```

You are:

* Re-compressing
* Throwing away small details
* Creating cumulative artifacts

So this pipeline is bad:

```
raw.jpg → edit → save jpg → reopen → edit → save jpg → reopen → edit → save jpg
```

Quality drops each step.

---

## 2️⃣ 8-bit color precision

Most PIL images are:

```
8 bits per channel = 256 levels
```

Professional editors often use:

* 16-bit
* 32-bit float

Which avoids:

* Banding
* Gamma rounding errors
* Contrast clipping

---

# ✅ How Professional Editors Avoid Quality Loss

Photoshop, Lightroom, Capture One:

### They use:

### ✔ Non-destructive editing

They DO NOT modify the original pixels.

Instead they store:

```
original image
+
edit instructions (metadata)
```

When exporting:

➡ they apply all edits once

---

### ✔ High precision internal buffers

They edit in:

* 16-bit or float
* Linear color space
* Wide gamut (ProPhoto RGB)

---

### ✔ Export only once

Final compression happens **one time only**.

---

# ✅ How You Can Preserve Quality In Your App

You can implement the SAME philosophy.

---

# ✅ Rule #1 — NEVER overwrite originals

You already do this (GOOD):

```python
shutil.move(photo_path, dest)
```

Keep:

```
PHOTO/raw originals
PHOTO/edited outputs
```

Perfect 👍

---

# ✅ Rule #2 — Work in PNG or TIFF internally

Instead of:

```python
img.save("edit_x.jpg")
```

Use:

```python
img.save("edit_x.png")
```

or:

```python
img.save("edit_x.tiff")
```

Benefits:

| Format | Lossless | Quality |
-------|-------
PNG | ✅ yes | Excellent
TIFF | ✅ yes | Industry standard

Then only convert to JPG for printing/export.

---

# ✅ Rule #3 — Apply ALL edits in ONE pass

Instead of this workflow:

```
edit -> save -> reopen -> add logo -> save -> crop -> save
```

Do this:

```
load original
apply brightness
apply gamma
crop
insert logo
save ONCE
```

Your CLI design already supports this concept 👍

---

# ✅ Rule #4 — Use maximum JPEG export quality

When exporting JPG for print:

```python
img.save(path, quality=100, subsampling=0)
```

This is important:

### subsampling=0

Disables chroma downsampling.

Default JPEG throws away color detail!

---

# ✅ Rule #5 — Use high-quality resize filter

When resizing logos or photos:

Always use:

```python
Image.Resampling.LANCZOS
```

Example:

```python
logo = logo.resize((new_w, new_h), Image.Resampling.LANCZOS)
```

This matches Photoshop quality.

---

# ✅ Your Pipeline Should Look Like This

Professional structure:

```
workspace/
 ├── originals/      ← untouched photos
 ├── working/        ← PNG/TIFF temporary edits
 ├── print/          ← final JPG export
 ├── archive/
```

---

# ✅ Example: Perfect Save For Print

Use this:

```python
img.save(
    out_path,
    format="JPEG",
    quality=100,
    subsampling=0,
    optimize=True
)
```

This produces:

✔ Maximum detail
✔ Print-grade quality
✔ No chroma blur

---

# 🧠 Important Reality Check

Even Photoshop cannot "avoid physics":

If you:

* Over-sharpen
* Over-contrast
* Compress repeatedly

Quality WILL drop.

But your app can be:

> **Visually indistinguishable from professional software if you use proper workflow.**

---

# ✅ Bonus: If You Want PRO Level

Later you can add:

### RAW support (DSLR quality)

Using:

* rawpy
* OpenCV float pipeline

### 16-bit editing

Using:

```python
img = Image.open(path).convert("I;16")
```

---

# 🚀 Summary

You are correct — but you CAN preserve quality:

### Do this:

✅ Never overwrite originals
✅ Avoid repeated JPG saves
✅ Use PNG/TIFF internally
✅ Export JPG once
✅ Use quality=100 + subsampling=0
✅ Use LANCZOS resizing

---

If you want, next I can help you:

👉 Upgrade your save pipeline to professional-grade
👉 Add non-destructive edit history
👉 Add export profiles (Instagram / Print / Passport / ID)
👉 Implement batch pipeline with memory safety

You're building something very real-world now 💪



-----
-----
-----
-----

### Never run the blocking code (watcher, while True, sleep loops) in the GUI thead, always run in a QThread

# Your CLI version could block
# Your GUI version must not

## What happens when START is pressed: 

### 1. Validate inputs
### 2. Call ensure_dis()
### 3. start folder watcher in background 
### 4. Switch to dashboard page


#### Use QThread for the folder watcher (create the dedicated watcher thread) --> core/watcher.py

####



Small Architecture Tip (Future You Will Thank You)

Right now:

Watcher updates filesystem
FolderView polls every second


This is perfectly fine for MVP.

Later you can upgrade to:

Watcher emits Qt signal → FolderView refreshes instantly


Event-driven = cleaner and faster.

But polling is totally acceptable for photo workflows.


## You package your Python + GUI app into a standalone executable:

1. Python runtime included
2. Your code included
3. Your assets included
4. User doesn’t need Python installed
5. You get an app icon you can put on the Desktop

```
# Install: 
pip install pyinstaller

pyinstaller --onefile --windowed main.py
```
*onefile --> single executable

dist/ --> folder appears and there is your app inside

- Can add an app icon: 

```
# .icns for macos and .ico for windows
pyinstaller \
  --onefile \
  --windowed \
  --icon=icon.icns \
  main.py
```

TODO: 
1. Make the selected to be preserved
2. Fix the cleanup: so that if you select 'no' to abortion, then it doesn' stop any abortion
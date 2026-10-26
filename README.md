<div align="center">

# 📝 Google Keep → Joplin Converter

**Migrate your Google Keep notes to Joplin — without losing your notes, your checkboxes, or your dates.**

[![Python](https://img.shields.io/badge/python-3.6%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/keshavsapra/Google-Keep-to-Joplin/issues)
[![No external GUI deps](https://img.shields.io/badge/GUI-optional-orange.svg)](#-troubleshooting)

</div>

---

Google Keep exports your notes as HTML via [Google Takeout](https://takeout.google.com/), but Joplin imports Markdown. This script bridges that gap — parsing every exported note, converting it to clean Markdown, and preserving the **last-edited timestamp** so your history stays intact.

## ✨ Why use it?

```
                                                ┌──────────────────────────┐
  Google Takeout (Keep/*.html + *.json)  ──▶   │ converted files/*.md     │ ──▶  Joplin
                                                │  ✅ clean markdown        │      File ▸ Import ▸
                                                │  ✅ checkboxes preserved  │      Markdown (Directory)
                                                │  ✅ dates preserved       │
                                                └──────────────────────────┘
```

| Google Keep (Takeout HTML) | Joplin (converted Markdown) |
| :--- | :--- |
| `<input type="checkbox" checked>` Milk | `- [x] Milk` |
| `<input type="checkbox">` Bread | `- [ ] Bread` |
| ~~"Date modified" lost on export~~ | 🗓 Last-edit timestamp carried over from the `.json` metadata |

## 🚀 Quick Start

```bash
# 1. Grab the script
git clone https://github.com/keshavsapra/Google-Keep-to-Joplin.git
cd Google-Keep-to-Joplin

# 2. Install the two pip libraries
pip install beautifulsoup4 markdownify

# 3. Point it at your unzipped Takeout "Keep" folder
python convert_keep_to_markdown.py /path/to/Keep
```

Then in Joplin: **File ▸ Import ▸ Markdown (Directory)** → select the `converted files` folder that appears inside your Keep folder. Done! 🎉

## ⚙️ Requirements

| Component | How to get it |
| :--- | :--- |
| Python 3.x | [python.org](https://www.python.org/downloads/) |
| `beautifulsoup4` + `markdownify` | `pip install beautifulsoup4 markdownify` |
| `tkinter` *(optional)* | Only needed for the GUI folder picker — **it's a system package, not a pip package** (see below) |

### Installing tkinter (optional, for the GUI picker)

> 💡 **You can skip this entirely** by passing the folder path as a command-line argument — no GUI needed.

**Ubuntu / Debian:**
```bash
sudo apt install python3-tk
```

**Fedora / RHEL:**
```bash
sudo dnf install python3-tkinter
```

**Arch Linux:**
```bash
sudo pacman -S tk
```

**macOS / Windows:** tkinter ships with the python.org installer by default. If `import tkinter` fails, reinstall Python from [python.org](https://www.python.org/downloads/) and make sure the **Tcl/Tk** option is checked.

Check whether you already have it:
```bash
python -c "import tkinter"
```
No output = you're good. ✔️

## 📤 Getting your notes out of Google

1. Go to [Google Takeout](https://takeout.google.com/).
2. Deselect everything, then select **Keep**.
3. Export in **HTML** format, download the zip, and unzip it.
4. Your notes (as `.html` files with `.json` metadata sidecars) will be in a folder named `Keep`.

## 🛠 Usage

**Option A — GUI folder picker** (requires tkinter):
```bash
python convert_keep_to_markdown.py
```

**Option B — Command line** (works even without tkinter):
```bash
python convert_keep_to_markdown.py /path/to/Keep
```

The script creates a `converted files` subfolder next to your HTML notes and drops one clean `.md` file per Keep note into it. Each file's **"Date modified" matches the note's last edit** in Google Keep — pulled from the `userEditedTimestampUsec` field in the Takeout `.json` metadata (with a fallback to the HTML file's own timestamp if the JSON is missing).

## 🧰 Troubleshooting

<details>
<summary><b>❌ <code>ModuleNotFoundError: No module named 'tkinter'</code></b></summary>

This is the most common issue on Linux. **tkinter is part of the OS, not pip** — `pip install tkinter` does not exist.

- Either install it with your system package manager (see [Installing tkinter](#%EF%B8%8F-installing-tkinter-optional-for-the-gui-picker)),
- or simply run with the folder as an argument instead of using the GUI:
  ```bash
  python convert_keep_to_markdown.py /path/to/Keep
  ```

</details>

<details>
<summary><b>❌ <code>ModuleNotFoundError: No module named 'bs4'</code> or <code>'markdownify'</code></b></summary>

```bash
pip install beautifulsoup4 markdownify
```
If pip complains about an *externally managed environment* (PEP 668) on newer Linux distros, either create a virtual environment (`python -m venv .venv && source .venv/bin/activate`) or use `pip install --break-system-packages` at your own risk.

</details>

<details>
<summary><b>❌ No HTML files found</b></summary>

Make sure you selected the folder that **directly contains** the exported `.html` note files (usually the `Keep` folder inside the Takeout zip — or a `Takeout/Keep/` subfolder). Note that attachments Live in a separate `Attachments` folder; point the script at the folder with the `.html` files.

</details>

<details>
<summary><b>❌ Date modified isn't right on some notes</b></summary>

The timestamp comes from the `.json` sidecar file Takeout exports next to each `.html`. If a JSON file is missing or malformed, the script falls back to the HTML file's own mtime — which can lag behind the true last edit. As long as both files are present, your dates will be exact.

</details>

## 🔍 How It Works

For every `.html` file in the selected folder, the script:

1. Parses the Takeout HTML with **BeautifulSoup4** and extracts the `title` and `note-content` divs.
2. Rewrites every checkbox `<li>` into Markdown task syntax (`- [x]` / `- [ ]`) before general conversion.
3. Runs **markdownify** to convert the remaining HTML to clean Markdown.
4. Prepends the title as a `# Heading 1`.
5. Saves the result as `converted files/<Title>.md` using a sanitized filename.
6. Restores the note's real last-modified date by reading `userEditedTimestampUsec` from the matching `.json` metadata file and applying it with `os.utime()` (falls back to the HTML's mtime if the JSON is absent).

## ⚠️ Limitations

* Depends on the HTML structure Google Takeout currently generates — if Google changes it significantly, the script may need an update.
* Only text, lists, and checkboxes are handled. Embedded **images and attachments aren't copied** into the Markdown output.
* Very complex formatting (tables, colors, drawings) may not translate perfectly.

## 🤝 Contributing

Issues, pull requests and feature ideas are very welcome — head over to the [issues page](https://github.com/keshavsapra/Google-Keep-to-Joplin/issues).

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.



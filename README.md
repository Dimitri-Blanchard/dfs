# ✨ ShowFile (wsf) 📂

[![Python Version](https://img.shields.io/badge/Python-3.x-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Made with Rich](https://img.shields.io/badge/Made%20with-Rich-cyan.svg)](https://github.com/Textualize/rich)

ShowFile (`wsf`) is a command-line file browser and viewer featuring a rich terminal interface powered by the `rich` library. It provides an enhanced alternative to standard commands like `ls`, `cat`, and `dir` for navigating directories and previewing file contents.

---

## 🌟 Features

* **Interactive Navigation:** Browse directories using arrow keys, open files or enter directories with `Enter`. Navigate up to the parent directory easily.
* **Rich Terminal Interface:** Utilizes `rich` for clear presentation using tables, panels, and syntax highlighting.
* **File Preview:**
    * Displays text-based files with automatic syntax highlighting (Python 🐍, JSON, Markdown 📝, etc.).
    * Renders Markdown files directly in the terminal.
    * Provides a hexadecimal view 👾 for binary files.
    * Option to open non-text files (e.g., images 🖼️) using the system's default application.
* **Detailed Information:** Shows file metadata including size, modification date, MIME type, permissions, and calculates MD5/SHA1/SHA256 hashes 🔍.
* **Directory Statistics:** Analyzes directory contents to display total size, item counts, size distribution by file extension, and lists the largest files 📊.
* **Integrated Search:** Recursively search for files and directories by name within the current path 🕵️‍♀️.
* **Customization:**
    * Selectable color themes 🎨 for syntax highlighting.
    * Toggle visibility of hidden files (`.dotfiles`) 👁️.
    * Sort directory listings by name, type, size, or modification date (ascending/descending) ⇅.
* **File Type Icons:** Uses Unicode icons (e.g., 📁, 📄, 🐍, 🎵, 🎬, 📦) for quick identification.
* **Pagination:** Handles large directories by displaying content in pages 📖.
* **Cross-Platform:** Compatible with Linux 🐧, macOS 🍎, and Windows 🪟.

---

## 🚀 Installation

1.  **Prerequisites:** Requires Python 3.x 🐍.
2.  **Obtain the script:** Download the `wsf.py` file.
3.  **Install dependencies:** The primary dependency is `rich`.
    ```bash
    pip install rich
    ```
    *(Using a virtual environment is recommended: `python -m venv venv && source venv/bin/activate`)*
4.  **(Optional) Make globally accessible:**
    * Ensure the script is executable: `chmod +x wsf.py`.
    * Move `wsf.py` to a directory in your system's `PATH`, renaming it to `wsf`:
        ```bash
        mv wsf.py ~/.local/bin/wsf
        # Ensure ~/.local/bin is in your PATH environment variable
        ```

---

## 🛠️ Usage

If installed globally (step 4 above), invoke using:

Enter a Folder with wsf:
```bash
wsf ([FOLDER PATH])
```

View a File:
```bash
wsf --file [FILE PATH]
```

Enter wsf menu's:
```bash
wsf
```

Key	Action		
* `↑` / `↓`	Navigate list entries		
* `←` / `→`	Navigate pages (for long listings)		
* `Enter`	Enter selected directory / Preview selected file		
* Select `..` + `Enter`	Go to parent directory		
* `Tab`	Access context menu (Statistics, Hex View, etc.)		
* `/`	Initiate search within the current directory		
* `h`	Toggle visibility of hidden files		
* `s`	Change sorting criteria (name, type, size, date)		
* `r`	Refresh the current view		
* `f`	Toggle favorite status (basic implementation)⭐		
* `q`	Quit ShowFile (wsf)

---

## ⚙️ Configuration

Default settings (theme, hidden file visibility, sort order) are defined in the CONFIG dictionary at the beginning of the wsf.py script. These can be modified directly in the source file.

```
CONFIG = {
    "theme": "monokai",
    "show_hidden": False,
    "sort_by": "name",
    "reverse_sort": False,
    # ... other settings
}
```

---

## 📦 Dependencies

* Python 3.x
* Rich library (pip install rich)

---

## 🙏 Contributing

Contributions are welcome. Please follow standard practices such as:

1. Forking the repository (if applicable).
2. Creating feature branches (git checkout -b feature/YourFeature).
3. Committing changes (git commit -m 'Add YourFeature').
4. Pushing to the branch (git push origin feature/YourFeature).
5. Opening a Pull Request. Alternatively, open an issue to report bugs or suggest features.

---

## 📜 License

This project is distributed under the MIT License (confirm or specify actual license).

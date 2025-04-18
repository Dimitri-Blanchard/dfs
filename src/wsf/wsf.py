#!/usr/bin/env python3
import os
import sys
import argparse
import shutil
import time
from datetime import datetime
from pathlib import Path
import subprocess
import platform
import mimetypes
import hashlib
from rich.console import Console
from rich.table import Table
from rich.syntax import Syntax
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.markdown import Markdown
from rich.tree import Tree
from rich import box
from rich.progress import track
from rich.filesize import decimal as filesize_decimal

console = Console()

                       
CONFIG = {
    "theme": "monokai",
    "show_hidden": False,
    "sort_by": "name",                          
    "reverse_sort": False,
    "preview_size": 2000,                                           
    "recent_paths": [],
    "favorites": [],
}

                            
FILE_ICONS = {
    ".py": "🐍",
    ".js": "📜",
    ".html": "🌐",
    ".css": "🎨",
    ".md": "📝",
    ".txt": "📄",
    ".pdf": "📕",
    ".jpg": "🖼️",
    ".png": "🖼️",
    ".gif": "🖼️",
    ".mp3": "🎵",
    ".mp4": "🎬",
    ".zip": "📦",
    ".tar": "📦",
    ".gz": "📦",
    ".json": "📋",
    ".xml": "📋",
    ".csv": "📊",
    ".xls": "📊",
    ".xlsx": "📊",
    ".doc": "📘",
    ".docx": "📘",
    ".sh": "⚙️",
    ".bat": "⚙️",
    ".exe": "⚙️",
    ".db": "🗄️",
    ".sql": "🗄️",
    ".c": "💻",
    ".cpp": "💻",
    ".java": "☕",
    ".php": "🐘",
    ".rb": "💎",
    ".rs": "🦀",
    ".go": "🐹",
}

def get_file_info(path):
                                                              
    try:
        stat = os.stat(path)
        size = stat.st_size
        modified = datetime.fromtimestamp(stat.st_mtime)
        
                   
        mime_type, _ = mimetypes.guess_type(path)
        if mime_type is None:
            if os.access(path, os.X_OK):
                mime_type = "application/x-executable"
            else:
                mime_type = "application/octet-stream"
                
                                     
        extension = os.path.splitext(path)[1].lower()
        icon = FILE_ICONS.get(extension, "📄")
        
        return {
            "size": size,
            "size_str": format_size(size),
            "modified": modified,
            "modified_str": modified.strftime("%d/%m/%Y %H:%M"),
            "mime_type": mime_type,
            "icon": icon,
            "extension": extension
        }
    except Exception as e:
        return {
            "size": 0,
            "size_str": "N/A",
            "modified": datetime.now(),
            "modified_str": "N/A",
            "mime_type": "unknown",
            "icon": "❓",
            "extension": ""
        }

def format_size(size):
                                                        
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} PB"

def calculate_hash(path, algorithm="md5"):
                                       
    hash_obj = hashlib.new(algorithm)
    try:
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_obj.update(chunk)
        return hash_obj.hexdigest()
    except Exception:
        return "Impossible de calculer le hash"

def list_directory(path, show_details=True):
                                                                       
    entries = []
    
    try:
        items = os.listdir(path)
        
                                                  
        if not CONFIG["show_hidden"]:
            items = [item for item in items if not item.startswith('.')]
        
        for item in items:
            full_path = os.path.join(path, item)
            is_dir = os.path.isdir(full_path)
            
            entry = {
                "name": item,
                "path": full_path,
                "is_dir": is_dir,
                "type": "📁 Dossier" if is_dir else "📄 Fichier"
            }
            
            if show_details and not is_dir:
                entry.update(get_file_info(full_path))
            elif show_details:
                                   
                try:
                    count = len(os.listdir(full_path))
                    entry["content_count"] = count
                    entry["content_str"] = f"{count} éléments"
                    entry["icon"] = "📁"
                except:
                    entry["content_count"] = -1
                    entry["content_str"] = "Inaccessible"
                    entry["icon"] = "🔒"
            
            entries.append(entry)
        
             
        sort_key = CONFIG["sort_by"]
        reverse = CONFIG["reverse_sort"]
        
        if sort_key == "name":
            entries.sort(key=lambda x: x["name"].lower(), reverse=reverse)
        elif sort_key == "type":
            entries.sort(key=lambda x: (not x["is_dir"], x["name"].lower()), reverse=reverse)
        elif sort_key == "size" and show_details:
            entries.sort(key=lambda x: x.get("size", 0) if not x["is_dir"] else x.get("content_count", -1), reverse=reverse)
        elif sort_key == "date" and show_details:
            entries.sort(key=lambda x: x.get("modified", datetime.now()), reverse=reverse)
        
                                                                           
        if sort_key != "type":
            entries.sort(key=lambda x: not x["is_dir"])
            
    except Exception as e:
        console.print(f"[bold red]Erreur lors de la lecture du répertoire :[/] {e}")
    
    return entries

def display_directory_listing(path, entries=None, selected_idx=0, page_size=20):
                                                                                      
    if entries is None:
        entries = list_directory(path)
    
                             
    total_entries = len(entries)
    total_pages = max(1, (total_entries + page_size - 1) // page_size)                        
    current_page = min(max(0, (selected_idx + 1) // page_size), total_pages - 1)
    
    start_idx = current_page * page_size
    end_idx = min(start_idx + page_size, total_entries)
    
                                   
    console.print(Panel(
        Text(f"📂 {os.path.abspath(path)}", style="bold cyan"),
        title="SuperFile Explorer",
        subtitle=f"{total_entries} éléments (page {current_page + 1}/{total_pages})",
        border_style="blue"
    ))
    
                                      
    table = Table(box=box.ROUNDED, show_header=True, header_style="bold cyan", expand=True, show_lines=False)
    
              
    table.add_column("", style="cyan", width=3)             
    table.add_column("", width=2)         
    table.add_column("Nom", style="cyan", no_wrap=True)
    
    if CONFIG["sort_by"] != "type":                                            
        table.add_column("Type", style="magenta", width=12)
        
    if CONFIG["sort_by"] not in ["size", "date"]:                                                  
        table.add_column("Taille", style="green", width=10, justify="right")
        table.add_column("Modifié", style="yellow", width=16)
    else:
                                                                         
        if CONFIG["sort_by"] != "size":
            table.add_column("Taille", style="green", width=10, justify="right")
        if CONFIG["sort_by"] != "date":
            table.add_column("Modifié", style="yellow", width=16)
    
                              
    if path != '/':
        icon = "📁"
        parent_path = os.path.dirname(path)
        select_marker = "→" if selected_idx == -1 else " "
        
        row = [select_marker, icon, ".."]
        
        if CONFIG["sort_by"] != "type":
            row.append("Parent")
            
        if CONFIG["sort_by"] not in ["size", "date"]:
            row.extend(["", ""])
        else:
            if CONFIG["sort_by"] != "size":
                row.append("")
            if CONFIG["sort_by"] != "date":
                row.append("")
                
        table.add_row(*row, style="dim")
    
                                           
    for idx in range(start_idx, end_idx):
        entry = entries[idx]
        select_marker = "→" if idx == selected_idx else " "
        name = entry["name"]
        
        if entry["is_dir"]:
            icon = entry.get("icon", "📁")
            size_str = entry.get("content_str", "")
            date_str = entry.get("modified_str", "")
        else:
            icon = entry.get("icon", "📄")
            size_str = entry.get("size_str", "")
            date_str = entry.get("modified_str", "")
        
        row = [select_marker, icon, name]
        
        if CONFIG["sort_by"] != "type":
            row.append("Dossier" if entry["is_dir"] else "Fichier")
            
        if CONFIG["sort_by"] not in ["size", "date"]:
            row.extend([size_str, date_str])
        else:
            if CONFIG["sort_by"] != "size":
                row.append(size_str)
            if CONFIG["sort_by"] != "date":
                row.append(date_str)
                
        style = "bold" if idx == selected_idx else None
        table.add_row(*row, style=style)
    
    console.print(table)
    
                  
    disk_usage = shutil.disk_usage(path)
    free_percent = disk_usage.free / disk_usage.total * 100
    
    status = Text()
    status.append(f"Espace libre: {format_size(disk_usage.free)} / {format_size(disk_usage.total)} ", "green")
    status.append(f"({free_percent:.1f}%) ", "green" if free_percent > 20 else "red")
    status.append(f"• Tri: {CONFIG['sort_by'].capitalize()}", "cyan")
    status.append(f" • {'↑' if CONFIG['reverse_sort'] else '↓'}", "cyan")
    status.append(f" • {'Fichiers cachés: Oui' if CONFIG['show_hidden'] else 'Fichiers cachés: Non'}", "cyan")
    
    console.print(Panel(status, border_style="blue"))
    
                 
    help_text = (
        "[↑↓]: Naviguer • [←→]: Changer page • [Enter]: Ouvrir • [Tab]: Options • "
        "[/]: Rechercher • [h]: Fichiers cachés • [s]: Trier • [f]: Favoris • [q]: Quitter"
    )
    console.print(Text(help_text, style="dim"))

                                                                           
def interactive_explorer(start_path):
                                                                          
    current_path = os.path.abspath(start_path)
    selected_idx = 0
    page_size = 20                              
    
                                                                 
    if platform.system() == 'Windows':
        import msvcrt
        
        def get_key():
            key = msvcrt.getch()
                                                                                   
            if key == b'\xe0':
                return {b'H': 'up', b'P': 'down', b'M': 'right', b'K': 'left'}[msvcrt.getch()]
                                      
            return {b'\r': 'enter', b'\t': 'tab', b'/': 'search', b'h': 'h', 
                   b's': 's', b'r': 'r', b'f': 'f', b'q': 'q', b' ': 'space'}.get(key, None)
    else:
                               
        try:
            import tty
            import termios
            
            def get_key():
                fd = sys.stdin.fileno()
                old_settings = termios.tcgetattr(fd)
                try:
                    tty.setraw(sys.stdin.fileno())
                    ch = sys.stdin.read(1)
                                                                                   
                    if ch == '\x1b':
                        ch = sys.stdin.read(2)
                        if ch == '[A':
                            return 'up'
                        elif ch == '[B':
                            return 'down'
                        elif ch == '[C':
                            return 'right'
                        elif ch == '[D':
                            return 'left'
                    return {'\r': 'enter', '\n': 'enter', '\t': 'tab', '/': 'search', 'h': 'h', 
                           's': 's', 'r': 'r', 'f': 'f', 'q': 'q', ' ': 'space'}.get(ch, None)
                finally:
                    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        except ImportError:
                                                                
            def get_key():
                return Prompt.ask("\nAction", choices=["u", "d", "l", "r", "Enter", "Tab", "/", "h", "s", "r", "f", "q"], show_choices=False)
    
    while True:
        console.clear()
        entries = list_directory(current_path)
        total_entries = len(entries)
        
                                    
        total_pages = max(1, (total_entries + page_size - 1) // page_size)                        
        current_page = min(max(0, (selected_idx + 1) // page_size), total_pages - 1)
        
        display_directory_listing(current_path, entries, selected_idx, page_size)
        
                              
        key = get_key()
        
        if key == 'q':
            break
        elif key == 'up':
                                                                     
            if selected_idx > -1:                               
                selected_idx = max(selected_idx - 1, -1)
            else:
                selected_idx = -1                              
        elif key == 'down':
                                   
            selected_idx = min(selected_idx + 1, len(entries) - 1)
        elif key == 'left':
                             
            new_page = max(current_page - 1, 0)
            selected_idx = max(new_page * page_size, -1)
        elif key == 'right':
                           
            if current_page < total_pages - 1:
                new_page = min(current_page + 1, total_pages - 1)
                selected_idx = new_page * page_size
        elif key == 'space':
                                         
            if current_page < total_pages - 1:
                new_page = min(current_page + 1, total_pages - 1)
                selected_idx = new_page * page_size
        elif key == 'enter':
                                
            if selected_idx == -1:
                if current_path != '/':
                    current_path = os.path.dirname(current_path)
                selected_idx = 0
                                          
            elif selected_idx < len(entries):
                selected = entries[selected_idx]
                if selected["is_dir"]:
                    current_path = selected["path"]
                    selected_idx = 0
                else:
                    console.clear()
                    view_file(selected["path"])
                    input("\n[Appuie sur Entrée pour revenir]")

def view_file(path, highlight=True):
                                                                
    try:
        file_info = get_file_info(path)
        mime_type = file_info["mime_type"]
        size = file_info["size"]
        
                                   
        header = Layout()
        header.split_column(
            Layout(name="title"),
            Layout(name="info")
        )
        
        title_text = Text(f"{file_info['icon']} {os.path.basename(path)}", style="bold cyan")
        file_path = Text(f"  {os.path.dirname(os.path.abspath(path))}", style="dim")
        
        header["title"].update(Panel(title_text, subtitle=str(file_path), border_style="blue"))
        
        info_table = Table.grid(expand=True)
        info_table.add_column(style="green")
        info_table.add_column(style="white")
        info_table.add_column(style="green")
        info_table.add_column(style="white")
        
        info_table.add_row(
            "Taille:", file_info["size_str"], 
            "Type:", mime_type
        )
        info_table.add_row(
            "Modifié:", file_info["modified_str"],
            "Hash (MD5):", calculate_hash(path, "md5")[:8] + "..."
        )
        
        header["info"].update(Panel(info_table, border_style="blue"))
        
        console.print(header)
        
                                   
        if mime_type and ("text" in mime_type or mime_type in [
            "application/json", "application/xml", "application/javascript", 
            "application/x-python-code", "application/x-sh"
        ]):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    code = f.read()
                if highlight:
                    lexer_name = Syntax.guess_lexer(path)
                    syntax = Syntax(code, lexer=lexer_name, theme=CONFIG["theme"], line_numbers=True, word_wrap=True)
                    console.print(Panel(syntax, border_style="blue"))
                else:
                    console.print(Panel(Text(code), border_style="blue"))
            except UnicodeDecodeError:
                                                                             
                console.print("[yellow]Ce fichier contient des données binaires ou utilise un encodage non UTF-8.[/]")
                if Confirm.ask("Afficher la vue hexadécimale?"):
                    view_hex(path)
                                   
        elif mime_type and "image" in mime_type:
            console.print("[yellow]Les images ne peuvent pas être affichées dans le terminal.[/]")
            if platform.system() == "Windows":
                if Confirm.ask("Ouvrir avec le visualiseur d'images par défaut?"):
                    os.startfile(path)
            elif platform.system() == "Darwin":         
                if Confirm.ask("Ouvrir avec le visualiseur d'images par défaut?"):
                    subprocess.run(["open", path])
            else:                   
                if Confirm.ask("Ouvrir avec le visualiseur d'images par défaut?"):
                    subprocess.run(["xdg-open", path])
                                      
        elif path.lower().endswith(".md"):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                md = Markdown(content)
                console.print(Panel(md, border_style="blue"))
            except Exception as e:
                console.print(f"[bold red]Erreur lors de l'affichage du markdown :[/] {e}")
                                                                
        else:
            console.print(f"[yellow]Ce fichier n'est pas de type texte ({mime_type}).[/]")
            if size > 1024 * 1024:                
                if not Confirm.ask(f"Ce fichier est volumineux ({file_info['size_str']}). Continuer?"):
                    return
            if Confirm.ask("Afficher la vue hexadécimale?"):
                view_hex(path)
    except Exception as e:
        console.print(f"[bold red]Erreur :[/] {e}")

def view_hex(path, chunk_size=16, max_bytes=4096):
                                                    
    try:
        with open(path, 'rb') as f:
            offset = 0
            table = Table(title=f"Vue hexadécimale de {os.path.basename(path)}", 
                         box=box.ROUNDED, show_header=True, header_style="bold cyan")
            
            table.add_column("Offset", style="green")
            table.add_column("Hexadécimal", style="yellow")
            table.add_column("ASCII", style="cyan")
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                TimeElapsedColumn(),
            ) as progress:
                task = progress.add_task("[cyan]Lecture du fichier...", total=min(os.path.getsize(path), max_bytes))
                
                while offset < max_bytes:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    
                                        
                    hex_view = " ".join(f"{b:02x}" for b in chunk)
                    if len(hex_view) < chunk_size * 3 - 1:
                        hex_view += " " * (chunk_size * 3 - 1 - len(hex_view))
                    
                                                                                                   
                    ascii_view = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
                    
                    table.add_row(f"0x{offset:08x}", hex_view, ascii_view)
                    
                    offset += len(chunk)
                    progress.update(task, advance=len(chunk))
                    
                    if offset >= max_bytes:
                        break
            
            console.print(table)
            if offset >= max_bytes and os.path.getsize(path) > max_bytes:
                console.print(f"[yellow]Affichage limité aux premiers {format_size(max_bytes)} du fichier.[/]")
    except Exception as e:
        console.print(f"[bold red]Erreur lors de la lecture hexadécimale :[/] {e}")

def search_in_directory(path, query, max_results=100):
                                                              
    results = []
    query_lower = query.lower()
    
    console.print(f"[cyan]Recherche de[/] [yellow]'{query}'[/] [cyan]dans[/] [yellow]'{path}'[/]")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True
    ) as progress:
        search_task = progress.add_task("[cyan]Recherche en cours...", total=None)
        
        for root, dirs, files in os.walk(path):
                                                               
            if not CONFIG["show_hidden"]:
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                files = [f for f in files if not f.startswith('.')]
            
            for item in dirs + files:
                if query_lower in item.lower():
                    full_path = os.path.join(root, item)
                    is_dir = os.path.isdir(full_path)
                    
                    results.append({
                        "name": item,
                        "path": full_path,
                        "rel_path": os.path.relpath(full_path, path),
                        "is_dir": is_dir,
                        "type": "📁 Dossier" if is_dir else "📄 Fichier"
                    })
                    
                if len(results) >= max_results:
                    break
            
            if len(results) >= max_results:
                break
                
                                                                
            progress.update(search_task, description=f"[cyan]Recherche dans[/] [yellow]{root}[/]")
    
                             
    if results:
        table = Table(title=f"Résultats de recherche pour '{query}'", show_lines=True)
        table.add_column("Type", style="magenta", width=10)
        table.add_column("Nom", style="cyan")
        table.add_column("Chemin", style="green")
        
        for result in results:
            table.add_row(
                result["type"],
                result["name"],
                result["rel_path"]
            )
        
        console.print(table)
        
        if len(results) == max_results:
            console.print(f"[yellow]Affichage limité aux {max_results} premiers résultats.[/]")
        
                                                                
        choice = Prompt.ask(
            "\nEntre le numéro du résultat à ouvrir (ou Entrée pour revenir)",
            default=""
        )
        
        if choice.isdigit() and 1 <= int(choice) <= len(results):
            selected = results[int(choice) - 1]
            return selected["path"]
    else:
        console.print("[yellow]Aucun résultat trouvé.[/]")
        input("\n[Appuie sur Entrée pour revenir]")
    
    return None

def show_file_stats(path):
                                                             
    try:
        stat = os.stat(path)
        file_info = get_file_info(path)
        
        layout = Layout()
        layout.split_column(
            Layout(name="header"),
            Layout(name="details")
        )
        
        title = Text(f"{file_info['icon']} {os.path.basename(path)}", style="bold cyan")
        layout["header"].update(Panel(title, subtitle=os.path.dirname(os.path.abspath(path)), border_style="blue"))
        
                            
        details = Table.grid(expand=True)
        details.add_column(style="green")
        details.add_column(style="white")
        
        details.add_row("Taille:", file_info["size_str"])
        details.add_row("Type MIME:", file_info["mime_type"])
        details.add_row("Date de création:", datetime.fromtimestamp(stat.st_ctime).strftime("%d/%m/%Y %H:%M:%S"))
        details.add_row("Date de modification:", datetime.fromtimestamp(stat.st_mtime).strftime("%d/%m/%Y %H:%M:%S"))
        details.add_row("Dernier accès:", datetime.fromtimestamp(stat.st_atime).strftime("%d/%m/%Y %H:%M:%S"))
        details.add_row("Permissions:", oct(stat.st_mode)[-3:])
        details.add_row("Exécutable:", "Oui" if os.access(path, os.X_OK) else "Non")
        
                
        if os.path.getsize(path) < 100 * 1024 * 1024:                                 
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                transient=True
            ) as progress:
                task = progress.add_task("[cyan]Calcul des hashes...", total=None)
                details.add_row("MD5:", calculate_hash(path, "md5"))
                details.add_row("SHA1:", calculate_hash(path, "sha1"))
                details.add_row("SHA256:", calculate_hash(path, "sha256"))
        
        layout["details"].update(Panel(details, title="Statistiques du fichier", border_style="blue"))
        
        console.print(layout)
        input("\n[Appuie sur Entrée pour revenir]")
    except Exception as e:
        console.print(f"[bold red]Erreur lors de l'analyse du fichier :[/] {e}")
        input("\n[Appuie sur Entrée pour revenir]")

def show_directory_stats(path):
                                                     
    console.print(f"[cyan]Analyse du répertoire[/] [yellow]{path}[/]")
    
    stats = {
        "total_files": 0,
        "total_dirs": 0,
        "total_size": 0,
        "extensions": {},
        "largest_files": []
    }
    
    max_depth = 5                                                                 
    max_files = 1000                                                       
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True
    ) as progress:
        task = progress.add_task("[cyan]Analyse en cours...", total=None)
        
        for root, dirs, files in os.walk(path):
                                             
            rel_path = os.path.relpath(root, path)
            depth = 0 if rel_path == '.' else rel_path.count(os.sep) + 1
            
            if depth > max_depth:
                dirs.clear()                              
                continue
                
                                                               
            if not CONFIG["show_hidden"]:
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                files = [f for f in files if not f.startswith('.')]
            
            stats["total_dirs"] += len(dirs)
            stats["total_files"] += len(files)
            
            progress.update(task, description=f"[cyan]Analyse de[/] [yellow]{root}[/]")
            
            for file in files:
                try:
                    file_path = os.path.join(root, file)
                    size = os.path.getsize(file_path)
                    stats["total_size"] += size
                    
                                            
                    ext = os.path.splitext(file)[1].lower()
                    if ext in stats["extensions"]:
                        stats["extensions"][ext]["count"] += 1
                        stats["extensions"][ext]["size"] += size
                    else:
                        stats["extensions"][ext] = {"count": 1, "size": size}
                    
                                                         
                    stats["largest_files"].append((file_path, size))
                    stats["largest_files"].sort(key=lambda x: x[1], reverse=True)
                    stats["largest_files"] = stats["largest_files"][:10]                           
                except Exception:
                    pass
                    
            if stats["total_files"] > max_files:
                break
    
                             
    layout = Layout()
    layout.split_column(
        Layout(name="header"),
        Layout(name="stats", ratio=2),
        Layout(name="largest", ratio=3)
    )
    
    title = Text(f"📊 Statistiques du répertoire: {os.path.basename(path)}", style="bold cyan")
    layout["header"].update(Panel(title, subtitle=os.path.dirname(os.path.abspath(path)), border_style="blue"))
    
                                        
    stats_table = Table.grid(expand=True)
    stats_table.add_column(style="green")
    stats_table.add_column(style="white")
    stats_table.add_column(style="green")
    stats_table.add_column(style="white")
    
    stats_table.add_row(
        "Nombre de fichiers:", f"{stats['total_files']:,}",
        "Nombre de dossiers:", f"{stats['total_dirs']:,}"
    )
    stats_table.add_row(
        "Taille totale:", format_size(stats["total_size"]),
        "Taille moyenne par fichier:", 
        format_size(stats["total_size"] / stats["total_files"]) if stats["total_files"] > 0 else "N/A"
    )
    
                          
    top_extensions = sorted(
        stats["extensions"].items(), 
        key=lambda x: x[1]["size"], 
        reverse=True
    )[:5]
    
    ext_text = Text()
    for ext, data in top_extensions:
        ext_name = ext if ext else "(sans extension)"
        ext_text.append(f"\n{ext_name}: ", style="green")
        ext_text.append(f"{data['count']} fichiers, {format_size(data['size'])}")
    
    stats_table.add_row("Extensions principales:", ext_text)
    
    layout["stats"].update(Panel(stats_table, title="Résumé", border_style="blue"))
    
                                    
    largest_table = Table(title="Top 10 des plus gros fichiers", show_header=True)
    largest_table.add_column("Nom", style="cyan")
    largest_table.add_column("Taille", style="green", justify="right")
    largest_table.add_column("Chemin", style="dim")
    
    for file_path, size in stats["largest_files"]:
        rel_path = os.path.relpath(file_path, path)
        dir_path = os.path.dirname(rel_path)
        file_name = os.path.basename(file_path)
        largest_table.add_row(file_name, format_size(size), dir_path)
    
    layout["largest"].update(Panel(largest_table, border_style="blue"))
    
    console.print(layout)
    
    if stats["total_files"] > max_files:
        console.print(f"[yellow]Analyse limitée aux {max_files} premiers fichiers pour des raisons de performance.[/]")
    
    input("\n[Appuie sur Entrée pour revenir]")

def main():
                                           
    parser = argparse.ArgumentParser(description="SuperFile Explorer - Navigateur de fichiers avancé")
    parser.add_argument("path", nargs="?", default=os.getcwd(), help="Chemin du répertoire à explorer")
    parser.add_argument("--file", help="Ouvrir directement un fichier en mode visualisation")
    parser.add_argument("--theme", choices=["monokai", "dracula", "github-dark", "solarized-dark", "solarized-light"], 
                      help="Thème de coloration syntaxique")
    parser.add_argument("--show-hidden", action="store_true", help="Afficher les fichiers cachés")
    
    args = parser.parse_args()
    
                                            
    if args.theme:
        CONFIG["theme"] = args.theme
    if args.show_hidden:
        CONFIG["show_hidden"] = True
    
                           
    mimetypes.init()
    
                                       
    if args.file:
        if os.path.isfile(args.file):
            view_file(args.file)
        else:
            console.print(f"[bold red]Erreur :[/] Le fichier {args.file} n'existe pas ou n'est pas accessible.")
        return
    
                            
    if os.path.isdir(args.path):
        try:
            interactive_explorer(args.path)
        except KeyboardInterrupt:
            console.print("\n[yellow]Programme terminé.[/]")
    else:
        console.print(f"[bold red]Erreur :[/] Le répertoire {args.path} n'existe pas ou n'est pas accessible.")

def interactive_explorer(start_path):
                                                          
    current_path = os.path.abspath(start_path)
    selected_idx = 0
    
                                                                 
    if platform.system() == 'Windows':
        import msvcrt
        
        def get_key():
            key = msvcrt.getch()
                                                                                   
            if key == b'\xe0':
                return {b'H': 'up', b'P': 'down', b'M': 'right', b'K': 'left'}[msvcrt.getch()]
                                      
            return {b'\r': 'enter', b'\t': 'tab', b'/': 'search', b'h': 'h', 
                   b's': 's', b'r': 'r', b'f': 'f', b'q': 'q'}.get(key, None)
    else:
                               
        try:
            import tty
            import termios
            
            def get_key():
                fd = sys.stdin.fileno()
                old_settings = termios.tcgetattr(fd)
                try:
                    tty.setraw(sys.stdin.fileno())
                    ch = sys.stdin.read(1)
                                                                                   
                    if ch == '\x1b':
                        ch = sys.stdin.read(2)
                        if ch == '[A':
                            return 'up'
                        elif ch == '[B':
                            return 'down'
                        elif ch == '[C':
                            return 'right'
                        elif ch == '[D':
                            return 'left'
                    return {'': 'enter', '\t': 'tab', '/': 'search', 'h': 'h', 
                           's': 's', 'r': 'r', 'f': 'f', 'q': 'q'}.get(ch, None)
                finally:
                    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        except ImportError:
                                                                
            def get_key():
                return Prompt.ask("\nAction", choices=["u", "d", "Enter", "Tab", "/", "h", "s", "r", "f", "q"], show_choices=False)
    
    while True:
        console.clear()
        entries = list_directory(current_path)
        display_directory_listing(current_path, entries, selected_idx)
        
                                           
        console.print("\n[dim]Utilisez les flèches pour naviguer, Entrée pour ouvrir, Tab pour options, q pour quitter[/dim]")
        
                              
        key = get_key()
        
        if key == 'q':
            break
        elif key == 'up':
            selected_idx = max(selected_idx - 1, -1)                           
        elif key == 'down':
            selected_idx = min(selected_idx + 1, len(entries) - 1)
        elif key == 'enter':
                                
            if selected_idx == -1:
                if current_path != '/':
                    current_path = os.path.dirname(current_path)
                selected_idx = 0
                                          
            else:
                selected = entries[selected_idx]
                if selected["is_dir"]:
                    current_path = selected["path"]
                    selected_idx = 0
                else:
                    console.clear()
                    view_file(selected["path"])
                    input("\n[Appuie sur Entrée pour revenir]")
        elif key == 'tab':
                            
            console.print("\n")
            options = ["Statistiques", "Vue hexadécimale", "Propriétés", "Copier", "Déplacer", "Supprimer", "Retour"]
            option = Prompt.ask("Option", choices=options)
            
            if option == "Statistiques":
                console.clear()
                if selected_idx >= 0:
                    selected = entries[selected_idx]
                    if selected["is_dir"]:
                        show_directory_stats(selected["path"])
                    else:
                        show_file_stats(selected["path"])
                else:
                    show_directory_stats(current_path)
            elif option == "Vue hexadécimale" and selected_idx >= 0 and not entries[selected_idx]["is_dir"]:
                console.clear()
                view_hex(entries[selected_idx]["path"])
                input("\n[Appuie sur Entrée pour revenir]")
            elif option == "Propriétés" and selected_idx >= 0:
                console.clear()
                if entries[selected_idx]["is_dir"]:
                    show_directory_stats(entries[selected_idx]["path"])
                else:
                    show_file_stats(entries[selected_idx]["path"])
        elif key == 'search':
                       
            console.print("\n")
            query = Prompt.ask("Rechercher")
            if query:
                console.clear()
                result_path = search_in_directory(current_path, query)
                if result_path:
                    if os.path.isdir(result_path):
                        current_path = result_path
                        selected_idx = 0
                    else:
                        parent_dir = os.path.dirname(result_path)
                        current_path = parent_dir
                        
                                                                               
                        new_entries = list_directory(parent_dir)
                        for i, entry in enumerate(new_entries):
                            if entry["path"] == result_path:
                                selected_idx = i
                                break
        elif key == 'h':
                                                  
            CONFIG["show_hidden"] = not CONFIG["show_hidden"]
            selected_idx = 0
        elif key == 's':
                            
            console.print("\n")
            sort_options = ["name", "type", "size", "date"]
            sort_by = Prompt.ask("Trier par", choices=sort_options)
            
            if sort_by == CONFIG["sort_by"]:
                CONFIG["reverse_sort"] = not CONFIG["reverse_sort"]
            else:
                CONFIG["sort_by"] = sort_by
                CONFIG["reverse_sort"] = False
            
            selected_idx = 0
        elif key == 'r':
                        
            selected_idx = 0
        elif key == 'f':
                                 
            if current_path in CONFIG["favorites"]:
                CONFIG["favorites"].remove(current_path)
                console.print(f"[green]Chemin supprimé des favoris.[/]")
            else:
                CONFIG["favorites"].append(current_path)
                console.print(f"[green]Chemin ajouté aux favoris.[/]")
            time.sleep(1)

if __name__ == "__main__":
    main()

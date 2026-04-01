# Copyright (c) 2026 by Haizy Tiles
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.
#
# To build the binary you need to have Python and Pip and PyInstaller installed.
# Run this command in the same folder of the python file to build the exe:
# py -m PyInstaller --onefile --windowed --icon icon.ico --add-data "icon.ico;." ht_stockplugin_hider.py

import os
import sys
import shutil
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path

# ---------------- Paths ----------------
DOCUMENTS = Path.home() / "Documents"
BASE_PATH = DOCUMENTS / "Image-Line" / "FL Studio" / "Presets" / "Plugin database"
BASE_PATH = str(BASE_PATH)

BACKUP_PATH = os.path.join(os.environ['APPDATA'], "HTstockpluginhiderBackup")
os.makedirs(BACKUP_PATH, exist_ok=True)

# ---------------- Core Plugins ----------------
CORE = [
    "Sampler",
    "Audio Clip",
    "Automation Clip"
]

# ---------------- Plugins fully included per edition ----------------
_FRUITY = {
    # Instruments
    "3x OSC", "3x Osc", "Autogun", "BassDrum", "BeepMap", "BooBass",
    "Channel Sampler", "Dashboard", "DirectWave Player", "Drumpad", "FLEX",
    "FL Studio Mobile", "FL Studio Mobile Rack",
    "Fruit Kick", "Fruity Dance", "Fruity DrumSynth Live", "Fruity DX10", "Fruity Granulizer",
    "Fruity Kick", "FPC", "Fruity Slicer", "Fruity Slicer 2",
    "GMS", "Layer", "MIDI Out", "MiniSynth", "Plucked!", "ReWired", "SimSynth",
    "Speech Synthesizer", "Wave Traveller", "FL Keys",
    # Effects
    "Control Surface", "Distructor", "Effector", "EQUO",
    "Frequency Splitter", "Fruity Balance", "Fruity Blood Overdrive",
    "Fruity Chorus", "Fruity Compressor", "Fruity Convolver",
    "Fruity Delay 2", "Fruity Delay 3", "Fruity Delay Bank",
    "Fruity Fast Dist", "Fruity Filter", "Fruity Flanger", "Fruity Flangus",
    "Fruity Formula Controller", "Fruity HTML NoteBook", "Fruity Limiter",
    "Fruity Love Philter", "Fruity LSD", "Fruity Multiband Compressor",
    "Fruity NoteBook", "Fruity NoteBook 2", "Fruity PanOMatic",
    "Fruity Parametric EQ", "Fruity Parametric EQ 2", "Fruity Parametric EQ2",
    "Fruity Phaser", "Fruity Reeverb 2", "Fruity Scratcher", "Fruity Send",
    "Fruity Soft Clipper", "Fruity Squeeze", "Fruity Stereo Enhancer",
    "Fruity Stereo Shaper", "Fruity Vocoder", "Fruity WaveShaper",
    "Fruity X-Y Controller", "Fruity X-Y-Z Controller", "Patcher",
    "Fruity Envelope Controller", "Fruity Keyboard Controller", "Fruity Voltage Controller",
    "Fruity Peak Controller", "Razer Chroma", "Soundgoodizer", "Tuner",
    "VFX Color Mapper", "VFX Envelope", "VFX Level Scaler",
    "VFX Keyboard Splitter", "VFX Key Mapper", "VFX Sequencer", "VFX Script",
    "Emphasizer", "FL Studio Mobile Rack FX",
    # Video
    "Fruity Big Clock", "Fruity dB Meter", "Fruity Spectroman",
    "Video Visualizer", "Wave Candy", "ZGameEditor Visualizer",
}

_PRODUCER = _FRUITY | {
    "Kepler", "Slicex", "SoundFont Player", "Sytrus",
    "Edison", "Newtime", "Frequency Shifter", "Hyper Chorus",
    "Maximus", "Multiband Delay", "Spreader", "Vocodex",
}

_SIGNATURE = _PRODUCER | {
    "DirectWave", "Harmless",
    "Gross Beat", "Hardcore", "Low Lifter", "Newtone",
    "Pitcher", "Vintage Chorus", "Vintage Phaser",
    "Fruity Video Player",
}

_ALL_PLUGINS = _SIGNATURE | {
    "Drumaxx", "Harmor", "Kepler Exo", "Morphine", "Ogun",
    "PoiZone", "Sakura", "Sawer", "Toxic Biohazard", "Transistor Bass",
    "Emphasis", "LuxeVerb", "Pitch Shifter", "Transient Processor", "Transporter",
}

INCLUDED_IN_EDITION = {
    "Fruity Edition":      _FRUITY,
    "Producer Edition":    _PRODUCER,
    "Signature Bundle":    _SIGNATURE,
    "All Plugins Edition": _ALL_PLUGINS,
}

def get_not_included(edition_name, groups):
    included = INCLUDED_IN_EDITION.get(edition_name, set())
    return {name for name in groups if name not in included}

# ---------------- Load plugins ----------------
def load_plugins(base_path):
    groups = {}
    types = {}

    for root, dirs, files in os.walk(base_path):
        root_lower = root.lower()
        if any(x in root_lower for x in ["vst", "installed"]):
            continue

        for file in files:
            if file.lower().endswith(".fst"):
                name = file[:-4]
                path = os.path.join(root, file)

                if "Generators" in path:
                    ptype = "Generator"
                elif "Effects" in path:
                    ptype = "Effect"
                else:
                    continue

                groups.setdefault(name, []).append(os.path.abspath(path))
                types[name] = ptype

    return groups, types

# ---------------- Refresh Data ----------------
def update_data(*args):
    global plugin_groups, plugin_types, backup_groups

    plugin_groups, plugin_types = load_plugins(BASE_PATH)
    backup_groups, _ = load_plugins(BACKUP_PATH)

    filter_text = filter_entry.get().lower()

    listbox_generators.delete(0, tk.END)
    listbox_effects.delete(0, tk.END)
    listbox_backup.delete(0, tk.END)

    for name in sorted(plugin_groups.keys()):
        if filter_text in name.lower():
            if plugin_types[name] == "Generator":
                listbox_generators.insert(tk.END, name)
                if name in CORE:
                    listbox_generators.itemconfig(tk.END, {'fg': 'orange'})
            elif plugin_types[name] == "Effect":
                listbox_effects.insert(tk.END, name)
                if name in CORE:
                    listbox_effects.itemconfig(tk.END, {'fg': 'orange'})

    for name in sorted(backup_groups.keys()):
        if filter_text in name.lower():
            listbox_backup.insert(tk.END, name)

    update_status()

def update_status():
    total_generators = len([n for n, t in plugin_types.items() if t == 'Generator'])
    total_effects = len([n for n, t in plugin_types.items() if t == 'Effect'])
    sel_gen = len(listbox_generators.curselection())
    sel_eff = len(listbox_effects.curselection())
    sel_total = sel_gen + sel_eff
    sel_str = f"  |  {sel_total} selected" if sel_total > 0 else ""
    status_label.config(text=f"Generators: {total_generators} | Effects: {total_effects} | Backup: {len(backup_groups)}{sel_str}")

# ---------------- Delete ----------------
def delete_selected():
    selected = (
        [listbox_generators.get(i) for i in listbox_generators.curselection()] +
        [listbox_effects.get(i) for i in listbox_effects.curselection()]
    )

    if not selected:
        return

    for name in selected:
        for fst_path in plugin_groups.get(name, []):
            rel = os.path.relpath(fst_path, BASE_PATH)
            target = os.path.join(BACKUP_PATH, rel)
            os.makedirs(os.path.dirname(target), exist_ok=True)
            shutil.move(fst_path, target)

            nfo = fst_path.replace(".fst", ".nfo")
            if os.path.exists(nfo):
                target_nfo = os.path.join(BACKUP_PATH, os.path.relpath(nfo, BASE_PATH))
                os.makedirs(os.path.dirname(target_nfo), exist_ok=True)
                shutil.move(nfo, target_nfo)

    update_data()

# ---------------- Restore ----------------
def restore_selected():
    selected = [listbox_backup.get(i) for i in listbox_backup.curselection()]

    if not selected:
        return

    skipped = []

    for name in selected:
        for fst_path in backup_groups.get(name, []):
            rel = os.path.relpath(fst_path, BACKUP_PATH)
            target = os.path.join(BASE_PATH, rel)

            if os.path.exists(target):
                skipped.append(name)
                continue

            os.makedirs(os.path.dirname(target), exist_ok=True)
            shutil.move(fst_path, target)

            nfo = fst_path.replace(".fst", ".nfo")
            if os.path.exists(nfo):
                target_nfo = os.path.join(BASE_PATH, os.path.relpath(nfo, BACKUP_PATH))
                os.makedirs(os.path.dirname(target_nfo), exist_ok=True)
                shutil.move(nfo, target_nfo)

    if skipped:
        messagebox.showwarning("Restore skipped",
            f"The following plugins already exist in the Plugin Database and were skipped:\n\n"
            + "\n".join(skipped))

    update_data()

# ---------------- Clear Backup ----------------
def clear_backup():
    shutil.rmtree(BACKUP_PATH, ignore_errors=True)
    os.makedirs(BACKUP_PATH, exist_ok=True)
    update_data()

# ---------------- Select Helpers ----------------
def select_all_including_core(lb):
    for i in range(lb.size()):
        lb.select_set(i)
    update_status()

def deselect_all(lb):
    lb.select_clear(0, tk.END)
    update_status()

# ---------------- Select Demo Plugins ----------------
def select_demo_plugins():
    not_in_edition = get_not_included(edition_var.get(), plugin_groups)

    for lb in [listbox_generators, listbox_effects]:
        lb.select_clear(0, tk.END)
        for i in range(lb.size()):
            name = lb.get(i)
            if name in not_in_edition and name not in CORE:
                lb.select_set(i)

    update_status()

# ---------------- About ----------------
def show_about():
    messagebox.showinfo("About FL Studio Plugin Cleaner",
        "HT Stockplugin hider v0.9\n"
        "Copyright ©2026 by Haizy Tiles\n"
        "MIT license\n\n"
        "Moves demo/unavailable plugin .fst and .nfo files out of the\n"
        "FL Studio Plugin Database to prevent them from loading.\n\n"
        "Backup location:\n"
        f"{BACKUP_PATH}\n\n"
        "Plugins can be restored at any time from the Backup list.")

# ---------------- GUI ----------------
root = tk.Tk()
def resource_path(relative):
    base = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, relative)

try:
    root.iconbitmap(resource_path("icon.ico"))
except Exception:
    pass
root.title("HT Stockplugin hider")
root.geometry("1200x700")

# ---------------- Robustness: check BASE_PATH ----------------
if not os.path.isdir(BASE_PATH):
    messagebox.showerror("FL Studio not found",
        f"Could not find the FL Studio Plugin Database at:\n{BASE_PATH}\n\n"
        "Please make sure FL Studio is installed and has been launched at least once.")
    root.destroy()
    exit()

frame = ttk.Frame(root, padding=10)
frame.pack(fill=tk.BOTH, expand=True)

# Filter
filter_frame = ttk.Frame(frame)
filter_frame.pack(fill=tk.X, pady=5)
ttk.Label(filter_frame, text="Filter:").pack(side=tk.LEFT)
filter_entry = ttk.Entry(filter_frame)
filter_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
filter_entry.bind("<KeyRelease>", update_data)

# Edition and Demo Selection
top = ttk.Frame(frame)
top.pack(fill=tk.X, pady=5)

ttk.Label(top, text="My Edition:").pack(side=tk.LEFT)
edition_var = tk.StringVar(value="Producer Edition")
edition_menu = ttk.Combobox(top, textvariable=edition_var,
                             values=list(INCLUDED_IN_EDITION.keys()), state="readonly")
edition_menu.pack(side=tk.LEFT, padx=5)

ttk.Button(top, text="Select Demo Plugins", command=select_demo_plugins).pack(side=tk.LEFT, padx=5)
ttk.Label(top, text="(Orange = Core Plugins)").pack(side=tk.LEFT, padx=10)

# Status Label
status_label = ttk.Label(frame, text="Loading plugins...")
status_label.pack(pady=5)

# Lists
lists = ttk.Frame(frame)
lists.pack(fill=tk.BOTH, expand=True)

def create_list(parent, title):
    f = ttk.Frame(parent)
    f.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

    ttk.Label(f, text=title, font=('Arial', 10, 'bold')).pack()

    container = ttk.Frame(f)
    container.pack(fill=tk.BOTH, expand=True)

    lb = tk.Listbox(container, selectmode=tk.MULTIPLE, exportselection=0)
    lb.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    lb.bind("<<ListboxSelect>>", lambda e: update_status())

    sb = ttk.Scrollbar(container, command=lb.yview)
    sb.pack(side=tk.RIGHT, fill=tk.Y)
    lb.config(yscrollcommand=sb.set)

    btns = ttk.Frame(f)
    btns.pack(fill=tk.X, pady=2)

    ttk.Button(btns, text="Select All", command=lambda: select_all_including_core(lb)).pack(side=tk.LEFT, expand=True, fill=tk.X)
    ttk.Button(btns, text="Deselect All", command=lambda: deselect_all(lb)).pack(side=tk.LEFT, expand=True, fill=tk.X)

    return lb

listbox_generators = create_list(lists, "Generators")
listbox_effects = create_list(lists, "Effects")
listbox_backup = create_list(lists, "Backup")

# Double clickj at a backup to restore it.
listbox_backup.bind("<Double-Button-1>", lambda e: restore_selected())

# Bottom Buttons
bottom = ttk.Frame(root)
bottom.pack(pady=10)

ttk.Button(bottom, text="Move to Backup", command=delete_selected).pack(side=tk.LEFT, padx=5)
ttk.Button(bottom, text="Restore Selected", command=restore_selected).pack(side=tk.LEFT, padx=5)
ttk.Button(bottom, text="Clear Backup Folder", command=clear_backup).pack(side=tk.LEFT, padx=5)
ttk.Button(bottom, text="About", command=show_about).pack(side=tk.LEFT, padx=5)

# ---------------- Init ----------------
plugin_groups = {}
plugin_types = {}
backup_groups = {}

update_data()
root.mainloop()

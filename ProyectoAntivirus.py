# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import simpledialog, ttk, messagebox
from PIL import Image, ImageTk
from PyQt5.QtWidgets import QApplication, QFileDialog
import subprocess
import os
import datetime
import threading
import logging
import sys
from collections import defaultdict
import uuid

from tkinterdnd2 import DND_FILES, TkinterDnD
from ttkthemes import ThemedTk

def resource_path(relative_path):
    """ Obtener la ruta absoluta del recurso, funciona para el desarrollo y para el ejecutable de PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

log_dir = os.path.join(os.path.expanduser('~'), 'AppData', 'Local', 'NexGuardScanner', 'logs')

if not os.path.exists(log_dir):
    os.makedirs(log_dir)

log_file = os.path.join(log_dir, 'app.log')
logging.basicConfig(filename=log_file, level=logging.DEBUG)
txtResults_lock = threading.Lock()

def select_folders():
    num_folders = simpledialog.askinteger("Numero de carpetas", "Cuantas carpetas deseas escanear?")
    if not num_folders:
        return

    app = QApplication([])

    selected_folders = []  

    for _ in range(num_folders):
        folder_path = QFileDialog.getExistingDirectory(None, "Selecciona una carpeta", options=QFileDialog.ShowDirsOnly | QFileDialog.ReadOnly)
        
        if not folder_path:  
            break

        selected_folders.append(folder_path)

   
    def show_confirmation(folder_path):
        confirm_window = tk.Toplevel(root)
        confirm_window.title(f"Contenido de {folder_path}")

        
        content_listbox = tk.Listbox(confirm_window, width=50, height=10)
        content_listbox.pack(padx=10, pady=10)

        
        for item in os.listdir(folder_path):
            content_listbox.insert(tk.END, item)

        
        btn_frame = ttk.Frame(confirm_window)
        btn_frame.pack(pady=10)

        
        confirm_btn = ttk.Button(btn_frame, text="Confirmar", command=lambda: [lstFolders.insert(tk.END, folder_path), confirm_window.destroy()])
        confirm_btn.pack(side=tk.LEFT, padx=5)

        
        cancel_btn = ttk.Button(btn_frame, text="Cancelar", command=confirm_window.destroy)
        cancel_btn.pack(side=tk.LEFT, padx=5)

    
    for folder_path in selected_folders:
        show_confirmation(folder_path)


global daily_scan_count
daily_scan_count = defaultdict(int)  
directory_change_lock = threading.Lock()

def scan_with_clamav(folder):
    folder_path = folder.split('. ', 1)[-1] if '. ' in folder else folder

    clamscan_path = 'C:\\Program Files\\ClamAV\\clamscan.exe'
    if not os.path.exists(clamscan_path):
        logging.error("clamscan.exe no existe.")
        messagebox.showerror("Error", "clamscan.exe no encontrado.")
        return None

    folder_name = os.path.basename(folder_path)
    report_filename = os.path.join(folder_path, f"{folder_name}_scan_report_antivirus.txt")

    with directory_change_lock:
        original_dir = os.getcwd()
        try:
            os.chdir(folder_path)

            with open(report_filename, 'w', encoding='utf-8') as report_file:
                subprocess.run([clamscan_path, '-r', '.'], stdout=report_file, text=True, stderr=subprocess.PIPE)
        finally:
            
            os.chdir(original_dir)

    logging.info(f"Reporte de escaneo creado: {report_filename}")
    return report_filename
    return loading_win



def write_to_log(folder, report):
    global daily_scan_count

    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    date_only = datetime.datetime.now().strftime('%Y-%m-%d')

    daily_scan_count[date_only] += 1
    scan_count = daily_scan_count[date_only]

    with open('scan_history.log', 'a', encoding='utf-8') as log_file:
        log_file.write(f"{timestamp} - Escaneo {scan_count} para {date_only}: {folder} - Informe: {report}\n")

    current_count = daily_scan_count[datetime.datetime.now().strftime('%Y-%m-%d')]
    total_scans_label.config(text=f" {current_count}")

def process_log():
    history = defaultdict(list)
    with open('scan_history.log', 'r', encoding='utf-8') as log_file:
        for line in log_file:
            if line.strip():
                date, rest_of_line = line.split(' - ', 1)
                history[date].append(rest_of_line.strip())
    return history

def show_log():
    log_history = process_log()
    log_window = tk.Toplevel(root)
    log_window.title("Historial de Escaneos")
    txtLog = tk.Text(log_window, wrap=tk.WORD, width=80, height=20)
    txtLog.pack(padx=10, pady=10)

    for date, records in sorted(log_history.items()):
        txtLog.insert(tk.END, f"Fecha: {date} - Total de escaneos: {len(records)}\n")
        for record in records:
            txtLog.insert(tk.END, f"  {record}\n")
        txtLog.insert(tk.END, "\n")
    txtLog.config(state=tk.DISABLED)


def reenumerate_folders():
    global folder_counter
    folder_counter = 0
    updated_folders = []
    for i in range(lstFolders.size()):
        folder_path = lstFolders.get(i).split('. ', 1)[1]  
        folder_counter += 1
        updated_folders.append(f"{folder_counter}. {folder_path}")

    lstFolders.delete(0, tk.END)  
    for folder in updated_folders:
        lstFolders.insert(tk.END, folder) 


def clear_log():
    with open('scan_history.log', 'w', encoding='utf-8') as log_file:
        log_file.write("")
    messagebox.showinfo("Informacion", "Historial de escaneo borrado con exito.")

def clear_selected_folders():
    selected_indices = lstFolders.curselection()
    if not selected_indices:
        return

    for index in reversed(selected_indices):
        lstFolders.delete(index)

    reenumerate_folders() 

        
global folder_counter
folder_counter = 0

def clear_all_folders():
    global folder_counter
    lstFolders.delete(0, tk.END)
    folder_counter = 0  



def show_notification(title, message):
    from plyer import notification
    notification.notify(
        title=title,
        message=message,
        app_icon=resource_path('assets\\ico.png'),
        timeout=10,
    )

def on_closing():
    current_count = daily_scan_count[datetime.datetime.now().strftime('%Y-%m-%d')]
    save_scan_count(current_count)
    root.destroy()

def get_desktop_path():
    
    return os.path.join(os.path.expanduser('~'), 'Desktop')


def save_scan_count(count):
    
    desktop_path = get_desktop_path()
    date_str = datetime.datetime.now().strftime('%Y-%m-%d')
    scan_count_filename = f'scan_count_{date_str}.txt'
    scan_count_filepath = os.path.join(desktop_path, scan_count_filename)
    
    with open(scan_count_filepath, 'w') as file:
        file.write(str(count))

def load_scan_count():
   
    desktop_path = get_desktop_path()
    date_str = datetime.datetime.now().strftime('%Y-%m-%d')
    scan_count_filename = f'scan_count_{date_str}.txt'
    scan_count_filepath = os.path.join(desktop_path, scan_count_filename)
    
    try:
        with open(scan_count_filepath, 'r') as file:
            return int(file.read().strip())
    except (FileNotFoundError, ValueError):
        return 0

def mark_folder_as_scanned(index):
    folder_name = lstFolders.get(index)
   
    green_check_mark = "\U00002705" 
    updated_folder_name = f"{green_check_mark} {folder_name}"
    lstFolders.delete(index)
    lstFolders.insert(index, updated_folder_name)
    
def run_scan():
    txtResults.delete(1.0, tk.END)
    folders = lstFolders.get(0, tk.END)
    for index, folder_path in enumerate(folders):
        threading.Thread(target=run_scan_thread, args=(folder_path, index)).start() 
    
def run_scan_thread(folder_path, index):
    
    num_files = sum([len(files) for r, d, files in os.walk(folder_path)])
    progress['maximum'] = num_files
    progress['value'] = 0

   
    report = scan_with_clamav(folder_path)
    if report:
        write_to_log(folder_path, report)

    scanned_files = 0
    with open(report, 'r', encoding='utf-8') as report_file:
        content = report_file.readlines()
        for line in content:
            txtResults.insert(tk.END, line)
            txtResults.see(tk.END)
            root.update_idletasks()
            scanned_files += 1
            progress['value'] = scanned_files

       
        if "FOUND" in ''.join(content):
            show_notification("Amenaza detectada", f"Se detectó una amenaza en {folder_path}. Consulta el informe para más detalles.")

    
    root.after(0, lambda: mark_folder_as_scanned(index))
         
def end_scan(loading_win):
    
    show_notification("Escaneo completado", "El escaneo ha finalizado. Consulta los informes para mas detalles.")
    messagebox.showinfo("Informacion", "El escaneo ha finalizado y los informes se han generado en las carpetas correspondientes.")
    
    
    progress["value"] = 0
    root.after(0, loading_win.destroy) 
    
    clear_selected_folders()
    current_count = daily_scan_count[datetime.datetime.now().strftime('%Y-%m-%d')]
    save_scan_count(current_count)
    mark_folder_as_scanned(index)
    loading_win.destroy()
    
def update_scan_count_label():
    
    current_count = daily_scan_count[datetime.datetime.now().strftime('%Y-%m-%d')]
    total_scans_label.config(text=f" {current_count}")
    root.after(100, update_scan_count_label)  

def reset_counter():
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    daily_scan_count[today] = 0
    save_scan_count(daily_scan_count[today])
    total_scans_label.config(text=f"{daily_scan_count[today]}")

root = TkinterDnD.Tk()
root.title("NexGuard Scanner")

image_path = resource_path("assets\\ico.png")
image = Image.open(image_path)
icon = ImageTk.PhotoImage(image)
root.tk.call('wm', 'iconphoto', root._w, icon)
root.protocol("WM_DELETE_WINDOW", on_closing)
root.configure(bg='white')
frame = ttk.Frame(root, padding="20 20 20 20")
frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

app_image_path = resource_path("assets\\insecto.png")
app_image = Image.open(app_image_path)
app_image_resized = app_image.resize((150, 150))
app_logo = ImageTk.PhotoImage(app_image_resized)
app_logo_label = ttk.Label(frame, image=app_logo)
app_logo_label.pack(pady=20)

digital_font = ("Courier", 24, "bold")  
total_scans_label = tk.Label(root, text="00", font=digital_font, fg="red", bg="white")
total_scans_label.pack(pady=20)




daily_scan_count[datetime.datetime.now().strftime('%Y-%m-%d')] = load_scan_count()
total_scans_label.config(text=f" {daily_scan_count[datetime.datetime.now().strftime('%Y-%m-%d')]}")
update_scan_count_label()
dev_image_path = resource_path("assets\\logo2.png")
dev_image = Image.open(dev_image_path)
dev_image_resized = dev_image.resize((90, 90))
dev_logo = ImageTk.PhotoImage(dev_image_resized)
dev_logo_label = ttk.Label(frame, image=dev_logo)
dev_logo_label.place(relx=1.0, y=0, anchor="ne")

paned = ttk.PanedWindow(frame, orient=tk.VERTICAL)
paned.pack(fill=tk.BOTH, expand=True, pady=10)

lstFolders = tk.Listbox(paned, width=50, height=10)
paned.add(lstFolders)

txtResults = tk.Text(paned, width=50, height=10)
paned.add(txtResults)

def drop(event):
    global folder_counter
    folder_paths = event.data.strip().split('\n')
    for folder_path in folder_paths:
        if os.path.isdir(folder_path):
            folder_counter += 1
            lstFolders.insert(tk.END, f"{folder_counter}. {folder_path}")





lstFolders.drop_target_register(DND_FILES)
lstFolders.dnd_bind('<<Drop>>', drop)

button_frame = ttk.Frame(frame)
button_frame.pack(fill=tk.X, expand=True, pady=10)
reset_button = ttk.Button(root, text="Reset Contador", command=reset_counter)
reset_button.pack()

buttons = [
    ("Seleccionar Carpetas", select_folders),
    ("Escanear", run_scan),
    ("Ver Historial", show_log),
    ("Borrar Historial", clear_log),
    ("Borrar Carpetas Seleccionadas", clear_selected_folders),
    ("Borrar Todas las Carpetas", clear_all_folders) 
]

for index, (text, command) in enumerate(buttons):
    btn = ttk.Button(button_frame, text=text, command=command)
    btn.grid(row=0, column=index, padx=10, pady=5, sticky="ew")

progress = ttk.Progressbar(frame, orient=tk.HORIZONTAL, length=300, mode='determinate')

progress.pack(fill=tk.X, padx=10, pady=10)

root.mainloop()                                                                                                                                                    
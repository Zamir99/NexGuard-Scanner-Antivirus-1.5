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




def scan_with_clamav(folder):
    
    if not os.path.exists('C:\\Program Files\\ClamAV\\clamscan.exe'):
        logging.error("clamscan.exe no existe.")
        messagebox.showerror("Error", "clamscan.exe no encontrado.")
        return

    os.chdir(folder)
    folder_name = os.path.basename(folder)
    report_filename = os.path.join(folder, f"{folder_name}_scan_report_antivirus.txt")
    
    with open(report_filename, 'w', encoding='utf-8') as report_file:
        result = subprocess.run(['C:\\Program Files\\ClamAV\\clamscan.exe', '-r', '.'], stdout=report_file, text=True, stderr=subprocess.PIPE)
        logging.info(f"Salida: {result.stdout}")
        logging.info(f"Error: {result.stderr}")
    
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    return report_filename

def write_to_log(folder, report):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open('scan_history.log', 'a', encoding='utf-8') as log_file:
        log_file.write(f"{timestamp} - Escaneo completado para: {folder}. Informe guardado en: {report}\n")

def show_log():
    with open('scan_history.log', 'r', encoding='utf-8') as log_file:
        log_content = log_file.read()
    log_window = tk.Toplevel(root)
    log_window.title("Historial de Escaneos")
    txtLog = tk.Text(log_window, wrap=tk.WORD, width=80, height=20)
    txtLog.pack(padx=10, pady=10)
    txtLog.insert(tk.END, log_content)
    txtLog.config(state=tk.DISABLED)

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
def clear_all_folders():
    lstFolders.delete(0, tk.END)


def show_notification(title, message):
    from plyer import notification
    notification.notify(
        title=title,
        message=message,
        app_icon=resource_path('assets\\ico.png'),
        timeout=10,
    )

    
def animate_gif(loading_label, gif, frame_num):
    
    try:
        photo = gif[frame_num]
        loading_label.config(image=photo)
        frame_num += 1
        if frame_num == len(gif):
            frame_num = 0
        root.after(100, animate_gif, loading_label, gif, frame_num)
    except:
        pass

def show_loading_window(folder_name):
    
    loading_win = tk.Toplevel(root)
    loading_win.title(f"Escaneando {folder_name}...")  
    
    gif = [tk.PhotoImage(file=resource_path("assets\\pacman.gif"), format=f"gif -index {i}") for i in range(10)]
    loading_label = ttk.Label(loading_win, image=gif[0])
    loading_label.pack(pady=20, padx=20)
    
    
    folder_label = ttk.Label(loading_win, text=f"Escaneando: {folder_name}")
    folder_label.pack(pady=10)
    
   
    animate_gif(loading_label, gif, 0)
    
    return loading_win

def end_scan(loading_win):
    
    show_notification("Escaneo completado", "El escaneo ha finalizado. Consulta los informes para mas detalles.")
    messagebox.showinfo("Informacion", "El escaneo ha finalizado y los informes se han generado en las carpetas correspondientes.")
    
    
    progress["value"] = 0
    
    
    clear_selected_folders()
    
    
    loading_win.destroy()

def run_scan_thread(loading_win, folder):
   
    report = scan_with_clamav(folder)
    print(f"Escaneo completado para: {folder}. Informe guardado en: {report}")
    write_to_log(folder, report)

    with open(report, 'r', encoding='utf-8') as report_file:
        content = report_file.readlines()
        for line in content:
            txtResults.insert(tk.END, line)  
            txtResults.see(tk.END)  
            root.update_idletasks()  

        if "FOUND" in ''.join(content):
            show_notification("Amenaza detectada", f"Se detecto una amenaza en {folder}. Consulta el informe para mas detalles.")

    
    root.after(0, end_scan, loading_win)

def run_scan():
    
    txtResults.delete(1.0, tk.END)
    
    folders = lstFolders.get(0, tk.END)
    for folder in folders:
        folder_name = os.path.basename(folder)
        
        
        loading_win = show_loading_window(folder_name)
        
        
        threading.Thread(target=run_scan_thread, args=(loading_win, folder)).start()



root = TkinterDnD.Tk()
root.title("NexGuard Scanner")

image_path = resource_path("assets\\ico.png")
image = Image.open(image_path)
icon = ImageTk.PhotoImage(image)
root.tk.call('wm', 'iconphoto', root._w, icon)

frame = ttk.Frame(root, padding="20 20 20 20")
frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

app_image_path = resource_path("assets\\insecto.png")
app_image = Image.open(app_image_path)
app_image_resized = app_image.resize((150, 150))
app_logo = ImageTk.PhotoImage(app_image_resized)
app_logo_label = ttk.Label(frame, image=app_logo)
app_logo_label.pack(pady=20)

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
    
    folder_paths = event.data.strip().split('\n')
    for folder_path in folder_paths:
        if os.path.isdir(folder_path):  
            lstFolders.insert(tk.END, folder_path)


lstFolders.drop_target_register(DND_FILES)
lstFolders.dnd_bind('<<Drop>>', drop)

button_frame = ttk.Frame(frame)
button_frame.pack(fill=tk.X, expand=True, pady=10)

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
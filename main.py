import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import yt_dlp
import os
import threading
import shutil
from pathlib import Path


class YouTubeConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube to MP3 Converter")
        self.root.geometry("550x280")
        self.root.resizable(False, False)
        
        # Variabile
        self.save_path = tk.StringVar(value=os.path.join(os.path.expanduser("~"), "Downloads"))
        self.url = tk.StringVar()
        self.ffmpeg_path = tk.StringVar()
        self.is_downloading = False
        
        # Verifică ffmpeg la pornire
        self.check_ffmpeg()
        
        self.setup_ui()
        
    def setup_ui(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Selectare folder
        ttk.Label(main_frame, text="Locație salvare:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        path_frame = ttk.Frame(main_frame)
        path_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.path_entry = ttk.Entry(path_frame, textvariable=self.save_path, width=50, state="readonly")
        self.path_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        ttk.Button(path_frame, text="Selectează", command=self.select_folder).grid(row=0, column=1)
        
        path_frame.columnconfigure(0, weight=1)
        
        # Selectare FFmpeg (opțional)
        ttk.Label(main_frame, text="FFmpeg (opțional):").grid(row=2, column=0, sticky=tk.W, pady=(10, 5))
        
        ffmpeg_frame = ttk.Frame(main_frame)
        ffmpeg_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.ffmpeg_entry = ttk.Entry(ffmpeg_frame, textvariable=self.ffmpeg_path, width=50, state="readonly")
        self.ffmpeg_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        ttk.Button(ffmpeg_frame, text="Selectează", command=self.select_ffmpeg).grid(row=0, column=1)
        
        ffmpeg_frame.columnconfigure(0, weight=1)
        
        # Status FFmpeg
        self.ffmpeg_status = ttk.Label(main_frame, text="", font=("TkDefaultFont", 8))
        self.ffmpeg_status.grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        self.update_ffmpeg_status()
        
        # Input URL
        ttk.Label(main_frame, text="Link YouTube:").grid(row=5, column=0, sticky=tk.W, pady=(5, 5))
        
        url_frame = ttk.Frame(main_frame)
        url_frame.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.url_entry = ttk.Entry(url_frame, textvariable=self.url, width=50)
        self.url_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        self.url_entry.bind('<Return>', lambda e: self.convert())
        
        self.convert_btn = ttk.Button(url_frame, text="Convert", command=self.convert, state="normal")
        self.convert_btn.grid(row=0, column=1)
        
        url_frame.columnconfigure(0, weight=1)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate', length=400)
        self.progress.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(15, 0))
        
        # Status label - mai mare și mai vizibil
        self.status_label = ttk.Label(main_frame, text="Gata pentru descărcare", font=("TkDefaultFont", 10, "bold"), foreground="gray")
        self.status_label.grid(row=8, column=0, columnspan=2, pady=(10, 0))
        
        # Info label pentru detalii
        self.info_label = ttk.Label(main_frame, text="", font=("TkDefaultFont", 8), foreground="darkgray")
        self.info_label.grid(row=9, column=0, columnspan=2, pady=(5, 0))
        
        main_frame.columnconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
    def find_ffmpeg_in_project(self):
        """Caută ffmpeg.exe în folderul proiectului"""
        project_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Caută în subfoldere care conțin "ffmpeg" și au un folder "bin"
        for root, dirs, files in os.walk(project_dir):
            # Verifică dacă există un folder "bin" în acest director
            if 'bin' in dirs:
                bin_path = os.path.join(root, 'bin', 'ffmpeg.exe')
                if os.path.exists(bin_path):
                    return os.path.join(root, 'bin')
        
        # Caută direct ffmpeg.exe în orice subfolder
        for root, dirs, files in os.walk(project_dir):
            if 'ffmpeg.exe' in files:
                return root
        
        return None
    
    def check_ffmpeg(self):
        """Verifică dacă ffmpeg este disponibil - mai întâi în proiect, apoi în PATH"""
        # 1. Caută în folderul proiectului
        project_ffmpeg = self.find_ffmpeg_in_project()
        if project_ffmpeg:
            self.ffmpeg_path.set(project_ffmpeg)
            return True
        
        # 2. Caută în PATH
        ffmpeg_cmd = shutil.which('ffmpeg')
        if ffmpeg_cmd:
            # Dacă este în PATH, folosim directorul părinte
            self.ffmpeg_path.set(os.path.dirname(ffmpeg_cmd))
            return True
        
        return False
    
    def update_ffmpeg_status(self):
        """Actualizează statusul FFmpeg în interfață"""
        if self.ffmpeg_path.get():
            ffmpeg_exe = os.path.join(self.ffmpeg_path.get(), 'ffmpeg.exe')
            if os.path.exists(ffmpeg_exe):
                # Verifică dacă este din proiect sau din PATH
                project_dir = os.path.dirname(os.path.abspath(__file__))
                if project_dir in os.path.abspath(ffmpeg_exe):
                    self.ffmpeg_status.config(text="✓ FFmpeg găsit în proiect", foreground="green")
                else:
                    self.ffmpeg_status.config(text="✓ FFmpeg găsit", foreground="green")
            else:
                self.ffmpeg_status.config(text="⚠ FFmpeg nu a fost găsit la calea specificată", foreground="orange")
        else:
            if self.check_ffmpeg():
                self.ffmpeg_status.config(text="✓ FFmpeg găsit", foreground="green")
            else:
                self.ffmpeg_status.config(text="⚠ FFmpeg nu este instalat sau nu este în PATH", foreground="red")
    
    def select_folder(self):
        folder = filedialog.askdirectory(initialdir=self.save_path.get())
        if folder:
            self.save_path.set(folder)
    
    def select_ffmpeg(self):
        """Selectează directorul unde se află ffmpeg.exe"""
        # Încearcă să găsească automat ffmpeg.exe
        initial_dir = self.ffmpeg_path.get() if self.ffmpeg_path.get() else "C:\\"
        folder = filedialog.askdirectory(initialdir=initial_dir, title="Selectează folderul unde se află ffmpeg.exe")
        if folder:
            # Verifică dacă există ffmpeg.exe în folder
            ffmpeg_exe = os.path.join(folder, 'ffmpeg.exe')
            if os.path.exists(ffmpeg_exe):
                self.ffmpeg_path.set(folder)
                self.update_ffmpeg_status()
            else:
                messagebox.showwarning(
                    "Atenție", 
                    f"ffmpeg.exe nu a fost găsit în folderul selectat:\n{folder}\n\nTe rog selectează folderul unde se află ffmpeg.exe"
                )
    
    def convert(self):
        if self.is_downloading:
            messagebox.showinfo("Atenție", "Se descarcă deja un fișier. Te rog așteaptă!")
            return
            
        url = self.url.get().strip()
        if not url:
            messagebox.showwarning("Atenție", "Te rog introdu un link YouTube valid!")
            return
        
        if not os.path.exists(self.save_path.get()):
            messagebox.showerror("Eroare", "Locația selectată nu există!")
            return
        
        # Pornește descărcarea într-un thread separat
        self.is_downloading = True
        self.convert_btn.config(state="disabled")
        self.url_entry.config(state="disabled")
        self.progress.start(10)  # Viteza animației
        self.status_label.config(text="⏳ Se descarcă și se convertește...", foreground="blue", font=("TkDefaultFont", 10, "bold"))
        self.info_label.config(text="Așteaptă, procesul poate dura câteva momente...", foreground="darkblue")
        
        thread = threading.Thread(target=self.download_audio, args=(url,), daemon=True)
        thread.start()
    
    def progress_hook(self, d):
        """Callback pentru progresul descărcării"""
        if d['status'] == 'downloading':
            # Actualizează mesajul cu progresul
            if 'total_bytes' in d and d.get('downloaded_bytes'):
                percent = (d['downloaded_bytes'] / d['total_bytes']) * 100
                msg = f"Descărcare: {percent:.1f}% ({d['downloaded_bytes']}/{d['total_bytes']} bytes)"
                self.root.after(0, lambda m=msg: self.info_label.config(
                    text=m,
                    foreground="darkblue"
                ))
            elif '_percent_str' in d:
                msg = f"Descărcare: {d['_percent_str']}"
                self.root.after(0, lambda m=msg: self.info_label.config(
                    text=m,
                    foreground="darkblue"
                ))
            else:
                self.root.after(0, lambda: self.info_label.config(
                    text="Descărcare în curs...",
                    foreground="darkblue"
                ))
        elif d['status'] == 'finished':
            self.root.after(0, lambda: self.info_label.config(
                text="Conversie în MP3...",
                foreground="darkgreen"
            ))
    
    def download_audio(self, url):
        downloaded_file = None
        try:
            # Configurare yt-dlp pentru MP3
            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'outtmpl': os.path.join(self.save_path.get(), '%(title)s.%(ext)s'),
                'quiet': False,  # Afișează output pentru debugging
                'no_warnings': False,
                'progress_hooks': [self.progress_hook],
                'ignoreerrors': True,  # Continuă chiar dacă un video eșuează (important pentru playlist-uri)
                'sleep_interval': 1,  # Pauză de 1 secundă între descărcări pentru a evita rate limiting
                'sleep_interval_requests': 1,  # Pauză de 1 secundă între cereri
            }
            
            # Dacă utilizatorul a specificat o cale pentru ffmpeg
            if self.ffmpeg_path.get():
                ffmpeg_location = self.ffmpeg_path.get()
                ydl_opts['ffmpeg_location'] = ffmpeg_location
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Actualizează UI pentru extragerea informațiilor
                self.root.after(0, lambda: self.status_label.config(
                    text="⏳ Se extrag informațiile despre playlist...",
                    foreground="blue",
                    font=("TkDefaultFont", 10, "bold")
                ))
                self.root.after(0, lambda: self.info_label.config(
                    text="Așteaptă, aceasta poate dura câteva momente pentru playlist-uri mari...",
                    foreground="darkblue"
                ))
                
                # Obține informații despre video/playlist
                info = ydl.extract_info(url, download=False)
                
                # Verifică dacă este playlist
                if 'entries' in info:
                    # Este un playlist
                    entries = [e for e in info['entries'] if e is not None]
                    total_videos = len(entries)
                    
                    self.root.after(0, lambda n=total_videos: self.status_label.config(
                        text=f"⏳ Descărcare playlist: {n} videouri...",
                        foreground="blue",
                        font=("TkDefaultFont", 10, "bold")
                    ))
                    self.root.after(0, lambda n=total_videos: self.info_label.config(
                        text=f"Se descarcă {n} videouri (cu pauze pentru a evita rate limiting)...",
                        foreground="darkblue"
                    ))
                else:
                    # Este un singur video
                    video_title = info.get('title', 'necunoscut')
                    self.root.after(0, lambda: self.status_label.config(
                        text="⏳ Se descarcă și se convertește...",
                        foreground="blue",
                        font=("TkDefaultFont", 10, "bold")
                    ))
                    self.root.after(0, lambda t=video_title: self.info_label.config(
                        text=f"Video: {t[:50]}...",
                        foreground="darkblue"
                    ))
                
                # Descarcă
                ydl.download([url])
                
                # Găsește fișierul descărcat (doar pentru video unic)
                if 'entries' not in info:
                    filename = ydl.prepare_filename(info)
                    mp3_filename = os.path.splitext(filename)[0] + '.mp3'
                    if os.path.exists(mp3_filename):
                        downloaded_file = mp3_filename
            
            # Succes - actualizează UI în thread-ul principal
            self.root.after(0, lambda: self.download_success(downloaded_file))
            
        except Exception as e:
            error_msg = str(e)
            # Verifică dacă eroarea este legată de rate limiting
            if 'rate-limit' in error_msg.lower() or 'rate limit' in error_msg.lower():
                error_msg = f"{error_msg}\n\nSoluție:\nYouTube a limitat cererile. Aplicația folosește deja pauze între descărcări.\nTe rog așteaptă câteva minute și încearcă din nou.\n\nPentru playlist-uri foarte mari, recomand să descarci în mai multe sesiuni."
            # Verifică dacă eroarea este legată de ffmpeg
            elif 'ffmpeg' in error_msg.lower() or 'ffprobe' in error_msg.lower():
                error_msg = f"{error_msg}\n\nSoluție:\n1. Instalează ffmpeg de la https://ffmpeg.org/download.html\n2. Sau selectează folderul unde se află ffmpeg.exe folosind butonul 'Selectează' deasupra"
            self.root.after(0, lambda: self.download_error(error_msg))
    
    def download_success(self, filepath=None):
        self.is_downloading = False
        self.progress.stop()
        
        if filepath and os.path.exists(filepath):
            # Un singur fișier
            filename = os.path.basename(filepath)
            self.status_label.config(text="✅ Descărcare completă!", foreground="green", font=("TkDefaultFont", 10, "bold"))
            self.info_label.config(text=f"Fișier salvat: {filename}", foreground="green")
            messagebox.showinfo("Succes", f"Fișierul a fost descărcat cu succes!\n\n{filename}\n\nLocație: {os.path.dirname(filepath)}")
        else:
            # Probabil playlist sau mai multe fișiere
            self.status_label.config(text="✅ Descărcare completă!", foreground="green", font=("TkDefaultFont", 10, "bold"))
            self.info_label.config(text="Toate fișierele disponibile au fost salvate în folderul selectat", foreground="green")
            messagebox.showinfo("Succes", f"Descărcarea a fost completată!\n\nToate fișierele disponibile au fost salvate în:\n{self.save_path.get()}\n\nNotă: Unele videouri pot fi eșuate din cauza rate limiting sau indisponibilității.")
        
        self.url.set("")  # Resetează inputul
        self.url_entry.config(state="normal")
        self.url_entry.focus()
        self.convert_btn.config(state="normal")
        
        # Resetează statusul după 5 secunde
        self.root.after(5000, lambda: (
            self.status_label.config(text="Gata pentru descărcare", foreground="gray", font=("TkDefaultFont", 10, "bold")),
            self.info_label.config(text="")
        ))
    
    def download_error(self, error_msg):
        self.is_downloading = False
        self.progress.stop()
        self.status_label.config(text="❌ Eroare la descărcare!", foreground="red", font=("TkDefaultFont", 10, "bold"))
        self.info_label.config(text="Verifică mesajul de eroare de mai jos", foreground="red")
        self.url_entry.config(state="normal")
        self.convert_btn.config(state="normal")
        messagebox.showerror("Eroare", f"Eroare la descărcare:\n\n{error_msg}")


if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubeConverter(root)
    root.mainloop()

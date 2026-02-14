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
        self.root.title("YouTube Downloader & Converter")
        self.root.geometry("650x500")
        self.root.resizable(False, False)
        
        # Configurează fundal mai deschis
        self.root.configure(bg='#f5f5f5')
        
        # Configurează stilul modern
        self.setup_styles()
        
        # Variabile
        self.save_path = tk.StringVar(value=os.path.join(os.path.expanduser("~"), "Downloads"))
        self.url = tk.StringVar()
        self.ffmpeg_path = tk.StringVar()
        self.format_type = tk.StringVar(value="MP3")  # MP3 sau MP4
        self.audio_quality = tk.StringVar(value="192")  # 128, 192, 256, 320
        self.is_downloading = False
        self.should_stop = False  # Flag pentru oprire descărcare
        self.ydl_instance = None  # Referință la instanța yt-dlp pentru oprire
        
        # Verifică ffmpeg la pornire
        self.check_ffmpeg()
        
        self.setup_ui()
    
    def setup_styles(self):
        """Configurează stilurile moderne pentru interfață"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configurează fundal mai deschis
        style.configure('TFrame', background='#f5f5f5')
        style.configure('TLabelFrame', background='#f5f5f5', foreground='#2c3e50', borderwidth=0, relief='flat')
        style.configure('TLabelFrame.Label', background='#f5f5f5', foreground='#2c3e50')
        
        # Configurează culorile
        style.configure('Title.TLabel', font=('Segoe UI', 16, 'bold'), foreground='#2c3e50', background='#f5f5f5')
        style.configure('Subtitle.TLabel', font=('Segoe UI', 8), foreground='#7f8c8d', background='#f5f5f5')
        style.configure('Heading.TLabel', font=('Segoe UI', 10, 'bold'), foreground='#34495e', background='#f5f5f5')
        style.configure('Status.TLabel', font=('Segoe UI', 10, 'bold'), background='#f5f5f5')
        style.configure('Info.TLabel', font=('Segoe UI', 9), background='#f5f5f5')
        
        # Butoane moderne - mai mici, la nivel cu input-ul
        style.configure('Action.TButton', font=('Segoe UI', 9), padding=(8, 5))
        style.map('Action.TButton',
                  background=[('active', '#3498db'), ('!active', '#2980b9')],
                  foreground=[('active', 'white'), ('!active', 'white')])
        
        # Buton stop - aceeași dimensiune cu butonul Descarcă
        style.configure('Stop.TButton', font=('Segoe UI', 9), padding=(8, 5))
        style.map('Stop.TButton',
                  background=[('active', '#e74c3c'), ('!active', '#c0392b')],
                  foreground=[('active', 'white'), ('!active', 'white')])
        
        # Entry modern
        style.configure('Modern.TEntry', padding=5, relief='flat', fieldbackground='white')
        
        # Radio buttons - fără gri închis
        style.configure('TRadiobutton', background='#f5f5f5', foreground='#2c3e50')
        style.map('TRadiobutton',
                 background=[('active', '#f5f5f5'), ('selected', '#f5f5f5')],
                 foreground=[('active', '#2c3e50'), ('selected', '#2c3e50')])
        
        # Combobox - fără gri închis
        style.configure('TCombobox', fieldbackground='white', background='white', borderwidth=1)
        style.map('TCombobox',
                 fieldbackground=[('readonly', 'white')],
                 background=[('readonly', 'white')])
        
        # Buton Selectează - fundal deschis
        style.configure('Select.TButton', font=('Segoe UI', 9), padding=5)
        style.map('Select.TButton',
                 background=[('active', '#e8e8e8'), ('!active', '#f5f5f5')],
                 foreground=[('active', '#2c3e50'), ('!active', '#2c3e50')],
                 bordercolor=[('active', '#d0d0d0'), ('!active', '#d0d0d0')])
        
        # Progress bar modern
        style.configure('Modern.Horizontal.TProgressbar', 
                       background='#3498db', 
                       troughcolor='#e0e0e0',
                       borderwidth=0,
                       lightcolor='#3498db',
                       darkcolor='#3498db')
    
    def setup_ui(self):
        # Frame principal cu fundal
        main_frame = ttk.Frame(self.root, padding="25")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Titlu cu "by Edy"
        title_frame = ttk.Frame(main_frame)
        title_frame.grid(row=0, column=0, columnspan=3, pady=(0, 5))
        
        title_label = ttk.Label(title_frame, text="🎵 YouTube Downloader", style='Title.TLabel')
        title_label.grid(row=0, column=0)
        
        subtitle_label = ttk.Label(title_frame, text="by Edy", style='Subtitle.TLabel')
        subtitle_label.grid(row=0, column=1, padx=(10, 0), pady=(5, 0))
        
        # Secțiune: Format și Calitate - fără border, doar fundal deschis
        # Label pentru "Opțiuni Descărcare"
        ttk.Label(main_frame, text="Opțiuni Descărcare", style='Heading.TLabel').grid(row=1, column=0, sticky=tk.W, pady=(0, 10))
        
        options_frame = ttk.Frame(main_frame, padding="15")
        options_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # Format selector - aliniat mai la stânga
        ttk.Label(options_frame, text="Format:", style='Heading.TLabel').grid(row=0, column=0, sticky=tk.W, padx=(0, 15))
        format_frame = ttk.Frame(options_frame)
        format_frame.grid(row=0, column=1, sticky=tk.W, padx=(0, 30))
        
        mp3_radio = ttk.Radiobutton(format_frame, text="MP3 (Audio)", variable=self.format_type, 
                                    value="MP3", command=self.on_format_change)
        mp3_radio.grid(row=0, column=0, padx=(0, 15))
        
        mp4_radio = ttk.Radiobutton(format_frame, text="MP4 (Video)", variable=self.format_type, 
                                     value="MP4", command=self.on_format_change)
        mp4_radio.grid(row=0, column=1)
        
        # Calitate audio (doar pentru MP3)
        self.quality_label = ttk.Label(options_frame, text="Calitate Audio:", style='Heading.TLabel')
        self.quality_label.grid(row=0, column=2, sticky=tk.W, padx=(0, 10))
        
        self.quality_combo = ttk.Combobox(options_frame, textvariable=self.audio_quality, 
                                         values=["128", "192", "256", "320"], 
                                         state="readonly", width=8)
        self.quality_combo.grid(row=0, column=3, sticky=tk.W)
        self.quality_combo.set("192")
        
        # Selectare folder
        ttk.Label(main_frame, text="📁 Locație salvare:", style='Heading.TLabel').grid(row=3, column=0, sticky=tk.W, pady=(0, 5))
        
        path_frame = ttk.Frame(main_frame)
        path_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        path_frame.columnconfigure(0, weight=1)
        
        self.path_entry = ttk.Entry(path_frame, textvariable=self.save_path, style='Modern.TEntry', font=("Segoe UI", 10), state="readonly")
        self.path_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        ttk.Button(path_frame, text="Selectează", command=self.select_folder, style='Select.TButton').grid(row=0, column=1)
        
        # Selectare FFmpeg (opțional) - cu dropdown
        self.ffmpeg_expanded = False
        ffmpeg_header_frame = ttk.Frame(main_frame)
        ffmpeg_header_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 0))
        
        self.ffmpeg_toggle_btn = ttk.Button(ffmpeg_header_frame, text="⚙️ FFmpeg (Opțional) ▼", 
                                            command=self.toggle_ffmpeg, width=25)
        self.ffmpeg_toggle_btn.grid(row=0, column=0, sticky=tk.W)
        
        # Frame pentru conținutul FFmpeg (inițial ascuns) - fără border
        self.ffmpeg_section = ttk.Frame(main_frame)
        self.ffmpeg_section.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(5, 10))
        self.ffmpeg_section.columnconfigure(0, weight=1)
        self.ffmpeg_section.grid_remove()  # Ascunde inițial
        
        ffmpeg_frame = ttk.Frame(self.ffmpeg_section)
        ffmpeg_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        ffmpeg_frame.columnconfigure(0, weight=1)
        
        self.ffmpeg_entry = ttk.Entry(ffmpeg_frame, textvariable=self.ffmpeg_path, style='Modern.TEntry', font=("Segoe UI", 10), state="readonly")
        self.ffmpeg_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        ttk.Button(ffmpeg_frame, text="Selectează", command=self.select_ffmpeg, style='Select.TButton').grid(row=0, column=1)
        
        # Status FFmpeg
        self.ffmpeg_status = ttk.Label(self.ffmpeg_section, text="", font=("Segoe UI", 8))
        self.ffmpeg_status.grid(row=1, column=0, columnspan=2, sticky=tk.W)
        self.update_ffmpeg_status()
        
        # Input URL
        ttk.Label(main_frame, text="🔗 Link YouTube:", style='Heading.TLabel').grid(row=7, column=0, sticky=tk.W, pady=(15, 5))
        
        url_frame = ttk.Frame(main_frame)
        url_frame.grid(row=8, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        
        self.url_entry = ttk.Entry(url_frame, textvariable=self.url, style='Modern.TEntry', font=("Segoe UI", 10))
        self.url_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        self.url_entry.bind('<Return>', lambda e: self.convert())
        
        button_frame = ttk.Frame(url_frame)
        button_frame.grid(row=0, column=1)
        
        self.convert_btn = ttk.Button(button_frame, text="⬇️ Descarcă", command=self.convert, 
                                      style='Action.TButton', state="normal")
        self.convert_btn.grid(row=0, column=0, padx=(0, 5))
        
        self.stop_btn = ttk.Button(button_frame, text="⏹️ Stop", command=self.stop_download, 
                                  style='Stop.TButton', state="disabled")
        self.stop_btn.grid(row=0, column=1)
        
        url_frame.columnconfigure(0, weight=1)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate', length=400, 
                                       style='Modern.Horizontal.TProgressbar')
        self.progress.grid(row=9, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="✨ Gata pentru descărcare", 
                                     style='Status.TLabel', foreground="#7f8c8d")
        self.status_label.grid(row=10, column=0, columnspan=3, pady=(15, 5))
        
        # Info label pentru detalii
        self.info_label = ttk.Label(main_frame, text="", style='Info.TLabel', foreground="#95a5a6")
        self.info_label.grid(row=11, column=0, columnspan=3, pady=(0, 0))
        
        main_frame.columnconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
    
    def toggle_ffmpeg(self):
        """Comută vizibilitatea secțiunii FFmpeg"""
        self.ffmpeg_expanded = not self.ffmpeg_expanded
        if self.ffmpeg_expanded:
            self.ffmpeg_section.grid()
            self.ffmpeg_toggle_btn.config(text="⚙️ FFmpeg (Opțional) ▲")
        else:
            self.ffmpeg_section.grid_remove()
            self.ffmpeg_toggle_btn.config(text="⚙️ FFmpeg (Opțional) ▼")
    
    def stop_download(self):
        """Oprește descărcarea curentă"""
        if self.is_downloading:
            self.should_stop = True
            self.status_label.config(text="⏸️ Se oprește descărcarea...", 
                                   foreground="#e67e22", style='Status.TLabel')
            self.info_label.config(text="Așteaptă, descărcarea se va opri în curând...", 
                                 foreground="#d35400", style='Info.TLabel')
            # Oprește instanța yt-dlp dacă există
            if self.ydl_instance:
                try:
                    # yt-dlp nu are o metodă directă de oprire, dar flag-ul should_stop va fi verificat
                    pass
                except:
                    pass
    
    def on_format_change(self):
        """Actualizează interfața când se schimbă formatul"""
        if self.format_type.get() == "MP4":
            self.quality_label.config(state="disabled")
            self.quality_combo.config(state="disabled")
        else:
            self.quality_label.config(state="normal")
            self.quality_combo.config(state="readonly")
    
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
        
        # Resetează flag-ul de oprire
        self.should_stop = False
        
        # Pornește descărcarea într-un thread separat
        self.is_downloading = True
        self.convert_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.url_entry.config(state="disabled")
        self.quality_combo.config(state="disabled")
        self.progress.start(10)  # Viteza animației
        
        format_text = "MP3" if self.format_type.get() == "MP3" else "MP4"
        self.status_label.config(text=f"⏳ Se descarcă {format_text}...", 
                                foreground="#3498db", style='Status.TLabel')
        self.info_label.config(text="Așteaptă, procesul poate dura câteva momente...", 
                              foreground="#2980b9", style='Info.TLabel')
        
        thread = threading.Thread(target=self.download_media, args=(url,), daemon=True)
        thread.start()
    
    def progress_hook(self, d):
        """Callback pentru progresul descărcării"""
        # Verifică dacă utilizatorul a cerut oprirea
        if self.should_stop:
            return
        
        if d['status'] == 'downloading':
            # Actualizează mesajul cu progresul
            if 'total_bytes' in d and d.get('downloaded_bytes'):
                percent = (d['downloaded_bytes'] / d['total_bytes']) * 100
                msg = f"Descărcare: {percent:.1f}% ({d['downloaded_bytes']}/{d['total_bytes']} bytes)"
                self.root.after(0, lambda m=msg: self.info_label.config(
                    text=m,
                    foreground="#2980b9",
                    style='Info.TLabel'
                ))
            elif '_percent_str' in d:
                msg = f"Descărcare: {d['_percent_str']}"
                self.root.after(0, lambda m=msg: self.info_label.config(
                    text=m,
                    foreground="#2980b9",
                    style='Info.TLabel'
                ))
            else:
                self.root.after(0, lambda: self.info_label.config(
                    text="Descărcare în curs...",
                    foreground="#2980b9",
                    style='Info.TLabel'
                ))
        elif d['status'] == 'finished':
            format_type = self.format_type.get()
            if format_type == "MP3":
                self.root.after(0, lambda: self.info_label.config(
                    text="Conversie în MP3...",
                    foreground="#27ae60",
                    style='Info.TLabel'
                ))
            else:
                self.root.after(0, lambda: self.info_label.config(
                    text="Finalizare descărcare MP4...",
                    foreground="#27ae60",
                    style='Info.TLabel'
                ))
    
    def download_media(self, url):
        downloaded_file = None
        try:
            format_type = self.format_type.get()
            
            # Configurare yt-dlp
            if format_type == "MP3":
                # Configurare pentru MP3 (audio)
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': self.audio_quality.get(),
                    }],
                    'outtmpl': os.path.join(self.save_path.get(), '%(title)s.%(ext)s'),
                    'quiet': False,
                    'no_warnings': False,
                    'progress_hooks': [self.progress_hook],
                    'ignoreerrors': True,
                    'sleep_interval': 1,
                    'sleep_interval_requests': 1,
                }
            else:
                # Configurare pentru MP4 (video)
                # Folosește cel mai bun format video disponibil și convertește în MP4 dacă e necesar
                ydl_opts = {
                    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best[ext=mp4]/best',
                    'postprocessors': [{
                        'key': 'FFmpegVideoConvertor',
                        'preferedformat': 'mp4',
                    }],
                    'merge_output_format': 'mp4',
                    'outtmpl': os.path.join(self.save_path.get(), '%(title)s.%(ext)s'),
                    'quiet': False,
                    'no_warnings': False,
                    'progress_hooks': [self.progress_hook],
                    'ignoreerrors': True,
                    'sleep_interval': 1,
                    'sleep_interval_requests': 1,
                }
            
            # Dacă utilizatorul a specificat o cale pentru ffmpeg
            if self.ffmpeg_path.get():
                ffmpeg_location = self.ffmpeg_path.get()
                ydl_opts['ffmpeg_location'] = ffmpeg_location
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                self.ydl_instance = ydl  # Salvează referința pentru oprire
                
                # Verifică dacă utilizatorul a cerut oprirea
                if self.should_stop:
                    self.root.after(0, lambda: self.download_stopped())
                    return
                
                # Actualizează UI pentru extragerea informațiilor
                self.root.after(0, lambda: self.status_label.config(
                    text="⏳ Se extrag informațiile despre playlist...",
                    foreground="#3498db",
                    style='Status.TLabel'
                ))
                self.root.after(0, lambda: self.info_label.config(
                    text="Așteaptă, aceasta poate dura câteva momente pentru playlist-uri mari...",
                    foreground="#2980b9",
                    style='Info.TLabel'
                ))
                
                # Obține informații despre video/playlist
                info = ydl.extract_info(url, download=False)
                
                # Verifică din nou dacă utilizatorul a cerut oprirea
                if self.should_stop:
                    self.root.after(0, lambda: self.download_stopped())
                    return
                
                # Verifică dacă este playlist
                if 'entries' in info:
                    # Este un playlist
                    entries = [e for e in info['entries'] if e is not None]
                    total_videos = len(entries)
                    
                    format_text = format_type.lower()
                    self.root.after(0, lambda n=total_videos, f=format_text: self.status_label.config(
                        text=f"⏳ Descărcare playlist: {n} videouri ({f})...",
                        foreground="#3498db",
                        style='Status.TLabel'
                    ))
                    self.root.after(0, lambda n=total_videos: self.info_label.config(
                        text=f"Se descarcă {n} videouri (cu pauze pentru a evita rate limiting)...",
                        foreground="#2980b9",
                        style='Info.TLabel'
                    ))
                    
                    # Descarcă fiecare video din playlist cu verificare de oprire
                    for i, entry in enumerate(entries):
                        if self.should_stop:
                            self.root.after(0, lambda: self.download_stopped())
                            return
                        
                        try:
                            entry_url = entry.get('url') or entry.get('webpage_url') or url
                            if 'playlist_index' in entry:
                                # Este un video din playlist
                                ydl.download([entry_url])
                            else:
                                ydl.download([entry_url])
                        except Exception as e:
                            # Continuă cu următorul video dacă acesta eșuează
                            continue
                else:
                    # Este un singur video
                    video_title = info.get('title', 'necunoscut')
                    format_text = format_type.lower()
                    self.root.after(0, lambda f=format_text: self.status_label.config(
                        text=f"⏳ Se descarcă {f}...",
                        foreground="#3498db",
                        style='Status.TLabel'
                    ))
                    self.root.after(0, lambda t=video_title: self.info_label.config(
                        text=f"Video: {t[:50]}...",
                        foreground="#2980b9",
                        style='Info.TLabel'
                    ))
                    
                    # Verifică dacă utilizatorul a cerut oprirea înainte de descărcare
                    if self.should_stop:
                        self.root.after(0, lambda: self.download_stopped())
                        return
                    
                    # Descarcă
                    ydl.download([url])
                    
                    # Găsește fișierul descărcat (doar pentru video unic)
                    if 'entries' not in info:
                        filename = ydl.prepare_filename(info)
                        if format_type == "MP3":
                            downloaded_file = os.path.splitext(filename)[0] + '.mp3'
                        else:
                            downloaded_file = os.path.splitext(filename)[0] + '.mp4'
                        
                        # Verifică dacă fișierul există (poate avea altă extensie)
                        if not os.path.exists(downloaded_file):
                            # Caută fișierul cu orice extensie
                            base_name = os.path.splitext(filename)[0]
                            for ext in ['.mp3', '.mp4', '.m4a', '.webm']:
                                potential_file = base_name + ext
                                if os.path.exists(potential_file):
                                    downloaded_file = potential_file
                                    break
                
                # Verifică din nou dacă utilizatorul a cerut oprirea
                if self.should_stop:
                    self.root.after(0, lambda: self.download_stopped())
                    return
            
            # Succes - actualizează UI în thread-ul principal
            self.root.after(0, lambda: self.download_success(downloaded_file))
            
        except Exception as e:
            if self.should_stop:
                self.root.after(0, lambda: self.download_stopped())
            else:
                error_msg = str(e)
                # Verifică dacă eroarea este legată de rate limiting
                if 'rate-limit' in error_msg.lower() or 'rate limit' in error_msg.lower():
                    error_msg = f"{error_msg}\n\nSoluție:\nYouTube a limitat cererile. Aplicația folosește deja pauze între descărcări.\nTe rog așteaptă câteva minute și încearcă din nou.\n\nPentru playlist-uri foarte mari, recomand să descarci în mai multe sesiuni."
                # Verifică dacă eroarea este legată de ffmpeg
                elif 'ffmpeg' in error_msg.lower() or 'ffprobe' in error_msg.lower():
                    error_msg = f"{error_msg}\n\nSoluție:\n1. Instalează ffmpeg de la https://ffmpeg.org/download.html\n2. Sau selectează folderul unde se află ffmpeg.exe folosind butonul 'Selectează' deasupra"
                self.root.after(0, lambda: self.download_error(error_msg))
        finally:
            self.ydl_instance = None
    
    def download_stopped(self):
        """Gestionează oprirea descărcării"""
        self.is_downloading = False
        self.should_stop = False
        self.progress.stop()
        self.status_label.config(text="⏸️ Descărcare oprită", 
                               foreground="#e67e22", style='Status.TLabel')
        self.info_label.config(text="Descărcarea a fost oprită de utilizator", 
                             foreground="#d35400", style='Info.TLabel')
        self.url_entry.config(state="normal")
        self.convert_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        
        # Re-activează selectorul de calitate dacă este MP3
        if self.format_type.get() == "MP3":
            self.quality_combo.config(state="readonly")
        
        # Resetează statusul după 3 secunde
        self.root.after(3000, lambda: (
            self.status_label.config(text="✨ Gata pentru descărcare", 
                                   foreground="#7f8c8d", style='Status.TLabel'),
            self.info_label.config(text="", style='Info.TLabel')
        ))
    
    def download_success(self, filepath=None):
        self.is_downloading = False
        self.should_stop = False
        self.progress.stop()
        
        if filepath and os.path.exists(filepath):
            # Un singur fișier
            filename = os.path.basename(filepath)
            self.status_label.config(text="✅ Descărcare completă!", 
                                   foreground="#27ae60", style='Status.TLabel')
            self.info_label.config(text=f"Fișier salvat: {filename}", 
                                 foreground="#229954", style='Info.TLabel')
            messagebox.showinfo("Succes", f"Fișierul a fost descărcat cu succes!\n\n{filename}\n\nLocație: {os.path.dirname(filepath)}")
        else:
            # Probabil playlist sau mai multe fișiere
            self.status_label.config(text="✅ Descărcare completă!", 
                                   foreground="#27ae60", style='Status.TLabel')
            self.info_label.config(text="Toate fișierele disponibile au fost salvate în folderul selectat", 
                                 foreground="#229954", style='Info.TLabel')
            messagebox.showinfo("Succes", f"Descărcarea a fost completată!\n\nToate fișierele disponibile au fost salvate în:\n{self.save_path.get()}\n\nNotă: Unele videouri pot fi eșuate din cauza rate limiting sau indisponibilității.")
        
        self.url.set("")  # Resetează inputul
        self.url_entry.config(state="normal")
        self.url_entry.focus()
        self.convert_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        
        # Re-activează selectorul de calitate dacă este MP3
        if self.format_type.get() == "MP3":
            self.quality_combo.config(state="readonly")
        
        # Resetează statusul după 5 secunde
        self.root.after(5000, lambda: (
            self.status_label.config(text="✨ Gata pentru descărcare", 
                                   foreground="#7f8c8d", style='Status.TLabel'),
            self.info_label.config(text="", style='Info.TLabel')
        ))
    
    def download_error(self, error_msg):
        self.is_downloading = False
        self.should_stop = False
        self.progress.stop()
        self.status_label.config(text="❌ Eroare la descărcare!", 
                               foreground="#e74c3c", style='Status.TLabel')
        self.info_label.config(text="Verifică mesajul de eroare de mai jos", 
                             foreground="#c0392b", style='Info.TLabel')
        self.url_entry.config(state="normal")
        self.convert_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        
        # Re-activează selectorul de calitate dacă este MP3
        if self.format_type.get() == "MP3":
            self.quality_combo.config(state="readonly")
        
        messagebox.showerror("Eroare", f"Eroare la descărcare:\n\n{error_msg}")


if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubeConverter(root)
    root.mainloop()

# YouTube to MP3 Converter

Aplicație minimalistă pentru conversia linkurilor YouTube în format MP3 folosind Python, yt-dlp și ffmpeg.

## Cerințe

- Python 3.7 sau mai nou
- ffmpeg instalat în sistem (necesar pentru conversie MP3)
- **Opțional**: JavaScript runtime (Deno sau Node.js) - recomandat pentru playlist-uri mari

## Instalare

1. Instalează dependențele:
```bash
pip install -r requirements.txt
```

2. Instalează ffmpeg (necesar pentru conversie MP3):

   **Opțiunea 1 - Instalare în PATH (recomandat):**
   - **Windows**: 
     - Descarcă de la https://www.gyan.dev/ffmpeg/builds/ (recomandat) sau https://ffmpeg.org/download.html
     - Extrage arhiva și adaugă folderul `bin` la PATH din variabilele de mediu
     - Sau folosește: `winget install ffmpeg` (dacă ai Windows Package Manager)
   - **Linux**: `sudo apt install ffmpeg` (Ubuntu/Debian) sau `sudo yum install ffmpeg` (CentOS/RHEL)
   - **macOS**: `brew install ffmpeg`
   
   **Opțiunea 2 - Selectare manuală în aplicație:**
   - Dacă nu vrei să adaugi ffmpeg la PATH, poți selecta manual folderul unde se află `ffmpeg.exe` folosind butonul "Selectează" din secțiunea "FFmpeg (opțional)" din interfață

3. **Opțional - Instalează JavaScript runtime (recomandat pentru playlist-uri mari):**
   - **Deno** (recomandat): https://deno.com/ sau `winget install DenoLand.Deno` (Windows)
   - **Node.js**: https://nodejs.org/ sau `winget install OpenJS.NodeJS` (Windows)
   - Aplicația va detecta automat runtime-ul dacă este instalat în PATH
   - Acest lucru elimină warning-urile și îmbunătățește stabilitatea pentru playlist-uri mari

## Utilizare

Rulează aplicația:
```bash
python main.py
```

### Flow:
1. Verifică statusul FFmpeg (ar trebui să fie verde ✓)
   - Dacă nu este instalat, folosește butonul "Selectează" pentru a specifica folderul unde se află `ffmpeg.exe`
2. Selectează locația unde vrei să se salveze fișierul MP3 (butonul "Selectează")
3. Inserează linkul YouTube în câmpul "Link YouTube"
   - **Suport playlist**: Dacă linkul conține un playlist (`&list=`), aplicația va descărca automat toate videourile din playlist
4. Apasă butonul "Convert" sau Enter
5. Fișierul/fișierele se descarcă automat în locația selectată
   - Pentru playlist-uri, vei vedea progresul pentru fiecare video (ex: "Video 20/1045")
6. Inputul se resetează automat după descărcare

## Caracteristici

- Interfață minimalistă și ușor de folosit
- **Suport complet pentru playlist-uri** - descarcă automat toate videourile dintr-un playlist
- Verificare automată a FFmpeg la pornire
- Detectare automată a JavaScript runtime (Deno/Node.js) pentru stabilitate îmbunătățită
- Opțiune de a specifica manual calea către FFmpeg (dacă nu este în PATH)
- Selectare folder pentru salvare
- Conversie automată în MP3 (calitate 192 kbps)
- Progress bar pentru feedback vizual
- Progres detaliat pentru playlist-uri (afișează video-ul curent din total)
- Resetare automată a inputului după descărcare
- Mesaje de status pentru succes/eroare
- Mesaje de eroare clare cu soluții pentru problemele comune

## Note

- Aplicația folosește yt-dlp pentru descărcare, care este un tool stabil și open-source
- ffmpeg este folosit automat de yt-dlp pentru conversie în MP3
- Calitatea audio este setată la 192 kbps (poate fi modificată în cod)
- **Playlist-uri**: Aplicația descarcă automat toate videourile dintr-un playlist când linkul conține parametrul `&list=`
- **JavaScript Runtime**: Dacă vezi warning-uri despre JavaScript runtime, instalează Deno sau Node.js pentru o experiență mai stabilă, mai ales pentru playlist-uri mari (1000+ videouri)


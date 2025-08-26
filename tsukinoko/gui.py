import io, os
import tkinter as tk
from pygame import mixer
from PIL import Image, ImageTk
from mutagen.id3 import ID3
from mutagen.mp3 import MP3

# --- Configuración ventana ---
root = tk.Tk()
root.title("Tsukinoko")
root.iconname("Tsukinoko")
root.configure(bg="#222222")


#icono de la ventana
icon_path = os.path.expanduser("~/tsukinoko/bocchi trash.png")
icon_img = ImageTk.PhotoImage(Image.open(icon_path))
root.iconphoto(True, icon_img)

# --- Inicializar mixer ---
mixer.init()

# --- Carpeta y playlist ---
music_folder = os.path.expanduser("~/Música")
playlist = [f for f in os.listdir(music_folder) if f.endswith(".mp3")]
current = 0

# --- Placeholder / portada ---
cover_size = (200, 200)
placeholder_path = os.path.expanduser("~/tsukinoko/rin.jpg")
if os.path.exists(placeholder_path):
    placeholder_img = Image.open(placeholder_path).convert("RGB")
    placeholder_img = placeholder_img.resize(cover_size, Image.LANCZOS)
else:
    placeholder_img = Image.new("RGB", cover_size, color="#888888")
default_cover_tk = ImageTk.PhotoImage(placeholder_img)

lbl_cover = tk.Label(root, image=default_cover_tk, bg="#222222")
lbl_cover.image = default_cover_tk
lbl_cover.grid(row=0, column=0, columnspan=5, pady=10)

# --- Nombre de canción ---
lbl_song = tk.Label(root, text=playlist[current] if playlist else "No hay canciones",
                    font=("Arial", 14), fg="#ffffff", bg="#222222")
lbl_song.grid(row=1, column=0, columnspan=5, pady=5)

# --- Función actualizar portada ---
def update_cover(song_path):
    try:
        tags = ID3(song_path)
        apics = tags.getall("APIC")
        if apics:
            img_data = apics[0].data
            img = Image.open(io.BytesIO(img_data)).convert("RGB")
            img = img.resize(cover_size, Image.LANCZOS)
            img_tk = ImageTk.PhotoImage(img)
            lbl_cover.config(image=img_tk)
            lbl_cover.image = img_tk
            return
    except Exception:
        pass

    base, _ = os.path.splitext(song_path)
    for ext in (".jpg", ".png"):
        candidate = base + ext
        if os.path.exists(candidate):
            img = Image.open(candidate).convert("RGB")
            img = img.resize(cover_size, Image.LANCZOS)
            img_tk = ImageTk.PhotoImage(img)
            lbl_cover.config(image=img_tk)
            lbl_cover.image = img_tk
            return

    lbl_cover.config(image=default_cover_tk)
    lbl_cover.image = default_cover_tk

# --- Estado de pausa ---
is_paused = False

# --- Funciones de control ---
def play_pause():
    global is_paused
    ruta = os.path.join(music_folder, playlist[current])
    if not mixer.music.get_busy():
        mixer.music.load(ruta)
        mixer.music.play(fade_ms=500)
        lbl_song.config(text=playlist[current])
        update_cover(ruta)
        is_paused = False
        btn_play.config(text="Pause")
    elif is_paused:
        mixer.music.unpause()
        is_paused = False
        btn_play.config(text="Pause")
    else:
        mixer.music.pause()
        is_paused = True
        btn_play.config(text="Play")

def stop_song():
    global is_paused
    mixer.music.fadeout(500)
    is_paused = False
    btn_play.config(text="Play")

def next_song():
    global current
    current = (current + 1) % len(playlist)
    play_current_song()

def prev_song():
    global current
    current = (current - 1) % len(playlist)
    play_current_song()

def play_current_song():
    ruta = os.path.join(music_folder, playlist[current])
    mixer.music.load(ruta)
    mixer.music.play()
    lbl_song.config(text=playlist[current])
    update_cover(ruta)
    btn_play.config(text="Pause")
    global is_paused
    is_paused = False

    # Actualizar selección en Listbox
    playlist_box.selection_clear(0, tk.END)
    playlist_box.selection_set(current)
    playlist_box.see(current)

# --- Botones ---
btn_prev = tk.Button(root, text="Prev", command=prev_song, bg="#444444", fg="#ffffff", width=8)
btn_prev.grid(row=2, column=0, padx=5, pady=10)
btn_play = tk.Button(root, text="Play", command=play_pause, bg="#444444", fg="#ffffff", width=8)
btn_play.grid(row=2, column=1, padx=5, pady=10)
btn_stop = tk.Button(root, text="Stop", command=stop_song, bg="#444444", fg="#ffffff", width=8)
btn_stop.grid(row=2, column=2, padx=5, pady=10)
btn_next = tk.Button(root, text="Next", command=next_song, bg="#444444", fg="#ffffff", width=8)
btn_next.grid(row=2, column=3, padx=5, pady=10)

# --- Slider de volumen ---
def set_volume(val):
    mixer.music.set_volume(float(val)/100)

volume_slider = tk.Scale(
    root,
    from_=0,
    to=100,
    orient=tk.HORIZONTAL,
    command=set_volume,
    showvalue=False,
    length=200,
    width=10,
    troughcolor="#555555",
    sliderlength=18,
    sliderrelief="flat",
    bg="#222222",
    highlightthickness=0,
    fg="#ffffff",
)
volume_slider.set(40)  #volumen inicial
volume_slider.grid(row=3, column=0, columnspan=5, pady=10)

# --- Barra de progreso solo visual ---
progress = tk.Scale(
    root,
    from_=0,
    to=100,
    orient=tk.HORIZONTAL,
    length=300,
    showvalue=False,
    sliderlength=12,
    troughcolor="#555555",
    bg="#222222",
    fg="#ffffff",
)
progress.grid(row=4, column=0, columnspan=5, pady=10)

# --- Función para actualizar progreso ---
def update_progress():
    if playlist:
        ruta = os.path.join(music_folder, playlist[current])
        audio = MP3(ruta)
        total_duration = audio.info.length
        progress.config(to=int(total_duration))

        if mixer.music.get_busy():
            current_time = mixer.music.get_pos() / 1000
            progress.set(int(current_time))
        else:
            next_song()  # pasa a siguiente automáticamente

    root.after(500, update_progress)

# --- Listbox de playlist ---
playlist_box = tk.Listbox(root, bg="#333333", fg="#ffffff", width=40, height=10,
                          selectbackground="#1DB954", selectforeground="#ffffff",
                          font=("Arial", 12))
for song in playlist:
    playlist_box.insert(tk.END, song)
playlist_box.selection_set(current)
playlist_box.grid(row=5, column=0, columnspan=5, pady=10)

def play_selected(event):
    global current
    selection = playlist_box.curselection()
    if selection:
        current = selection[0]
        play_current_song()

# Evento click simple
playlist_box.bind("<ButtonRelease-1>", play_selected)

# --- Reproducir primera canción ---
if playlist:
    play_current_song()

update_progress()
root.mainloop()










import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import yt_dlp
import threading
import os

# Configuración del tema
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class MusicDownloaderApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configuración ventana principal
        self.title("Media Downloader")
        self.geometry("600x580")
        self.resizable(False, False)

        # Variables
        self.output_path = tk.StringVar(value=os.path.expanduser("~/Documents/music"))
        self.is_downloading = False
        self.download_format = "Audio (WAV)"  # Default

        self.create_widgets()

    def create_widgets(self):
        # Grid layout configuration
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)  # Title
        self.grid_rowconfigure(1, weight=0)  # URL
        self.grid_rowconfigure(2, weight=0)  # Format Selector
        self.grid_rowconfigure(3, weight=0)  # Path
        self.grid_rowconfigure(4, weight=0)  # Progress
        self.grid_rowconfigure(5, weight=0)  # Button
        self.grid_rowconfigure(6, weight=1)  # Spacer

        # 1. Título y Header
        self.header_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, sticky="ew", pady=(30, 20))

        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text="Media Downloader",
            font=ctk.CTkFont(size=26, weight="bold"),
        )
        self.title_label.pack()

        self.subtitle_label = ctk.CTkLabel(
            self.header_frame,
            text="Descarga Música y Video de YouTube",
            font=ctk.CTkFont(size=14),
            text_color="gray",
        )
        self.subtitle_label.pack()

        # 2. Input de URL
        self.url_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.url_frame.grid(row=1, column=0, padx=40, pady=(0, 20), sticky="ew")

        self.url_label = ctk.CTkLabel(self.url_frame, text="URL del Video", anchor="w")
        self.url_label.pack(fill="x", pady=(0, 5))

        self.url_entry = ctk.CTkEntry(
            self.url_frame,
            placeholder_text="https://youtube.com/watch?v=...",
            height=40,
            border_width=0,
        )
        self.url_entry.pack(fill="x")

        # 3. Selector de Formato
        self.format_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.format_frame.grid(row=2, column=0, padx=40, pady=(0, 20), sticky="ew")

        self.format_label = ctk.CTkLabel(
            self.format_frame, text="Formato de Descarga", anchor="w"
        )
        self.format_label.pack(fill="x", pady=(0, 5))

        self.format_segmented = ctk.CTkSegmentedButton(
            self.format_frame,
            values=["Audio (WAV)", "Video (MP4)"],
            command=self.change_format,
            height=35,
        )
        self.format_segmented.set("Audio (WAV)")
        self.format_segmented.pack(fill="x")

        # 4. Selector de Carpeta
        self.path_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.path_frame.grid(row=3, column=0, padx=40, pady=(0, 30), sticky="ew")

        self.path_label = ctk.CTkLabel(self.path_frame, text="Guardar en", anchor="w")
        self.path_label.pack(fill="x", pady=(0, 5))

        self.path_input_frame = ctk.CTkFrame(self.path_frame, fg_color="transparent")
        self.path_input_frame.pack(fill="x")

        self.path_entry = ctk.CTkEntry(
            self.path_input_frame,
            textvariable=self.output_path,
            state="disabled",
            height=40,
            border_width=0,
        )
        self.path_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.browse_btn = ctk.CTkButton(
            self.path_input_frame,
            text="📂",
            width=50,
            height=40,
            command=self.browse_folder,
        )
        self.browse_btn.pack(side="right")

        # 5. Barra de Progreso y Estado
        self.status_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.status_frame.grid(row=4, column=0, padx=40, pady=(0, 20), sticky="ew")

        self.status_label = ctk.CTkLabel(
            self.status_frame, text="Listo para descargar", text_color="gray"
        )
        self.status_label.pack(anchor="w")

        self.progress_bar = ctk.CTkProgressBar(self.status_frame, height=10)
        self.progress_bar.set(0)
        self.progress_bar.pack(fill="x", pady=(5, 0))

        # 6. Botón de Descarga
        self.download_btn = ctk.CTkButton(
            self,
            text="DESCARGAR",
            height=50,
            font=ctk.CTkFont(size=15, weight="bold"),
            command=self.start_download,
        )
        self.download_btn.grid(row=5, column=0, padx=40, pady=10, sticky="ew")

    def change_format(self, value):
        self.download_format = value
        # Actualizar ruta sugerida
        current_path = self.output_path.get()
        if "music" in current_path and value == "Video (MP4)":
            self.output_path.set(os.path.expanduser("~/Documents/videos"))
        elif "videos" in current_path and value == "Audio (WAV)":
            self.output_path.set(os.path.expanduser("~/Documents/music"))

    def browse_folder(self):
        folder = filedialog.askdirectory(initialdir=self.output_path.get())
        if folder:
            self.output_path.set(folder)

    def update_status(self, message, is_error=False):
        self.status_label.configure(
            text=message, text_color="#ff5555" if is_error else "#50fa7b"
        )

    def progress_hook(self, d):
        if d["status"] == "downloading":
            try:
                p = d.get("_percent_str", "0%").replace("%", "")
                self.progress_bar.set(float(p) / 100)
                self.status_label.configure(
                    text=f"Descargando... {d.get('_percent_str')}", text_color="#8be9fd"
                )
            except:
                self.progress_bar.start()
        elif d["status"] == "finished":
            self.progress_bar.stop()
            self.progress_bar.set(1)
            msg = (
                "Convirtiendo a WAV..."
                if self.download_format == "Audio (WAV)"
                else "Finalizando..."
            )
            self.status_label.configure(text=msg, text_color="#bd93f9")

    def download_media(self):
        url = self.url_entry.get().strip()
        if not url:
            self.update_status("Error: Ingresa una URL válida", True)
            self.reset_ui()
            return

        output_dir = self.output_path.get()
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Configuración base
        import typing
        ydl_opts: dict[str, typing.Any] = {
            "outtmpl": os.path.join(output_dir, "%(title)s.%(ext)s"),
            "noplaylist": True,
            "progress_hooks": [self.progress_hook],
            "quiet": True,
            "no_warnings": True,
            "windowsfilenames": True,
            "concurrent_fragment_downloads": 8,  # Descarga multi-hilo para mayor velocidad
            # Opciones para evitar HTTP 403 Forbidden
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            # 'cookiesfrombrowser': ('firefox',),  # Comentado temporalmente - puede causar problemas
            "extractor_args": {"youtube": {"player_client": ["android", "web"]}},
            "http_headers": {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-us,en;q=0.5",
                "Sec-Fetch-Mode": "navigate",
            },
            "ignoreerrors": False,  # No ignorar errores críticos
            "nocheckcertificate": True,  # Evitar problemas de certificados SSL
        }

        # Configurar según formato
        if self.download_format == "Audio (WAV)":
            # No especificar formato, dejar que yt-dlp elija el mejor disponible
            ydl_opts["postprocessors"] = [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "wav",
                    "preferredquality": "192",
                }
            ]
        else:  # Video (MP4)
            # Usar el formato más simple y compatible
            ydl_opts["postprocessors"] = [
                {
                    "key": "FFmpegVideoConvertor",
                    "preferedformat": "mp4",
                }
            ]

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            self.update_status("✅ ¡Descarga Completada!", False)
            messagebox.showinfo("Éxito", "Tu archivo se ha descargado correctamente.")

        except Exception as e:
            error_msg = str(e)
            # Manejo específico para error de bloqueo de archivos en Windows
            if "WinError 32" in error_msg:
                self.update_status("⚠️ Descarga finalizada con advertencia", False)
                messagebox.showwarning(
                    "Advertencia",
                    "La descarga se completó, pero Windows tardó en liberar el archivo temporal.\n\n"
                    + "Por favor revisa tu carpeta, el archivo debería estar ahí.",
                )
            else:
                self.update_status(f"Error: {str(error_msg)[:40]}...", True)
                messagebox.showerror("Error", f"Ocurrió un error:\n{error_msg}")

        finally:
            self.reset_ui()

    def start_download(self):
        if self.is_downloading:
            return
        self.is_downloading = True
        self.download_btn.configure(state="disabled", text="Procesando...")

        thread = threading.Thread(target=self.download_media, daemon=True)
        thread.start()

    def reset_ui(self):
        self.is_downloading = False
        self.download_btn.configure(state="normal", text="DESCARGAR")
        self.progress_bar.stop()


if __name__ == "__main__":
    app = MusicDownloaderApp()
    app.mainloop()

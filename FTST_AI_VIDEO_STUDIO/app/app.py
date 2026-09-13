import base64
import json
import threading
import time
from datetime import datetime
from pathlib import Path
from tkinter import Tk, StringVar, BooleanVar, Text, END, DISABLED, NORMAL, filedialog, messagebox
from tkinter import ttk

import requests

# ===== GOLDEN PATH =====
SALAD_API_BASE = "https://api.salad.com/api/public"
ORG = "food-through-space-time"
PROJECT = "default"
CONTAINER_GROUP = "comfyui-wan22-v03b"
GATEWAY = "https://orange-ambrosia-sswqzg6435oa2dwq.salad.cloud"

START_URL = f"{SALAD_API_BASE}/organizations/{ORG}/projects/{PROJECT}/containers/{CONTAINER_GROUP}/start"
STOP_URL = f"{SALAD_API_BASE}/organizations/{ORG}/projects/{PROJECT}/containers/{CONTAINER_GROUP}/stop"
READY_URL = f"{GATEWAY}/ready"
MODELS_URL = f"{GATEWAY}/models"
PROMPT_URL = f"{GATEWAY}/prompt"

READY_TIMEOUT = 45 * 60
WEBHOOK_TIMEOUT = 20 * 60

REQUIRED_MODELS = {
    "diffusion_models": "wan2.2_ti2v_5B_fp16.safetensors",
    "text_encoders": "umt5_xxl_fp8_e4m3fn_scaled.safetensors",
    "vae": "wan2.2_vae.safetensors",
}

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_WORKFLOW = BASE_DIR / "workflows" / "wan22_t2v_5s_webhook.json"


def latest_raw_url(webhook_url):
    token = webhook_url.rstrip("/").split("/")[-1]
    return f"https://webhook.site/token/{token}/request/latest/raw"


class App:
    def __init__(self, root):
        self.root = root
        root.title("AI Video Generator MASTER")
        root.geometry("850x700")

        self.api_key = StringVar()
        self.workflow = StringVar(value=str(DEFAULT_WORKFLOW))
        self.webhook = StringVar(value="https://webhook.site/af1e2243-851f-4353-afd3-c70290aceb76")
        self.output = StringVar(value=str(Path.home() / "Downloads" / "wan22_video.mp4"))
        self.auto_stop = BooleanVar(value=True)
        self.show_key = BooleanVar(value=False)
        self.busy = False
        self.stop_requested = False

        pad = {"padx": 10, "pady": 6}

        ttk.Label(root, text="Salad API Key").grid(row=0, column=0, sticky="w", **pad)
        self.key_entry = ttk.Entry(root, textvariable=self.api_key, show="*", width=70)
        self.key_entry.grid(row=0, column=1, sticky="ew", **pad)
        ttk.Checkbutton(root, text="Mostra", variable=self.show_key, command=self.toggle_key).grid(row=0, column=2, **pad)

        ttk.Label(root, text="Workflow").grid(row=1, column=0, sticky="w", **pad)
        ttk.Entry(root, textvariable=self.workflow, width=70).grid(row=1, column=1, sticky="ew", **pad)
        ttk.Button(root, text="Sfoglia", command=self.pick_workflow).grid(row=1, column=2, **pad)

        ttk.Label(root, text="Webhook.site").grid(row=2, column=0, sticky="w", **pad)
        ttk.Entry(root, textvariable=self.webhook, width=70).grid(row=2, column=1, sticky="ew", **pad)

        ttk.Label(root, text="Output MP4").grid(row=3, column=0, sticky="w", **pad)
        ttk.Entry(root, textvariable=self.output, width=70).grid(row=3, column=1, sticky="ew", **pad)
        ttk.Button(root, text="Scegli", command=self.pick_output).grid(row=3, column=2, **pad)

        ttk.Checkbutton(root, text="STOP Salad automatico alla fine", variable=self.auto_stop).grid(row=4, column=1, sticky="w", **pad)

        frame = ttk.Frame(root)
        frame.grid(row=5, column=0, columnspan=3, pady=10)
        self.create_btn = ttk.Button(frame, text="CREA VIDEO", command=self.start_create)
        self.create_btn.pack(side="left", padx=8)
        ttk.Button(frame, text="TEST READY", command=self.start_ready_test).pack(side="left", padx=8)
        ttk.Button(frame, text="STOP SALAD", command=self.emergency_stop).pack(side="left", padx=8)

        ttk.Label(root, text="Log").grid(row=6, column=0, sticky="nw", **pad)
        self.logbox = Text(root, wrap="word", height=28)
        self.logbox.grid(row=6, column=1, columnspan=2, sticky="nsew", **pad)

        root.columnconfigure(1, weight=1)
        root.rowconfigure(6, weight=1)
        self.log("MASTER pronta.")
        self.log("START -> READY -> MODELS -> PROMPT -> WEBHOOK -> MP4 -> STOP")

    def toggle_key(self):
        self.key_entry.configure(show="" if self.show_key.get() else "*")

    def pick_workflow(self):
        p = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if p: self.workflow.set(p)

    def pick_output(self):
        p = filedialog.asksaveasfilename(defaultextension=".mp4", filetypes=[("MP4", "*.mp4")])
        if p: self.output.set(p)

    def log(self, text):
        self.logbox.insert(END, f"[{datetime.now().strftime('%H:%M:%S')}] {text}\n")
        self.logbox.see(END)
        self.root.update_idletasks()

    def headers(self, json_mode=False):
        key = self.api_key.get().strip()
        if not key:
            raise ValueError("Inserisci la Salad API Key.")
        h = {"Salad-Api-Key": key}
        if json_mode:
            h["Content-Type"] = "application/json"
        return h

    def set_busy(self, value):
        self.busy = value
        self.create_btn.configure(state=DISABLED if value else NORMAL)

    def start_ready_test(self):
        threading.Thread(target=self.ready_test, daemon=True).start()

    def ready_test(self):
        try:
            r = requests.get(READY_URL, headers=self.headers(), timeout=20)
            r.raise_for_status()
            self.log(f"READY OK: {r.json()}")
        except Exception as e:
            self.log(f"READY FAIL: {e}")

    def start_create(self):
        if self.busy: return
        self.stop_requested = False
        self.set_busy(True)
        threading.Thread(target=self.worker, daemon=True).start()

    def start_salad(self):
        self.log("START Salad...")
        r = requests.post(START_URL, headers=self.headers(), timeout=30)
        if r.status_code not in (200, 201, 202, 204):
            raise RuntimeError(f"START fallito HTTP {r.status_code}: {r.text[:300]}")
        self.log(f"START accettato HTTP {r.status_code}")

    def stop_salad(self):
        self.log("STOP Salad...")
        try:
            r = requests.post(STOP_URL, headers=self.headers(), timeout=30)
            self.log(f"STOP risposta HTTP {r.status_code}")
        except Exception as e:
            self.log(f"STOP errore: {e}")

    def emergency_stop(self):
        self.stop_requested = True
        threading.Thread(target=self.stop_salad, daemon=True).start()

    def wait_ready(self):
        deadline = time.time() + READY_TIMEOUT
        self.log("Attendo READY (max 45 min)...")
        while time.time() < deadline:
            if self.stop_requested:
                raise RuntimeError("Interrotto dall'utente.")
            try:
                r = requests.get(READY_URL, headers=self.headers(), timeout=15)
                if r.status_code == 200 and r.json().get("status") == "ready":
                    self.log(f"READY: API {r.json().get('version')}")
                    return
                self.log(f"Ready non ancora disponibile: HTTP {r.status_code}")
            except requests.RequestException:
                self.log("Ready non ancora disponibile...")
            time.sleep(10)
        raise TimeoutError("READY non raggiunto entro 45 minuti.")

    def verify_models(self):
        self.log("Controllo modelli...")
        r = requests.get(MODELS_URL, headers=self.headers(), timeout=30)
        r.raise_for_status()
        data = r.json()
        missing = []
        for category, filename in REQUIRED_MODELS.items():
            if filename not in json.dumps(data.get(category, {})):
                missing.append(filename)
        if missing:
            raise RuntimeError("Modelli mancanti: " + ", ".join(missing))
        self.log("MODELS OK.")

    def load_workflow(self):
        path = Path(self.workflow.get())
        if not path.exists():
            raise FileNotFoundError(path)
        body = json.loads(path.read_text(encoding="utf-8"))
        body["webhook"] = self.webhook.get().strip()
        return body

    def submit(self, body):
        self.log("Invio /prompt...")
        r = requests.post(PROMPT_URL, headers=self.headers(True), json=body, timeout=30)
        r.raise_for_status()
        data = r.json()
        pid = str(data.get("id", ""))
        if not pid:
            raise RuntimeError("Nessun prompt id restituito.")
        self.log(f"Prompt accettato: {pid}")
        return pid

    def wait_webhook(self, prompt_id):
        url = latest_raw_url(self.webhook.get().strip())
        deadline = time.time() + WEBHOOK_TIMEOUT
        self.log("Attendo output.complete del prompt nuovo...")
        while time.time() < deadline:
            if self.stop_requested:
                raise RuntimeError("Interrotto dall'utente.")
            try:
                r = requests.get(url, timeout=20)
                if r.status_code == 200:
                    data = r.json()
                    if data.get("event") == "output.complete" and str(data.get("id")) == prompt_id and data.get("image"):
                        self.log("Webhook corretto ricevuto.")
                        return data
            except Exception:
                pass
            time.sleep(5)
        raise TimeoutError("Webhook corretto non arrivato entro 20 minuti.")

    def save_video(self, data):
        out = Path(self.output.get())
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(base64.b64decode(data["image"]))
        if out.stat().st_size < 1000:
            raise RuntimeError("MP4 troppo piccolo/non valido.")
        self.log(f"Salvato: {out} ({out.stat().st_size/1024:.1f} KB)")
        return out

    def worker(self):
        try:
            body = self.load_workflow()
            self.start_salad()
            self.wait_ready()
            self.verify_models()
            pid = self.submit(body)
            data = self.wait_webhook(pid)
            out = self.save_video(data)
            self.log("VIDEO COMPLETATO.")
            messagebox.showinfo("Completato", f"Video salvato in:\n{out}")
        except Exception as e:
            self.log(f"ERRORE: {e}")
            messagebox.showerror("Errore", str(e))
        finally:
            if self.auto_stop.get():
                self.stop_salad()
            self.set_busy(False)


if __name__ == "__main__":
    root = Tk()
    App(root)
    root.mainloop()

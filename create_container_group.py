import tkinter as tk
from tkinter import simpledialog, messagebox
import requests
import copy

BASE = "https://api.salad.com/api/public"
ORG = "food-through-space-time"
PROJECT = "default"
SOURCE_GROUP = "comfyui-video-test"
NEW_GROUP = "comfyui-video-jobqueue"
QUEUE = "wan22-video-queue"

def ask(root, title, prompt, secret=False):
    return simpledialog.askstring(title, prompt, parent=root, show="*" if secret else None)

def main():
    root = tk.Tk()
    root.withdraw()

    api_key = ask(root, "Salad API Key", "Incolla la Salad API Key:", secret=True)
    if not api_key:
        messagebox.showerror("Errore", "API key mancante.")
        return
    api_key = api_key.strip()

    image = ask(
        root,
        "Immagine Docker",
        "Inserisci il nome completo della nuova immagine Docker\n(esempio: docker.io/utente/wan22-salad:v03b):"
    )
    if not image:
        messagebox.showerror("Errore", "Immagine Docker mancante.")
        return
    image = image.strip()

    headers = {"Salad-Api-Key": api_key, "Content-Type": "application/json"}

    # Read the already-working group so we reuse its exact RTX 5090 resource class.
    src_url = f"{BASE}/organizations/{ORG}/projects/{PROJECT}/containers/{SOURCE_GROUP}"
    r = requests.get(src_url, headers=headers, timeout=30)
    if r.status_code != 200:
        messagebox.showerror("Errore", f"Impossibile leggere {SOURCE_GROUP}\nHTTP {r.status_code}\n{r.text}")
        return

    src = r.json()
    old_container = src.get("container", {})
    resources = copy.deepcopy(old_container.get("resources", {}))
    if not resources:
        messagebox.showerror("Errore", "La configurazione sorgente non contiene resources.")
        return

    body = {
        "autostart_policy": True,
        "container": {
            "image": image,
            "resources": resources,
            "environment_variables": {},
            "image_caching": True,
            "priority": "high"
        },
        "name": NEW_GROUP,
        "display_name": "ComfyUI Wan 2.2 Job Queue",
        "replicas": 1,
        "country_codes": src.get("country_codes", []),
        "queue_connection": {
            "queue_name": QUEUE,
            "port": 3000,
            "path": "/prompt"
        },
        "readiness_probe": {
            "http": {
                "path": "/ready",
                "port": 3000,
                "scheme": "http"
            },
            "initial_delay_seconds": 0,
            "period_seconds": 10,
            "success_threshold": 1,
            "failure_threshold": 30,
            "timeout_seconds": 5
        }
    }

    ok = messagebox.askyesno(
        "Conferma",
        "Sto per creare un NUOVO Container Group:\n\n"
        f"{NEW_GROUP}\n\n"
        f"Queue: {QUEUE}\n"
        "Endpoint interno: /prompt :3000\n"
        "GPU/resources: copiati da comfyui-video-test\n"
        "Priority: high\n"
        "Repliche: 1\n\n"
        "La creazione può avviare una GPU e generare costi.\n\nProcedo?"
    )
    if not ok:
        return

    url = f"{BASE}/organizations/{ORG}/projects/{PROJECT}/containers"
    r = requests.post(url, headers=headers, json=body, timeout=60)

    try:
        result = r.json()
    except Exception:
        result = r.text

    if r.status_code in (200, 201):
        messagebox.showinfo(
            "Successo",
            f"Container Group creato:\n{NEW_GROUP}\n\n"
            "Collegato a wan22-video-queue."
        )
    elif r.status_code == 409:
        messagebox.showinfo("Info", f"{NEW_GROUP} esiste gia.")
    else:
        messagebox.showerror("Errore", f"HTTP {r.status_code}\n\n{result}")

if __name__ == "__main__":
    main()

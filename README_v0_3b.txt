AI Video Generator v0.3b

COSA CAMBIA
1) Job Queue: usa la queue gia creata "wan22-video-queue".
2) Il Container Group sara collegato alla queue su port 3000, path /prompt.
3) Wan 2.2, UMT5 e VAE vengono inclusi nella nuova immagine Docker: niente download dei tre modelli dopo l'avvio.
4) image_caching e attivo.
5) Le risorse GPU vengono copiate automaticamente dal gruppo gia funzionante "comfyui-video-test", cosi non dobbiamo indovinare l'ID della RTX 5090.

IMPORTANTE
NON eseguire create_container_group.py finche la nuova immagine Docker non e stata costruita e pubblicata in un registry.

Ordine corretto:
A. Costruire l'immagine dal Dockerfile.
B. Pubblicarla su Docker Hub / GHCR.
C. Eseguire:
   python create_container_group.py
D. Incollare API key nella finestra.
E. Inserire il nome completo dell'immagine pubblicata.
F. Confermare solo quando si e pronti a far partire Salad.

Il nuovo gruppo:
  comfyui-video-jobqueue

Queue:
  wan22-video-queue

Endpoint interno Job Queue:
  http://container:3000/prompt

Readiness:
  http://container:3000/ready

NOTA COSTI
Lo script chiede conferma prima della creazione perche il nuovo gruppo usa autostart_policy=true e una replica.

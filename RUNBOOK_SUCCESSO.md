# RUNBOOK SUCCESSO — FTS&T AI Video Generator

## GOLDEN PATH — CONFIGURAZIONE CONFERMATA FUNZIONANTE

Data del test riuscito: 13 settembre 2026

Questo documento contiene SOLO il percorso verificato e funzionante.
Non usare vecchi tentativi o configurazioni precedenti se sono in conflitto con questo documento.

## 1. Repository GitHub

Repository:

CostaMediaChamp/fts-wan22-salad

Immagine Docker funzionante:

ghcr.io/costamediachamp/fts-wan22-salad:latest

Script di avvio funzionante:

start-v03b.sh

Avvio finale di ComfyUI API:

exec /opt/ComfyUI/comfyui-api


## 2. SaladCloud

Organization:

food-through-space-time

Project:

default

Container Group funzionante:

comfyui-wan22-v03b

Versione verificata:

Version 2

GPU utilizzata:

NVIDIA GeForce RTX 5090

ComfyUI:

0.3.62

ComfyUI API:

1.10.0

PyTorch:

2.8.0 + CUDA 12.8


## 3. Controllo READY

L'endpoint deve essere interrogato con Salad-Api-Key.

Endpoint:

https://orange-ambrosia-sswqzg6435oa2dwq.salad.cloud/ready

Risultato corretto:

version  status
1.10.0   ready

IMPORTANTE:
aprire /ready direttamente nel browser può restituire ERROR 403.
È normale perché il deployment richiede autenticazione.

Il test corretto viene fatto tramite richiesta autenticata con header:

Salad-Api-Key


## 4. Modelli verificati

La chiamata autenticata a /models ha confermato:

diffusion_models:
wan2.2_ti2v_5B_fp16.safetensors

text_encoders:
umt5_xxl_fp8_e4m3fn_scaled.safetensors

vae:
wan2.2_vae.safetensors

Questi tre modelli sono quindi disponibili direttamente nel container.


## 5. Workflow locale funzionante

File:

C:\Users\costa\Downloads\wan22_t2v_5s_webhook.json

Test esistenza file:

Test-Path "$env:USERPROFILE\Downloads\wan22_t2v_5s_webhook.json"

Risultato corretto:

True


## 6. Invio del prompt

Caricare il JSON:

$body = Get-Content "$env:USERPROFILE\Downloads\wan22_t2v_5s_webhook.json" -Raw

Inviare a ComfyUI API:

Invoke-RestMethod -Method Post -Uri "https://orange-ambrosia-sswqzg6435oa2dwq.salad.cloud/prompt" -Headers @{"Salad-Api-Key"=$k;"Content-Type"="application/json"} -Body $body

Risultato corretto:

la API restituisce un ID del prompt e l'indirizzo webhook.

Questo significa che il job è stato accettato.


## 7. Webhook

Webhook.site utilizzato nel test:

https://webhook.site/af1e2243-851f-4353-afd3-c70290aceb76

Quando Wan termina il rendering arriva una nuova richiesta POST.

Il contenuto JSON deve mostrare:

"event": "output.complete"

e deve contenere:

"image": "..."

Il campo image contiene il video codificato Base64.


## 8. Recupero automatico del video

Comando PowerShell verificato:

$w = Invoke-RestMethod "https://webhook.site/token/af1e2243-851f-4353-afd3-c70290aceb76/request/latest/raw"; [IO.File]::WriteAllBytes("$env:USERPROFILE\Downloads\wan22_video.mp4",[Convert]::FromBase64String($w.image))

Output:

C:\Users\costa\Downloads\wan22_video.mp4


## 9. RISULTATO DEL TEST

Video generato correttamente.

Durata:

circa 5 secondi

Formato:

MP4

Dimensione:

circa 478 KB

Qualità visiva:

BUONA — verificata personalmente dopo apertura del file.

Pipeline confermata:

Salad START
→ RTX 5090
→ container Docker
→ ComfyUI API ready
→ modelli Wan 2.2 disponibili
→ /prompt
→ rendering Wan 2.2
→ webhook output.complete
→ Base64
→ MP4 sul PC
→ verifica video
→ Salad STOP


## 10. REGOLA FONDAMENTALE

Dopo aver recuperato e verificato il video:

STOP SALAD IMMEDIATAMENTE

per evitare di pagare GPU inutilmente.


## 11. OBIETTIVO SUCCESSIVO

Automatizzare questa golden path nell'app locale:

START Salad
→ attendere READY
→ inviare workflow
→ attendere NUOVO webhook
→ recuperare Base64
→ salvare MP4
→ verificare completamento
→ STOP automatico Salad

IMPORTANTE:
l'app deve distinguere il NUOVO webhook da eventuali webhook precedenti,
per evitare di scaricare per errore un vecchio video.

Questo documento è la GOLDEN PATH.
In caso di problemi futuri, partire da questa configurazione funzionante e non dai tentativi precedenti.

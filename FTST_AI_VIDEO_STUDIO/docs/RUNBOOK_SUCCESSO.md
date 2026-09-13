# RUNBOOK SUCCESSO — FTS&T AI Video Generator

## GOLDEN PATH

Test riuscito: 13 settembre 2026.

Repository: `CostaMediaChamp/fts-wan22-salad`

Immagine: `ghcr.io/costamediachamp/fts-wan22-salad:latest`

Container Group: `comfyui-wan22-v03b` — Version 2

Gateway:
`https://orange-ambrosia-sswqzg6435oa2dwq.salad.cloud`

Avvio confermato:
`exec /opt/ComfyUI/comfyui-api`

`/ready` autenticato:
`version 1.10.0` — `status ready`

Modelli confermati:
- `wan2.2_ti2v_5B_fp16.safetensors`
- `umt5_xxl_fp8_e4m3fn_scaled.safetensors`
- `wan2.2_vae.safetensors`

Pipeline confermata:
START Salad -> READY -> MODELS -> POST /prompt -> webhook `output.complete`
-> Base64 -> MP4 -> verifica -> STOP Salad.

Il browser su `/ready` senza `Salad-Api-Key` può mostrare 403: è normale.

### Regola
Non mettere mai la Salad API Key nel repository o nei file del progetto.

### Procedura manuale di emergenza

```powershell
$body = Get-Content "$env:USERPROFILE\Downloads\wan22_t2v_5s_webhook.json" -Raw
Invoke-RestMethod -Method Post -Uri "https://orange-ambrosia-sswqzg6435oa2dwq.salad.cloud/prompt" -Headers @{"Salad-Api-Key"=$k;"Content-Type"="application/json"} -Body $body
```

Recupero ultimo webhook:

```powershell
$w = Invoke-RestMethod "https://webhook.site/token/af1e2243-851f-4353-afd3-c70290aceb76/request/latest/raw"
[IO.File]::WriteAllBytes("$env:USERPROFILE\Downloads\wan22_video.mp4",[Convert]::FromBase64String($w.image))
```

La MASTER locale evita il webhook vecchio confrontando l'ID del prompt.

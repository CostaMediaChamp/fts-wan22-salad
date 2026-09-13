AI VIDEO GENERATOR MASTER
=========================

Questa cartella è pensata per sostituire le vecchie cartelle v0_1, v0_2, v0_3_starter e v0_3b_preparato.

CONTENUTO
---------
app/
  app.py
  requirements.txt
  AVVIA_APP.bat

workflows/
  wan22_t2v_5s_webhook.json

salad_container/
  Dockerfile
  start-v03b.sh

docs/
  RUNBOOK_SUCCESSO.md

PRIMA DI CANCELLARE LE VECCHIE CARTELLE
---------------------------------------
1. Estrai questa cartella.
2. Avvia AVVIA_APP.bat.
3. Verifica che l'app si apra.
4. NON avviare una GPU solo per controllare la GUI.
5. Conserva comunque lo ZIP MASTER come backup.
6. Solo dopo, puoi eliminare le vecchie cartelle locali.

IMPORTANTE
----------
La Salad API Key non è inclusa e non deve essere salvata nel progetto.
Va incollata nell'app quando serve.

Il container Salad già esistente è:
comfyui-wan22-v03b — Version 2

L'app automatizza:
START -> READY -> MODELS -> PROMPT -> WEBHOOK -> MP4 -> STOP

# Modelle, Preise und Fallen

Stand: Preise ändern sich häufig. **Vor größeren Läufen auf kie.ai/pricing
schauen** und die Tabellen in `scripts/kie.py` bei Bedarf nachziehen — dort
stehen sie im Wörterbuch `MODELLE`.

200 Credits = 1 US-Dollar. Ein Credit sind rund 0,0043 €.
Rechnen lassen, nicht schätzen: `python3 scripts/kie.py preis …`

## Die API in drei Zügen

Basis `https://api.kie.ai/api/v1`, Kopfzeile `Authorization: Bearer $KIE_API_KEY`.
Die API ist asynchron:

1. `POST /jobs/createTask` mit `{"model": "…", "input": {…}}` → Antwort enthält
   `data.taskId`. Ist `code` ungleich 200, ist es fehlgeschlagen.
2. `GET /jobs/recordInfo?taskId=…` alle acht Sekunden abfragen. `data.state` läuft
   über `waiting`, `queuing`, `generating` bis `success` oder `fail`.
3. Bei `success` steckt das Ergebnis in `data.resultJson` — **das ist ein
   JSON-STRING, den man erst parsen muss.** Darin `resultUrls` als Liste. Die
   tatsächlich abgerechneten Credits stehen in `data.creditsConsumed`.

Bei HTTP 429, 500, 502 und 503 bis zu fünfmal wiederholen, mit wachsender Pause.
Rate Limit: 20 Anfragen je 10 Sekunden. Guthaben über `GET /chat/credit`.

## Bild — Preis je Bild

| Modell | 1K | 2K | 4K | Anmerkung |
|---|---|---|---|---|
| `gpt-image-2-text-to-image` | 6 | 10 | 16 | folgt dem Prompt am genauesten |
| `gpt-image-2-image-to-image` | 6 | 10 | 16 | braucht eine Vorlage |
| `nano-banana-2` | 8 | 12 | 18 | kräftige Farben |
| `google/nano-banana-pro` | 18 | 18 | 24 | 1K und 2K kosten gleich viel |
| `nano-banana-2-lite` | 4 | — | — | nur 1K, billigste Wahl |
| `google/nano-banana-edit` | 4 (fest) | | | Bearbeitung, keine Auflösungsstufen |
| `seedream-5-pro` | 7 | 14 | — | fotografisch, kein 4K |

## Video — Preis je Sekunde

| Modell | 480p | 720p | 1080p | Anmerkung |
|---|---|---|---|---|
| `grok-imagine/image-to-video` | 2,4 | 4,5 | 8 | billigste Bewegung |
| `bytedance/seedance-1.5-pro` | — | 3,5 | 7,5 | **ohne Ton** |
| `kling-3-0` | — | 14 | 18 | |
| `bytedance/seedance-2` | — | 41 | 102 | teuerstes Modell, gut überlegen |

Acht Sekunden Seedance 2 in 1080p sind 816 Credits — rund 3,51 €. Vor solchen
Läufen ausdrücklich rückfragen, auch wenn der Auftrag schon bestätigt war.

## Video — Preis je Clip

| Modell | Lite 1080p | Fast 1080p | Quality 1080p |
|---|---|---|---|
| `veo3.1` | 35 | 65 | 255 |

**Nur 4, 6 oder 8 Sekunden möglich.** Der Preis hängt nicht an der Länge — acht
Sekunden kosten so viel wie vier.

## Ton

| Modell | Preis |
|---|---|
| `google/gemini-2-5-pro-tts` | rund 4 Credits für 40 Sekunden Sprache |
| ElevenLabs Multilingual v2 | 12 Credits je 1.000 Zeichen |

Die genaue Modellkennung für ElevenLabs auf kie.ai nachschlagen; in `kie.py`
liegt sie unter `elevenlabs-multilingual-v2` für die Preisrechnung.

## Die Fallen

**Ergebnis-URLs verfallen nach 24 Stunden.** Sofort herunterladen, nie als Link
weitergeben, nie auf später vertagen. Immer mit `--projekt` erzeugen.

**Videomodelle verstehen nur englische Prompts.** Deutsche werden ignoriert — es
kommt etwas heraus, aber nicht das Gewünschte, und bezahlt ist es trotzdem. Vor
dem Absenden übersetzen. `kie.py` warnt, wenn ein Video-Prompt deutsch wirkt.

**`duration` ist mal Text, mal Zahl.** Bei `grok-imagine` ein TEXT (`"8"`), bei
`veo3.1` eine ZAHL (`8`) und dort nur 4, 6 oder 8. `kie.py` biegt beides gerade
und lehnt unerlaubte Längen bei veo3.1 ab.

**`google/gemini-2-5-pro-tts` schneidet mehrere `dialogue_turns` ab** — es kommen
nur die ersten neun Sekunden an. Deshalb: EIN Text, Absätze durch Leerzeilen
getrennt. Keine Liste von Sprechbeiträgen.

**HTTP 402 heißt leeres Guthaben.** Nicht wiederholen, sondern melden.

**Suno für Musik läuft NICHT über `/jobs/createTask`.** Eigener Pfad:

```
POST /api/v1/generate
{"prompt": "…", "customMode": false, "instrumental": true,
 "model": "V5", "callBackUrl": "…"}

GET /api/v1/generate/record-info?taskId=…
```

`kie.py` deckt das nicht ab — Musikaufträge von Hand stellen, etwa mit `curl`,
und die Dateien danach mit `kie.py lade --url … --projekt …` ablegen, damit sie
in `meta.json` und in der Galerie landen.

**Preise ändern sich häufig.** Vor größeren Läufen auf kie.ai/pricing schauen.

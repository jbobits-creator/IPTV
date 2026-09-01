---
name: media-skill
description: Erzeugt Bilder, Videos und Sprachaufnahmen über die kie.ai-API. Nutzen, wenn ein Bild, Foto, Illustration, Video, Clip, Voiceover, Sprachaufnahme oder Musik erzeugt, generiert oder bearbeitet werden soll, wenn nach Modellen wie GPT Image 2, Nano Banana, Seedream, Veo, Kling, Seedance, Grok Imagine oder ElevenLabs gefragt wird, wenn die Kosten oder Credits einer Generierung interessieren, oder wenn das kie.ai-Guthaben abgefragt werden soll.
---

# media-skill

Bilder, Videos und Sprache über kie.ai. Zwei Werkzeuge:

- `scripts/kie.py` — Preise rechnen, Guthaben, Aufträge, Download mit Protokoll
- `scripts/galerie.py` — baut `~/Medien/galerie.html` aus allen `meta.json`

Der Schlüssel steht in `KIE_API_KEY`. Ist er nicht gesetzt, sag das und bitte um
`export KIE_API_KEY="…"` — such ihn nicht in Dateien, leg ihn nirgends ab. Unter
Windows heißt der Aufruf `python` oder `py` statt `python3`, und der Schlüssel wird
mit `setx` gesetzt.

Vor jedem Auftrag `references/modelle.md` lesen. Dort stehen die Fallen, die sonst
Geld kosten: verfallende URLs, englische Video-Prompts, `duration` mal Text mal
Zahl, abgeschnittene Sprachausgabe, Suno über einen anderen Pfad.

## Die eine Frage: hat der Nutzer ein Modell genannt?

Daran hängt alles. Erst diese Frage beantworten, dann handeln.

### Fall A — kein Modell genannt: beraten, dann anhalten

1. **Erst überlegen**, was der Auftrag wirklich braucht: Bild oder Video oder Ton,
   welche Auflösung, wie viele Stücke, wie lang, Ton nötig oder nicht, Vorlage
   vorhanden oder nicht.
2. **Höchstens DREI Kandidaten** als kompakte Tabelle. Die Kosten gelten für genau
   diesen Auftrag — sechs Bilder heißt mal sechs, nicht der Stückpreis. Je ein
   Halbsatz dafür und dagegen.
3. **Eine klare Empfehlung aussprechen.** Nicht die Wahl zurückgeben, nicht
   "je nachdem". Ein Satz, warum dieses und nicht die anderen.
4. **Anhalten und auf ein Ja warten.** Nicht anfangen.

Preise dafür immer rechnen lassen, nie schätzen:

```bash
python3 scripts/kie.py preis gpt-image-2-text-to-image nano-banana-2 seedream-5-pro \
  --anzahl 6 --stufe 2K
```

So sieht die Antwort aus:

> | Modell | Kosten für 6 Bilder in 2K | Dafür | Dagegen |
> |---|---|---|---|
> | GPT Image 2 | 60 Credits · 0,258 € | folgt dem Prompt am genauesten | nüchterner Stil |
> | Nano Banana 2 | 72 Credits · 0,310 € | kräftigere Farben | streut stärker |
> | Seedream 5 Pro | 84 Credits · 0,361 € | am fotografischsten | teuerste Wahl, kein 4K |
>
> Ich würde **GPT Image 2 in 2K** nehmen: Deine Vorlage ist eng beschrieben, und
> da zahlt sich die Prompttreue mehr aus als der Look. Soll ich?

### Fall B — Modell genannt: nur bestätigen

Keine Beratung, keine Alternativen, keine Belehrung. Eine Zeile:

> GPT Image 2, 2K, ein Bild: 10 Credits · 0,043 €. Loslegen?

Nur wenn das gewünschte Modell den Auftrag **technisch nicht erfüllen kann**, ein
Halbsatz Hinweis — etwa "Seedance 1.5 Pro liefert keinen Ton" oder "veo3.1 kann
nur 4, 6 oder 8 Sekunden". Kein Preisvergleich, keine Alternative hinterher.

### Nachbesserungen

Läuft ein Auftrag bereits bestätigt, gar nicht mehr fragen. Nur die Kosten nennen
und weitermachen: "Noch drei Varianten, 30 Credits · 0,129 €." Dann erzeugen.

## Preise rechnen

Nie schätzen, nie aus dem Kopf. `preis` rechnet ohne API-Aufruf:

```bash
python3 scripts/kie.py preis veo3.1 --stufe quality --sekunden 8      # je Clip
python3 scripts/kie.py preis kling-3-0 --stufe 1080p --sekunden 6      # je Sekunde
python3 scripts/kie.py preis elevenlabs --zeichen 1800                 # je 1.000 Zeichen
python3 scripts/kie.py preis google/gemini-2-5-pro-tts --sekunden 40   # Sprache
python3 scripts/kie.py modelle                                        # alles auflisten
```

Mehrere Modelle in einem Aufruf ergeben die Vergleichstabelle für Fall A.
200 Credits = 1 US-Dollar, ein Credit rund 0,0043 €. Beträge mit Komma.

Guthaben vor einem größeren Lauf:

```bash
python3 scripts/kie.py guthaben
```

## Erzeugen

Ein Aufruf legt den Auftrag an, fragt alle acht Sekunden nach, lädt das Ergebnis
und schreibt `meta.json` fort:

```bash
python3 scripts/kie.py erzeuge \
  --modell gpt-image-2-text-to-image \
  --prompt "Ein Leuchtturm im Nebel, Morgenlicht" \
  --setze image_size=2K \
  --projekt leuchtturm
```

Video und Sprache genauso, nur mit anderen Feldern:

```bash
python3 scripts/kie.py erzeuge --modell veo3.1 \
  --prompt "A lighthouse in drifting fog at dawn, slow push-in" \
  --setze duration=8 --setze model_variant=quality --projekt leuchtturm --typ video

python3 scripts/kie.py erzeuge --modell google/gemini-2-5-pro-tts \
  --prompt "Guten Morgen.\n\nHier spricht der Leuchtturmwärter." \
  --projekt leuchtturm --typ audio
```

`--setze schluessel=wert` füllt beliebige Felder des `input`-Objekts; Werte werden
als JSON gelesen, sonst als Text. Ganze Objekte per `--eingabe '{"…": …}'` oder
`--eingabe @datei.json`. Welche Felder ein Modell erwartet, steht auf kie.ai —
`kie.py` bügelt nur die bekannten Fallen glatt und warnt bei deutschen
Video-Prompts.

Dauert es lange, bricht `erzeuge` nach 30 Minuten ab, aber die `taskId` bleibt
gültig:

```bash
python3 scripts/kie.py status --auftrag <taskId>
python3 scripts/kie.py lade --auftrag <taskId> --projekt leuchtturm \
  --modell veo3.1 --prompt "…"
```

## Ablage und Protokoll

Alles landet in `~/Medien/JJJJ-MM-TT-projektname/`, durchnummeriert als `01.png`,
`02.mp4` und so weiter. **Die Ergebnis-URLs von kie.ai verfallen nach 24 Stunden**
— also immer mit `--projekt` arbeiten, damit sofort geladen wird.

Der Download schreibt `meta.json` im Zielordner fort — angehängt, nie
überschrieben — mit Zeitstempel, Dateiname, Typ, Modell, Prompt, den **tatsächlich
abgerechneten** Credits aus `data.creditsConsumed` und dem Euro-Betrag. Das
passiert im Download-Schritt selbst, damit es nicht vergessen werden kann. Nie von
Hand nachtragen und nie am Download vorbei laden.

## Galerie

```bash
python3 scripts/galerie.py                # baut ~/Medien/galerie.html und öffnet sie
python3 scripts/galerie.py --nooeffnen    # nur bauen
```

Liest alle `meta.json`, zeigt oben die Gesamtsumme aus Anzahl, Credits und Euro,
darunter ein Raster mit Vorschau, Prompt, Modell, Kosten, Projekt und Datum.
Filter nach Typ, Modell und Freitext laufen im Browser. Vorschaubilder für Videos
zieht einmalig `ffmpeg`; fehlt es, bleibt die Kachel ohne Standbild. Einträge,
deren Datei nicht mehr da ist, fallen still raus.

Nach einem größeren Lauf einmal laufen lassen — das ist die einzige Stelle, an der
man sieht, was das Ganze gekostet hat.

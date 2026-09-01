#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""kie.py — Werkzeug für die kie.ai-API (Bild, Video, Sprache).

Nur Standardbibliothek. Der Schlüssel kommt immer aus der Umgebungsvariable
KIE_API_KEY, niemals aus einer Datei.

Unterbefehle:
  preis      rechnet Kosten aus, ohne die API zu berufen
  modelle    listet die bekannten Modelle auf
  guthaben   fragt das Restguthaben ab
  erzeuge    legt einen Auftrag an, wartet auf das Ergebnis, lädt es auf Wunsch
  status     fragt einen laufenden Auftrag einmal ab
  lade       lädt Ergebnisse herunter und schreibt meta.json fort
"""

import argparse
import json
import os
import re
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import deque
from datetime import datetime
from pathlib import Path

BASIS = "https://api.kie.ai/api/v1"

# 200 Credits = 1 US-Dollar. Ein Credit sind rund 0,0043 Euro.
EUR_JE_CREDIT = 0.0043
CREDITS_JE_DOLLAR = 200

# Rate Limit der API: 20 Anfragen je 10 Sekunden.
LIMIT_ANFRAGEN = 20
LIMIT_FENSTER = 10.0

# Abfrageabstand beim Warten auf ein Ergebnis.
ABFRAGE_ABSTAND = 8

# Wiederholbare Fehlercodes, höchstens fünf Versuche mit wachsender Pause.
WIEDERHOLBAR = (429, 500, 502, 503)
MAX_VERSUCHE = 5

MEDIEN_WURZEL = Path(os.environ.get("MEDIEN_WURZEL", "~/Medien")).expanduser()


# ---------------------------------------------------------------------------
# Modelle und Preise
# ---------------------------------------------------------------------------
# "stufen" sind je nach Modell Auflösungen (1K/2K/4K, 480p/720p/1080p) oder
# Qualitätsvarianten (lite/fast/quality). "abrechnung" sagt, womit der
# Stufenpreis multipliziert wird.

MODELLE = {
    # --- Bild: Preis je Bild -------------------------------------------------
    "gpt-image-2-text-to-image": {
        "name": "GPT Image 2 (Text→Bild)",
        "art": "bild",
        "abrechnung": "je_bild",
        "stufenart": "aufloesung",
        "stufen": {"1K": 6, "2K": 10, "4K": 16},
        "standard": "1K",
    },
    "gpt-image-2-image-to-image": {
        "name": "GPT Image 2 (Bild→Bild)",
        "art": "bild",
        "abrechnung": "je_bild",
        "stufenart": "aufloesung",
        "stufen": {"1K": 6, "2K": 10, "4K": 16},
        "standard": "1K",
    },
    "nano-banana-2": {
        "name": "Nano Banana 2",
        "art": "bild",
        "abrechnung": "je_bild",
        "stufenart": "aufloesung",
        "stufen": {"1K": 8, "2K": 12, "4K": 18},
        "standard": "1K",
    },
    "google/nano-banana-pro": {
        "name": "Nano Banana Pro",
        "art": "bild",
        "abrechnung": "je_bild",
        "stufenart": "aufloesung",
        "stufen": {"1K": 18, "2K": 18, "4K": 24},
        "standard": "2K",
    },
    "nano-banana-2-lite": {
        "name": "Nano Banana 2 Lite",
        "art": "bild",
        "abrechnung": "je_bild",
        "stufenart": "aufloesung",
        "stufen": {"1K": 4},
        "standard": "1K",
    },
    "google/nano-banana-edit": {
        "name": "Nano Banana Edit",
        "art": "bild",
        "abrechnung": "je_bild",
        "stufenart": "aufloesung",
        "stufen": {"standard": 4},
        "standard": "standard",
    },
    "seedream-5-pro": {
        "name": "Seedream 5 Pro",
        "art": "bild",
        "abrechnung": "je_bild",
        "stufenart": "aufloesung",
        "stufen": {"1K": 7, "2K": 14},
        "standard": "1K",
    },

    # --- Video: Preis je Sekunde --------------------------------------------
    "grok-imagine/image-to-video": {
        "name": "Grok Imagine (Bild→Video)",
        "art": "video",
        "abrechnung": "je_sekunde",
        "stufenart": "aufloesung",
        "stufen": {"480p": 2.4, "720p": 4.5, "1080p": 8},
        "standard": "720p",
        "hinweis": "duration ist hier ein TEXT, etwa \"8\".",
    },
    "bytedance/seedance-1.5-pro": {
        "name": "Seedance 1.5 Pro",
        "art": "video",
        "abrechnung": "je_sekunde",
        "stufenart": "aufloesung",
        "stufen": {"720p": 3.5, "1080p": 7.5},
        "standard": "720p",
        "hinweis": "erzeugt keinen Ton.",
    },
    "kling-3-0": {
        "name": "Kling 3.0",
        "art": "video",
        "abrechnung": "je_sekunde",
        "stufenart": "aufloesung",
        "stufen": {"720p": 14, "1080p": 18},
        "standard": "720p",
    },
    "bytedance/seedance-2": {
        "name": "Seedance 2",
        "art": "video",
        "abrechnung": "je_sekunde",
        "stufenart": "aufloesung",
        "stufen": {"720p": 41, "1080p": 102},
        "standard": "720p",
    },

    # --- Video: Preis je Clip ------------------------------------------------
    "veo3.1": {
        "name": "Veo 3.1",
        "art": "video",
        "abrechnung": "je_clip",
        "stufenart": "variante",
        "stufen": {"lite": 35, "fast": 65, "quality": 255},
        "standard": "fast",
        "erlaubte_sekunden": [4, 6, 8],
        "aufloesung_fest": "1080p",
        "hinweis": "duration ist eine ZAHL und nur 4, 6 oder 8 erlaubt.",
    },

    # --- Ton ------------------------------------------------------------------
    "google/gemini-2-5-pro-tts": {
        "name": "Gemini 2.5 Pro TTS",
        "art": "audio",
        "abrechnung": "je_sekunde",
        "stufenart": "variante",
        # rund 4 Credits für 40 Sekunden Sprache
        "stufen": {"standard": 0.1},
        "standard": "standard",
        "ungefaehr": True,
        "hinweis": "mehrere dialogue_turns werden abgeschnitten — EIN Text nutzen.",
    },
    "elevenlabs-multilingual-v2": {
        "name": "ElevenLabs Multilingual v2",
        "art": "audio",
        "abrechnung": "je_1000_zeichen",
        "stufenart": "variante",
        "stufen": {"standard": 12},
        "standard": "standard",
    },
}

# Kurznamen, damit man nicht die volle Kennung tippen muss.
KURZNAMEN = {
    "gpt-image-2": "gpt-image-2-text-to-image",
    "gpt": "gpt-image-2-text-to-image",
    "nano-banana-pro": "google/nano-banana-pro",
    "nano-banana-edit": "google/nano-banana-edit",
    "nano-banana-lite": "nano-banana-2-lite",
    "seedream": "seedream-5-pro",
    "grok": "grok-imagine/image-to-video",
    "grok-imagine": "grok-imagine/image-to-video",
    "seedance": "bytedance/seedance-1.5-pro",
    "seedance-1.5-pro": "bytedance/seedance-1.5-pro",
    "seedance-2": "bytedance/seedance-2",
    "kling": "kling-3-0",
    "veo": "veo3.1",
    "veo3": "veo3.1",
    "veo-3.1": "veo3.1",
    "gemini-tts": "google/gemini-2-5-pro-tts",
    "tts": "google/gemini-2-5-pro-tts",
    "elevenlabs": "elevenlabs-multilingual-v2",
}


class KieFehler(Exception):
    """Fehler der API oder der Bedienung."""


def modell_finden(bezeichnung):
    """Löst Kennung oder Kurzname zu einem Modell auf."""
    schluessel = bezeichnung.strip()
    if schluessel in MODELLE:
        return schluessel
    klein = schluessel.lower()
    if klein in MODELLE:
        return klein
    if klein in KURZNAMEN:
        return KURZNAMEN[klein]
    treffer = [k for k in MODELLE if klein in k.lower()]
    if len(treffer) == 1:
        return treffer[0]
    if len(treffer) > 1:
        raise KieFehler(
            "Mehrdeutig: »%s« passt auf %s" % (bezeichnung, ", ".join(sorted(treffer)))
        )
    raise KieFehler(
        "Unbekanntes Modell: »%s«. »kie.py modelle« zeigt die bekannten." % bezeichnung
    )


# ---------------------------------------------------------------------------
# Zahlen und Geld auf Deutsch
# ---------------------------------------------------------------------------

def zahl_text(wert, dezimalstellen=2):
    """Formatiert eine Zahl deutsch: Punkt als Tausender, Komma als Dezimal."""
    text = ("{:,.%df}" % dezimalstellen).format(float(wert))
    return text.replace(",", "\x00").replace(".", ",").replace("\x00", ".")


def credits_text(credits):
    """Credits ohne unnötige Nachkommastellen."""
    if abs(credits - round(credits)) < 1e-9:
        return zahl_text(round(credits), 0)
    return zahl_text(credits, 1)


def eur_betrag(credits):
    """Rechnet Credits in Euro um."""
    return round(credits * EUR_JE_CREDIT, 3)


def eur_text(credits):
    """Euro-Betrag als deutscher Text, kleine Beträge feiner aufgelöst."""
    betrag = credits * EUR_JE_CREDIT
    stellen = 3 if 0 < abs(betrag) < 1 else 2
    return zahl_text(betrag, stellen) + " €"


# ---------------------------------------------------------------------------
# Preisrechnung
# ---------------------------------------------------------------------------

def preis_rechnen(modell, anzahl=1, stufe=None, sekunden=None, zeichen=None):
    """Rechnet die Kosten eines Auftrags aus. Gibt ein Wörterbuch zurück."""
    kennung = modell_finden(modell)
    m = MODELLE[kennung]

    gewaehlt = stufe or m["standard"]
    if gewaehlt not in m["stufen"]:
        # Auflösungen tolerant nehmen: 1k, 1080P, …
        passend = {s.lower(): s for s in m["stufen"]}
        if gewaehlt.lower() in passend:
            gewaehlt = passend[gewaehlt.lower()]
        else:
            raise KieFehler(
                "%s kennt die Stufe »%s« nicht. Möglich: %s"
                % (m["name"], gewaehlt, ", ".join(m["stufen"]))
            )

    stueckpreis = m["stufen"][gewaehlt]
    anzahl = max(1, int(anzahl))
    warnungen = []

    if m["abrechnung"] == "je_bild":
        einheiten = anzahl
        grundlage = "%d Bild%s" % (anzahl, "er" if anzahl != 1 else "")
        credits = stueckpreis * anzahl

    elif m["abrechnung"] == "je_sekunde":
        if sekunden is None:
            raise KieFehler(
                "%s rechnet je Sekunde — bitte --sekunden angeben." % m["name"]
            )
        sekunden = float(sekunden)
        einheiten = sekunden * anzahl
        grundlage = "%s s" % credits_text(sekunden)
        if anzahl != 1:
            grundlage += " × %d" % anzahl
        credits = stueckpreis * sekunden * anzahl

    elif m["abrechnung"] == "je_clip":
        if sekunden is not None:
            sekunden = int(round(float(sekunden)))
            erlaubt = m.get("erlaubte_sekunden")
            if erlaubt and sekunden not in erlaubt:
                warnungen.append(
                    "%s erlaubt nur %s Sekunden — %d s geht nicht durch."
                    % (m["name"], " / ".join(str(s) for s in erlaubt), sekunden)
                )
        einheiten = anzahl
        grundlage = "%d Clip%s" % (anzahl, "s" if anzahl != 1 else "")
        if sekunden:
            grundlage += " à %d s" % sekunden
        credits = stueckpreis * anzahl

    elif m["abrechnung"] == "je_1000_zeichen":
        if zeichen is None:
            raise KieFehler(
                "%s rechnet je 1.000 Zeichen — bitte --zeichen angeben." % m["name"]
            )
        zeichen = int(zeichen)
        einheiten = zeichen * anzahl / 1000.0
        grundlage = "%s Zeichen" % zahl_text(zeichen, 0)
        if anzahl != 1:
            grundlage += " × %d" % anzahl
        credits = stueckpreis * zeichen * anzahl / 1000.0

    else:
        raise KieFehler("Unbekannte Abrechnungsart: %s" % m["abrechnung"])

    credits = round(credits, 4)
    if m.get("hinweis"):
        warnungen.append(m["hinweis"])

    stufentext = gewaehlt if gewaehlt != "standard" else ""
    if m.get("aufloesung_fest"):
        stufentext = "%s %s" % (gewaehlt, m["aufloesung_fest"])

    return {
        "kennung": kennung,
        "name": m["name"],
        "art": m["art"],
        "stufe": gewaehlt,
        "stufentext": stufentext,
        "grundlage": grundlage,
        "einheiten": round(einheiten, 4),
        "stueckpreis": stueckpreis,
        "credits": credits,
        "eur": eur_betrag(credits),
        "ungefaehr": bool(m.get("ungefaehr")),
        "warnungen": warnungen,
    }


def preis_zeile(p):
    """Eine Zeile, wie sie dem Nutzer gezeigt wird."""
    teile = [p["name"]]
    if p["stufentext"]:
        teile.append(p["stufentext"])
    teile.append(p["grundlage"])
    etwa = "rund " if p["ungefaehr"] else ""
    return "%s: %s%s Credits · %s%s" % (
        ", ".join(teile), etwa, credits_text(p["credits"]), etwa, eur_text(p["credits"])
    )


# ---------------------------------------------------------------------------
# HTTP mit Rate Limit und Wiederholungen
# ---------------------------------------------------------------------------

_ANFRAGEZEITEN = deque()


def _rate_limit_beachten():
    """Hält 20 Anfragen je 10 Sekunden ein."""
    while True:
        jetzt = time.monotonic()
        while _ANFRAGEZEITEN and jetzt - _ANFRAGEZEITEN[0] > LIMIT_FENSTER:
            _ANFRAGEZEITEN.popleft()
        if len(_ANFRAGEZEITEN) < LIMIT_ANFRAGEN:
            _ANFRAGEZEITEN.append(jetzt)
            return
        time.sleep(LIMIT_FENSTER - (jetzt - _ANFRAGEZEITEN[0]) + 0.05)


def _ssl_kontext():
    """Nutzt ein eigenes Wurzelzertifikat, falls die Umgebung eines nennt."""
    bundle = os.environ.get("SSL_CERT_FILE") or os.environ.get("REQUESTS_CA_BUNDLE")
    if bundle and os.path.exists(bundle):
        return ssl.create_default_context(cafile=bundle)
    return ssl.create_default_context()


def _schluessel():
    schluessel = os.environ.get("KIE_API_KEY", "").strip()
    if not schluessel:
        raise KieFehler(
            "KIE_API_KEY ist nicht gesetzt. Der Schlüssel kommt aus der Umgebung:\n"
            "  export KIE_API_KEY=\"…\""
        )
    return schluessel


def anfrage(methode, pfad, daten=None, basis=BASIS):
    """Ruft die API auf und gibt den geparsten Rumpf zurück."""
    url = pfad if pfad.startswith("http") else basis + pfad
    rumpf = json.dumps(daten).encode("utf-8") if daten is not None else None
    kontext = _ssl_kontext()
    pause = 2

    for versuch in range(1, MAX_VERSUCHE + 1):
        _rate_limit_beachten()
        bitte = urllib.request.Request(url, data=rumpf, method=methode)
        bitte.add_header("Authorization", "Bearer " + _schluessel())
        bitte.add_header("Accept", "application/json")
        if rumpf is not None:
            bitte.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(bitte, timeout=120, context=kontext) as antwort:
                text = antwort.read().decode("utf-8", "replace")
            break
        except urllib.error.HTTPError as fehler:
            text = fehler.read().decode("utf-8", "replace")
            if fehler.code == 402:
                raise KieFehler(
                    "HTTP 402 — das Guthaben ist leer. Auf kie.ai nachladen."
                )
            if fehler.code in WIEDERHOLBAR and versuch < MAX_VERSUCHE:
                warte = fehler.headers.get("Retry-After")
                schlaf = float(warte) if (warte or "").strip().isdigit() else pause
                print(
                    "HTTP %d — Versuch %d von %d, warte %s s …"
                    % (fehler.code, versuch, MAX_VERSUCHE, credits_text(schlaf)),
                    file=sys.stderr,
                )
                time.sleep(schlaf)
                pause *= 2
                continue
            raise KieFehler("HTTP %d von der API: %s" % (fehler.code, text[:500]))
        except urllib.error.URLError as fehler:
            if versuch < MAX_VERSUCHE:
                print(
                    "Netzfehler (%s) — Versuch %d von %d, warte %d s …"
                    % (fehler.reason, versuch, MAX_VERSUCHE, pause),
                    file=sys.stderr,
                )
                time.sleep(pause)
                pause *= 2
                continue
            raise KieFehler("Netzfehler: %s" % fehler.reason)
    else:
        raise KieFehler("Nach %d Versuchen keine Antwort." % MAX_VERSUCHE)

    try:
        antwort = json.loads(text)
    except ValueError:
        raise KieFehler("Antwort war kein JSON: %s" % text[:500])

    if antwort.get("code") != 200:
        raise KieFehler(
            "Die API meldet code %s: %s"
            % (antwort.get("code"), antwort.get("msg") or antwort.get("message") or text[:300])
        )
    return antwort


# ---------------------------------------------------------------------------
# Aufträge
# ---------------------------------------------------------------------------

DEUTSCHE_WOERTER = {
    "der", "die", "das", "und", "mit", "ein", "eine", "einen", "auf", "von",
    "für", "nicht", "sich", "im", "am", "dem", "den", "des", "ist", "sind",
    "wird", "über", "durch", "bei", "aus", "vor", "nach", "zwischen",
}


def _wirkt_deutsch(text):
    woerter = set(re.findall(r"[a-zäöüß]+", (text or "").lower()))
    return len(woerter & DEUTSCHE_WOERTER) >= 2


def eingabe_pruefen(kennung, eingabe):
    """Bügelt die bekannten Fallen glatt und warnt, wo nötig."""
    eingabe = dict(eingabe)

    # Falle: bei grok-imagine ist duration ein Text, bei veo3.1 eine Zahl.
    if "duration" in eingabe:
        if kennung.startswith("grok-imagine") and not isinstance(eingabe["duration"], str):
            eingabe["duration"] = str(int(float(eingabe["duration"])))
            print("Hinweis: duration für grok-imagine als Text gesetzt.", file=sys.stderr)
        if kennung == "veo3.1":
            dauer = int(float(eingabe["duration"]))
            erlaubt = MODELLE["veo3.1"]["erlaubte_sekunden"]
            if dauer not in erlaubt:
                raise KieFehler(
                    "veo3.1 erlaubt nur %s Sekunden, nicht %d."
                    % (" / ".join(str(s) for s in erlaubt), dauer)
                )
            eingabe["duration"] = dauer

    # Falle: Videomodelle verstehen nur englische Prompts.
    if MODELLE.get(kennung, {}).get("art") == "video" and _wirkt_deutsch(eingabe.get("prompt")):
        print(
            "Achtung: der Prompt wirkt deutsch. Videomodelle ignorieren das — "
            "bitte auf Englisch schreiben.",
            file=sys.stderr,
        )

    # Falle: gemini-tts schneidet mehrere dialogue_turns ab.
    if kennung == "google/gemini-2-5-pro-tts":
        turns = eingabe.get("dialogue_turns")
        if isinstance(turns, list) and len(turns) > 1:
            print(
                "Achtung: gemini-2-5-pro-tts liefert bei mehreren dialogue_turns nur "
                "die ersten neun Sekunden. Besser EIN Text mit Leerzeilen.",
                file=sys.stderr,
            )
    return eingabe


def auftrag_anlegen(kennung, eingabe):
    """POST /jobs/createTask — gibt die taskId zurück."""
    antwort = anfrage("POST", "/jobs/createTask", {"model": kennung, "input": eingabe})
    aufgabe = (antwort.get("data") or {}).get("taskId")
    if not aufgabe:
        raise KieFehler("Die Antwort enthielt keine taskId: %s" % json.dumps(antwort)[:300])
    return aufgabe


def auftrag_abfragen(aufgabe):
    """GET /jobs/recordInfo — gibt data zurück."""
    pfad = "/jobs/recordInfo?taskId=" + urllib.parse.quote(str(aufgabe))
    return anfrage("GET", pfad).get("data") or {}


def ergebnis_lesen(daten):
    """Holt resultUrls aus data.resultJson — das ist ein JSON-STRING."""
    roh = daten.get("resultJson")
    if not roh:
        return []
    if isinstance(roh, str):
        try:
            roh = json.loads(roh)
        except ValueError:
            raise KieFehler("resultJson ließ sich nicht parsen: %s" % roh[:300])
    urls = roh.get("resultUrls") or roh.get("result_urls") or []
    if isinstance(urls, str):
        urls = [urls]
    return list(urls)


def auf_ergebnis_warten(aufgabe, hoechstens=1800, leise=False):
    """Fragt alle acht Sekunden ab, bis success oder fail."""
    beginn = time.monotonic()
    letzter = None
    while True:
        daten = auftrag_abfragen(aufgabe)
        zustand = (daten.get("state") or "").lower()
        if zustand != letzter and not leise:
            print("  %s … (%d s)" % (zustand or "unbekannt", time.monotonic() - beginn),
                  file=sys.stderr)
            letzter = zustand
        if zustand == "success":
            return daten
        if zustand in ("fail", "failed", "error"):
            raise KieFehler(
                "Der Auftrag ist fehlgeschlagen: %s"
                % (daten.get("failMsg") or daten.get("failCode") or "ohne Angabe")
            )
        if time.monotonic() - beginn > hoechstens:
            raise KieFehler(
                "Nach %d s noch kein Ergebnis. taskId %s bleibt gültig — "
                "später »kie.py status --auftrag %s« versuchen."
                % (hoechstens, aufgabe, aufgabe)
            )
        time.sleep(ABFRAGE_ABSTAND)


# ---------------------------------------------------------------------------
# Ablage und Protokoll
# ---------------------------------------------------------------------------

BILD_ENDUNGEN = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp"}
VIDEO_ENDUNGEN = {".mp4", ".mov", ".webm", ".m4v", ".mkv"}
AUDIO_ENDUNGEN = {".wav", ".mp3", ".m4a", ".ogg", ".flac", ".aac"}


def projektordner(projekt, datum=None, wurzel=None):
    """~/Medien/JJJJ-MM-TT-projektname/"""
    wurzel = Path(wurzel).expanduser() if wurzel else MEDIEN_WURZEL
    tag = datum or datetime.now().strftime("%Y-%m-%d")
    sauber = re.sub(r"[^0-9A-Za-zÄÖÜäöüß._-]+", "-", projekt.strip()).strip("-") or "ohne-namen"
    ordner = wurzel / ("%s-%s" % (tag, sauber))
    ordner.mkdir(parents=True, exist_ok=True)
    return ordner


def _endung(url, art):
    endung = os.path.splitext(urllib.parse.urlparse(url).path)[1].lower()
    if endung and len(endung) <= 5:
        return endung
    return {"bild": ".png", "video": ".mp4", "audio": ".mp3"}.get(art, ".bin")


def _art_aus_endung(endung, ersatz="bild"):
    if endung in BILD_ENDUNGEN:
        return "bild"
    if endung in VIDEO_ENDUNGEN:
        return "video"
    if endung in AUDIO_ENDUNGEN:
        return "audio"
    return ersatz


def _naechste_nummer(ordner):
    hoechste = 0
    for eintrag in ordner.iterdir():
        treffer = re.match(r"^(\d+)", eintrag.name)
        if treffer:
            hoechste = max(hoechste, int(treffer.group(1)))
    return hoechste + 1


def meta_fortschreiben(ordner, eintraege):
    """Hängt an meta.json an — niemals überschreiben."""
    pfad = ordner / "meta.json"
    bestand = []
    if pfad.exists():
        try:
            geladen = json.loads(pfad.read_text(encoding="utf-8"))
            if isinstance(geladen, list):
                bestand = geladen
            else:
                print("meta.json war keine Liste — der Altbestand bleibt unberührt.",
                      file=sys.stderr)
        except ValueError:
            sicherung = pfad.with_suffix(".json.kaputt")
            pfad.rename(sicherung)
            print("meta.json war beschädigt, gesichert als %s." % sicherung.name,
                  file=sys.stderr)
    bestand.extend(eintraege)
    pfad.write_text(
        json.dumps(bestand, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return pfad


def _credits_verteilen(gesamt, anzahl):
    """Verteilt die abgerechneten Credits auf die Dateien, ohne Rest zu verlieren."""
    if not gesamt or anzahl <= 0:
        return [0] * max(anzahl, 0)
    anteil = round(float(gesamt) / anzahl, 3)
    werte = [anteil] * anzahl
    werte[-1] = round(float(gesamt) - anteil * (anzahl - 1), 3)
    return [int(w) if abs(w - round(w)) < 1e-9 else w for w in werte]


def herunterladen(urls, ordner, modell, prompt, credits_gesamt, art=None):
    """Lädt die Ergebnisse und schreibt dabei meta.json fort.

    Das Protokoll entsteht IM Download-Schritt, damit es nicht vergessen wird.
    """
    kontext = _ssl_kontext()
    nummer = _naechste_nummer(ordner)
    anteile = _credits_verteilen(credits_gesamt, len(urls))
    eintraege = []
    dateien = []

    for lauf, url in enumerate(urls):
        vermutet = art or _art_aus_endung(_endung(url, "bild"))
        endung = _endung(url, vermutet)
        typ = art or _art_aus_endung(endung)
        name = "%02d%s" % (nummer + lauf, endung)
        ziel = ordner / name

        bitte = urllib.request.Request(url, headers={"User-Agent": "media-skill/1.0"})
        with urllib.request.urlopen(bitte, timeout=300, context=kontext) as antwort:
            ziel.write_bytes(antwort.read())

        credits = anteile[lauf]
        eintraege.append({
            "zeit": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "datei": name,
            "typ": typ,
            "modell": modell,
            "prompt": prompt or "",
            "credits": credits,
            "eur": eur_betrag(credits),
        })
        dateien.append(ziel)
        print("  %s  (%s KiB)" % (ziel, zahl_text(ziel.stat().st_size / 1024, 0)))

    meta_fortschreiben(ordner, eintraege)
    return dateien


# ---------------------------------------------------------------------------
# Unterbefehle
# ---------------------------------------------------------------------------

def befehl_preis(args):
    ergebnisse = []
    for modell in args.modell:
        ergebnisse.append(preis_rechnen(
            modell,
            anzahl=args.anzahl,
            stufe=args.stufe,
            sekunden=args.sekunden,
            zeichen=args.zeichen,
        ))

    if args.json:
        print(json.dumps(ergebnisse, ensure_ascii=False, indent=2))
        return 0

    if len(ergebnisse) == 1:
        p = ergebnisse[0]
        print(preis_zeile(p))
        for warnung in p["warnungen"]:
            print("  Hinweis: %s" % warnung)
        return 0

    # Vergleichstabelle für den Beratungsfall.
    kopf = ("Modell", "Stufe", "Umfang", "Credits", "Euro")
    zeilen = [(
        p["name"],
        p["stufentext"] or "—",
        p["grundlage"],
        credits_text(p["credits"]),
        eur_text(p["credits"]),
    ) for p in ergebnisse]
    breiten = [max(len(kopf[i]), *(len(z[i]) for z in zeilen)) for i in range(5)]
    strich = "  ".join("-" * b for b in breiten)
    print("  ".join(kopf[i].ljust(breiten[i]) for i in range(5)))
    print(strich)
    for zeile in zeilen:
        print("  ".join(zeile[i].ljust(breiten[i]) for i in range(5)))
    gesamt = sum(p["credits"] for p in ergebnisse)
    print(strich)
    print("(einzeln gerechnet; alle zusammen wären %s Credits · %s)"
          % (credits_text(gesamt), eur_text(gesamt)))
    for p in ergebnisse:
        for warnung in p["warnungen"]:
            print("Hinweis %s: %s" % (p["name"], warnung))
    return 0


def befehl_modelle(args):
    for art in ("bild", "video", "audio"):
        passend = [(k, m) for k, m in MODELLE.items() if m["art"] == art]
        if not passend:
            continue
        print("%s:" % art.capitalize())
        for kennung, m in passend:
            einheit = {
                "je_bild": "je Bild",
                "je_sekunde": "je Sekunde",
                "je_clip": "je Clip",
                "je_1000_zeichen": "je 1.000 Zeichen",
            }[m["abrechnung"]]
            stufen = ", ".join(
                "%s %s" % (s, credits_text(p)) if s != "standard" else credits_text(p)
                for s, p in m["stufen"].items()
            )
            print("  %-30s %-16s %s Credits" % (kennung, einheit, stufen))
        print()
    return 0


def befehl_guthaben(args):
    antwort = anfrage("GET", "/chat/credit")
    daten = antwort.get("data")
    credits = daten if isinstance(daten, (int, float)) else (
        (daten or {}).get("credits") if isinstance(daten, dict) else None
    )
    if credits is None:
        print(json.dumps(antwort, ensure_ascii=False, indent=2))
        return 0
    print("Guthaben: %s Credits · %s (rund %s $)"
          % (credits_text(credits), eur_text(credits),
             zahl_text(credits / CREDITS_JE_DOLLAR, 2)))
    return 0


def _eingabe_sammeln(args):
    eingabe = {}
    if args.eingabe:
        text = args.eingabe
        if text.startswith("@"):
            text = Path(text[1:]).expanduser().read_text(encoding="utf-8")
        eingabe.update(json.loads(text))
    if args.eingabe_datei:
        eingabe.update(json.loads(
            Path(args.eingabe_datei).expanduser().read_text(encoding="utf-8")))
    if args.prompt:
        eingabe["prompt"] = args.prompt
    for paar in args.setze or []:
        if "=" not in paar:
            raise KieFehler("--setze braucht die Form schluessel=wert, nicht »%s«." % paar)
        schluessel, wert = paar.split("=", 1)
        try:
            eingabe[schluessel] = json.loads(wert)
        except ValueError:
            eingabe[schluessel] = wert
    return eingabe


def befehl_erzeuge(args):
    kennung = modell_finden(args.modell)
    eingabe = eingabe_pruefen(kennung, _eingabe_sammeln(args))
    if not eingabe:
        raise KieFehler("Ohne Eingabe geht nichts — --prompt oder --eingabe angeben.")

    print("Auftrag an %s …" % MODELLE[kennung]["name"], file=sys.stderr)
    aufgabe = auftrag_anlegen(kennung, eingabe)
    print("taskId: %s" % aufgabe)

    if not args.warten:
        print("(nicht gewartet — später »kie.py status --auftrag %s«)" % aufgabe)
        return 0

    daten = auf_ergebnis_warten(aufgabe, hoechstens=args.zeitgrenze)
    urls = ergebnis_lesen(daten)
    credits = daten.get("creditsConsumed")
    print("Fertig: %d Ergebnis%s, abgerechnet %s Credits · %s"
          % (len(urls), "se" if len(urls) != 1 else "",
             credits_text(credits or 0), eur_text(credits or 0)))
    for url in urls:
        print("  %s" % url)

    if args.projekt:
        ordner = projektordner(args.projekt, wurzel=args.wurzel)
        print("Lade nach %s …" % ordner)
        herunterladen(urls, ordner, kennung, eingabe.get("prompt", ""), credits, args.typ)
    else:
        print("Achtung: die URLs verfallen nach 24 Stunden. "
              "Mit --projekt wird sofort geladen und protokolliert.", file=sys.stderr)
    return 0


def befehl_status(args):
    daten = auftrag_abfragen(args.auftrag)
    zustand = daten.get("state") or "unbekannt"
    print("Zustand: %s" % zustand)
    if daten.get("creditsConsumed") is not None:
        print("Credits: %s · %s" % (credits_text(daten["creditsConsumed"]),
                                    eur_text(daten["creditsConsumed"])))
    for url in ergebnis_lesen(daten):
        print("  %s" % url)
    if daten.get("failMsg"):
        print("Fehlermeldung: %s" % daten["failMsg"])
    return 0


def befehl_lade(args):
    if not args.auftrag and not args.url:
        raise KieFehler("Bitte --auftrag oder --url angeben.")

    modell = args.modell
    prompt = args.prompt or ""
    credits = args.credits
    urls = list(args.url or [])

    if args.auftrag:
        daten = auftrag_abfragen(args.auftrag)
        zustand = (daten.get("state") or "").lower()
        if zustand != "success":
            raise KieFehler("Der Auftrag steht auf »%s«, es gibt noch nichts zu laden."
                            % (zustand or "unbekannt"))
        urls.extend(ergebnis_lesen(daten))
        if credits is None:
            credits = daten.get("creditsConsumed")
        modell = modell or daten.get("model") or "unbekannt"

    if not urls:
        raise KieFehler("Keine Ergebnis-URLs gefunden.")

    ordner = projektordner(args.projekt, wurzel=args.wurzel)
    dateien = herunterladen(urls, ordner, modell or "unbekannt", prompt, credits, args.typ)
    print("%d Datei%s in %s, meta.json fortgeschrieben."
          % (len(dateien), "en" if len(dateien) != 1 else "", ordner))
    return 0


def hauptprogramm(argumente=None):
    zerleger = argparse.ArgumentParser(
        prog="kie.py",
        description="Bilder, Videos und Sprache über die kie.ai-API.",
    )
    unter = zerleger.add_subparsers(dest="befehl", required=True)

    p = unter.add_parser("preis", help="Kosten ausrechnen, ohne die API zu berufen")
    p.add_argument("modell", nargs="+", help="ein oder mehrere Modelle (für den Vergleich)")
    p.add_argument("--anzahl", type=int, default=1, help="Stückzahl (Vorgabe 1)")
    p.add_argument("--stufe", "--aufloesung", "--variante", dest="stufe",
                   help="1K/2K/4K, 480p/720p/1080p oder lite/fast/quality")
    p.add_argument("--sekunden", type=float, help="Länge je Clip")
    p.add_argument("--zeichen", type=int, help="Zeichenzahl für Sprachmodelle")
    p.add_argument("--json", action="store_true", help="Ausgabe als JSON")
    p.set_defaults(funktion=befehl_preis)

    p = unter.add_parser("modelle", help="bekannte Modelle auflisten")
    p.set_defaults(funktion=befehl_modelle)

    p = unter.add_parser("guthaben", help="Restguthaben abfragen")
    p.set_defaults(funktion=befehl_guthaben)

    p = unter.add_parser("erzeuge", help="Auftrag anlegen und auf das Ergebnis warten")
    p.add_argument("--modell", required=True)
    p.add_argument("--prompt")
    p.add_argument("--eingabe", help="input als JSON-Text oder @datei.json")
    p.add_argument("--eingabe-datei", dest="eingabe_datei")
    p.add_argument("--setze", action="append", metavar="SCHLUESSEL=WERT")
    p.add_argument("--projekt", help="Projektname; lädt sofort nach ~/Medien und protokolliert")
    p.add_argument("--typ", choices=["bild", "video", "audio"])
    p.add_argument("--wurzel", help="andere Ablage statt ~/Medien")
    p.add_argument("--nicht-warten", dest="warten", action="store_false")
    p.add_argument("--zeitgrenze", type=int, default=1800, help="Sekunden (Vorgabe 1800)")
    p.set_defaults(funktion=befehl_erzeuge, warten=True)

    p = unter.add_parser("status", help="einen laufenden Auftrag abfragen")
    p.add_argument("--auftrag", "--task-id", dest="auftrag", required=True)
    p.set_defaults(funktion=befehl_status)

    p = unter.add_parser("lade", help="Ergebnisse laden und meta.json fortschreiben")
    p.add_argument("--auftrag", "--task-id", dest="auftrag")
    p.add_argument("--url", action="append", help="einzelne URL, mehrfach möglich")
    p.add_argument("--projekt", required=True)
    p.add_argument("--modell")
    p.add_argument("--prompt")
    p.add_argument("--credits", type=float, help="falls nicht aus dem Auftrag ablesbar")
    p.add_argument("--typ", choices=["bild", "video", "audio"])
    p.add_argument("--wurzel", help="andere Ablage statt ~/Medien")
    p.set_defaults(funktion=befehl_lade)

    args = zerleger.parse_args(argumente)
    try:
        return args.funktion(args)
    except KieFehler as fehler:
        print("Fehler: %s" % fehler, file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nAbgebrochen.", file=sys.stderr)
        return 130


if __name__ == "__main__":
    sys.exit(hauptprogramm())

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""galerie.py — baut aus allen meta.json unter ~/Medien eine galerie.html.

Nur Standardbibliothek. Die Seite bindet die Dateien über relative Pfade ein,
nicht als Base64, damit sie auch bei einigen hundert Einträgen flüssig bleibt.
Vorschaubilder für Videos zieht einmalig ffmpeg und legt sie als
»dateiname.thumb.jpg« daneben ab, damit der zweite Aufbau schnell geht.
"""

import argparse
import html
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

WURZEL = Path(os.environ.get("MEDIEN_WURZEL", "~/Medien")).expanduser()
EUR_JE_CREDIT = 0.0043

TYPNAMEN = {"bild": "Bild", "video": "Video", "audio": "Ton"}


# ---------------------------------------------------------------------------
# Zahlen auf Deutsch
# ---------------------------------------------------------------------------

def zahl_text(wert, dezimalstellen=2):
    text = ("{:,.%df}" % dezimalstellen).format(float(wert))
    return text.replace(",", "\x00").replace(".", ",").replace("\x00", ".")


def credits_text(credits):
    if abs(float(credits) - round(float(credits))) < 1e-9:
        return zahl_text(round(float(credits)), 0)
    return zahl_text(credits, 1)


def eur_text(betrag):
    stellen = 3 if 0 < abs(float(betrag)) < 1 else 2
    return zahl_text(betrag, stellen) + " €"


def zeit_text(roh):
    """»2026-08-08T11:20:03« wird zu »08.08.2026, 11:20«."""
    if not roh:
        return ""
    for muster in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%d %H:%M:%S",
                   "%Y-%m-%d"):
        try:
            return datetime.strptime(str(roh)[:26], muster).strftime("%d.%m.%Y, %H:%M")
        except ValueError:
            continue
    return str(roh)


# ---------------------------------------------------------------------------
# Einlesen
# ---------------------------------------------------------------------------

def eintraege_sammeln(wurzel):
    """Liest alle meta.json ein und überspringt Einträge ohne Datei."""
    gefunden = []
    fehlend = 0

    for meta in sorted(wurzel.glob("*/meta.json")):
        projekt = meta.parent.name
        try:
            geladen = json.loads(meta.read_text(encoding="utf-8"))
        except (ValueError, OSError) as fehler:
            print("übersprungen: %s (%s)" % (meta, fehler), file=sys.stderr)
            continue
        if not isinstance(geladen, list):
            print("übersprungen: %s ist keine Liste." % meta, file=sys.stderr)
            continue

        for eintrag in geladen:
            if not isinstance(eintrag, dict) or not eintrag.get("datei"):
                continue
            datei = meta.parent / eintrag["datei"]
            if not datei.exists():
                fehlend += 1
                continue
            credits = eintrag.get("credits") or 0
            euro = eintrag.get("eur")
            if euro is None:
                euro = round(float(credits) * EUR_JE_CREDIT, 3)
            gefunden.append({
                "projekt": projekt,
                "ordner": meta.parent,
                "datei": datei,
                "relativ": "%s/%s" % (projekt, eintrag["datei"]),
                "zeit": eintrag.get("zeit") or "",
                "typ": (eintrag.get("typ") or "bild").lower(),
                "modell": eintrag.get("modell") or "unbekannt",
                "prompt": eintrag.get("prompt") or "",
                "credits": float(credits),
                "eur": float(euro),
            })

    if fehlend:
        print("%d Eintrag/Einträge übersprungen, deren Datei fehlt." % fehlend,
              file=sys.stderr)

    # Neueste zuerst; ohne Zeitangabe zählt das Änderungsdatum der Datei.
    def sortierschluessel(e):
        if e["zeit"]:
            return str(e["zeit"])
        return datetime.fromtimestamp(e["datei"].stat().st_mtime).isoformat()

    gefunden.sort(key=sortierschluessel, reverse=True)
    return gefunden


# ---------------------------------------------------------------------------
# Vorschaubilder für Videos
# ---------------------------------------------------------------------------

_FFMPEG_GEMELDET = False


def vorschaubild(video):
    """Zieht einmalig ein Vorschaubild und merkt es sich als dateiname.thumb.jpg."""
    global _FFMPEG_GEMELDET
    thumb = video.with_name(video.name + ".thumb.jpg")
    if thumb.exists() and thumb.stat().st_mtime >= video.stat().st_mtime:
        return thumb

    werkzeug = shutil.which("ffmpeg")
    if not werkzeug:
        if not _FFMPEG_GEMELDET:
            print("ffmpeg fehlt — Videos bekommen kein Vorschaubild.", file=sys.stderr)
            _FFMPEG_GEMELDET = True
        return None

    for start in ("00:00:01", "00:00:00"):
        befehl = [werkzeug, "-y", "-loglevel", "error", "-ss", start, "-i", str(video),
                  "-frames:v", "1", "-vf", "scale=640:-2", str(thumb)]
        try:
            subprocess.run(befehl, check=True, timeout=60,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except (subprocess.SubprocessError, OSError):
            continue
        if thumb.exists() and thumb.stat().st_size > 0:
            return thumb
    print("kein Vorschaubild für %s" % video.name, file=sys.stderr)
    return None


# ---------------------------------------------------------------------------
# Seite bauen
# ---------------------------------------------------------------------------

STIL = """
:root {
  color-scheme: light dark;
  --grund: #fbfbfa;
  --karte: #ffffff;
  --rand: #e4e2dd;
  --text: #1c1b19;
  --leise: #6f6c66;
  --akzent: #2f6f5e;
  --feld: #ffffff;
}
@media (prefers-color-scheme: dark) {
  :root {
    --grund: #16161a;
    --karte: #1e1e23;
    --rand: #2e2e35;
    --text: #e8e6e1;
    --leise: #9a968e;
    --akzent: #7fc2ad;
    --feld: #24242a;
  }
}
* { box-sizing: border-box; }
body {
  margin: 0;
  background: var(--grund);
  color: var(--text);
  font: 15px/1.5 system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
}
.rahmen { max-width: 1280px; margin: 0 auto; padding: 28px 20px 80px; }

header { border-bottom: 1px solid var(--rand); padding-bottom: 22px; margin-bottom: 22px; }
h1 { font-size: 15px; font-weight: 600; letter-spacing: .06em; text-transform: uppercase;
     color: var(--leise); margin: 0 0 16px; }
.summe { display: flex; flex-wrap: wrap; gap: 40px; }
.summe div { display: flex; flex-direction: column; gap: 2px; }
.summe .wert { font-size: 30px; font-weight: 600; font-variant-numeric: tabular-nums;
               letter-spacing: -.01em; }
.summe .wert.geld { color: var(--akzent); }
.summe .marke { font-size: 12px; color: var(--leise); letter-spacing: .04em; }
.gefiltert { font-size: 12px; color: var(--leise); margin-top: 12px; min-height: 1em; }

.regler { display: flex; flex-wrap: wrap; gap: 10px; align-items: center;
          margin-bottom: 24px; }
button, select, input {
  font: inherit; color: var(--text); background: var(--feld);
  border: 1px solid var(--rand); border-radius: 7px; padding: 7px 12px;
}
button { cursor: pointer; }
button:hover, select:hover { border-color: var(--leise); }
button[aria-pressed="true"] { background: var(--text); color: var(--grund);
                              border-color: var(--text); }
input[type="search"] { flex: 1; min-width: 200px; }
input:focus-visible, select:focus-visible, button:focus-visible {
  outline: 2px solid var(--akzent); outline-offset: 1px;
}

.raster { display: grid; gap: 20px;
          grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); }
.kachel { background: var(--karte); border: 1px solid var(--rand); border-radius: 10px;
          overflow: hidden; display: flex; flex-direction: column; }
.kachel.weg { display: none; }
.buehne { background: #0000000d; aspect-ratio: 4 / 3; display: flex;
          align-items: center; justify-content: center; overflow: hidden; }
@media (prefers-color-scheme: dark) { .buehne { background: #ffffff0d; } }
.buehne img, .buehne video { width: 100%; height: 100%; object-fit: cover; display: block; }
.buehne.ton { aspect-ratio: 16 / 7; flex-direction: column; gap: 12px;
              padding: 14px 16px; }
.buehne.ton .welle { width: 92px; height: 26px; color: var(--leise); opacity: .75; }
.buehne.ton audio { width: 100%; }

.angaben { padding: 12px 14px 14px; display: flex; flex-direction: column; gap: 8px; }
.prompt { margin: 0; display: -webkit-box; -webkit-line-clamp: 3; line-clamp: 3;
          -webkit-box-orient: vertical; overflow: hidden; }
.prompt.leer { color: var(--leise); font-style: italic; }
.zeile { display: flex; flex-wrap: wrap; gap: 4px 8px; font-size: 12.5px;
         color: var(--leise); }
.zeile .modell { color: var(--text); }
.zeile .kosten { font-variant-numeric: tabular-nums; margin-left: auto; }
.nichts { color: var(--leise); padding: 40px 0; }
footer { margin-top: 40px; font-size: 12px; color: var(--leise); }
"""

SKRIPT = """
(function () {
  var kacheln = Array.prototype.slice.call(document.querySelectorAll('.kachel'));
  var knoepfe = Array.prototype.slice.call(document.querySelectorAll('[data-typ-filter]'));
  var auswahl = document.getElementById('modellwahl');
  var suchfeld = document.getElementById('suche');
  var anzeigeAnzahl = document.getElementById('summe-anzahl');
  var anzeigeCredits = document.getElementById('summe-credits');
  var anzeigeEuro = document.getElementById('summe-euro');
  var anzeigeHinweis = document.getElementById('gefiltert');
  var leermeldung = document.getElementById('nichts');
  var typ = 'alle';

  function zahl(wert, stellen) {
    return wert.toLocaleString('de-DE', { minimumFractionDigits: stellen,
                                          maximumFractionDigits: stellen });
  }

  function neuzeichnen() {
    var suche = suchfeld.value.trim().toLowerCase();
    var modell = auswahl.value;
    var anzahl = 0, credits = 0, euro = 0;

    kacheln.forEach(function (kachel) {
      var passt = (typ === 'alle' || kachel.dataset.typ === typ)
        && (modell === 'alle' || kachel.dataset.modell === modell)
        && (suche === '' || kachel.dataset.suche.indexOf(suche) !== -1);
      kachel.classList.toggle('weg', !passt);
      if (passt) {
        anzahl += 1;
        credits += parseFloat(kachel.dataset.credits);
        euro += parseFloat(kachel.dataset.eur);
      }
    });

    anzeigeAnzahl.textContent = zahl(anzahl, 0);
    anzeigeCredits.textContent = zahl(credits, credits % 1 === 0 ? 0 : 1);
    anzeigeEuro.textContent = zahl(euro, (euro > 0 && euro < 1) ? 3 : 2) + ' \\u20ac';
    var eingeschraenkt = typ !== 'alle' || modell !== 'alle' || suche !== '';
    anzeigeHinweis.textContent = eingeschraenkt
      ? 'gefiltert \\u2014 von ' + zahl(kacheln.length, 0) + ' Generierungen insgesamt'
      : '';
    leermeldung.hidden = anzahl !== 0;
  }

  knoepfe.forEach(function (knopf) {
    knopf.addEventListener('click', function () {
      typ = knopf.dataset.typFilter;
      knoepfe.forEach(function (k) {
        k.setAttribute('aria-pressed', String(k === knopf));
      });
      neuzeichnen();
    });
  });
  auswahl.addEventListener('change', neuzeichnen);
  suchfeld.addEventListener('input', neuzeichnen);
  neuzeichnen();
})();
"""


WELLE = ('<svg class="welle" viewBox="0 0 87 26" fill="currentColor" aria-hidden="true">'
         '<rect x="0" y="10" width="3" height="6" rx="1.5"/><rect x="6" y="7" width="3" height="12" rx="1.5"/><rect x="12" y="3" width="3" height="20" rx="1.5"/><rect x="18" y="0" width="3" height="26" rx="1.5"/><rect x="24" y="5" width="3" height="16" rx="1.5"/><rect x="30" y="2" width="3" height="22" rx="1.5"/><rect x="36" y="8" width="3" height="10" rx="1.5"/><rect x="42" y="4" width="3" height="18" rx="1.5"/><rect x="48" y="1" width="3" height="24" rx="1.5"/><rect x="54" y="6" width="3" height="14" rx="1.5"/><rect x="60" y="9" width="3" height="8" rx="1.5"/><rect x="66" y="5" width="3" height="16" rx="1.5"/><rect x="72" y="2" width="3" height="22" rx="1.5"/><rect x="78" y="7" width="3" height="12" rx="1.5"/><rect x="84" y="10" width="3" height="6" rx="1.5"/></svg>')


def kachel_bauen(eintrag):
    quelle = html.escape(eintrag["relativ"], quote=True)
    prompt = eintrag["prompt"].strip()
    typ = eintrag["typ"]

    if typ == "video":
        thumb = vorschaubild(eintrag["datei"])
        poster = ""
        if thumb:
            poster = ' poster="%s"' % html.escape(
                "%s/%s" % (eintrag["projekt"], thumb.name), quote=True)
        buehne = (
            '<div class="buehne"><video src="%s"%s controls preload="metadata" '
            'playsinline></video></div>' % (quelle, poster)
        )
    elif typ == "audio":
        buehne = (
            '<div class="buehne ton">%s'
            '<audio src="%s" controls preload="none"></audio></div>' % (WELLE, quelle)
        )
    else:
        buehne = (
            '<div class="buehne"><img src="%s" alt="%s" loading="lazy" '
            'decoding="async"></div>'
            % (quelle, html.escape(prompt[:120] or eintrag["datei"].name, quote=True))
        )

    prompttext = (html.escape(prompt) if prompt
                  else '<span class="prompt leer">ohne Prompt</span>')
    promptblock = ('<p class="prompt" title="%s">%s</p>'
                   % (html.escape(prompt, quote=True), prompttext))

    suchtext = html.escape(
        " ".join([prompt, eintrag["modell"], eintrag["projekt"]]).lower(), quote=True)

    return (
        '<article class="kachel" data-typ="%s" data-modell="%s" data-suche="%s" '
        'data-credits="%s" data-eur="%s">%s'
        '<div class="angaben">%s'
        '<div class="zeile"><span class="modell">%s</span>'
        '<span class="kosten">%s Credits · %s</span></div>'
        '<div class="zeile"><span>%s</span><span class="kosten">%s</span></div>'
        '</div></article>'
        % (
            html.escape(typ, quote=True),
            html.escape(eintrag["modell"], quote=True),
            suchtext,
            eintrag["credits"],
            eintrag["eur"],
            buehne,
            promptblock,
            html.escape(eintrag["modell"]),
            credits_text(eintrag["credits"]),
            eur_text(eintrag["eur"]),
            html.escape(eintrag["projekt"]),
            html.escape(zeit_text(eintrag["zeit"])),
        )
    )


def seite_bauen(eintraege):
    anzahl = len(eintraege)
    credits = sum(e["credits"] for e in eintraege)
    euro = sum(e["eur"] for e in eintraege)

    vorhandene_typen = [t for t in ("bild", "video", "audio")
                        if any(e["typ"] == t for e in eintraege)]
    knoepfe = ['<button type="button" data-typ-filter="alle" aria-pressed="true">'
               'Alle</button>']
    for typ in vorhandene_typen:
        knoepfe.append(
            '<button type="button" data-typ-filter="%s" aria-pressed="false">%s</button>'
            % (typ, html.escape(TYPNAMEN.get(typ, typ)))
        )

    modelle = sorted({e["modell"] for e in eintraege}, key=str.lower)
    optionen = ['<option value="alle">Alle Modelle</option>']
    for modell in modelle:
        optionen.append('<option value="%s">%s</option>'
                        % (html.escape(modell, quote=True), html.escape(modell)))

    kacheln = "\n".join(kachel_bauen(e) for e in eintraege)

    return """<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Mediengalerie</title>
<style>%s</style>
</head>
<body>
<div class="rahmen">
<header>
  <h1>Mediengalerie</h1>
  <div class="summe">
    <div><span class="wert" id="summe-anzahl">%s</span>
         <span class="marke">Generierungen</span></div>
    <div><span class="wert" id="summe-credits">%s</span>
         <span class="marke">Credits</span></div>
    <div><span class="wert geld" id="summe-euro">%s</span>
         <span class="marke">ausgegeben</span></div>
  </div>
  <div class="gefiltert" id="gefiltert"></div>
</header>

<div class="regler">
  %s
  <select id="modellwahl" aria-label="Modell">%s</select>
  <input type="search" id="suche" placeholder="Suche in Prompt, Modell, Projekt"
         aria-label="Suche">
</div>

<div class="raster">
%s
</div>
<p class="nichts" id="nichts" hidden>Nichts gefunden.</p>

<footer>Erzeugt am %s · %s Projekt(e) unter %s</footer>
</div>
<script>%s</script>
</body>
</html>
""" % (
        STIL,
        zahl_text(anzahl, 0),
        credits_text(credits),
        eur_text(euro),
        "\n  ".join(knoepfe),
        "".join(optionen),
        kacheln if kacheln else '<!-- noch nichts da -->',
        datetime.now().strftime("%d.%m.%Y, %H:%M"),
        zahl_text(len({e["projekt"] for e in eintraege}), 0),
        html.escape(str(WURZEL)),
        SKRIPT,
    )


def oeffnen(pfad):
    """Startet die Seite mit »open«, unter Linux notfalls mit »xdg-open«."""
    for werkzeug in ("open", "xdg-open"):
        if shutil.which(werkzeug):
            try:
                subprocess.run([werkzeug, str(pfad)], check=False)
                return True
            except OSError:
                continue
    print("Konnte die Seite nicht öffnen — bitte selbst aufrufen: %s" % pfad,
          file=sys.stderr)
    return False


def hauptprogramm(argumente=None):
    global WURZEL
    zerleger = argparse.ArgumentParser(
        prog="galerie.py",
        description="Baut aus allen meta.json unter ~/Medien eine galerie.html.",
    )
    zerleger.add_argument("--wurzel", default=str(WURZEL),
                          help="Ordner mit den Projekten (Vorgabe ~/Medien)")
    zerleger.add_argument("--ausgabe", help="Zieldatei (Vorgabe <wurzel>/galerie.html)")
    zerleger.add_argument("--nooeffnen", action="store_true",
                          help="die Seite am Ende nicht öffnen")
    args = zerleger.parse_args(argumente)

    WURZEL = Path(args.wurzel).expanduser()
    if not WURZEL.is_dir():
        print("%s gibt es noch nicht — es wurde wohl noch nichts erzeugt."
              % WURZEL, file=sys.stderr)
        return 1

    eintraege = eintraege_sammeln(WURZEL)
    ziel = Path(args.ausgabe).expanduser() if args.ausgabe else WURZEL / "galerie.html"
    ziel.write_text(seite_bauen(eintraege), encoding="utf-8")

    credits = sum(e["credits"] for e in eintraege)
    euro = sum(e["eur"] for e in eintraege)
    print("%s: %s Generierungen · %s Credits · %s"
          % (ziel, zahl_text(len(eintraege), 0), credits_text(credits), eur_text(euro)))

    if not args.nooeffnen:
        oeffnen(ziel)
    return 0


if __name__ == "__main__":
    sys.exit(hauptprogramm())

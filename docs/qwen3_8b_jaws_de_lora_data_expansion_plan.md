# Qwen3-8B LoRA Data Expansion Plan

## Ausgangspunkt

Der aktuelle Clean-Freeze ist formal sauber und gate-kompatibel, aber der erste echte 4090-v2-Run zeigt im Post-Run-Smoke-Test noch klare inhaltliche Generalisierungsluecken.

Beobachtete Muster:

- `faq_direct_answer`: kurze, atomare Settings-/Definitionsfragen driften in benachbarte Themen ab
- `step_by_step`: Format wird gelernt, konkrete Ablaufinhalte aber noch nicht stabil
- `clarification`: zu wenig diszipliniert, teils repetitiv und nicht fokussiert genug
- `troubleshooting`: Antworten werden generisch, wenn der Quellabschnitt eher beschreibend als diagnostisch ist
- `uncertainty_escalation`: bereits der stabilste Bereich

## Prioritaeten

## 1. Clarification stark ausbauen

Ziel:

- von aktuell `33` auf mindestens `80-120` belastbare Beispiele

Fokus:

- genau eine fokussierte Rueckfrage
- keine Folgefragen
- keine Listenentgleisung
- Prioritaet auf `jaws_de_braille` und `jaws_de_settingscenter`

## 2. Atomare FAQ-Faelle ergaenzen

Ziel:

- mehr kurze, praezise Dokumentationsantworten fuer einzelne Optionen und Begriffe

Fokus:

- Settings-/Definitionsabschnitte wie `Acht Punkt Braille`
- Antworten kurz, treu und ohne thematischen Drift

## 3. Echte Schrittfolgen verbreitern

Ziel:

- mehr lange, konkrete `step_by_step`-Faelle aus BrailleIn, Uebersetzung und SettingsCenter

Fokus:

- dokumentierte Menue- und Tastensequenzen
- keine generischen Re-Formulierungen
- mehrere verwandte Abschnitte aus derselben Themenfamilie

## 4. Troubleshooting enger kuratieren

Ziel:

- echte Diagnose- und Handlungssituationen staerker von beschreibenden UI-/Optionstexten trennen

Fokus:

- beschreibende Hilfetexte eher als `faq_direct_answer`
- `troubleshooting` nur dort, wo die Quelle wirklich ein dokumentiertes Pruefen, Umschalten oder Eingrenzen nahelegt

## 5. Nahe Chunk-Abdeckung fuer Smoke-kritische Themen

Ziel:

- problematische Themencluster im Train-Set dichter abdecken, ohne Eval direkt zu duplizieren

Fokus:

- Braille-Grundoptionen
- BrailleIn-/Uebersetzungsworkflows
- SettingsCenter-Visualisierung
- Tutorial-Abschnitte mit Evidenzgrenzen

## Zielgroessen fuer den naechsten Ausbau

- `clarification`: `80-120`
- `faq_direct_answer`: `+80-150` neue atomare Faelle
- `step_by_step`: `+30-60` neue prozedurale Faelle
- `troubleshooting`: Bestand bereinigen und nur gezielt erweitern
- `uncertainty_escalation`: nur moderat ausbauen, da bereits relativ stark

## Aktueller Ausbau-Stand

- `qwen_data_expansion_wave1` hat aus bereits human-reviewten Wave2-Outputs nur `18` sicher promotable Rows geliefert, ohne neue `faq_direct_answer`- oder `step_by_step`-Ausbeute.
- Die neue fokussierte Teacher-Welle `qwen_focus_wave_v1` kann den FAQ-Bereich sofort verbreitern: `136` Jobs fuer `faq_direct_answer` plus `1` verbliebener `step_by_step`-Job.
- Der separate Gap-Audit zeigt, dass nach den aktuellen Gold- und Ausbau-Exclusions im bestehenden Chunk-Pool nur noch `1` echter `step_by_step`-Kandidat uebrig ist.
- Daraus folgt: Der naechste echte Hebel ist keine weitere generische Chunk-Welle, sondern eine neue gezielte Quell- oder Teacher-Welle fuer prozedurale BrailleIn-/SettingsCenter-Abschnitte.

## Akzeptanzkriterien vor dem naechsten grossen Run

- neuer Clean-Stand bleibt stub-/artifact-frei
- Source-Faithfulness-Audit bleibt auf `0` verbleibende Flags
- `clarification`-Verhalten ist im Spot-Check fokussiert und nicht repetitiv
- mehrere neue Smoke-nahe Themencluster sind im Train-Set vertreten
- ein neuer Freeze ist gegen den aktuellen 4090-v2-Lauf qualitativ begruendbar besser, nicht nur groesser

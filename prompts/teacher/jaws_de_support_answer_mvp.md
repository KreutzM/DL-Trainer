# Teacher Prompt: JAWS-DE Support Answer MVP

## Rolle

Du erzeugst eine hochwertige, dokumentationsgebundene Support-Antwort fuer eine simulierte JAWS-DE-Nutzeranfrage.

## Ziel

Beantworte die simulierte Nutzeranfrage nur anhand des bereitgestellten Quellkontexts so, dass die Antwort fuer einen spaeteren Support-Datensatz taugt.

## Regeln

- Nutze ausschliesslich die bereitgestellten Quellen.
- Keine erfundenen Fakten, Menuepunkte, Tastenkombinationen oder Voraussetzungen.
- Antworte auf die konkrete simulierte Nutzeranfrage, nicht auf einen generischen Dokumenttitel.
- Wenn die Quelle eine klare direkte Antwort traegt, antworte direkt.
- Wenn die Quelle eine echte Schrittfolge traegt, gib nur diese Schritte aus.
- Wenn der Fall ohne weitere Eingrenzung nicht sicher beantwortbar ist, stelle genau eine fokussierte Rueckfrage.
- Wenn die Quelle nicht ausreicht, markiere die Unsicherheit knapp und eskaliere sauber statt zu raten.
- Kein Chain-of-thought, keine Erklaerungen ausserhalb des JSON.

## Gewuenschte Qualitaet

- supporttauglich
- sachlich und knapp
- klar an der Nutzerfrage ausgerichtet
- dokumentationsgebunden
- ohne Tabellen-, Hinweis- oder Truncation-Artefakte

## Task-Type-spezifische Regeln

- `faq_direct_answer`: direkt beantworten, ohne unnötige Vorrede.
- `troubleshooting`: symptombezogen antworten und die dokumentierte Bedingung oder Prüfung klar benennen.
- `step_by_step`: nur echte Schritte aus der Quelle ausgeben.
- `step_by_step`: genau eine konsolidierte Prozedur liefern, keine Doppelausgabe und keine alternative zweite Schrittfolge.
- `step_by_step`: nur Schritte aus derselben dokumentierten Prozedur mischen; zwei getrennte Verfahren nicht zu einem Ablauf verschmelzen.
- `step_by_step`: wenn Quelle oder Nutzerziel benachbarte, aber getrennte Verfahren beruehren, genau einen durchgaengigen Ablauf waehlen statt einen Hybrid aus beiden.
- `step_by_step`: die Prozedur bis zum eigentlichen Zielzustand der Nutzerfrage zu Ende fuehren; nicht vor dem letzten entscheidenden Schritt abbrechen.
- `step_by_step`: der letzte Schritt muss den gefragten Zielzustand wirklich erreichen oder bestaetigen, nicht nur das naechste Dialogfenster oeffnen.
- `step_by_step`: Reihenfolge eindeutig und kohärent halten; Schritte knapp, aber operativ brauchbar formulieren.
- `step_by_step`: die eigentliche Prozedur in `steps` ablegen, nicht zusaetzlich noch einmal als nummerierte oder aufgelistete Schrittfolge in `answer`.
- `step_by_step`: wenn die Nutzerfrage nach einem Ablauf fragt, liefere eine Prozedur und keine Rueckfrage.
- `step_by_step`: beginne nicht mitten in einer Prozedur, wenn der davorliegende dokumentierte Einstieg im selben Fall sichtbar ist.
- `step_by_step`: wenn ein sauberer Abschluss im sichtbaren Kontext belegt ist, fuehre die Prozedur bis zu diesem Abschluss statt nur Teilschritte zu nennen.
- `step_by_step`: bei Chunk-Grenzen den sichtbaren Ablauf als zusammenhaengend behandeln, solange er zur selben dokumentierten Prozedur gehoert.
- `step_by_step`: keine Evidenzgrenze als Ersatz fuer eine noch sichtbare, durchgehende Schrittfolge ausgeben.
- `step_by_step`: den letzten entscheidenden Zielschritt nicht durch eine blosse Zwischenstation ersetzen.
- `step_by_step`: bei Import- und Assistentenfolgen sowohl den Start als auch den Abschluss derselben Prozedur im Blick behalten.
- `step_by_step`: keine benachbarten Teilziele als zwei getrennte Antworten behandeln, wenn sie zur selben dokumentierten Prozedur gehoeren.
- `step_by_step`: wenn mehrere Verfahren in der Quelle stehen, waehle nur das eine, das die Nutzerfrage wirklich trifft.
- `step_by_step`: hybride Schrittfolgen aus Start eines Verfahrens und Ende eines anderen vermeiden.
- `step_by_step`: keine Rueckfrage oder Eskalation ausgeben, wenn die Quelle die geforderte Prozedur bereits hergibt.
- `step_by_step`: die Antwort soll den Zielzustand erreichen, nicht nur den naechsten Zwischenzustand beschreiben.
- `clarification`: genau eine fokussierte Rueckfrage stellen, wenn der Fall nicht sicher direkt beantwortbar ist.
- `uncertainty_escalation`: klar benennen, was die Quelle trägt und wo die Evidenzgrenze liegt; nicht so tun, als sei mehr belegt als dokumentiert.

## Feldpflichten pro Fall

- Setze `task_type` exakt wie vorgegeben.
- `clarification`:
  - `needs_clarification=true`
  - `clarification_question` genau eine fokussierte Frage
  - `answer` enthaelt nur diese Rueckfrage und endet mit `?`
  - `steps=[]`
  - `escalate=false`
- `uncertainty_escalation`:
  - `escalate=true`
  - `uncertainty_reason` kurz und konkret
  - `needs_clarification=false`
- `faq_direct_answer`, `troubleshooting`, `step_by_step`:
  - `needs_clarification=false`
  - `clarification_question=null`
- `step_by_step`:
  - `steps` nur fuellen, wenn die Quelle eine echte Bedienfolge traegt
  - `steps` muessen genau eine geordnete, zusammenhaengende Prozedur abbilden
  - `answer` darf nur leerer Rahmen oder eine kurze Einleitung sein, aber keine nummerierte, bulleted oder anderweitig ausgeschriebene Schrittfolge enthalten
  - wenn die Quelle mehrere getrennte Prozeduren beschreibt, nur die zur Nutzerfrage passende ausgeben statt sie zu vermischen
  - bei benachbarten Teilzielen keinen Hybrid aus Oeffnen, Wechseln und zweitem Folgeablauf bauen; Anfang und Abschluss muessen zur selben dokumentierten Prozedur gehoeren
  - die letzten zielerreichenden Schritte nicht weglassen

## Ausgabe

JSON gemaess Output-Schema.

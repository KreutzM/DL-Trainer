# Teacher Prompt: JAWS-DE User Simulation

## Rolle

Du simulierst eine realistische deutschsprachige Support-Anfrage fuer JAWS.

## Ziel

Erzeuge genau eine hochwertige Nutzeranfrage, die plausibel zu einem realen Supportfall passt und sich eng am bereitgestellten Dokumentkontext orientiert.

## Regeln

- Nutze nur den bereitgestellten Quellkontext.
- Erfinde keine Menues, Tastenkombinationen oder Funktionen.
- Verwende keine Chunk-Titel als starre Schablone.
- Formuliere die Anfrage so, wie ein echter Anwender oder Helpdesk-Nutzer sie stellen koennte.
- Variiere Schwierigkeitsgrad und Formulierungsstil sinnvoll.
- Die Anfrage darf unvollstaendig oder alltagsnah sein, aber sie muss zum dokumentierten Fall passen.
- Keine Loesung in die Anfrage schreiben.
- Kein Chain-of-thought, keine Erklaerungen ausserhalb des JSON.

## Gewuenschte Qualitaet

- konkret statt generisch
- supportnah statt dokumenttitelartig
- glaubwuerdig fuer den jeweiligen `task_type`
- bei `clarification` oder `uncertainty_escalation` darf die Anfrage bewusst etwas unklar sein
- bei `step_by_step` sollte die Anfrage typischerweise um eine Bedienfolge oder Vorgehensweise bitten

## Task-Type-spezifische Leitplanken

- `faq_direct_answer`: die Anfrage soll auf eine konkrete, direkt beantwortbare Informationsfrage hinauslaufen.
- `troubleshooting`: die Anfrage soll ein plausibles Problem, eine Einschränkung oder ein unerwartetes Verhalten schildern.
- `step_by_step`: die Anfrage soll klar um eine Vorgehensweise, Bedienfolge oder Einrichtung bitten.
- `clarification`: die Anfrage soll bewusst noch nicht eng genug sein, sodass eine fokussierte Rueckfrage sinnvoll bleibt.
- `uncertainty_escalation`: die Anfrage darf einen Randfall, eine Voraussetzung oder eine Grenze ansprechen, bei der die Quelle nur begrenzt Antwort gibt.

## Ausgabe

JSON mit:
- `request_text`
- `user_goal`
- `difficulty`
- `phrasing_style`
- `scenario_summary`
- `notes`

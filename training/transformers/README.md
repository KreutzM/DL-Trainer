# transformers

Dieser Ordner enthaelt den generischen `transformers`-Trainingsstack.

Fuer JAWS-DE wurden die alten versionierten Qwen-Trainingsconfigs und Exportpfade im aktiven Repo bewusst entfernt. Grund: die zugrunde liegenden historischen Gold- und Exportdaten gelten nicht mehr als belastbarer produktiver Startpunkt.

Aktueller JAWS-DE-Status:

- kein aktiver versionierter JAWS-DE-Trainingsfreeze im Repo
- kein produktiver JAWS-DE-Startskript-/Runbook-Pfad mehr aus alten Exporten
- Neustart erst wieder ab frischen echten Teacher-Outputs, reviewtem Gold und neu gebautem Export

Beibehalten werden nur die generischen Trainingsbausteine wie `run_qwen_lora_training.py`, damit spaetere saubere JAWS-DE- oder andere Produktlaeufe darauf wieder aufsetzen koennen.

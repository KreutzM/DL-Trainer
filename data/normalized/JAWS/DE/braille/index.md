# JAWS – Braille (Allgemein & Focus)

## Braillesymbole hinzufügen und verändern

Obwohl JAWS die am häufigsten genutzten Braillesymbole ordnungsgemäß darstellt, kann es vorkommen, dass Sie die Brailledarstellung bestimmter Symbole verändern oder neue hinzufügen müssen. Wenn beim Lesen eines Dokuments ein bestimmtes Symbol nicht richtig in Braille dargestellt wird, oder wenn Ihre Braillezeile ein leeres Modul anstatt eines Symbols anzeigt, dann gehen Sie bitte folgendermaßen vor:

1. Stellen Sie sicher, dass die Brailleübersetzung ausgeschaltet ist. Das ist vor allem dann wichtig, wenn Sie mit fremdsprachlichen Dokumenten und mathematischen und wissenschaftlichen Texten arbeiten.
2. Drücken Sie **EINFÜGEN+V** , um die Schnelleinstellung zu öffnen und geben Sie "Übersetzungstabelle" ohne die Anführungsstriche in das Sucheingabefeld ein.
3. Anschließend drücken Sie **PFEIL RUNTER** , um zur bevorzugten Übersetzungstabelle in der Strukturansicht zu springen.
4. Drücken Sie **LEERTASTE** , um eine passende Tabelle auszuwählen. Sie müssen eine Tabelle auswählen, die das Wort "unicode" im Titel enthält.
5. Betätigen Sie den OK Schalter.

**Hinweis:** Wenn die Einstellung für die bevorzugte Übersetzungstabelle in der Schnelleinstellung nicht verfügbar ist, dann müssen Sie zuerst mindestens eine weitere bevorzugte Übersetzungstabelle in der Einstellungsverwaltung konfigurieren. Lesen Sie das Kapitel [Brailletabellen](SettingsCenter.chm::/Braille/Advanced/Braille_Tables_Dialog.htm) für weitere Informationen.

Lesen Sie das Symbol in Ihrem Dokument erneut. Sollte das Symbol immer noch als leeres Modul erscheinen, gehen Sie bitte folgendermaßen vor:

1. Öffnen Sie die Einstellungsverwaltung ( **EINFÜGEN+F2** ) und erweitern Sie die Gruppe Bilder und Symbole.
2. Aktivieren Sie das Kontrollfeld Zeichenwert hexadezimal sprechen.
3. Wählen Sie OK, um die Änderungen zu speichern und die Einstellungsverwaltung zu schließen.
4. Kehren Sie in das Dokument zurück. Bewegen Sie den Cursor auf ein kleines "a" (sollte keines vorhanden sein, dann geben Sie eins ein) und drücken Sie **NUM 5** dreimal hintereinander. JAWS sollte "Zeichen U+61HEX" ansagen. Wenn Sie irgendeine andere Meldung hören, dürfen Sie diese Schritte nicht weiter ausführen.
5. Bewegen Sie den Cursor auf das Zeichen, dessen Brailledarstellung geändert werden soll und drücken Sie **NUM 5** dreimal schnell hintereinander, damit Sie den Hexadezimal Unicode Wert des Zeichen erhalten. Notieren Sie sich sicherheitshalber den Wert, da Sie diesen für die nächsten Schritte benötigen.
6. Öffnen Sie mit einem Texteditor wie Notepad die zur Zeit aktive Brailletabelle. Die Tabellen werden in Dateien mit der Endung .jbt im JAWS Verzeichnis (standardmäßig C:\Programme\Freedom Scientific\JAWS\ *X* (wobei *X* für Ihre JAWS Versionsnummer steht)) gespeichert.Die Standard Brailletabellen-Datei heißt EURO_Unicode.jbt. Die Tabellendateien legen die Brailledarstellung für eine Reihe von Symbolen fest. Der erste Abschnitt enthält die grundlegenden 127 ANSI Zeichen. Danach folgen die Unicode-Einträge. Das Format der Einträge lautet: U+XXX=YYYYYY Wobei XXX der Hexadezimal Unicode Wert des Symbols ist, und YYYY die Braillepunkte, die das Symbol darstellen.
7. Wenn Sie ein Symbol verändern möchten, das in Braille falsch dargestellt wird, müssen Sie es zuerst in der Brailletabelle suchen. Dies tun Sie mit der Funktion Suchen in Ihrem Texteditor, damit der entsprechende Eintrag auch gefunden wird. Um zum Beispiel die Brailledarstellung für das Unicode Zeichen 2018 zu verändern, müssen Sie den String "2018" suchen. Daraufhin würden Sie folgende Zeile finden: U+2018=34578 Dadurch wird angezeigt, dass das Unicode Zeichen 2018 in Braille durch die Punkte 3, 4, 5, 7 und 8 dargestellt wird. Um die Brailledarstellung zu verändern, ersetzen Sie die vorhandenen Ziffern der Punkte mit denen Ihrer Wahl.
8. Sollte ein bestimmtes Symbol überhaupt nicht auf Ihrer Zeile dargestellt werden, können Sie es der Brailletabelle hinzufügen. Die Tabelleneinträge sind in der Reihenfolge Ihre Hexadezimal Unicode Werte angeordnet. Wenn Sie mit den Hexadezimalzahlen einverstanden sind, dann möchten Sie Ihren Eintrag wahrscheinlich im entsprechenden Bereich einfügen. Wenn nicht, dann fügen Sie ihn einfach am Ende der Tabelle ein. Wenn zum Beispiel das Symbol als "Zeichen U+259HEX" wiedergegeben wird, und Sie möchten es in Braille mit den Punkten 3, 4, 6 und 8 darstellen, dann sollte Ihr Tabelleneintrag folgendermaßen aussehen: U+259=3468
9. Speichern Sie nach dem Ändern die Datei. Beenden Sie danach JAWS und starten es erneut. Die Veränderungen der Brailletabelle sollten jetzt wirksam sein.

*Siehe auch:*

[Speziellen Symbolen Sprache hinzufügen](JFW.chm::/using_jaws/controlling_speech/Adding_Speech_for_Special_Symbols.htm)

Quelle: Adding_and_Modifying_Braille_Symbols.htm

## Automatisches Weiterbewegen

Der Modus Automatisches Weiterbewegen ist gleichbedeutend mit dem Befehl Alles lesen für Brailleleser. Die Braillezeile wird automatisch in einer definierten Geschwindigkeit durch ein gesamtes Dokument weiterbewegt, überspringt automatisch leere Bereiche und Leerzeichen. Sie können die Geschwindigkeit während des Lesens erhöhen oder verringern, rückwärts oder vorwärts springen (mit den Navigationstasten auf der Zeile), oder den Modus beenden, indem Sie eine Routingtaste drücken (oder den Anwendungsfokus verändern). Die Dauer, die die Braillezeile wartet, bevor zum nächsten Textsegment weiter bewegt wird, hängt von der Länge der aktuelle Braille Textzeile ab. So wird beispielsweise bei kurzen Zeilen schneller weiter bewegt, so dass Sie schneller zum nächsten Segment gelangen, ohne dass Sie warten müssen, wenn Sie mit dem Lesen fertig sind, in langen Zeilen hingegen wird langsamer weiter bewegt.

Sie können die maximale Dauer festlegen, die JAWS warten soll, bevor die Braillezeile automatisch weiterbewegt wird. Die Wartezeit ist von 500 bis 20.000 Millisekunden (1000 Millisekunden = 1 Sekunde) einstellbar. Standardmäßig ist die maximale Dauer, die JAWS beim Lesen im Modus des Automatischen Weiterbewegens wartet, 5000 Millisekunden. Das bedeutet, dass JAWS bei einer überwiegend mit Text ausgefüllten Braillezeile, 5 Sekunden wartet, bevor zum folgenden Segment weiterbewegt wird. Wird die Braillezeile zu einer kurzen Zeile weiterbewegt, die nur wenige Worte enthält und wo die restlichen Zellen leer bleiben, was häufiger bei großen Braillezeilen, wie etwa mit 40 oder 80 Zellen, auftreten kann, dann wartet JAWS nur 2 Sekunden, bevor automatisch zum nächsten Textsegment weiterbewegt wird.

Das Intervall für das automatische Lesen kann über die Einstellungsverwaltung festgelegt werden. Weitere Informationen hierzu finden Sie unter [Gruppe Braille-Optionen](SettingsCenter.chm::/Braille/braille_options_dialog.htm) .

JAWS weist die Befehle für das automatische Weiterbewegen allen Freedom Scientific Braillezeilen und Notizgeräten zu. Informationen über das Starten des automatischen Weiterbewegens erhalten Sie in den Hilfethemen Ihrer Freedom Scientific Braillezeile oder Ihres Notizgerätes:

- [Focus 14, Focus 40 und Focus 80 Blue](focus/Controls_for_Focus_14_40_and_80_Blue.htm)
- [Klassische Focus 40 Blue](focus/Controls_for_Focus_40_Blue.htm)
- [Focus 40/80](focus/Controls_for_Focus_40_and_80.htm)
- [Focus 44, 70, 84](focus/focus_ww_ab_crk.htm)
- [Die tragbare PAC Mate Braillezeile](braille/pacmate_display.htm)
- [Braille Lite M20](braille/braille_lite_20_millennium_edition.htm)
- [Braille Lite M40](braille/braille_lite_40_millennium_edition.htm)
- [Braille Lite 2000](braille/96braille_lite_18.htm)
- [Braille Lite 40](braille/braille_lite_40.htm)

Quelle: Auto_Advance_Mode.htm

## Die Modi der Braillezeilen

Mit JAWS kann die Braillezeile in einem von vier Modi betrieben werden: Strukturiert, Flächen, Sprachausgabe und Attribute. Fast alle Zeilen verfügen über eine Taste, mit der man zwischen diesen vier Modi hin- und herschalten kann.

[Strukturierter Modus](#Structured_Mode)

[Flächenmodus](#Line_Mode)

[Sprachausgabemodus](#Speech_Box_Mode)

[Attributmodus](#Attribute_Mode)

## Strukturierter Modus

Im strukturierten Modus erhalten Sie beschreibende Informationen über das aktuelle Dialogfeld und/oder das aktuelle Steuerelement. Wenn keine speziellen beschreibenden Informationen wie zum Beispiel in einem Textdokument vorhanden sind, verhält sich die Braillezeile so wie im Flächenmodus. Standardmäßig verwendet JAWS den strukturierten Modus.

Der strukturierte Modus liefert ein- oder zweizeilige beschreibende Informationen über Menüdialoge und deren Steuerelemente. Die zusätzlichen Informationen im strukturierten Modus sind besonders nützlich, da Sie mit ihrer Hilfe ein Dialogfeld und die Steuerelemente schneller navigieren können. Wenn spezielle Informationen über den Typ des Dialogfeldes und/oder des Steuerelements im Fokus sind, verwendet JAWS spezielle Braille-Kürzel, um eine "strukturierte Zeile" zu erzeugen, die die Bildschirminformationen auf Ihrer Braillezeile wiedergibt. JAWS versucht auch, die strukturierte Zeile auf der Braillezeile so auszurichten, dass die relevanteste Information, wie eine Eingabeaufforderung, am Anfang der Braillezeile erscheinen. Wenn Braille folgt Aktiv gewählt ist, schaltet JAWS in den Flächenmodus um, sobald der Braillecursor vom Steuerelement im Fokus wegbewegt wird. Dadurch erhält man eine genaue Widerspiegelung der Bildschirminformationen. Sobald der Braillecursor auf das Steuerelement im Fokus zurück bewegt wird, schaltet JAWS in den strukturierten Modus zurück.

### Ein Beispiel für eine strukturierte Zeile

Nachdem Sie **ALT+EINGABE** auf der Taskleiste gedrückt haben, wird eine ähnliche Zeile wie die folgende auf Ihrer Braillezeile erscheinen:

> "kf Eigenschaften von Taskleiste und Startmenü Taskleiste Taskleistendarstellung gf [x] Taskleiste fixieren"

Diese Information ähnelt dem, was JAWS ansagt:

> "Eigenschaften von Taskleiste und Startmenü Dialogfeld Taskleiste Seite Taskleistendarstellung Gruppenfeld Taskleiste fixieren Kontrollfeld aktiviert."

Beachten Sie bitte die Symbole und Kürzel in dem Braille-Beispiel. Lesen Sie dazu bitte das Thema [Spezielle JAWS Braille-Kürzel](JAWS_Specific_Braille_Abbreviations.htm) , in dem Sie eine komplette Liste mit Beschreibungen finden.

Die Wörter "Dialog", "Seite" und "Kontrollfeld nicht aktiviert" erscheinen in diesem Zusammenhang niemals auf dem Bildschirm. Da es sich bei Windows um eine dreidimensionale grafische Umgebung handelt, richten sich die Informationen auf der Braillezeile nicht nach der Reihenfolge, die von der JAWS Sprachausgabe gesprochen werden.

Um zu überprüfen, wie die Informationen ohne den strukturierten Modus aussehen, lesen Sie bitte das Thema [Der Flächenmodus](#Line_Mode) .

### Den strukturierten Modus konfigurieren

In der Einstellungsverwaltung können Sie konfigurieren, wie Informationen im strukturierten Modus erscheinen. Sie können angeben, welche Informationen für verschiedene Kontrollelemente angezeigt werden, wie auch die Position des Textes in der strukturierten Zeile.

Erfahrenere Anwender können nun auch die Braillesymbole für Steuerelemente, die Reihenfolge, in der sie angezeigt werden und die Braille-Darstellung des Status' von Steuerelementen modifizieren. Damit legen Sie für jede Anwendung auf Ihrem Computer fest, wie und welche Informationen auf Ihrer Braillezeile dargestellt werden.

Um auf die Einstellungen für den Strukturierten Modus zuzugreifen, öffnen Sie die Einstellungsverwaltung ( **EINFÜGEN+F2** ), erweitern Sie die Gruppe Braille und wählen Sie dann die Gruppe Strukturierter Modus. Sie können jetzt die folgenden Elemente ändern.

- Öffnen sie die Gruppe Optionale Komponenten einbeziehen, um zu konfigurieren, welche Elementinformationen auf der Braillezeile angezeigt werden. Hierzu gehören Steuerelemente, Level und Positionen, Kurztasten, Hinweise, Dialogtitel, beschreibende Dialogtexte und Steuerungsgruppen.
- Legen Sie fest, ob JAWS die Anzeige am strukturierten Element ausrichten soll, wenn das Element den Fokus erhält.
- Legen Sie fest, ob die strukturierte Zeile in umgekehrter Reihenfolge dargestellt werden soll. Wenn ja, dann wird zuerst die Steuerelementinfo gezeigt, gefolgt von der Gruppe und erst dann die Dialogfensterinformationen.
- Drücken Sie **LEERTASTE** auf Erweitert, um das Dialogfenster Optionen für Elementtypen zu öffnen, in dem Sie Symbole anpassen können, die auf Ihrer Braillezeile die Elemente darstellen, wie auch die Symbole, die den Elementstatus anzeigen – wie aktiviert oder deaktiviert bei einem Kontrollfeld.

Für weitere Informationen lesen Sie bitte: [Der strukturierte Modus](SettingsCenter.chm::/Braille/braille_options_dialog.htm#StructuredMode) . Weitere Informationen zum Konfigurieren anderer Brailleoptionen finden Sie unter [Braillegruppeneinstellungen.](SettingsCenter.chm::/Braille/braille_options_dialog.htm)

### Eine strukturierte Zeile navigieren

Wenn die strukturierte Zeile auf der Braillezeile erscheint, dann wir sie an der fokussierten Steuerelementinformation ausgerichtet, wie zum Beispiel dem Status oder dem Kontrollfeldnamen, da diese als für den Anwender am informativsten angenommen wird. Es kann sein, dass Sie die **LINKE LESETASTE** drücken müssen, damit Sie den Dialogfenstertitel und den Seitentitel bei mehrseitigen Dialogen sehen können. In einer strukturierte Zeile können Sie mit den Ausschnitt-Tasten auch die Informationen erreichen, die auf der Braillezeile nicht mehr angezeigt werden. Dieses ist speziell für Braillezeilen mit 40 oder weniger Zellen hilfreich.

Darüber hinaus können Sie, während Sie auf einer strukturierten Zeile stehen, segmentweise lesen. Eine Zeile könnte beispielsweise den Dialogtitel, den Titel eines Gruppenfelds mit verschiedenen Elementen und den aktuellen Elementstatus des fokussierten Objekts enthalten. Wenn Sie eine Freedom Scientific Focus Braillezeile verwenden, dann können Sie die **UMSCHALT** Taste in Verbindung mit der **LINKEN** oder **RECHTEN LESETASTE** drücken, um sich im strukturierten Segment zu bewegen. Das nächste oder vorherige Segment startet dann ganz links auf der Braillezeile in der ersten Zelle, die nicht als Statuszelle verwendet wird. Besitzen Sie eine andere Braillezeile als die Focus, dann können Sie diesen Befehl über den JAWS Tastaturmanager zuweisen.

Beachten Sie bitte, dass man im strukturierten Modus mit den Tasten für **BRAILLE RAUF** und **BRAILLE RUNTER** , mit denen man sich genauso wie mit den Pfeiltasten auf der Tastatur zwischen Steuerelementen bewegt, eine strukturierte Zeile nicht navigieren kann. Sie können jedoch mit den Routingtasten Schalter aktivieren, Text in einem Eingabefeld hervorheben und den Status von Kontrollfeldern umschalten.

## Flächenmodus

Im Flächenmodus erhalten Sie die genaue Darstellung der Bildschirminformationen, genauso wie mit dem JAWS Cursor.

Im Flächenmodus benutzt JAWS Bildschirmkoordinaten, um festzulegen, welche Informationen an die Braillezeile gesendet werden. Mit seinem Braillecursor gibt JAWS die Informationen genauso an die Braillezeile weiter, wie sie auf dem Computerbildschirm formatiert sind. Obwohl Sie dadurch einen besseren Überblick über das Bildschirmlayout und das Druckformat erhalten, könnte das Brailleformat verwirren, da Text in Windows überall auf dem Bildschirm erscheinen kann.

Unser Beispiel aus dem Abschnitt strukturierter Modus würde wie folgt auf der Braillezeile angezeigt werden:

> Wenn das Dialogfeld Eigenschaften für Taskleiste und Startmenü zum ersten Mal geöffnet wird:
> Kontrollfeld Taskleiste fixieren
> Eine Zeile nach oben:
> Taskleisten Optionen Startmenü
> Taskleiste Eigenschaften Hilfesymbol Schließen Symbol
> Beachten Sie bitte, dass die Textzeilen nicht aneinandergereiht sind. Das liegt daran, dass Text im Flächenmodus das Windowsformat benutzt. Um den gesamten Text sehen zu können, sollten Sie
> AUSSCHNITT RECHTS
> und
> AUSSCHNITT LINKS
> drücken.

Im Flächenmodus können Sie mit JAWS die Text-Darstellung auf Ihrer Braillezeile verändern. Die Standardeinstellung ist 8, was bedeutet, dass JAWS 8 leere Pixel als eine Leerzelle auf der Braillezeile ansieht. Weitere Informationen über Pixel-Leerzellen auf Ihrer Braillezeile finden Sie im Thema [Brailleformatierung](Braille_Formatting.htm) .

## Sprachausgabemodus

Der Sprachausgabemodus ist eine strenge Abbildung dessen, was die Sprachausgabe spricht. Dieser Modus ist besonders für Anwender wichtig, die blind und taub sind, weil Sie nun auf Informationen zugreifen können, die auf dem Computerbildschirm nicht sichtbar sind. Wenn die Informationen, die von der Sprachausgabe kommen, mehr als zehn Zeilen umfassen, wird nur der letzte Teil der Informationen angezeigt. In diesem Fall müssen Sie nach links schwenken, damit der Textanfang dargestellt wird.

Im Sprachausgabemodus können Sie mit den Navigationstasten nachlesen, was die Sprachausgabe gesprochen hat, die Routingtasten haben jedoch keine Auswirkungen.

## Attributmodus

Wenn Sie den Attributmodus auswählen, zeigt JAWS alle Attribute an, einem Textblock mit einem Buchstaben oder Symbol zugewiesen wurden. Attribute beinhalten Veränderungen wie zum Beispiel fett, kursiv, unterstrichen und so weiter. Diese Informationen erscheinen in den [Statuszellen](Status_Cells.htm) der Zeile. Wenn demselben Textblock mehrere Attribute zugewiesen sind, zeigt die Braillezeile jedes dieser Attribute nacheinander an. Um festzulegen, wie schnell die Anzeige wechselt, nutzen Sie die Einstellung Attributrotation, die Sie in der Gruppe Braillemarkierungen innerhalb der Gruppe Braille in der Einstellungsverwaltung finden.

**Hinweis:** Um den Attribut-Modus nutzen zu können, benötigen Sie eine Braillezeile mit Statuszellen.

Quelle: Braille_Display_Modes.htm

## Braille Blitzmeldungen

Braille Blitzmeldungen sind kurze Beschreibungen, die auf Ihrer Braillezeile ein paar Sekunden lang erscheinen. Diese Meldungen beinhalten die Startbenachrichtigungen von Anwendungen, Fehlermeldungen, Hilfe-Sprechblasen, JAWS Meldungen, Smart-Hilfe-Infos, Statusinformationen und Information, die vom Benutzer angefordert werden.

Braille Blitzmeldungen erscheinen nach einer kurzen Zeitspanne automatisch, aber Sie können sie jederzeit verschwinden lassen, indem Sie eine Cursorroutingtaste drücken. Wenn Sie mehr Zeit benötigen, die Meldung zu lesen, drücken Sie auf Ihrer Braillezeile die Navigationstaste, um die Meldung länger anzuzeigen.

Gehen Sie folgendermaßen vor, um die Blitzmeldungen ein- oder auszuschalten, die Ausführlichkeitsstufe der Meldungen zu verändern und die Zeitspanne festlegen, die die Meldung auf der Zeile stehen bleiben soll:

1. Wählen Sie im Menü Optionen den Eintrag Braille.
2. Drücken Sie auf den Schalter Erweitert.
3. Aktivieren Sie den Schalter Blitzmeldungen, um festzulegen, wie JAWS die Blitzmeldungen anzeigen soll.

Quelle: Braille_Flash_Messages.htm

## Braille-Formatierung

Mit der Option **8 Pixel Pro Leerschritt Umschalten** , eine komfortable und effiziente Methode, Braille zu lesen, können Sie die Leerzellen auf Ihrer Braillezeile optimieren, wodurch mehr Informationen in einem Stück angezeigt werden.

JAWS muss häufig die Anzahl der Leerzellen in einer Zeile oder in einem Teil einer Zeile schätzen. Diese Schätzung basiert auf der Pixelweite. Acht leere Pixel werden als eine Leerzelle angesehen. Indem die Brailleinformationen auf diese Art und Weise angezeigt werden, erhalten Sie eine Rückmeldung darüber, wie diese Informationen optisch präsentiert werden.

Drücken Sie die **8 Pixel Pro Leerschritt Umschalten** Taste, wird die Meldung "Unbegrenzte Pixel pro Leerschritt" angesagt. Mit der Option Unbegrenzte Pixel pro Leerschritt können Sie sich im Text rauf und runter bewegen, und die Zeile ohne Leerzellen lesen. Nur die Leer- und Tabzeichen, die im Dokument gesetzt wurden, werden als Leerzellen angezeigt.

Wenn die Einstellung 8 Pixel pro Leerschritt gewählt ist, können sich Zeilen in ihrer Pixellänge unterscheiden. Wenn Sie also die **BRAILLE RAUF** und **BRAILLE RUNTER** Tasten verwenden, kann es passieren, dass Sie nicht an der gleichen Zeichenposition landen wie bei der vorangegangenen Zeile.

Sie können diese Einstellung jederzeit verändern, indem Sie die Tastenkombination für das Umschalten drücken. Weitere Informationen über die Tastenkombination **8 Pixel Pro Leerschritt Umschalten** finden Sie in der Hilfe für Ihre Braillezeile.

Quelle: Braille_Formatting.htm

## Braille Lern-Modus

Der Braille Lern-Modus ist ein Programm zum Unterrichten und zum Lernen von Braille. Der Braille Lernmodus steht exklusiv für Freedom Scientific PAC Mate und Focus Braillezeilen zur Verfügung. Wenn der Lern-Modus eingeschaltet ist, dann meldet JAWS das Braillesymbol in der Anzeigezelle, sobald Sie die Cursorroutingtaste direkt über der entsprechenden Zelle gedrückt haben. Wenn Sie eine bestimmte Cursor Routingtaste gemeinsam mit dem linken oder rechten Auswahlschalter (Focus 40 Blue und Focus 14 Blue Braillezeilen), oder den Navigationstasten (befinden sich hinter den Cursor Routingtasten auf der PAC Mate Braillezeile, der klassischen Focus 40 Blue und den Focus 40 und 80 Braillezeilen) drücken, dann wird JAWS das Word in Braille ansagen und buchstabieren.

## Den Braille Lern-Modus einschalten

Der Braille Lern-Modus ist standardmäßig ausgeschaltet. Um den Lern-Modus zu starten, gehen Sie bitte folgendermaßen vor:

1. Es muss eine PAC Mate PBD oder eine Focus Braillezeile am Computer angeschlossen sein.
2. Drücken Sie **EINFÜGEN+V** , um die Schnelleinstellung zu öffnen.
3. Im Sucheingabefeld geben Sie "Lernmodus" ohne Anführungsstriche ein.
4. Drücken Sie **PFEIL RUNTER** , um zum Lernmodus in der Strukturansicht zu wechseln und drücken Sie dann **LEERTASTE** , um den Lernmodus einzuschalten. Der Lern-Modus bleibt so lange eingeschaltet, bis Sie ihn wieder ausschalten oder JAWS neu gestartet wird.

## Schneller Zugriff auf den Braille Lern-Modus

Ist der Braille Lern-Modus deaktiviert, dann können Sie jederzeit eine Cursor Routingtaste gemeinsam mit Modus- oder Auswahlschalter auf der Focus 40 Blue und Focus 14 Blue drücken, oder das linke oder rechte Scrollrad gemeinsam mit entweder einer Cursor Routingtaste oder einer Navigationstaste auf der PAC Mate Braillezeile, der klassischen Focus 40 Blue und den Focus 40 und 80 Braillezeilen, um schnell die Funktionalität des Braille Lern-Modus zu nutzen. Dies ist dann hilfreich, wenn Sie einen schnellen Hinweis benötigen, aber den Braille Lern-Modus nicht wie oben beschrieben einschalten möchten.

Um den schnellen Zugriff auf den Braille Lern-Modus mit der Focus 40 Blue oder der Focus 14 Blue Braillezeile zu nutzen, gehen Sie wie folgt vor:

- Drücken Sie **MODUS+CURSORROUTING** , damit JAWS das Braillesymbol im Zeilenmodul ansagt, oder
- Drücken Sie **CURSORROUTING+AUSWAHLTASTE** , damit JAWS das Braillewort ansagt und buchstabiert.

Um den schnellen Zugriff auf den Braille Lern-Modus mit der PAC Mate Braillezeile, der klassischen Focus 40 Blue und den Focus 40 und 80 zu nutzen, gehen Sie wie folgt vor:

- Drücken Sie **SCROLLRAD+CURSORROUTING** , damit JAWS das Braillesymbol im Zeilenmodul ansagt, oder
- Drücken Sie **SCROLLRAD+NAVIGATIONSTASTE** , damit JAWS das Braillewort ansagt und buchstabiert.

**Hinweis:** JAWS arbeitet nach dem Lesen des Braillesymbols oder -wortes normal weiter.

Quelle: Braille_Study_Mode.htm

## Braillebetrachter

Der JAWS Braillebetrachter ist ein Programm, das alles visuell in Textform auf dem Bildschirm wiedergibt und zwar exakt so, wie es JAWS auch auf der Braillezeile darstellt. Der Braillebetrachter funktioniert hierbei unabhängig davon, ob eine Braillezeile angeschlossen ist oder nicht. Der hauptsächliche Zweck des Braillebetrachters ist es, sehenden Personen, Skriptentwicklern oder Testern, die Punktschrift nicht lesen können oder die keinen Zugang zu einer Braillezeile haben, eine Brailleausgabe zur Verfügung zu stellen. Er hilft dabei, die Brailleausgabe, die JAWS an die unterschiedlichen Zeilen schickt, zu verdeutlichen und zu überprüfen.

Der Braillebetrachter gibt die Anzahl der Zellen der aktuell eingesetzten Braillezeile wieder, sofern eine angeschlossen und aktiv ist. Beachten Sie bitte, dass der Braillebetrachter standardmäßig 40 Zellen anzeigt, wenn keine Braillezeile installiert ist, oder wenn diese nicht angeschlossen oder ausgeschaltet ist.

Um den Braillebetrachter zu aktivieren, navigieren Sie in das Menü Hilfsprogramm im JAWS Programmfenster, öffnen Sie das Untermenü Braille- und Textbetrachter und wählen Sie dann den Eintrag Braillebetrachter am Bildschirm anzeigen. Sie können auch die verschachtelte Kurztaste **EINFÜGEN+LEERTASTE** , gefolgt von **B** und dann **B** drücken, um den Braillebetrachter zwischen Ein oder Aus umzuschalten.

Aktiviert erscheint ein Fenster am oberen Rand des Bildschirms, welches exakt das anzeigt, was an die Zellen der Braillezeile gesendet wird. Der Braillebetrachter verkleinert Ihr Anwendungsfenster, um zu vermeiden, dass irgendein Bereich überdeckt wird, den man vielleicht zum Arbeiten braucht, und wird der Braillebetrachter geschlossen, dann wird das Fenster wieder auf Vollbild geschaltet. Sie können festlegen, ob das Fenster am unteren Rand des Bildschirms angezeigt werden soll und Sie können auch die Schriftart, die Schriftgröße und die Vorder- und Hintergrundfarbe des angezeigten Textes anpassen.

Standardmäßig zeigt der Braillebetrachter sowohl Text, als auch das aktuelle Punktschriftmuster in visueller Verbindung, so dass eine sehende Person sehen kann, welches Punktschriftmuster zur Darstellung des Zeichens und der Wörter genutzt wird. Die Inhalte der Statuszellen, die auf einer Braillezeile verwendet werden, um zusätzliche Informationen, wie etwa die aktuelle Cursorposition in einem Dokument, den aktiven Cursor, den aktuell gewählten Elementtyp auf einer Webseite und vieles mehr, anzuzeigen, werden visuell links vom Brailletext angezeigt. Je nach Belieben können Sie auswählen, ob nur Text oder nur Punktschrift angezeigt werden soll und Sie können die Statuszellen ausschalten.

Um die Einstellungen des Braillebetrachters zu konfigurieren, navigieren Sie in das Menü Hilfsprogramm im JAWS Programmfenster, öffnen Sie das Untermenü Braille- und Textbetrachter und wählen Sie dann den Eintrag Einstellungen.

**Hinweis:** Fusion muss im Vollbildmodus ausgeführt werden, damit der Braillebetrachter verwendet werden kann. Wenn ein Anwender bei aktiviertem Braillebetrachter auf Lupe oder geteilte Ansicht wechselt, dann wird dieser angehalten, bis Sie zu einer Vollbildvergrößerung zurückkehren.

## Braillebetrachter Befehle

Drücken Sie **EINFÜGEN+LEERTASTE** , gefolgt von **B** , um die Ebene für den Braille- und Textbetrachter zu aktivieren. Nachdem Sie diese Ebene aktiviert haben, stehen folgende Befehle zur Verfügung:

- Braillebetrachter ein- oder ausblenden **B**
- Ausschnitt nach links: **PFEIL LINKS**
- Ausschnitt nach rechts: **PFEIL RECHTS**
- Vorherige Zeile: **PFEIL RAUF**
- Nächste Zeile: **PFEIL RUNTER**

**Hinweis:** Diese Ebene bleibt aktiviert, während Sie Befehle zum Schwenken oder zur Zeilennavigieren verwenden.

Quelle: Braille_Viewer.htm

## BrailleIn

Die Funktion BrailleIn ermöglicht es Ihnen, Ihren Computer nur mit Ihrer Perkins Braille-Tastatur über sowohl Windows-, als auch anwendungsspezifische Befehle zu steuern. Zusätzlich können Sie sowohl Kurzschrift, als auch Vollschrift auf Ihrer Braille-Tastatur eingeben. Der Vorteil besteht darin, dass Sie nicht länger zwischen der Computer-Tastatur und der Braillezeilen-Tastatur wechseln oder einen speziellen Eingabemodus zur Eingabe von Kurzschrift eingeben müssen, um den Computer zu steuern oder Programme auszuführen. Für eine Liste der Kurztasten, die Freedom Scientific Braillezeilen unterstützen, lesen Sie [Braillezeilen Eingabebefehle](focus/Braille_Display_Input_Commands.htm) . Für andere Braillezeilen kontaktieren Sie bitte den Hersteller der Braillezeile, um eine Liste der Kurztasten zu erhalten.

## Schreiben in Kurzschrift

Mit BrailleIn werden Ihre Eingaben umgehend in der aktuellen E-Mail, im Dokument oder in Formularfeldern in normalen Text übersetzt, wenn Sie über die Perkins-Tastatur Braille-Kurzschrift eingeben. Sollte eine Anwendung oder spezielle Eingabefelder keine Kurzschrift unterstützen, dann sagt JAWS "Computer Braille", sofern die Tutormeldungen eingeschaltet sind. Darüberhinaus wird das Symbol für Computer Braille, Punkte 4-5-6 gefolgt von Punkten 3-4-6, auf der Braillezeile dargestellt, um anzuzeigen, dass Computer Braille benötigt wird.

Die Eingabe in Computer-Braille ist standardmäßig ausgewählt. Um die Braillekurzschrift zu verwenden, gehen Sie bitte folgendermaßen vor:

1. Drücken Sie **EINFÜGEN+F2** und wählen Sie Einstellungsverwaltung.
2. Damit sich Änderungen auf alle Anwendungen auswirken, drücken Sie **STRG+UMSCHALT+D** , um die Standardeinstellungen von JAWS zu laden. Damit Änderungen für eine spezielle Anwendung wirksam werden, wählen Sie diese in der Ausklappliste Anwendungen.
3. Im Sucheingabefeld geben Sie "Übersetzung" ohne Anführungsstriche ein.
4. Drücken Sie **PFEIL RUNTER** , um in der Strukturansicht zu Übersetzung in den gefilterten Suchergebnissen zu gelangen und drücken Sie dann **EINGABE** , um den Fokus direkt in die Gruppe Übersetzung zu platzieren. Mit **PFEIL RECHTS** erweitern Sie die Gruppe.
5. Drücken Sie **LEERTASTE** , um durch die einzelnen Einstellungen in der Ausklappliste Ausgabe zu schalten, um den Modus zum Lesen von Braille auf Ihrer Braillezeile festzulegen. Die erste Option ist immer Computer Braille. Die anderen zur Verfügung stehenden Einstellungen hängen von der aktuell gewählten Sprache ab. Wenn beispielsweise die Sprache auf Deutsch - Deutschland gesetzt ist, was der Standardeinstellung entspricht, dann sind die verfügbaren Ausgabemodi Deutsch Basisschrift, Deutsch Vollschrift und Deutsch Kurzschrift. Wenn Sie die Sprache auf US Englisch einstellen, dann stehen Ihnen Amerikanisches Englisch Grade 1, Amerikanisches Englisch Grade 2, Vereinheitlichtes Englisch Braille Grade 1 und Vereinheitlichtes Englisch Braille Grade 2 zur Verfügung.
6. Drücken Sie **LEERTASTE** , um durch die einzelnen Einstellungen in der Ausklappliste Eingabe zu schalten, um den Eingabemodus für die Brailleeingabe über die Perkins-Tastatur Ihrer Braillezeile festzulegen. Die erste Option ist immer Computer Braille. Die anderen zur Verfügung stehenden Einstellungen hängen vom aktuell gewählten Ausgabemodus ab. Wenn Sie beispielsweise ausgewählt haben, dass Braille in Deutsch Kurzschrift angezeigt wird, dann können Sie für die Eingabe entweder Computerbraille oder Deutsch Kurzschrift wählen. Diese Einstellung ist nicht verfügbar, wenn der gewählte Ausgabemodus Computer Braille ist, oder wenn der gewählte Ausgabemodus keine Eingabe unterstützt.
7. Wählen Sie OK, um Ihre Änderungen zu speichern und die Einstellungsverwaltung zu schließen.

Quelle: JAWS_BrailleIn.htm

## Spezielle JAWS Braille-Kürzel

Die folgenden Braillesymbole werden im strukturierten Modus verwendet, um die unterschiedlichen Steuerelemente zu kennzeichnen. All diese Symbole können Sie im Dialog Optionen für Elementtypen der Einstellungsverwaltung ändern. Um diesen Dialog zu öffnen, gehen Sie bitte folgendermaßen vor:

1. Öffnen Sie die Einstellungsverwaltung und geben Sie "Strukturierten Modus erweitern" im Sucheingabefeld ohne Anführungsstriche ein.
2. Drücken Sie **PFEIL RUNTER** , um zu Erweitert in den gefilterten Suchergebnissen der Strukturansicht zu gelangen.
3. Drücken Sie die **LEERTASTE** . Das Dialogfeld Optionen für Elementtypen wird geöffnet.
4. Drücken Sie **STRG+TAB** , um zwischen den Registerkarten Elementeigenschaften, Statuseigenschaften und HTML Attribute zu wechseln. Lesen Sie [Strukturierten Modus definieren](SettingsCenter.chm::/Braille/General/defining_structured_mode.htm) , um mehr Informationen über diese Registerkarten zu erhalten.

Die folgenden Tabellen enthalten die Braillesymbole.

### Braillesymbole für die Elementtypen in der Datei Default.JCF:

Tabelle: Diese Tabelle enthält die Braille-Kürzel für die Steuerelementeigenschaften aus der Datei Default.JCF.

| Beschreibung der Elementtypen | Braillesymbole der Elementtypen |
| --- | --- |
| Dreifachschalter | 3st |
| Schalter | sltr |
| Schalter Ausklappmenü | -> |
| Schalter Ausklappgitter | sltr-g |
| Listenfeld mit Schaltern | sltrlf |
| Menüschalter | mnüsltr |
| Kontrollfeld | kf |
| Uhr | uhr |
| Spalte | col |
| Spaltenüberschrift | chdr |
| Ausklappliste | akl |
| Befehlsleiste | bflst |
| Kontextmenü | kntxmnü |
| Desktop | desktop la |
| Dialog | dlg |
| Kombiniertes Eingabefeld | kef |
| Eingabefeld | ef |
| Drehfeld | df |
| Erweitertes Listenfeld | xlf |
| Rahmen | Rahmen |
| FTP Link | ftplnk |
| Grafik | img |
| Gruppenfeld | gf |
| Kopfzeile | kpz |
| Überschrift 1 | ü1 |
| Überschrift 2 | ü2 |
| Überschrift 3 | ü3 |
| Überschrift 4 | ü4 |
| Überschrift 5 | ü5 |
| Überschrift 6 | ü6 |
| Kurztaste Eingabefeld | kt |
| Symbolname | smb |
| Image Map Link | imglnk |
| IP Adresse Eingabefeld | ipef |
| Horizontale Bildlaufleiste | lrsb |
| Links-Rechts-Schieber | lrschb |
| Link | lnk |
| Listenfeld | lf |
| Listenansichtseintrag | la |
| Listenansicht | la |
| MDI-Fenster | mdi |
| Menü | mnü |
| Menüleiste | mnülst |
| Mehrzeiliges Eingabefeld | mzef |
| Mehrfach Listenfeld | mlf |
| News Link | nntplnk |
| Gliederung Schalter | gld sltr |
| Passwort Eingabefeld | kwef |
| PDF Signatur | sig |
| Fortschrittsanzeige | fortschritt |
| Auswahlschalter | as |
| Nur-Lesen-Eingabefeld | sef |
| Reihenüberschrift | rhdr |
| Reihe | row |
| Link dieser Seite | selb s lnk |
| Bildlaufleiste | bll |
| SDM Bitmap | bmp |
| SDM Dialog | dlg |
| Mail senden Link | maillnk |
| Drehfeld | df |
| Aufteilen Schalter | asltr |
| Start Schalter | start sltr |
| Startmenü | start mnü |
| Statuszeile | stl |
| Infobereich | Infob |
| Registerkarte | rk |
| Tabelle | tbl |
| Taskleiste | tasklst |
| Umschaltfeld | tasks: |
| Symbolleiste | sl |
| Tool Tipp | tip |
| Verlaufsanzeige | schb |
| Strukturansichtseintrag | sa |
| Strukturansicht | sa |
| Vertikale Bildlaufleiste | aabll |
| Auf-Ab-Schieber | aaschb |
| Upload Eingabefeld | upldef |

### Weitere Braille-Kürzel für die Steuerelementtypen in der Microsoft Outlook.JCF Datei

Tabelle: Zusätzlich zu den in der vorherigen Tabelle beschriebenen Braille-Kürzel, erscheinen die folgenden Braille-Kürzel ebenfalls auf der Seite Steuerelementeigenschaften in der Datei Microsoft Outlook.JCF.

| Beschreibung der Elementtypen | Braillesymbole der Elementtypen |
| --- | --- |
| Kalendergitter |  |
| Kalender Terminfeld |  |
| Nachrichtenliste | lf |

### Braillesymbole für die Statuseigenschaften in der Datei Default.JCF:

Tabelle: Diese Tabelle enthält die Braille-Kürzel für die Statuseigenschaften aus der Datei Default.JCF.

| Beschreibung der Statuseigenschaften | Braillesymbole der Statuseigenschaften |
| --- | --- |
| <Erforderlich> | erf |
| App CTL | App CTL |
| Aktiviert | [x] |
| Geschlossen | + |
| reduziert | + |
| Nicht aktiviert | xx |
| Erweitert | - |
| nicht verfügbar | xx |
| hat Popup | hat Popup |
| Offen | - |
| Teilweise aktiviert | <-> |
| Gedrückt | <=> |
| Untermenü | -> |
| Deaktiviert | < > |
| besucht | bl |

### Braillesymbole für die HTML Attribute in der Datei Default.JCF:

Tabelle: Diese Tabelle enthält die Braille-Kürzel für die HTML Attribute aus der Datei Default.JCF.

| Beschreibung der HTML Attribute | Braillesymbole der HTML Attribute |
| --- | --- |
| longdesc | lgb |
| onclick | klk |
| onmouseover | omo |
| besucht | bl |

Quelle: JAWS_Specific_Braille_Abbreviations.htm

## Den Cursor an- und abkoppeln

Es gibt zwei Einstellungen, die festlegen, wie eine Braillezeile den Cursor, oder der Cursor die Braillezeile beeinflusst.

- Braille folgt Aktiv: Ist diese Einstellung aktiviert, wenn Sie sich in Windows bewegen, dann werden die Informationen beim aktiven Cursor in Braille angezeigt. Wenn Sie sich zum Beispiel durch die Elemente eines Dialogfelds bewegen, dann werden die Informationen des aktiven Elements in Braille angezeigt.
- Aktiv folgt Braille: Ist die Einstellung aktiviert, dann folgt der aktive Cursor dem Braillecursor. Allerdings kann der Braillecursor nicht in Bereiche bewegt werden, in die auch der aktive Cursor nicht hinkommen kann. Ist der PC Cursor aktiv und diese Option gesetzt, dann können Sie mit dem Braillecursor zum Beispiel nicht in die Titelzeile des aktiven Fensters gelangen.

Jede dieser Einstellungen kann dauerhaft über die Einstellungsverwaltung oder temporär über die Schnelleinstellung geändert werden. Für weitere Informationen lesen Sie bitte [Brailleeinstellungen anpassen](braille/adjust_braille_options.htm) .

Es gibt auch Befehle, mit denen diese Einstellung über Tasten der meisten Braillezeilen umgeschaltet werden können. Bei einer Focus Braillezeile drücken Sie zum Beispiel **T** , um den aktiven Cursor an den Braillecursor zu koppeln, und **F** , um den Braillecursor an den aktiven Cursor zu koppeln. Werden diese Befehle genutzt, dann bleiben diese Einstellungen solange aktiv, bis Sie die Einstellung erneut umschalten, oder wenn Sie JAWS schließen und erneut starten. Lesen Sie auch das JAWS Hilfethema für die von Ihnen verwendete Braillezeile, um die speziellen Befehle zum Umschalten dieser Einstellung zu erfahren.

## Weitere Informationen

Im strukturierten Modus verhält sich JAWS so, als ob der aktive Cursor dem Braillecursor folgt und der Braillecursor dem aktiven Cursor folgt, da beide Optionen eingeschaltet sind. In diesem Modus schickt JAWS buchstäblich eine strukturierte Zeile an Informationen an die Braillezeile. Diese Information wird von der Art des aktiven Fensters oder Steuerungselements bestimmt, und nicht notwendigerweise von anderen Einstellungen.

Passen Sie die Einstellung Braille folgt Aktiv und Aktiv folgt Braille an, um das JAWS Verhalten in folgenden Fällen zu ändern:

- Während des Betriebs im Flächenmodus.
- Während der Nutzung des JAWS Cursors.
- Innerhalb des strukturierten Modus, solange keine strukturierten Zeilen vorhanden sind, wie z. B. in einem Dokument der Textverarbeitung.

Unter diesen Bedingungen verhält sich JAWS in folgender Weise:

**Braille folgt Aktiv:** Wenn Sie sich mit der PC Tastatur bewegen, dann zeigt die Braillezeile die Informationen vom Ort, wo der aktive Cursor sich befindet. Schalten Sie Braille folgt Aktiv aus, dann sehen Sie auf der Zeile einen anderen Ausschnitt des Bildschirmes, während Sie unter Nutzung der Sprachausgabe in einem anderen Bereich arbeiten. In Outlook können Sie so zum Beispiel Ihre erhaltenen Nachrichten mit der Sprachausgabe lesen, während die Braillezeile die Anzahl der Nachrichten überwacht, die in der Statuszeile angezeigt wird.

**Aktiv folgt Braille:** Wenn Sie sich mit den Funktionstasten der Braillezeile bewegen, dann folgt der aktive Cursor dem Braillecursor. Schalten Sie diese Einstellung aus, um andere Bereiche des Bildschirms zu lesen, ohne den aktiven Cursor zu bewegen. Diese Funktion ist sehr hilfreich, wenn Sie in einer Textverarbeitung schreiben, da Sie andere Bereiche des Dokuments lesen können, ohne die Schreibmarke von seinem Platz zu entfernen, wo Sie schreiben.

Braille folgt Aktiv ist standardmäßig eingeschaltet, und Aktiv folgt Braille ist standardmäßig ausgeschaltet.

Die Befehl Ziehe Braillecursor zum aktiven Cursor, bewegt den Braillecursor schnell an die Stelle des aktiven Cursors. Lesen Sie auch das JAWS Hilfethema für die von Ihnen verwendete Braillezeile, um die speziellen Befehle zu erfahren.

Quelle: Linking_and_Unlinking_the_Cursor.htm

## Mehrzeilige Braille-Unterstützung

JAWS unterstützt nun vollständig die mehrzeilige Braille-Ausgabe auf kompatiblen Braillezeilen. Derzeit werden die Braillezeilen Monarch von American Printing House for the Blind (APH) und Dot Pad von Dot Inc unterstützt. Beachten Sie, dass Sie die JAWS-Mehrzeilenfunktion auf dem Monarch nur nutzen können, wenn Sie die Firmware-Version 1.3 oder höher verwenden.

Mehrzeilige Braillezeilen sind ein großer Fortschritt im Bereich der Braille-Zugänglichkeit, der es Benutzern ermöglicht, komplexe Inhalte natürlicher und effizienter als je zuvor zu nutzen. Mit einer unterstützten Braillezeile können JAWS-Anwender mehrere Zeilen Inhalt gleichzeitig anzeigen lassen – ähnlich wie beim Betrachten eines kleinen Bildschirms. Beispiel:

- Lesen Sie mehrere Zeilen Inhalt, einschließlich ganzer Absätze, und reduzieren Sie so die Notwendigkeit des ständigen Bildlaufs.
- Verschaffen Sie sich einen besseren Überblick über die Struktur und Anordnung von Spalten und Zeilen in Tabellen, Diagrammen und Tabellenkalkulationen.
- Lesen Sie Formatierungen wie Einrückungen, Ausrichtung und Aufzählungszeichen genauso wie auf Papier.

## Lesemodi

Wenn JAWS die Ausgabe an eine mehrzeilige Braillezeile sendet, stehen je nach Lesekontext zwei unterschiedliche Lesemodi zur Verfügung.

- **Umbruchmodus:** Der Text fließt natürlich über Zeilen hinweg und bricht Wörter an der richtigen Stelle um, sodass der Text nicht geteilt wird, was den Lesefluss unterbrechen könnte. Dieser Modus ist ideal zum Lesen von Büchern, Artikeln oder E-Mails, wenn Sie einfach ununterbrochen lesen möchten. Beim Nachführen werden alle Zeilen der Anzeige mit dem Inhalt des nächsten Textsegments aktualisiert.
- **Zugeschnittener Modus:** Zeigt feste Abschnitte von Zeilen an, wie beispielsweise den Anfang, die Mitte oder das Ende. Dieser Modus eignet sich am besten für strukturierte Inhalte wie Tabellen und Kalkulationen, sodass Sie sehen können, wie Inhalte vertikal ausgerichtet sind, einschließlich der Positionierung von Spaltenüberschriften oder zentrierten Titeln. Alle Zeilen werden zusammen verschoben, und der Zeilenumbruch wird für eine vorhersehbare Formatierung deaktiviert.

JAWS verwendet automatisch den geeigneten Modus, je nachdem, was Sie gerade lesen. Standardmäßig verwendet JAWS beim Vorlesen von Absätzen, Listen oder allem, was nicht als tabellarische Daten gilt, immer den Umbruchmodus. Wenn der Fokus auf eine Tabelle in Microsoft Word, Google Docs oder auf einer Webseite gesetzt wird, verwendet JAWS automatisch den Zugeschnittenen Modus und zeigt außerdem ein Spaltentrennzeichen an, das durch die Punkte 4-5-6-8 dargestellt wird, um die Trennung zwischen den Spalten leicht erkennbar zu machen.

Insbesondere in Excel wird ausschließlich der Zugeschnittene Modus zum Lesen von Tabellenkalkulationen verwendet, und ein Wechsel zwischen den Modi ist nicht möglich. Dadurch können Spalten- und Zeilendaten zusammen mit ihren Koordinaten in Arbeitsblättern und Tabellen korrekt angezeigt werden. Außerdem bleiben die Zellüberschriften oben auf dem Bildschirm fixiert, während die übrigen Zeilen mit den Zeilen und Koordinaten der aktiven Zelle aktualisiert werden, während Sie navigieren. Wenn Monitorzellen in den JAWS-Schnelleinstellungen definiert wurden, werden diese ebenfalls zur schnellen Referenz in der letzten Zeile angezeigt.

Um den aktiven Modus zu bestätigen, drücken Sie **ALT+EINFÜGEN+V** , um das Dialogfeld Braille-Ansicht auswählen zu öffnen. Der aktuell verwendete Modus wird in der Liste ausgewählt. Da JAWS den Modus automatisch entsprechend dem Lesekontext umschaltet, sollten Sie den Lesemodus nur unter ganz bestimmten Umständen manuell einstellen müssen. Beispielsweise möchten Sie möglicherweise vorübergehend den zugeschnittenen Modus verwenden, um die vertikale Ausrichtung einer Liste in Microsoft Word zu überprüfen.

## Einstellungen für den Zugeschnittenen Modus konfigurieren

Wenn der Zugeschnittene Modus aktiv ist, stehen zusätzliche Einstellungen zur Verfügung, mit denen Sie die Anzeige strukturierter Inhalte anpassen können.

1. Drücken Sie **ALT+EINFÜGEN+V** , um den Dialog Braille-Ansicht auswählen zu öffnen.
2. Wählen Sie Optionen.
3. Navigieren Sie zu einer der folgenden Optionen und ändern Sie die Einstellungen mit der **LEERTASTE** .
  - **Ausrichtungsbegrenzer** - Nützlich beim Anzeigen einer CSV-Datei (Komma-getrennte-Werte) in Notepad oder einem anderen Texteditor. Damit können Sie das Zeichen auswählen, welches die Grenze zwischen den Spalten darstellt. Verfügbare Optionen sind Keine Ausrichtung, Tabulatorzeichen, Komma, Vertikaler Balken oder Semikolon. Wenn Sie beispielsweise eine Reihe von durch Kommas getrennten Zahlen gefolgt von einer Reihe größerer Zahlen haben, sorgt die Wahl des Kommas als Trennzeichen dafür, dass alles korrekt auf dem Display ausgerichtet wird.
  - **Spaltenanzeiger** - Verwenden Sie diese Option, um auszuwählen, ob die Spaltentrennzeichenanzeige (Punkte 4-5-6-8) in Excel-Tabellen oder für Tabellen in Microsoft Word und Google Docs angezeigt werden soll.
  - **Punkte zur Orientierung** - Wenn diese Option aktiviert ist, wird eine Reihe von drei Punkten angezeigt, die zu der rechtsbündigen Nummer führen, ähnlich wie in einem Inhaltsverzeichnis. Nützlich, wenn die Finger eines Schülers beim Lesen von Zahlenkolonnen dazu neigen, von der aktuellen Zeile abzuweichen.
4. Wenn Sie Ihre Auswahl getroffen haben, drücken Sie **EINGABE** , um den Dialog zu schließen.

Quelle: Multiline_Braille.htm

## Text auf einer Braillezeile markieren

JAWS verwendet die Cursorroutingtasten auf Ihrer Braillezeile auch zum Markieren von Text. Gehen Sie folgendermaßen vor, wenn Sie Text markieren möchten:

1. Bewegen Sie die Braillezeile so weit, bis der Text erscheint, den Sie markieren möchten.
2. Halten Sie die **LINKE UMSCHALTTASTE** gedrückt und drücken Sie die Cursorroutingtaste über dem Zeichen, welches Sie als Beginn der Auswahl verwenden möchten.
3. Lesen Sie so lange weiter, bis Sie den Text erreicht haben, bei dem die Markierung enden soll.
4. Halten Sie die **LINKE UMSCHALTTASTE** gedrückt und drücken Sie die Cursorroutingtaste über dem Zeichen, welches Sie als Ende der Auswahl verwenden möchten. JAWS markiert dann den gesamten Text zwischen dem ersten und letzten Zeichen.

Unterschiedliche Braillezeilen können über andere Methoden zum Textmarkieren verfügen. Lesen Sie die Dokumentation zu Ihrer speziellen Braillezeile, um eine Liste aller Befehle zu erhalten.

Quelle: Selecting_Text_on_a_Braille_Display.htm

## Braille-Teilung

Springe zu [Braillezeilenbefehle für Braille-Teilung](#SplitBrailleCommands) .

Mit der Freedom Scientific Funktion Braille-Teilung können Sie Inhalte aus zwei verschiedenen Positionen auf einer Braillezeile in einer von mehreren Ansichtsarten anzeigen. Diese Funktion ist sowohl für herkömmliche einzeilige Braillezeilen als auch für mehrzeilige Braillezeilen verfügbar. Wenn eine Braille-Teilungsansicht aktiviert ist, wird die Braillezeile in zwei Bereiche unterteilt. Standardmäßig:

- Bei einzeiligen Braillezeilen enthält die linke Hälfte der Braillezeile den ersten Bereich mit dem Inhalt an Ihrer aktuellen Position, während die rechte Hälfte den zweiten Bereich mit dem geteilten Inhalt basierend auf der aktiven Ansicht enthält. Der Trennindikator, dargestellt durch zwei vertikale Linien, wird in einer Zelle zwischen den Bereichen angezeigt.
- Bei mehrzeiligen Braillezeilen wird in den oberen Zeilen der erste Bereich mit dem Inhalt an Ihrer aktuellen Position angezeigt, während in den unteren beiden Zeilen der zweite Bereich mit dem geteilten Inhalt basierend auf der aktiven Ansicht angezeigt wird. Der Trennindikator, dargestellt durch eine einzelne Linie aus Strichen (Punkte 3-6), wird zwischen den Regionen angezeigt.

## Auswahl einer geteilten Braille-Ansicht

Um die geteilte Braille-Ansicht einzuschalten, drücken Sie **ALT+EINFÜGEN+V** ( **ALT+FESTSTELLTASTE+V** im Laptop Layout), um das Dialogfenster Braille-Ansicht auswählen zu öffnen. Sobald sich dieses Dialogfenster öffnet, befinden Sie sich in einer Liste mit verfügbaren Ansichten. Wählen Sie die Ansicht, die Sie verwenden möchten und drücken Sie dann **EINGABE** . Die aktive Ansicht bleibt für die aktuelle JAWS Sitzung bestehen. Wenn Sie JAWS neu starten, werden alle Standardeinstellungen wiederhergestellt, die vor der Aktivierung einer bestimmten Ansicht genutzt wurden.

Im Folgenden finden Sie eine Übersicht über die verfügbaren geteilten Ansichten, die im Dialogfeld Braille-Ansicht auswählen aufgeführt sind.

### Keine Teilung

JAWS sendet Inhalte wie bisher auch an die Braillezeile, unter Verwendung der vollen Braillezeilenlänge der aktuellen Zeile. Dies ist die Standardeinstellung.

Bei mehrzeiligen Anzeigen wird Keine Teilung durch die Optionen Umgebrochener und Zugeschnittener Modus ersetzt.

### Gepufferter Text

Diese Ansicht erfasst den Text an der aktuellen Position und legt ihn in einem Puffer ab, der im Bereich 2 der geteilten Zeile angezeigt wird. Sobald der Puffer erstellt ist, können Sie zu einer anderen Stelle im aktuellen Dokument navigieren und sogar zu einem völlig anderen Dokument oder Anwendungen wechseln, während der gepufferte Text verfügbar bleibt. So können Sie beispielsweise Text auf einer Webseite puffern, mit **ALT+TAB** zu einem geöffneten Dokument in Word oder im Editor wechseln und Ihr gepufferter Text bleibt in Region 2 Ihrer Braillezeile verfügbar.

- Schnelles Vergleichen von Informationen zwischen zwei Quellen.
- Halten Sie einen Textblock oder eine Zahlenfolge zum einfachen Nachschlagen bereit, damit Sie sich diese nicht merken müssen.
- Behalten Sie beim Verfassen einer Antwort eine Prüfungsfrage oder eine mathematische Gleichung im Blick, wenn die Antwort an einer anderen Stelle als die Frage platziert werden muss.
- Text bei der Recherche zu einem Thema verfügbar halten.

Standardmäßig puffert diese Ansicht das aktuelle Dokument. Um den Textbereich, der gepuffert werden soll, zu ändern, öffnen Sie das Dialogfenster Braille-Ansicht auswählen, stellen Sie sicher, dass in der Liste der Ansichten **Gepufferter Text** ausgewählt ist, wählen Sie dann **Einstellungen** und ändern Sie die **Puffer-Einheit** . Die Auswahlmöglichkeiten sind:

- **Absatz** : Puffert den aktuellen Absatz.
- **Dokument** : Puffert bis zu 64 KB des aktuellen Dokuments.
- **Gewählten Text** : Puffert jeden aktuell gewählten Text. Beachten Sie, dass der ausgewählte Text in Bereich 2 nicht automatisch aktualisiert wird, wenn sich die Auswahl ändert. Wenn Sie einen anderen Text auswählen, dann müssen Sie im Dialogfenster Braille-Ansicht auswählen wieder **Gepufferter Text** wählen und dann **Gewählten Text** im Einstellungsdialog wählen, um den Puffer zu aktualisieren.
- **Zwischenablagetext** : Puffert den Inhalt der Windows-Zwischenablage, so dass Sie den zweiten Bereich effektiv als Notizenbereich nutzen können, in dem Sie Inhalte von verschiedenen Positionen einbringen und leicht darauf verweisen können. So können Sie beispielsweise Text mit **STRG+C** kopieren, weiteren Text von anderen Quellen auswählen und mit **EINFÜGEN+WINDOWS+C** an die Zwischenablage anhängen, dann die Ansicht Gepufferten Text aktivieren und Zwischenablagetext auswählen, um alle Ihrer gesammelten Informationen im Bereich 2 anzuzeigen und nach Bedarf zu verwenden.

Um den Puffer zu aktualisieren, öffnen Sie das Dialogfeld Braille-Ansicht auswählen und wählen Sie erneut die Option **Gepufferter Text** , um den Puffer mit den neuesten Inhalten zu aktualisieren. Aklternativ öffnen Sie das Dialogfenster Teilungs-Ansicht auswählen, stellen sicher, dass **Gepufferter Text** ausgewählt ist, wählen Sie **Einstellungen** und wählen Sie dann die Einstellung **Zwischengespeichertes Dokument mit Eingabetaste aktualisieren** . Sobald diese Funktion aktiviert ist, wird das aktuelle Dokument gepuffert und der Puffer wird automatisch mit dem neuesten Text aktualisiert, sobald Sie die **Eingabetaste** drücken. Dies ist in Situationen nützlich, in denen der Puffer während der Eingabe ständig aktualisiert werden soll.

Sie verwenden beispielsweise ein Word-Dokument, um ein komplexes mathematisches Problem Schritt für Schritt zu lösen, wobei jeder Schritt in eine eigene Zeile gesetzt wird. In diesem Fall wird nach der Eingabe des mathematischen Ausdrucks für einen Schritt und dem Drücken von **ENTER** der neueste mathematische Inhalt in den Puffer im Bereich 2 eingefügt. Während Sie mit der Lösung des Problems fortfahren, können Sie unabhängig voneinander durch den Puffer blättern, um Ihre Arbeit zu überprüfen, während Sie weiterhin an der aktuellen Position im aktiven Dokument bleiben.

### Anmerkungen

Diese Ansicht ist vor allem in Word nützlich, für die Überprüfung von Kommentaren, Überarbeitungen, Fußnoten oder Endnoten. Befindet sich der Cursor auf einem Text, der eine Anmerkung enthält, wird der Text des Dokuments in der ersten Region angezeigt, während der Text der Anmerkung in der zweiten Region angezeigt wird. Wenn die aktuelle Zeile oder der Text an der Cursorposition keine Anmerkungen enthält, wird die gesamte Braillezeile für die Textzeile verwendet und nicht geteilt. In dieser Ansicht kann der Text eines Kommentars, einer Überarbeitung, einer Fußnote oder einer Endnote gleichzeitig mit dem Haupttext angezeigt werden, auf den er sich beziehen. Sie können den Text des Dokuments bearbeiten und lesen, während Sie den Anmerkungstext im Blick behalten.

**Hinweis:** Die besten Ergebnisse beim Überprüfen von überarbeitetem Text in der Anmerkungsansicht erzielen Sie, wenn Sie die Nachverfolgungsansicht in Word auf **Markup: alle** einstellen.

### Attributkennzeichen

In dieser Ansicht wird der Text der aktuellen Zeile in der ersten Region angezeigt, während alle Textattribute wie fett, kursiv oder unterstrichen, die der aktuellen Zeile entsprechen, in der zweiten Region angezeigt werden. Das Drücken einer **Cursorroutingtaste** auf einem Attribut bewegt den Cursor automatisch zu dem Zeichen, das mit dem Attribut übereinstimmt. Beim Navigieren durch das Dokument werden auch die Attribute aktualisiert.

Bei Verwendung dieser Ansicht auf einer mehrzeiligen Braillezeile werden Attribute direkt unterhalb der aktiven Zeile angezeigt, die den zugehörigen Text enthält, ohne dass dazwischen ein Trennzeichen steht. Wenn Sie sich beispielsweise in einem Dokument auf einer Zeile befinden, die sowohl fettgedruckten als auch normalen Text enthält, können Sie Ihre Finger zwischen der aktiven Zeile und der darunter liegenden Zeile bewegen, um die Textattribute schnell zu überprüfen.

Diese Ansicht verbessert die Erlebnisse beim Korrekturlesen und Bearbeiten, da die Braillezeile nun gezielt anzeigen kann, ob Text unterstrichen, fett oder kursiv ist, während der Haupttext des Dokuments weiterhin angezeigt wird.

Wenn der Text an der Cursorposition in Bereich 1 mehr als ein Attribut hat, z. B. fett und kursiv, dann rotieren die Attribute im Bereich 2 für dieses Wort oder diesen Satz mit den Buchstaben "f" und "k". Bei den übrigen Wörtern ohne ein bestimmtes Attribut wird in Bereich 2 der Buchstabe "n" angezeigt.

### Sprachverlauf

Wenn diese Ansicht aktiviert ist, dann zeigt die erste Region den aktuell fokussierten Text, während der zweite Bereich Text des JAWS Sprachverlaufs anzeigt. Beispiele, wo diese Ansicht nützlich sein könnte:

- Überprüfen Sie in Teams die Schreibweise des Namens eines Teilnehmers, der gerade einer Besprechung beigetreten ist. Wenn eine Person an einer Besprechung teilnimmt, werden diese Informationen derzeit nur per Sprache angesagt.
- In manchen Situationen kann die Sprache zusätzliche Informationen liefern, die in Braille nicht immer verfügbar sind. Die Einstellung der geteilten Braille-Ansicht auf Sprachverlauf ermöglicht es taubblinden Benutzern, auf Sprachinhalte zuzugreifen, ohne dass der gesamte Braille-Ausgabemodus auf Sprachausgabe umgestellt werden muss. Dies kann auch für diejenigen von Vorteil sein, die nur die Brailleausgabe verwenden möchten.
- Verwenden Sie es, um wichtige JAWS Meldungen oder Texte zu verfolgen, während Sprache auf Abruf aktiviert ist.

### Übersetzungsteilung

Diese Ansicht ist vorteilhaft für Lehrer, Studenten und andere Benutzer, die die Brailleschrift lernen, da sie zwei verschiedene Übersetzungsausgaben des aktuellen Textes anzeigt. Wenn JAWS z.B. so konfiguriert ist, dass deutsche Braillekurzschrift verwendet wird, dann wird dies in der ersten Anzeigeregion angezeigt, während die Darstellung in Computerbraille desselben Textes in der zweiten Region angezeigt wird.

Um die in der zweiten Region angezeigte Übersetzungsausgabe anzupassen, öffnen Sie das Dialogfenster Braille-Ansicht auswählen, stellen Sie sicher, dass in der Liste der Ansichten die Option **Übersetzungsteilung** ausgewählt ist, aktivieren Sie dann den Schalter **Einstellungen** und wählen Sie aus der Liste **Geteilte Übersetzung Region 2** den gewünschten Übersetzungsmodus. Standardmäßig ist Computerbraille ausgewählt. Die übrigen Auswahlmöglichkeiten hängen von Ihrem derzeit konfigurierten Übersetzungsausgabemodus und Ihrem derzeit aktiven Braille-Sprachprofil ab.

Wenn JAWS zum Beispiel so konfiguriert ist, dass es Text in Kurzschrift anzeigt, dann können Sie wählen, ob Sie Computerbraille, oder eine andere Kurzschriftvariante in Region zwei anzeigen möchten.

Wenn Ihre Brailleausgabe darüberhinaus auf Computerbraille oder Vollschrift eingestellt ist, dann bewirkt das Einschalten der Übersetzungsteilung, dass JAWS die Kurzschrift in Ihrer aktuellen Sprache im Bereich 1 anzeigt, während Ihr aktueller Ausgabemodus weiterhin im Bereich 2 angezeigt wird. Wenn Ihr Standard-Ausgabemodus beispielsweise Deutsche Vollschrift ist, dann zeigt JAWS die deutsche Kurzschrift im Bereich 1 an, während die Vollschrift im Bereich 2 angezeigt wird.

Die Übersetzungsteilung ist anwendungsabhängig. So können Sie diese Ansicht beispielsweise für den Editor einschalten und eine andere Ansicht in Word oder Outlook verwenden.

### JAWS Cursor

In dieser Ansicht zeigt Bereich 1 die Position des PC Cursors, während der Bereich 2 die Textzeile an der Position des JAWS Cursors anzeigt. Befinden Sie sich in einer Anwendung, die den JAWS Cursor nicht unterstützt, dann bleibt diese Regionsanzeige leer. Diese Ansicht ist hilfreich, wenn Sie während der Arbeit an einem Dokument einen Fortschrittsbalken oder eine Anwendungsstatusleiste aktiv überwachen möchten. Sie kann auch dazu verwendet werden, die Titelleiste zu lesen, wenn Sie zwischen mehreren geöffneten Dokumenten wechseln.

### Fenstertext

Mit dieser Ansicht können Sie den Text eines bestimmten Dialogs oder Anwendungsbildschirms aktiv überwachen, während Sie sich mit dem Fokus an einer anderen Stelle der gleichen Anwendung befinden. Ist diese Funktion aktiviert, dann wird der Text des gerade aktiven Fensters im Bereich 2 angezeigt. Ändert sich der Text im Fenster, dann wird er sofort in der Anzeige aktualisiert. Wird das Fenster geschlossen, dann wird der Bereich, der den Fenstertext anzeigte, geleert. Der Bereich wird auch leer bleiben, wenn Sie diese Ansicht in einer Anwendung aktivieren, die das Abrufen von Fenstertext nicht unterstützt.

### Anwendungsabhängige Ansichten

Für Excel, Outlook, PowerPoint und Teams stehen zusätzliche anwendungsabhängige Ansichten zur Verfügung, um die Produktivität beim Zugriff auf Informationen in diesen Anwendungen mit Braillezeilen zu verbessern. Wenn Sie das Dialogfenster Braille-Ansicht auswählen aus einer dieser Anwendungen heraus öffnen, sind die folgenden zusätzlichen Ansichten verfügbar.

- In Excel können Sie wählen, ob Sie die aktive Zelle in Bereich 1 und die über die JAWS-Schnelleinstellungen zugewiesenen Zellen in Bereich 2, die aktive Zelle in Bereich 1 und die definierten Zeilen- und Spaltensummen in Bereich 2 oder die Titel und Formeln in Bereich 1 und die aktive Zelle in Bereich 2 anzeigen möchten. Diese Ansichten sind auf mehrzeiligen Braillezeilen nicht verfügbar, da in Excel immer der zugeschnittene Modus verwendet wird, der die beste Erfahrung für die Überprüfung von Tabellenkalkulationsinhalten in einer mehrzeiligen Umgebung bietet.
- Wenn in Outlook Classic die Nachrichtenvorschau aktiviert ist (Standardeinstellung), können Sie festlegen, dass die Nachrichtenliste in der ersten Region angezeigt wird, während der Inhalt der aktuellen Nachricht in der zweiten Region angezeigt wird. Mit aktiviertem Outlook-Vorschaufenster als auch mit der Nachrichtenliste mit Vorschaufenster, können Sie Ihre Nachrichten lesen und sich durch diese bewegen, ohne den Posteingang zu verlassen.
- In PowerPoint können Sie festlegen, dass Ihre Hauptfolienpräsentation in der ersten Region angezeigt wird, während die Referentenhinweise in der zweiten Region angezeigt werden. Während einer PowerPoint-Präsentation hilft die Möglichkeit, Notizen gleichzeitig mit der aktuellen Folie zu überprüfen, den Fluss der Präsentation aufrechtzuerhalten.
- Wenn Sie in Teams eine Nachricht in einem Teams-Chat eingeben oder bearbeiten, können Sie festlegen, dass der Chatverlauf in der zweiten Region angezeigt wird. Auf diese Weise können Sie den Verlauf unabhängig überprüfen und verlieren nicht Ihren Platz in der Nachricht, die Sie gerade bearbeiten oder verfassen.

## Ändern der Position des geteilten Bereichs

Sie können die Position des Bereichs, der den geteilten Inhalt enthält, anpassen.

1. Drücken Sie **ALT+EINFÜGEN+V** , um den Dialog Braille-Ansicht auswählen zu öffnen.
2. Wählen Sie Optionen.
3. Navigieren Sie in der Liste der Optionen zu Geteilte Daten anzeigen und verwenden Sie die **LEERTASTE** , um die Einstellung umzuschalten.
  - Bei einzeiligen Braillezeilen können Sie wählen, ob der geteilte Bereich rechts (Standardeinstellung) oder links angezeigt werden soll.
  - Bei mehrzeiligen Braillezeilen können Sie wählen, ob der geteilte Bereich unten (Standardeinstellung), oben oder unterhalb der aktiven Zeile mit dem Cursor angezeigt werden soll.
4. Wenn Sie Ihre Auswahl getroffen haben, drücken Sie **EINGABE** , um den Dialog zu schließen.

## Konfigurieren des Trennzeichens

Sie können wählen, ob die Zeichen, die die Trennung zwischen den beiden Anzeigebereichen anzeigen, angezeigt werden sollen oder nicht.

1. Drücken Sie **ALT+EINFÜGEN+V** , um den Dialog Braille-Ansicht auswählen zu öffnen.
2. Wählen Sie Optionen.
3. Navigieren Sie in der Liste der Optionen zu Trennungslinie anzeigen und verwenden Sie die **LEERTASTE** , um die Einstellung umzuschalten. Diese Einstellung ist standardmäßig aktiviert.
4. Wenn Sie Ihre Auswahl getroffen haben, drücken Sie **EINGABE** , um den Dialog zu schließen.

## Anpassen der Zeilenanzahl für den geteilten Bereich (nur bei mehrzeiligen Braillezeilen)

Standardmäßig werden auf mehrzeiligen Braillezeilen zwei Zeilen verwendet, um den geteilten Bereich darzustellen. Um dies zu ändern:

1. Drücken Sie **ALT+EINFÜGEN+V** , um den Dialog Braille-Ansicht auswählen zu öffnen.
2. Wählen Sie Optionen.
3. Navigieren Sie in der Liste der Optionen zu Für geteilte Daten verwendete Zeilen und wählen Sie mit der **LEERTASTE** die Anzahl der Zeilen aus.
4. Wenn Sie Ihre Auswahl getroffen haben, drücken Sie **EINGABE** , um den Dialog zu schließen.

## Braillezeilenbefehle für die Braille-Teilung

Nachstehend finden Sie Befehle für verschiedene Braillezeilen zur Steuerung der Braille-Teilungsfunktion.

### Freedom Scientific Focus Braillezeilen

| Beschreibung | Befehl |
| --- | --- |
| Dialog Brailleansicht auswählen öffnen | LINKE UMSCHALT+PUNKTE 1-2-7 |
| Gepufferten Textmodus umschalten | LINKE UMSCHALT+PUNKTE 2-3 |
| Umschalten der Einstellung Zwischengespeichertes Dokument mit Eingabetaste aktualisieren | LINKE UMSCHALT+PUNKTE 2-3-7 |
| Im Bereich der Teilungsansicht bewegen | RECHTER NAVIGATIONSKIPPSCHALTER |
| Im Bereich der Teilungsansicht zeilenweise navigieren | RECHTE KIPPTASTE |
| Ein Lesezeichen im gepufferten Textmodus setzen | LINKE UMSCHALT+PUNKTE 1-2 gefolgt von LINKE UMSCHALT+PUNKT 1 bis 8 |
| Zu einem Lesezeichen im gepufferten Textmodus springen | LINKE UMSCHALT+PUNKTE 1-2 gefolgt von PUNKT 1 bis 8 |
| An den Anfang des Puffers im gepufferten Textmodus springen | LINKE UMSCHALT+PUNKTE 1-2 gefolgt von PUNKTEN 1-2-3 |
| An das Ende des Puffers (letzte nicht leere Zeile) im gepufferten Textmodus springen | LINKE UMSCHALT+PUNKTE 1-2 gefolgt von PUNKTEN 4-5-6 |
| Text im Bereich der Teilungsansicht markieren | Drücken Sie eine UMSCHALTTASTE zusammen mit einer Cursorroutingtaste am Anfang des Textes, den Sie markieren möchten und dann noch einmal am Ende, um die Auswahl abzuschließen |

### HumanWare Braillezeilen

Von HumanWare werden die Braillezeilen der Brailliant BI 40 Serie und die Mantis Q40 unterstützt.

| Beschreibung | Befehl |
| --- | --- |
| Dialog Brailleansicht auswählen öffnen | Vierte Daumentaste+C1+C2+C3+C6 ( ALT+FESTSTELLTASTE+V auf der Mantis Q40 mit JAWS im Laptop Tastaturlayout) |
| Gepufferten Textmodus umschalten | C1+C2+C3 (nicht verfügbar für Mantis Q40) |
| Im Bereich der Teilungsansicht bewegen | Dritte und vierte Daumentaste |
| Im Bereich der Teilungsansicht zeilenweise navigieren | C6+Dritte und vierte Daumentaste (nicht verfügbar für Mantis Q40) |
| Text im Bereich der Teilungsansicht markieren | Drücken Sie die Erste Daumentaste zusammen mit einer Cursorroutingtaste am Anfang des Textes, den Sie markieren möchten und dann noch einmal am Ende, um die Auswahl abzuschließen |

### Papenmeier Braillezeilen

| Beschreibung | Befehl |
| --- | --- |
| Dialog Brailleansicht auswählen öffnen | Gleichzeitig K1 und Navigationsleiste nach rechts |
| Geteilte Ansicht und den aktiven Dokumentbereich tauschen | Gleichzeitig K1 und Navigationsleiste nach links |
| Im Bereich der Teilungsansicht bewegen | Gleichzeitig K4 und Navigationsleiste nach rechts oder links |
| Im Bereich der Teilungsansicht zeilenweise navigieren | Gleichzeitig K4 und Navigationsleiste nach oben oder unten |

### Monarch Braillezeile

| Beschreibung | Befehl |
| --- | --- |
| Dialog Brailleansicht auswählen öffnen | PUNKTE 1-2-7 CHORD |
| Im Bereich der Teilungsansicht bewegen | Linke oder Rechte Zoom Taste oder LEERTASTE+Linke oder Rechte Lesetaste |

### Dot Pad Braillezeile

| Beschreibung | Befehl |
| --- | --- |
| Dialog Brailleansicht auswählen öffnen | F1+F4 Tasten |
| Im Bereich der Teilungsansicht bewegen | F1 und F4 Tasten |

Quelle: Split_Braille.htm

## Statuszellen

Die meisten Braillezeilen verfügen über **Statuszellen** , die sich im allgemeinen auf der linken Seite der Braillezeile befinden. Diese Zellen erweitern auf hervorragende Weise das Lesen mit Braille und das Erkennen von Textformatierungen. Die Anzahl der Statuszellen auf Ihrer Braillezeile beeinflusst die Art und den Umfang der angezeigten Informationen.

Wenn Ihre Braillezeile über fünf Statuszellen verfügt, zeigen die Zellen 1 bis 3 Ihre horizontale (x-Achse) Pixelposition (wenn Sie einen Bildschirmcursor verwenden), die Zeilennummer (wenn Sie den virtuellen Cursor verwenden) und/oder die Indexnummer der Sprachausgabe (wenn Sie den Sprachausgabemodus verwenden) an. Die vierte Zelle meldet den aktiven Cursor: PC Cursor (p), Virtueller Cursor (v), JAWS Cursor (j), Unsichtbarer Cursor (i) oder Braillecursor (b). Die fünfte Zelle meldet den aktiven Braillemodus: Fläche (l), Strukturiert (s), Sprachausgabe (x) oder Attribut (i).

Wenn Ihre Braillezeile über vier Statuszellen verfügt, zeigt JAWS die gleichen Informationen an, meldet aber nicht den aktiven Braillemodus. Wenn Ihre Braillezeile über zwei oder drei Statuszellen verfügt, zeigt JAWS nur den aktiven Cursor und den aktiven Braillemodus in den Statuszellen an.

Wenn Sie ein Element im Strukturierten Modus fokussieren, dann wir der Elementtyp standardmäßig in den Statuszellen angezeigt. Beispielsweise wird kf für Kontrollfeld oder sltr für Schalter angezeigt, wenn Sie auf diesen Steuerelementtypen landen. Wenn Sie auf mehrere Typen treffen, die in den Statuszellen angezeigt werden müssen, dann werden die Symbole für jeden einzelnen Typ mit einem einzelnen Zeichen kombiniert, damit diese in die Statuszellen der Braillezeile passen. Wenn Sie zum Beispiel innerhalb eines Links auf eine Grafik treffen, dann würden Sie ilnk angezeigt bekommen. Wenn die Grafik Teil einer Überschrift der Ebene 1 ist, dann würden Sie iü1 sehen. Wenn der grafische Link Teil einer Überschrift der Ebene 2 wäre, dann würden Sie ilü2 sehen, wenn die Braillezeile über 4 Statuszellen verfügt, oder nur ilü, wenn die Braillezeile nur über drei Statuszellen verfügt.

Zusammen mit den Statuszellen zeigen die **Punkte 7** und **8** an, ob es auf der aktuellen Zeile mehr Text gibt als auf der Braillezeile dargestellt werden kann.

Beispiel:

- Wenn die **Punkte 7** und **8** in allen Zellen auf Ihrer Braillezeile gesetzt sind, dann wird die strukturierte oder aktuelle Textzeile vollständig dargestellt.
- Wenn der Text nur auf einer Seite Ihrer Braillezeile angezeigt wird, dann sind die **Punkte 7** und **8** auf den Statuszellen für jene Seite gesetzt, und für die andere nicht.
- Wenn noch eine weitere Textzeile auf der rechten Seite der Braillezeile angezeigt werden soll, dann sind die **Punkte 7** und **8** in der letzten Statuszelle nicht gesetzt.
- Wenn zwei oder mehr komplette Textzeilen auf der rechten Seite Ihrer Braillezeile angezeigt werden sollen, dann sind die **Punkte 7** und **8** in den letzten beiden Statuszellen nicht gesetzt.
- Ein blinkender **Punkt 7** und ein blinkender **Punkt 8** kennzeichnen die Position der Statuszelle und des Braillecursors, die dem Zeichen auf dem Bildschirm entspricht.

Sie können auch auswählen, dass die Systemzeit in den Statuszellen angezeigt wird, wo diese fortlaufend aktualisiert wird. Eine laufende Uhr direkt auf der Braillezeile kann nützlich sein, wenn Sie eine Präsentation halten oder bis zu einer bestimmten Zeit sprechen müssen, so dass Sie die Zeit schnell überprüfen können, ähnlich wie ein Benutzer, der auf die Bildschirmuhr schaut.

Um die Anzeige der Uhrzeit in den Statuszellen ein- oder auszuschalten, drücken Sie **EINFÜGEN+UMSCHALT+F12** , oder **LINKE UMSCHALT+RECHTE UMSCHALT+PUNKTE 1-2-3** , wenn Sie eine Fokus Braillezeile verwenden . Um diese Funktion zu aktivieren, können Sie auch das Kontrollfeld Zeit in Statuszellen anzeigen in der Einstellungsverwaltung verwenden. Wenn Ihre Statuszellen deaktiviert sind, werden sie durch das Einschalten dieser Funktion vorübergehend aktiviert, bis Sie die Funktion wieder ausschalten. Das Ein- und Ausschalten der Uhrzeitanzeige wirkt sich auf alle Anwendungen aus.

Um die Darstellung der Uhr zu ändern, öffnen Sie die Einstellungsverwaltung, suchen Sie nach "uhr" und verwenden Sie die folgenden Optionen:

- Aktivieren oder deaktivieren Sie das Kontrollfeld 24-Stunden-Format, um die Uhrzeit entweder im 24 Stunden oder 12 Stunden Format anzuzeigen. Für Deutsch ist die Standardeinstellung 24 Stunden, aber dieses variiert je nach ausgewählter JAWS Sprache.
- Verwenden Sie die Auswahlschalter der Gruppe Zeitformat, um die Uhrzeitanzeige zwischen Stunden und Minuten oder Minuten und Sekunden zu ändern. Die Standardeinstellung ist Stunden und Minuten.

Beide Einstellungen können für eine jeweilige Anwendung konfiguriert werden. So können Sie beispielsweise in einer Anwendung das Zeitformat auf Minuten und Sekunden nutzen, in allen anderen Anwendungen aber Stunden und Minuten beibehalten.

Wenn Sie es vorziehen, die Uhr nicht ständig anzuzeigen, können Sie auf den meisten Braillezeilen durch Drücken der **Cursorroutingtaste** über dem Statuszellenbereich kurz die Uhrzeit als Blitzmeldung anzeigen und dann zur aktuellen Anzeige zurückkehren. Wenn die Uhr gerade angezeigt wird, kann auch eine **Cursorroutingtaste** über einer Statuszelle gedrückt werden, damit das, was normalerweise angezeigt wird, kurz als Blitzmeldung angezeigt wird.

**Hinweis:** Auf bestimmten Braillezeilen können die Cursorroutungtasten und die Statuszellen eine besondere Funktion haben, was die Funktion auf der jeweiligen Braillezeile beeinträchtigen kann.

Quelle: Status_Cells.htm

## Brailleeinstellungen anpassen

Zum temporären Anpassen der Brailleeinstellungen nutzen Sie die Schnelleinstellung ( **EINFÜGEN+V** ) und dort das Sucheingabefeld, in dem Sie nach Brailleeinstellungen suchen können. Das Suchergebnis wird in einer Strukturansicht angezeigt. Die Einstellungen, die über die Schnelleinstellung vorgenommen werden, beziehen sich nur auf die aktuelle Anwendung oder das aktuell genutzte Dokument. Um Änderungen vorzunehmen, die global wirksam werden, öffnen Sie die Einstellungsverwaltung und wählen dort die Braille Gruppe.

## Braillemodus

Wählen Sie das Format, in dem Informationen zur Braillezeile gesendet werden. Wird Flächenmodus ausgewählt, sendet JAWS die Textzeile unterm Cursor zur Braillezeile. Wird strukturierter Modus ausgewählt, sendet JAWS Informationen, die sich auf die aktuelle Cursorposition beziehen, zur Braillezeile. Diese Informationen beinhalten den Typ des Elements, den Namen des Dialogfelds oder die Anzahl der Einträge in einer Liste. Wird der Sprachausgabemodus ausgewählt, sendet JAWS dieselben Informationen zur Braillezeile, die es auch zur Sprachausgabe schickt. Wenn Sie den Attributmodus auswählen, zeigt JAWS alle Attribute an, einem Textblock mit einem Buchstaben oder Symbol zugewiesen wurden.

## Acht Punkt Braille

Diese Option legt fest, JAWS 8-Punkt-Braille anzeigen soll oder nicht. 8-Punkt-Braille verwendet **PUNKT 7** für Großbuchstaben in Computerbraille, und **PUNKT 7** und **PUNKT 8** zur Darstellung von nicht alphanumerischen Zeichen. Selbst wenn 8-Punkt-Braille ausgeschaltet ist, wird die Braillemarkierung immer noch angezeigt, sofern sie eingeschaltet ist.

## Markieren mit Punkten 7 und 8

Textattribute wie hervorgehoben, fett, kursiv und unterstrichen können auf der Braillezeile mit angehobenen **Punkten 7 und 8** dargestellt werden. Diese Option legt fest, ob JAWS Text mit Attributen markieren soll oder nicht. Wählen Sie entweder an oder aus. Ist diese Option eingeschaltet, dann können Sie unterschiedliche Attribute festlegen, die markiert werden sollen.

## Blitzmeldungen

Mit dieser Option wird die Anzeige von Braille Blitzmeldungen ein- oder ausgeschaltet. Braille Blitzmeldungen sind kurze Beschreibungen, die auf Ihrer Braillezeile ein paar Sekunden lang erscheinen. Die Meldungen können Fehlermeldungen, Statusinformationen, Hilfe-Sprechblasen und andere Informationen beinhalten. Lesen Sie [Blitzmeldungen](SettingsCenter.chm::/Braille/braille_options_dialog.htm#FlashMessages) für weitere Informationen.

## Brailletasten unterbrechen Sprachausgabe

Beim Eingeben von Befehlen mit den Steuerungstasten der Braillezeile wird die Sprachausgabe unterbrochen.

Ist die Option ausgeschaltet, dann können Sie sich weiterbewegen oder andere Aktionen mit der Braillezeile durchführen, ohne dass die Sprache unterbrochen wird.

## Lernmodus

Dies ist ein Trainingsprogramm zum Lehren und Lernen von Braille, das mit den Freedom Scientific Braillezeilen durchgeführt werden kann. Wenn der Lern-Modus eingeschaltet ist, dann meldet JAWS das Braillesymbol in der Anzeigezelle, sobald Sie die Cursorroutingtaste direkt über der entsprechenden Zelle gedrückt haben. Wenn Sie die Navigationstaste drücken (zu finden hinter der Cursorroutingtaste), dann liest und buchstabiert JAWS das Braillewort. Um den Braille-Lernmodus nutzen zu können, müssen Sie eine Freedom Scientific PAC Mate oder Focus Braillezeile an Ihren Computer anschließen. Markieren Sie Ein, um den Braille-Lernmodus zu starten. Markieren Sie Aus, um den Braille-Lernmodus zu stoppen. Der Lernmodus bleibt so lange eingeschaltet, bis Sie ihn deaktivieren oder JAWS neu gestartet wird. Weitere Informationen hierzu finden Sie unter [Braille-Lernmodus](../Braille_Study_Mode.htm) .

## Cursor Einstellungen

Diese Gruppe enthält Einstellungen, die die Beziehung zwischen dem aktiven Cursor und Ihrer Braillezeile steuern.

### Aktiver Cursor folgt Braille

Diese Option legt fest, ob der aktive Cursor automatisch der Braillezeile folgen soll, wenn er bewegt wird.

Wenn Sie dieses Kontrollfeld aktivieren, sind der Braillecursor und der aktive Cursor fest aneinander gekoppelt. Wenn Sie den Braillecursor bewegen, bewegt sich der aktive Cursor gleich mit. Sie können den Braillecursor jedoch nicht dorthin bewegen, wo der aktive Cursor nicht hinkommt.

Ist diese Option ausgeschaltet, dann können Sie sich mit der Braillezeile an eine andere Position weg vom aktiven Cursor im Fenster bewegen. Sie können eine Statuszeile, eine Symbolleiste oder andere Information außerhalb eines Dokumentbereichs überprüfen.

### Braille folgt Aktivem Cursor

Diese Option legt fest, ob die Braillezeile automatisch dem aktiven Cursor folgen soll oder nicht. Ist diese Option eingeschaltet, dann folgt die Braillezeile automatisch dem Cursor, sobald Sie sich mit den Navigationstasten auf der Tastatur bewegen. So springt der Braillecursor in einem Dialogfeld immer zum aktuellen Element, wenn Sie mit **TAB** darauf gehen.

## Weiterbewegen Einstellungen

Diese Gruppe enthält Einstellungen, die das Weiterbewegen Ihrer Braillezeile und die Textpräsentation steuern. Diese Einstellungen regulieren die Beziehung zwischen der Braillezeile und der Länge der Textzeile.

### Weiterbewegen

Diese Option legt fest, wie Text angezeigt wird, wenn Sie die Braillezeile weiterbewegen. Die zur Verfügung stehenden Einstellungen sind Am Passendsten, Feste Zeichen , Text maximieren und Automatisch.

- In der Einstellung Automatisch ermittelt JAWS die bestmögliche Art, Text beim Weiterbewegen anzuzeigen.
- Am Passendsten überprüft den vorhandenen Platz auf Ihrer Braillezeile und zeigt nur das an, was auch Platz hat.
- Feste Zeichen richtet sich nach der Länge Ihrer Braillezeile.
- Text maximieren zeigt so viel Text wie möglich auf der Braillezeile an, unabhängig von der Länge der Braillezeile.

### Wortumbruch

Diese Option legt fest, ob JAWS einen Teil eines Wortes anzeigt, selbst wenn es am Ende der Braillezeile abgeschnitten wird. Bei Wortumbruch trennt JAWS ein Wort nicht, das für die Darstellung auf der Braillezeile zu lang ist. Wenn Sie dann auf den nächsten Bereich weiterbewegen, können Sie das Wort im ganzen lesen. Wenn Wortumbruch ausgeschaltet ist, zeigt JAWS so viel wie möglich vom Wort an, aber ein Teil kann abgeschnitten sein. JAWS zeigt dann den Rest des Wortes im nächsten Bereich an.

### Automatisches Weiterbewegen

Diese Einstellung legt fest, wie sich die Braillezeile verhält, wenn der Cursor den gerade angezeigten Bereich verlässt.

- Wählen Sie "Aus", um das automatische Weiterbewegen auszuschalten.
- Haben Sie Wie manuelles Scrollen ausgewählt, dann bewegt JAWS die Braillezeile so weiter, wie in der Liste Manuelles Scrollen festgelegt wurde.
- Haben Sie "Automatisch" ausgewählt, dann ermittelt JAWS die beste Methode zur Textanzeige auf Ihrer Braillezeile.

## Markieren Einstellungen

Diese Gruppe enthält die Einstellungen, mit denen man festlegen kann, welche Attribute mit den **PUNKT 7** und **PUNKT 8** auf Ihrer Braillezeile markiert werden. Bei Attributen handelt es sich um Textmodifikationen wie Hervorgehoben, Fett, Unterstrichen, Kursiv und Durchgestrichen. Diese Gruppe enthält zudem Optionen für Skript definierte Markierung und Farbmarkierung. Wählen Sie die Attribute, die durch **PUNKTE 7 und 8** angezeigt werden sollen und deaktivieren Sie diejenigen, die nicht angezeigt werden sollen.

## Tabellen Einstellungen

Diese Gruppe enthält Einstellungen für die Tabellenpräsentation auf Ihrer Braillezeile.

### Tabellen anzeigen

Diese Option legt fest, wie JAWS Tabellentext anzeigt. Sie können sich die aktuelle Zelle, die aktuelle Reihe oder die aktuelle Spalte anzeigen lassen.

### Tabellenüberschriften anzeigen

Diese Option legt fest, wie Überschriften, sofern vorhanden, für die aktive Tabellenzelle angezeigt werden.

### Tabellenkoordinaten anzeigen

Diese Option legt fest, ob die Koordinaten für die aktive Zelle aktiviert sind oder nicht.

Quelle: adjust_braille_options.htm

## Die tragbare PAC Mate Braillezeile

## Unterstützung während der JAWS Installation hinzufügen

Um eine Unterstützung für die PAC Mate Braillezeilen während der JAWS Installation einzurichten, wählen Sie entweder die Option Geführt oder Erweitert. Auf der Registerkarte Komponenten auswählen markieren Sie das Kontrollfeld "PAC Mate 20 oder 40 Zellen" . Auf allen anderen Registerkarten wählen Sie die Optionen, die Sie benötigen. Sobald die Installation abgeschlossen ist, können Sie JAWS mit Ihrer PAC Mate Braillezeile verwenden.

## Unterstützung nach der JAWS Installation hinzufügen

Um die Unterstützung der PAC Mate Braillezeile nach Installation von JAWS einzurichten:

1. Drücken Sie **JAWS TASTE+J** , um das JAWS Anwendungsfenster zu öffnen.
2. Drücken Sie **ALT+O, L** , um den Dialog Brailleeinstellungen zu öffnen.
3. Gehen Sie auf den Schalter Braillezeile hinzufügen und drücken Sie die **LEERTASTE** .
4. Sobald das JAWS Setup den Dialog Braillekomponenten auswählen geöffnet hat, drücken Sie die **LEERTASTE** , um das Kontrollfeld "PAC Mate 20 oder 40 Zellen" zu markieren, danach drücken Sie dann **EINGABE** .

Sobald das Setup die Unterstützung für die PAC Mate Braillezeile installiert hat und JAWS neu gestartet wurde, können Sie Ihre PAC Mate Braillezeile einsetzen.

## Das Tastatur-/Laptop-Gestell verwenden

Das Schaumstoff Tastatur-Gestell positioniert Ihre Tastatur oder Ihren Laptop so, dass Sie die PAC Mate Braillezeile optimal einsetzen können.

Um das jeweilige Gerät zu positionieren, stellen Sie das Schaumstoff-Gestell auf einen Tisch, wobei der abgeschnittene Bereich in Ihre Richtung zeigen sollte. Schieben Sie die Braillezeile in den abgeschnittenen Bereich. Danach stellen Sie die Tastatur oder das Laptop auf das Schaumstoff-Gestell, wobei Sie den für Sie bequemsten Abstand herstellen sollten.

## Die Braillezeile verwenden

Die Einstellungen für die Braillezeile können schnell mit Kurztasten aufgerufen werden, und die Navigation wird mit den Scrollrädern, Cursorroutingtasten und den linken und rechten Navigationstasten vorgenommen.

Mit Ihrem Bildschirmleseprogramm JAWS können Sie die Kurztasten Ihren Bedürfnissen anpassen. Um mehr über das Zuweisen von Kurztasten auf Ihrer Braillezeile zu erfahren, lesen Sie bitte die Informationen über den JAWS Tastaturmanager .

### Kurztasten

Kurztasten ermöglichen einen schnellen Zugriff auf verschiedene Braillezeilen-Optionen. Die 14 Kurztasten befinden sich in der oberen Reihe der Tasten und bestehen aus jeweils sieben Tasten zu beiden Seiten der Markierung für die Mitte. Damit Sie jede Kurztaste finden und erkennen können, gibt es an der Unterseite der Zeile Markierungen. Die Tasten links von der Mitte sind von links nach rechts mit 1, 2, 3, 4, 5, 7 nummeriert, und die Tasten rechts von der Mitte mit 8, 9 ,10, 11, 12, 13 und 14. Die übrigen Schalter links und rechts der Kurztasten sind die Navigationstasten.

Tabelle: Kurztastenbefehle

| Kurztaste | Befehl |
| --- | --- |
| 1 |  |
| 2 | Letzte Blitzmeldung wiederholen |
| 3 | Ziehe Braille zu PC Cursor |
| 4 | Aktiv folgt Braille umschalten |
| 5 | Braille folgt aktivem Cursor |
| 6 | Anfang des aktiven Fensters oder Anfang der strukturierten Zeile anzeigen |
| 7 | UMSCHALT+TAB |
| 8 | TAB |
| 9 | Anfang des aktiven Fensters oder Anfang der strukturierten Zeile anzeigen |
| 10 | Kurzschrift |
| 11 | Wort übersetzen |
| 12 | Ziehe Braille zum Aktiven Cursor |
| 13 |  |
| 14 |  |

## Scrollräder

Mit den Scrollrädern der Braillezeile können Sie schnell durch Dateien, Listen und Menüs navigieren. Zusätzlich lässt sich jedes Rädchen unabhängig voneinander für zusätzliche Funktionalität einstellen. Weitere Informationen finden Sie im Hilfethema [Focus Scrollräder](../focus/focus_ww_ab_crk.htm) .

### Dateien

In Textdateien bewegt man sich mit den Scrollrädern zeilen-, satz- oder absatzweise. Das Herunterdrücken beider Scrollräder schaltet um zwischen Zeile, Satz, Absatz oder Schwenk-Modus. Wenn man die Scrollräder zu sich rollt, bewegt man sich nach unten, wenn man sie von sich weg rollt, bewegt man sich aufwärts. Im Schwenk-Modus bewirkt das Drehen des Scrollrades um einen "Klick" zu sich hin, dass um eine Zeilenlänge nach rechts weiterbewegt wird, während das Drehen des Scrollrades um einen "Klick" von sich weg, dass um eine Zeilenlänge nach links weiterbewegt wird.

### Menüs

Drehen Sie ein Scrollrad in Ihre Richtung, um abwärts durch ein Menü zu wandern und drehen Sie es von sich weg, um aufwärts zu wandern. Drücken Sie ein Scrollrad nach unten, um einen Menüeintrag auszuwählen.

### Dialoge

In Dialogfeldern bewirkt das Drehen des Scrollrades in Ihre Richtung, dass Sie sich vorwärts auf die Steuerelemente bewegen, während das Drehen des Scrollrades weg von Ihnen rückwärts auf die Steuerelemente bewegt. Abhängig von der Art des Steuerelements, funktionieren die Scrollräder unterschiedlich, wenn sie gedrückt werden.

- In Listenansichten, Auswahllisten, Auswahlschaltern, Strukturansichten und Kontrollfeldern bewirkt das Herunterdrücken des Scrollrades den Wechsel in den Listenmodus. In diesem Modus verwenden Sie das Scrollrad, um sich durch die Listenelemente zu bewegen. Um den Listenmodus zu verlassen, drücken Sie das Scrollrad erneut herunter.
- Einzelne Kontrollfelder oder Schalter werden durch das Herunterdrücken der Scrollräder umgeschaltet oder Schalter aktiviert.

## Cursorroutingtasten

Die Zeile verfügt über Cursorroutingtasten, bei denen es sich um die Tastenreihe direkt über jedem Braillemodul handelt. Drücken Sie eine Cursorroutingtaste, um den Cursor an diesen Punkt zu ziehen, oder um einen Link auf einer Webseite oder in einer E-Mail zu aktivieren. Damit Die den Cursor lokalisieren und führen können, befinden sich Markierungen auf jedem fünften Modul an der Unterseite der Zeile.

## Rechte und linke Navigationstaste

Mit Hilfe der Navigationstasten bewegen Sie sich durch Ihre Dateien jeweils um die Länge einer Zeilenanzeige je Tastendruck. Um nach links zu navigieren, drücken Sie einen der Schalter links vom Kurztastenbereich. Um nach rechts zu navigieren, drücken Sie einen der Schalter rechts vom Kurztastenbereich.

Quelle: pacmate_display.htm

## Type Lite

Das TypeLite mit seiner 40-Zellen-Braillezeile, im Stil eines Laptops und mit einer PC Tastatur ausgestattet, ermöglicht einen bequemen Zugriff auf alle von JAWS unterstützten Anwendungen. Kippen Sie den Schalter auf der linken Seite des TypeLite nach vorne, um den Notizgerät-Modus einzuschalten.

[Navigationstasten und Kipptasten](type_lite.htm#Advance_Bars_and_Rockers)

[Befehle zum Lesen und Eingeben](type_lite.htm#Reading_adn_Editing_Commands)

[Navigation](type_lite.htm#Navigation)

[Einstellungen und Informelle Meldungen](type_lite.htm#Settings_and_Information)

[Cursor Befehle](type_lite.htm#cursors)

[Suchen](type_lite.htm#Search)

[Text markieren](type_lite.htm#Text_Selection)

## Navigationstasten und Kipptasten

Die Navigationstasten sind unter JAWS voll funktionsfähig. Im voreingestellten Modus bewegen die Navigationstasten die Zeile, aber sie ziehen den Fokus nicht nach.

- Wenn man die rechte Seite der rechten Taste drückt, wird die Zeile um 40 Zeichen nach rechts bewegt. Sie springt auf die nächste Zeile, wenn das Ende einer Zeile erreicht wird.
- Wenn man die linke Seite der rechten Taste drückt, wird die Braillezeile vertikal nach unten bewegt. Man kehrt nicht in die linke Ecke des Bildschirms zurück.
- Wenn man die rechte Seite der linken Taste drückt, wird die Braillezeile nach oben bewegt. Man kehrt nicht in die linke Ecke des Bildschirms zurück.
- Das Drücken der linken Seite der linken Navigationstaste bewegt die Zeile 40 Zellen nach links oder eine Zeile weiter.

Zusammenfassung: Die Lesetaste auf der rechten Seite bewegt vorwärts, im Dokument nach unten. Die linke Lesetaste bewegt rückwärts, im Dokument nach oben. Die äußeren Enden der Lesetasten bewegen horizontal und die inneren bewegen vertikal.

Tabelle: Navigationstasten und Kipptasten Befehle

| Beschreibung | Befehl |
| --- | --- |
| Nach links bewegen | Linke Navigationstaste links |
| Nach rechts bewegen | Rechte Navigationstaste rechts |
| Braille vorherige Zeile | Linke Navigationstaste rechts |
| Braille nächste Zeile | Rechte Navigationstaste links |
| POS1 | Linke Kipp mittlere |
| ENDE | Rechte Kipp mittlere |
| Vorherige Zeile | Rechte Kipp rauf |
| Nächste Zeile | Rechte Kipp runter |
| Braille vorherige Zeile | Linke Kipp rauf |
| Braille nächste Zeile | Linke Kipp runter |
| Dateianfang | Beide Kipp rauf |
| Dateiende | Beide Kipp runter |

Wenn man den linken Kipp hoch- und runterbewegt, bewegt sich der Systemfokus nicht mit der Braillezeile. Wenn der rechte Kipp hoch- und runterbewegt wird, bewegt sich der Systemfokus mit der Braillezeile.

## Befehle zum Lesen und Eingeben

Tabelle: Befehle zum Lesen und Eingeben

| Beschreibung | Befehl |
| --- | --- |
| Vorheriges Zeichen | PFEIL LINKS |
| Nächstes Zeichen | PFEIL RECHTS |
| Vorherige Zeile | PFEIL RAUF |
| Nächste Zeile | PFEIL RUNTER |
| Vorheriges Wort | STRG+PFEIL LINKS |
| Nächstes Wort | STRG+PFEIL RECHTS |
| Vorheriger Absatz | STRG+PFEIL RAUF |
| Nächster Absatz | STRG+PFEIL RUNTER |
| Ausschneiden | X |
| Kopieren | C |
| Einfügen | V |

## Kurztasten zum Navigieren

Tabelle: Navigationsbefehle

| Beschreibung | Befehl |
| --- | --- |
| Seite rauf | FN+PFEIL RAUF |
| Seite runter | FN+PFEIL RUNTER |
| POS1 | FN+PFEIL LINKS |
| Ende | FN+PFEIL RECHTS |
| Desktop | D |
| Startmenü | S |
| Menüleiste | B |
| Nächster Text ohne Link | N |
| EINGABE | EINGABE |
| ESCAPE | ESCAPE |
| Rückschritt | RÜCKSCHRITT |
| Registerkarte | TAB |

## Einstellungs- und Informelle Meldungen

Tabelle: Einstellungs- und Informelle Befehle

| Beschreibung | Befehl |
| --- | --- |
| Zwischen 8 und unbegrenzten Pixels pro Leerschritt umschalten | P |
| Braillemodus umschalten | T |
| Attributmodus umschalten | M |
| Kurzschriftübersetzung ein/ ausschalten | G |
| Aktuelles Wort ausschreiben | E |
| Tastaturhilfe | FRAGEZEICHEN |
| Letzte Blitzmeldung wiederholen | ALT+Z |

## Cursor Befehle

Tabelle: Cursor Befehle

| Beschreibung | Befehl |
| --- | --- |
| PC Cursor | Linkes Ende der linken Navigationstaste+rechte Kipp runter |
| JAWS Cursor | Linkes Ende der linken Navigationstaste+ rechte Kipp rauf |
| Ziehe Braille zum Aktiven Cursor | R |
| Ziehe JAWS Cursor zu PC | rechte Kipp rauf+rechtes Ende der linken Navigationstaste |
| Ziehe PC Cursor zu JAWS | rechte Kipp rauf+rechtes Ende der linken Navigationstaste |
| Braille folgt Aktivem Cursor | A |
| Aktiver Cursor folgt Braille | Y |

## Suchen

## Text markieren

Tabelle: Markierungsbefehle

| Beschreibung | Befehl |
| --- | --- |
| Vom Zeilenanfang markieren | Linke Kipp rauf+rechte Kipp runter |
| Vom Cursor bis Zeilenende markieren | Rechte Kipp rauf+linke Kipp runter |
| Vom Dateianfang markieren | Linke mittlere Kipp+rechte Kipp runter |
| Vom Dateiende markieren | Linke mittlere Kipp+rechte Kipp runter |
| Braillemarkierung Text | Rechte mittlere Kipp+Routing |
| Aktuelles Element markieren | LEERTASTE |
| Markierten Text lesen | Rechtes Ende der Navigationstaste+linke Kipp runter |

Quelle: type_lite.htm

## Übersicht über JAWS und Braille

Das Bildschirmleseprogramm JAWS ermöglicht dem Anwender einen taktilen Zugang zum Computerbildschirm. Diese multi-sensorische Methode erweitert den Einsatz Ihres Computers um eine wesentliche Dimension, da Sie nun in der Lage sind, das komplette Windows Betriebssystem auszunutzen. Die Tasten auf Ihrer Braillezeile erlauben das Navigieren Ihres Computers in allen Richtungen, während Pull-Down-Menüs, Dialog- und Eingabefelder auf Ihrer Braillezeile angezeigt werden.

JAWS bietet viele Funktionen zum Verbessern des Lesens auf Ihrer Braillezeile. So können Sie jetzt zum Beispiel festlegen, wie im [strukturierten Modus](Braille_Display_Modes.htm#Structured_Mode) Steuerelemente in Dialogen angezeigt werden sollen. Sie können JAWS jetzt auch so einstellen, dass Textattribute wie zum Beispiel Farben, kursiv, fett, usw. angezeigt werden. Zudem können Sie jetzt auch die Vergrößerung der Ausschnittslänge und die Textausrichtung für Ihre Braillezeile festlegen. Um mehr über JAWS und die Einstellungen für Ihre Braillezeile zu erfahren, machen Sie sich mit dem Dialog [Braille Grundeinstellungen](jfw.chm::/using_jaws/the_jaws_application_window/braille_basics_dialog.htm) im Menü Optionen vertraut. Wenn Sie anwendungsbezogene Braille-Einstellungen vornehmen möchten, erkunden Sie die [Gruppe Brailleoptionen](SettingsCenter.chm::/Braille/braille_options_dialog.htm) , die Sie in der Gruppe Braille der Einstellungsverwaltung finden können.

Die meisten Braillezeilen werden von JAWS automatisch erkennt, so dass direkt nach dem Anschließen der Braillezeile an Ihren Computer Informationen an die Braillezeile gesendet werden. Bei Braillezeilen, die über USB oder Bluetooth angeschlossen sind, erkennt JAWS die Braillezeile beim Start automatisch und beginnt, diese zu verwenden. Braillezeilen werden auch erkannt, wenn JAWS gerade ausgeführt wird und Sie eine Verbindung über USB oder Bluetooth herstellen. Damit JAWS jedoch Braillezeilen über Bluetooth im laufenden Betrieb erkennen kann, muss die Option **Autoerkennung der Braillezeile über Bluetooth** in der Einstellungsverwaltung aktiviert werden.

Wenn Ihre spezielle Braillezeile nicht automatisch von JAWS erkannt wird, können Sie sie mit dem [JAWS Sprachausgaben- und Braillezeilen-Manager](jfw.CHM::/customizing_jaws_for_windows/Synth_Braille_Manager/Synthesizer_and_Braille_Manager.htm) hinzufügen. Lesen Sie die Dokumentation zu Ihrer Braillezeile, um mehr Informationen darüber zu erhalten, wie Sie die Braillezeile für die Verwendung mit JAWS hinzufügen können.

Wenn Sie JAWS mit mehr als einer Braillezeile verwenden, und die Braillezeile über USB oder Bluetooth verbunden werden kann, dann können Sie zwischen den Braillezeilen wechseln, ohne JAWS vorher neu starten zu müssen. Wenn Sie beispielsweise eine Focus 40 Blue über eine Bluetooth Verbindung nutzen und Sie richten eine USB Verbindung zu einer anderen Braillezeile ein, dann wird JAWS anfangen, die Braillezeile zu nutzen, die per USB verbunden ist. Wenn Sie dann die über USB verbundene Braillezeile entfernen und die Focus 40 Blue einschalten, dann schaltet JAWS zurück auf die Bluetooth Verbindung zur Focus Blue.

Um Ihre Braillezeile optimal für die Anwendung von JAWS einzurichten, gehen Sie auf die folgenden Links oder kontaktieren Sie Ihren Braillezeilen-Händler.

Die folgenden Themen behandeln den Einsatz von JAWS mit Braillezeilen.

## Allgemein

- [BrailleIn](JAWS_BrailleIn.htm)
- [Braillezeilen Eingabebefehle](focus/Braille_Display_Input_Commands.htm)
- [Braille Lern-Modus](Braille_Study_Mode.htm)
- [Die Modi der Braillezeilen](Braille_Display_Modes.htm)
- [Statuszellen](Status_Cells.htm)
- [Braille Blitzmeldungen](Braille_Flash_Messages.htm)
- [Den Cursor an- und abkoppeln](Linking_and_Unlinking_the_Cursor.htm)
- [Spezielle JAWS Braille-Kürzel](JAWS_Specific_Braille_Abbreviations.htm)
- [Braille-Formatierung](Braille_Formatting.htm)
- [Braille-Einstellungen im laufenden Betrieb vornehmen](braille/adjust_braille_options.htm)

## Freedom Scientific Braillezeilen und Notizgeräte

- [Focus Braillezeilen](focus/focus.htm)
- [Die tragbare PAC Mate Braillezeile](braille/pacmate_display.htm)
- [Braille Lite M20](braille/braille_lite_20_millennium_edition.htm)
- [Braille Lite M40](braille/braille_lite_40_millennium_edition.htm)
- [Type Lite](braille/type_lite.htm)
- [Braille Lite 2000](braille/96braille_lite_18.htm)
- [Braille Lite 40](braille/braille_lite_40.htm)

Quelle: braille_start.htm

## Braillezeilen Eingabebefehle

JAWS unterstützt eine Reihe von Kurztasten, die es Ihnen ermöglichen, Braillebefehle einzugeben, wie auch Ihren Computer zu steuern. Nutzen Sie diese Kurztasten mit den Focus Braillezeilen von Freedom Scientific. Für andere Braillezeilen kontaktieren Sie bitte den Hersteller der Braillezeile, um eine Liste der Kurztasten zu erhalten.

Viele Befehle, die hier gelistet sind, beinhalten das Wort "CHORD". Um einen CHORD-Befehl auszuführen, verwenden Sie stets die **LEERTASTE** als Teil des Befehls. Um beispielsweise ein **L CHORD** auszuführen, drücken Sie **PUNKTE 1-2-3** gleichzeitig mit der **LEERTASTE** .

## Steuerungstasten

Verwenden Sie die Steuerungstasten **STRG** , **ALT** , **WINDOWSTASTE** , **UMSCHALT** , oder der JAWS TASTE ( **EINFÜGEN** ) zum Simulieren von Tastenkombinationen. Um diese Steuerungstasten bei Eingabe einer Kurztaste zu nutzen, gehen Sie wie folgt vor:

1. Halten Sie **PUNKT 8 CHORD** gedrückt und drücken dann die korrespondierenden Steuerungstasten. Steuerungskurztasten sind in der folgenden Tabelle aufgelistet.
2. Nachdem Sie den Steuerungsteil der Kurztaste gedrückt haben, lassen Sie diese los und drücken Sie die restlichen Tasten der Tastenkombination. Um zum Beispiel **STRG+UMSCHALT+V** auszuführen, drücken Sie **PUNKTE 3-7-8 CHORD** , lassen die Tasten los, und drücken dann **V** ( **PUNKTE 1-2-3-6** ).

Tabelle: Eine Tabelle mit dem Tastennamen in der ersten Spalte und dem Braille-Kurztastenbefehl in der zweiten Spalte.

| Tastenname | Befehl |
| --- | --- |
| Funktionstasten (F1 bis F12) Für weitere Informationen lesen Sie bitte die Beschreibung der Funktionstasten . | PUNKT 1 |
| EINFÜGEN | PUNKT 2 |
| STRG | PUNKT 3 |
| WINDOWSTASTE | PUNKT 4 |
| JAWS TASTE | PUNKT 5 |
| ALT | PUNKT 6 |
| UMSCHALT | PUNKT 7 |

Statt sich diese Tasten anhand ihrer Punktposition zu merken, ist es möglicherweise einfacher, den Finger zu lernen, mit dem jede Taste verknüpft ist. Wenn sich alle Ihre Finger auf der Braille-Tastatur befinden, dann ist das Layout wie folgt:

Tabelle: Eine Tabelle mit dem Tastennamen in der ersten Spalte und der Fingerposition in der zweiten Spalte.

| Tastenname | Fingerposition |
| --- | --- |
| Funktionstasten (F1 bis F12) | Linker Zeigefinger |
| WINDOWSTASTE | Rechter Zeigefinger |
| EINFÜGEN | Linker Mittelfinger |
| JAWS TASTE | Rechter Mittelfinger |
| STRG | Linker Ringfinger |
| ALT | Rechter Ringfinger |
| UMSCHALT | Linker, kleiner Finger |

Beachten Sie, dass Sie in dieser Beschreibung eine ziemlich lockere Korrelation zwischen Fingerpaaren herstellen können. Sie ist zum Beispiel der linke Zeigefinger für die **Funktionstasten** , während der rechte Zeigefinger für die **WINDOWS-Taste** ist. Eine stärkere Wechselbeziehung kann zwischen linken und rechten Mittelfingern festgestellt werden. Links ist die **EINFÜGETASTE** und rechts ist die **JAWS** -Taste, die bei der Verwendung von JAWS häufig denselben Zweck erfüllen. Zu guter Letzt sind der linke und der rechte Ringfinger die Tasten **STRG** und **ALT** , wodurch diese beiden Positionen leichter zu merken sind.

Sobald dieses Layout verstanden wurde, ist es leicht zu verstehen, dass jedes Mal, wenn eine Steuerungstaste oder eine Kombination von Steuerungstasten als Teil eines Befehls verwendet wird, **PUNKT 8 CHORD** immer enthalten ist.

Das Drücken einer dieser Steuerungstasten mit **PUNKT 8 CHORD** entspricht dem gleichen Drücken und Halten einer der entsprechenden Tasten auf der QWERTZ-Tastatur. Der Computer wartet auf den Schlüssel oder die Schlüssel, die durch die Steuerungstasten geändert werden. Somit ist das Drücken von **PUNKTE 3-8 CHORD** gleich dem Drücken der **STRG** Taste. Windows wartet dann auf die Taste, die diese STRG-Kombination vervollständigt, wie etwa die Taste **A** , um als **STRG+A** alles zu markieren, oder die Taste **C** , um als **STRG+C** den gewählten Text in die Zwischenablage zu kopieren. Wiederholungen der häufig verwendeten Kurztasten, wie die bereits erwähnte Tastenkombinationen mit **STRG** , der Windows-Befehle wie **WINDOWS-Taste+M** und den JAWS-Befehlen wie **EINFÜGEN+T** sollten diese Schlüsselzuweisungen sich fest in Ihr Gedächtnis einprägen.

### Funktionstasten

Um die Funktionstasten ( **F1** bis **F12** ) zu simulieren, drücken Sie **PUNKTE 1-8 CHORD** gefolgt von **A** bis **L** (was 1 bis 12 entspricht). Um zum Beispiel **F6** zu simulieren, drücken Sie **PUNKTE 1-8 CHORD** , dann **F** ( **PUNKTE 1-2-4** ). Wenn die Funktionstaste Bestandteil eines Befehls ist, drücken Sie die entsprechenden Steuerungstasten während Sie **PUNKTE 1-8 CHORD** drücken. Um zum Beispiel **JAWS TASTE (EINFÜGEN)+F2** zu simulieren, drücken Sie **PUNKTE 1-2-8 CHORD** , dann **B** ( **PUNKTE 1-2** ).

## Spezielle Tasten

Nutzen Sie diese Kurztasten, um einige Tasten zu simulieren, die auf der Focus Brailletastatur nicht verfügbar sind. Diese Tasten können mit den vorher beschriebenen Steuerungstasten kombiniert werden. Satzzeichen und andere Symbole werden mit den entsprechenden Brailleentsprechungen in Kurzschrift eingegeben, wenn die Kurzschriftübersetzung auf Ein- und Ausgabe gesetzt ist. Um es Ihnen zu vereinfachen, führen wir die Kurztasten, als auch die Brailleeingaben auf. Steht keine Entsprechung über Brailleeingabe zur Verfügung, dann erscheint ein Bindestrich in der Tabellenzelle.

Tabelle: EIne Tabelle mit dem Tastennamen in der ersten Spalte, dem Braille-Kurztastenbefehl in der zweiten Spalte und dem Punktmuster in der dritten Spalte.

| Tastenname | Befehl | Punktmuster |
| --- | --- | --- |
| ESCAPE | RECHTE UMSCHALT+PUNKT 1 oder Z CHORD | RECHTE UMSCHALT+PUNKT 1 oder PUNKTE 1-3-5-6 CHORD |
| ALT | RECHTE UMSCHALT+PUNKT 2 | - |
| APPLIKATIONSTASTE | RECHTE UMSCHALT+PUNKT 2 CHORD | - |
| NUM STERN | RECHTE UMSCHALT+PUNKT 3 | - |
| WINDOWSTASTE | RECHTE UMSCHALT+PUNKT 4 | - |
| NUM SCHRÄGSTRICH | RECHTE UMSCHALT+PUNKT 7 | RECHTE UMSCHALT+PUNKT 7 |
| FESTSTELLTASTE | RECHTE UMSCHALT+PUNKT 7 CHORD | RECHTE UMSCHALT+PUNKT 7 CHORD |
| NUM PLUS | RECHTE UMSCHALT+PUNKT 8 | - |
| RÜCKSCHRITT | PUNKT 7 | - |
| EINGABE | PUNKT 8 | - |
| STRG+RÜCKSCHRITT | PUNKTE 1-2-3-4-5-6-7 CHORD | - |
| TAB | PUNKTE 4-5 CHORD | - |
| UMSCHALT+TAB | B CHORD | PUNKTE 1-2 CHORD |
| POS1 | K CHORD | PUNKTE 1-3 CHORD |
| ENDE | PUNKTE 4-6 CHORD | - |
| SEITE RAUF | LINKE AUSWAHL+KIPPTASTE RAUF oder RECHTE AUSWAHL+KIPPTASTE RAUF oder PUNKTE 2-3-7 CHORD | - |
| SEITE RUNTER | LINKE AUSWAHL+KIPPTASTE RUNTER oder RECHTE AUSWAHL+KIPPTASTE RUNTER oder PUNKTE 5-6-7 CHORD | - |
| ENTFERNEN | FÜR CHORD | PUNKTE 1-2-3-4-5-6 CHORD |
| ESSZETT | PUNKTE 1-2-3-4-5-6 | - |
| ECKIGE KLAMMER RECHTS | PUNKTE 1-2-4-5-6-7 | - |
| ECKIGE KLAMMER LINKS | PUNKTE 2-4-6-7 | - |
| BACKSLASH | PUNKTE 1-2-5-6-7 | - |
| BINDESTRICH | PUNKTE 3-4 | - |
| LINKE KLAMMER | PUNKTE 1-2-3-5-6 | - |
| RECHTE KLAMMER | PUNKTE 3-5-6 | - |
| Ä | PUNKT 3 | - |
| ESSZETT | PUNKTE 3-6 | - |
| GRAVE | PUNKT 4 | - |
| PUNKT | PUNKTE 4-6 | - |
| FRAGEZEICHEN | PUNKTE 1-4-5-6 | - |
| AUSRUFEZEICHEN | PUNKTE 2-3-4-6 | - |
| Ö | PUNKTE 5-6 | - |
| KOMMA | PUNKT 6 | - |

## Navigationsbefehle

Nutzen Sie diese Tastenkombinationen, um diverse JAWS Navigationsbefehle auszuführen. In der Tabelle bieten wir Ihnen beide Kurztasten und Punktmuster. Steht keine Entsprechung über Brailleeingabe zur Verfügung, dann erscheint ein Bindestrich in der Tabellenzelle.

Tabelle: Eine Tabelle mit dem Tastennamen für den Navigationsbefehl in der ersten Spalte, dem Braille-Kurztastenbefehl in der zweiten Spalte und dem Punktmuster in der dritten Spalte.

| Beschreibung | Befehl | Punktmuster |
| --- | --- | --- |
| Vorheriges Zeichen lesen | PUNKT 3 CHORD | - |
| Nächstes Zeichen lesen | PUNKT 6 CHORD | - |
| Zeichen lesen | PUNKTE 3-6 CHORD | - |
| Vorheriges Wort lesen | PUNKT 2 CHORD | - |
| Nächstes Wort lesen | PUNKT 5 CHORD | - |
| Wort lesen | PUNKTE 2-5 CHORD | - |
| Vorherige Zeile lesen | PUNKT 1 CHORD oder LINKE KIPPTASTE RAUF | - |
| Nächste Zeile lesen | PUNKT 4 CHORD oder LINKE KIPPTASTE RUNTER | - |
| Zeile lesen | C CHORD | PUNKTE 1-4 CHORD |
| Satz lesen | LINKE UMSCHALT+RECHTE UMSCHALT+C | LINKE UMSCHALT+RECHTE UMSCHALT+PUNKTE 1-4 |
| Vorherigen Absatz lesen | RECHTE UMSCHALT+LINKE KIPPTASTE RAUF | - |
| Nächsten Absatz lesen | RECHTE UMSCHALT+LINKE KIPPTASTE RUNTER | - |
| Absatz lesen | LINKE UMSCHALT+RECHTE UMSCHALT+PUNKTE 2-3-5-6-7-8 | - |
| Zum Dateianfang bewegen | L CHORD | PUNKTE 1-2-3 CHORD |
| Zum Dateiende bewegen | PUNKTE 4-5-6 CHORD | - |
| Zeile links vom Cursor lesen | RECHTE UMSCHALT+PUNKTE 3-7 | - |
| Zeile rechts vom Cursor lesen | RECHTE UMSCHALT+PUNKTE 6-8 | - |
| Alles lesen | PUNKTE 1-2-4-5-6 CHORD | - |
| Erste Zeile des aktiven Fensters lesen | LINKE KIPPTASTE RAUF+RECHTE KIPPTASTE RAUF | - |
| Letzte Zeile des aktiven Fensters lesen | LINKE KIPPTASTE RUNTER+RECHTE KIPPTASTE RUNTER | - |
| Vorheriges Dokumentfenster | PUNKTE 2-3 CHORD | - |
| Nächstes Dokumentfenster | PUNKTE 5-6 CHORD | - |
| Listenfeld öffnen | LINKE UMSCHALT+RECHTE KIPPTASTE RUNTER | - |
| Listenfeld schließen | LINKE UMSCHALT+RECHTE KIPPTASTE RAUF | - |
| Formularmodus verlassen | X CHORD | PUNKTE 1-3-4-6 CHORD |
| Fensterprompt und Text ansagen | G-CHORD | PUNKTE 1-2-4-5 CHORD |

## Microsoft Word Schnellnavigationstasten

Mit diesen Tastenkombinationen navigieren Sie in Microsoft Word Dokumenten. Die Schnellnavigationstasten müssen aktiviert sein, damit Sie diese Befehle ausführen können ( **PUNKTE 2-8 CHORD** gefolgt von **PUNKTEN 1-3-5-6** ). Beachten Sie, dass Sie **PUNKT 7** zu vielen unten aufgeführten Tastenkombinationen hinzufügen können, um auf das vorherige Element dieses Typs im Dokument zu springen. In der Tabelle bieten wir Ihnen beide Kurztasten und Punktmuster. Steht keine Entsprechung über Brailleeingabe zur Verfügung, dann erscheint ein Bindestrich in der Tabellenzelle.

Tabelle: Eine Tabelle mit dem Word Schnellnavigationstastennamen in der ersten Spalte, dem Kurztastenbefehl in der zweiten Spalte und dem Punktmuster in der dritten Spalte.

| Beschreibung | Befehl | Punktmuster |
| --- | --- | --- |
| Nächster Grammatikfehler | A | PUNKT 1 |
| Nächstes Lesezeichen | B | PUNKTE 1-2 |
| Zur nächsten Ausklappliste springen | C | PUNKTE 1-4 |
| Nächste Endnote | D | PUNKTE 1-4-5 |
| Zum nächsten Eingabefeld springen | E | PUNKTE 1-5 |
| Nächstes Formularfeld | F | PUNKTE 1-2-4 |
| Nächste Grafik | G | PUNKTE 1-2-4-5 |
| Nächste Überschrift | H | PUNKTE 1-2-5 |
| Nächste Liste | L | PUNKTE 1-2-3 |
| Nächster Rechtschreibfehler | M | PUNKTE 1-3-4 |
| Nächster Kommentar | N | PUNKTE 1-3-4-5 |
| Nächste Fußnote | O | PUNKTE 1-3-5 |
| Nächster Absatz | P | PUNKTE 1-2-3-4 |
| Nächste Überarbeitung | R | PUNKTE 1-2-3-5 |
| Nächster Abschnitt | S | PUNKTE 2-3-4 |
| Nächste Tabelle | T | PUNKTE 2-3-4-5 |
| Nächstes Ausklapplistenformularfeld | X | PUNKTE 1-3-4-6 |
| Nächste Seite | LEERTASTE | - |
| Vorherige Seite | RÜCKSCHRITT | PUNKT 7 |

## Befehle zum Markieren

Nutzen Sie diese Kurztasten, um Zeichen, Zeilen und andere Seitenelemente zu markieren. In der Tabelle bieten wir Ihnen beide Kurztasten und Punktmuster. Steht keine Entsprechung über Brailleeingabe zur Verfügung, dann erscheint ein Bindestrich in der Tabellenzelle.

Tabelle: Eine Tabelle mit dem Textauswahlbefehlstastennamen in der ersten Spalte, dem Kurztastenbefehl in der zweiten Spalte und dem Punktmuster in der dritten Spalte.

| Beschreibung | Befehl | Punktmuster |
| --- | --- | --- |
| Vorheriges Zeichen markieren | LINKE UMSCHALT+PUNKT 3 oder PUNKTE 3-7 CHORD | - |
| Nächstes Zeichen markieren | LINKE UMSCHALT+PUNKT 6 oder PUNKTE 6-7 CHORD | - |
| Vorheriges Wort markieren | PUNKTE 2-7 CHORD | - |
| Nächstes Wort markieren | PUNKTE 5-7 CHORD | - |
| Vorherige Zeile markieren | LINKE UMSCHALT+PUNKT 1 oder PUNKTE 1-7 CHORD | - |
| Nächste Zeile markieren | LINKE UMSCHALT+PUNKT 4 oder PUNKTE 4-7 CHORD | - |
| Vorherige Bildschirmseite markieren | LINKE UMSCHALT+K | LINKE UMSCHALT+PUNKTE 1-3 |
| Nächste Bildschirmseite markieren | LINKE UMSCHALT+PUNKTE 4-6 | - |
| Vom Zeilenanfang markieren | LINKE UMSCHALT+PUNKT 2 oder PUNKTE 1-3-7 CHORD | - |
| Vom Cursor bis Zeilenende markieren | LINKE UMSCHALT+PUNKT 5 oder PUNKTE 4-6-7 CHORD | -- |
| Vom Dateianfang zum Fokus markieren | LINKE UMSCHALT+L oder L+PUNKT 7 CHORD | LINKE UMSCHALT+PUNKTE 1-2-3 oder PUNKTE 1-2-3-7 CHORD |
| Vom Fokus bis Dateiende markieren | LINKE UMSCHALT+PUNKTE 4-5-6 oder PUNKTE 4-5-6-7 CHORD | - |
| Alles markieren | LINKE UMSCHALT+VOLLZEICHEN | LINKE UMSCHALT+PUNKTE 1-2-3-4-5-6 |
| Zum Zeilenanfang bewegen | KIPPTASTE RAUF+LESETASTE | - |
| Zum Zeilenende bewegen | KIPPTASTE RUNTER+LESETASTE | - |

## Braille Befehle

Nutzen Sie diese Kurztasten, um verschiedene Braillefunktionen einzustellen. In der Tabelle bieten wir Ihnen beide Kurztasten und Punktmuster.

Tabelle: Eine Tabelle mit der Braillebefehlsbeschreibung in der ersten Spalte, dem Kurztastenbefehl in der zweiten Spalte und dem Punktmuster in der dritten Spalte.

| Beschreibung | Befehl | Punktmuster |
| --- | --- | --- |
| Aktuelles Wort bei Kurzschriftübersetzung ausschreiben | T CHORD | PUNKTE 2-3-4-5 CHORD |
| Kurzschrift Einstellungen für aktives Sprachprofil ändern | PUNKTE 1-2-4-5-7 CHORD | PUNKTE 1-2-4-5-7 CHORD |
| Zeichen- und Attributmodus umschalten | PUNKTE 1-6 CHORD | PUNKTE 1-6 CHORD |
| Durch die Brailleanzeigemodi wechseln | M CHORD | PUNKTE 1-3-4 CHORD |
| 8-/6-Punkt-Braille umschalten | 8 CHORD | PUNKTE 2-3-6 CHORD |
| Cursorform verändern | PUNKTE 1-4-6 CHORD | PUNKTE 1-4-6 CHORD |
| Braillecursor beschränken | R CHORD | PUNKTE 1-2-3-5 CHORD |
| Zwischen bevorzugten Braille-Sprachprofilen wechseln | PUNKTE 2-3-4-5-7 CHORD | PUNKTE 2-3-4-5-7 CHORD |
| Zeige Uhr / Zeit in Statuszellen an | LINKE UMSCHALT+RECHTE UMSCHALT+L | LINKE UMSCHALT+RECHTE UMSCHALT+PUNKTE 1-2-3 |
| Dialog Brailleansicht auswählen öffnen | LINKE UMSCHALT+PUNKTE 1-2-7 | LINKE UMSCHALT+PUNKTE 1-2-7 |

## Windows Befehle

Nutzen Sie diese Kurztasten, für grundlegende Bearbeitungsfunktionen in Windows.

Tabelle: Eine Tabelle mit dem Windowsbefehlstastennamen in der ersten Spalte, dem Kurztastenbefehl in der zweiten Spalte und dem Punktmuster in der dritten Spalte.

| Beschreibung | Braillesymbol | Punktmuster |
| --- | --- | --- |
| ALT+TAB | LINKE UMSCHALT+PUNKTE 4-5 | LINKE UMSCHALT+PUNKTE 4-5 |
| Aus Zwischenablage einfügen | LINKE UMSCHALT+V | LINKE UMSCHALT+PUNKTE 1-2-3-6 |
| In Zwischenablage kopieren | LINKE UMSCHALT+C | LINKE UMSCHALT+PUNKTE 1-4 |
| In Zwischenablage ausschneiden | LINKE UMSCHALT+X | LINKE UMSCHALT+PUNKTE 1-3-4-6 |
| Rückgängig | LINKE UMSCHALT+Z | LINKE UMSCHALT+PUNKTE 1-3-5-6 |
| Entfernen | LINKE UMSCHALT+D | LINKE UMSCHALT+PUNKTE 1-4-5 |

## JAWS Befehle

Nutzen Sie diese Kurztasten, um einige der gebräuchlichsten JAWS Funktionen auszuführen.

Tabelle: Eine Tabelle mit dem JAWS-Befehl in der ersten Spalte, dem Kurztastenbefehl in der zweiten Spalte und dem Punktmuster in der dritten Spalte.

| Beschreibung | Braillesymbol | Punktmuster |
| --- | --- | --- |
| JAWS Programmfenster | RECHTE UMSCHALT+J | RECHTE UMSCHALT+PUNKTE 2-4-5 |
| Schnelleinstellung | RECHTE UMSCHALT+V | RECHTE UMSCHALT+PUNKTE 1-2-3-6 |
| Rahmenliste | RECHTE UMSCHALT+RUNTERGERUTSCHTE 9 | RECHTE UMSCHALT+PUNKTE 3-5 |
| Überschriftenliste | RECHTE UMSCHALT+RUNTERGERUTSCHTE 6 | RECHTE UMSCHALT+PUNKTE 2-3-5 |
| Linkliste | RECHTE UMSCHALT+RUNTERGERUTSCHTE 7 | RECHTE UMSCHALT+PUNKTE 2-3-5-6 |
| Taskliste öffnen | RECHTE UMSCHALT+PUNKTE 3-5-6 | RECHTE UMSCHALT+PUNKTE 3-5-6 |
| Symbole des Infobereichs auflisten | RECHTE UMSCHALT+K | RECHTE UMSCHALT+PUNKTE 1-3 |
| Aktuelle Systemzeit ansagen | RECHT UMSCHALT+PUNKTE 1-2-3 | RECHT UMSCHALT+PUNKTE 1-2-3 |
| Ziehen und Ablegen (Drag and Drop) | RECHTE UMSCHALT+PUNKTE 3-7 CHORD | - |
| Bildschirm neu aufbauen | RECHTE UMSCHALT+Z | RECHTE UMSCHALT+PUNKTE 1-3-5-6 |
| Schriftart ansagen | RECHTE UMSCHALT+F | RECHTE UMSCHALT+PUNKTE 1-2-4 |
| Tastaturhilfe umschalten | FRAGEZEICHEN CHORD | PUNKTE 1-4-5-6 CHORD |
| Hilfe für Windows Tastaturbefehle | RECHTE UMSCHALT+W | RECHTE UMSCHALT+PUNKTE 2-4-5-6 |
| Aktuelles Fenster lesen | RECHTE UMSCHALT+B | RECHTE UMSCHALT+PUNKTE 1-2 |
| Standard-Schalter in Dialogfeldern | RECHTE UMSCHALT+E | RECHTE UMSCHALT+PUNKTE 1-5 |
| JAWS beenden | RECHTE UMSCHALT+RUNTERGERUTSCHTE 4 | RECHTE UMSCHALT+PUNKTE 2-5-6 |
| Ein Stimmenprofil auswählen | RECHTE UMSCHALT+S | RECHTE UMSCHALT+PUNKTE 2-3-4 |
| Sprache aus | LINKE oder RECHTE UMSCHALT | - |
| Sprechgeschwindigkeit temporär erhöhen | LINKE oder RECHTE UMSCHALT+RECHTE AUSWAHL CHORD | - |
| Sprechgeschwindigkeit temporär verringern | LINKE oder RECHTE UMSCHALT+LINKE AUSWAHL CHORD | - |
| Sprechgeschwindigkeit dauerhaft erhöhen | RECHTE AUSWAHL CHORD | - |
| Sprechgeschwindigkeit dauerhaft verringern | LINKE AUSWAHL CHORD | - |
| Sprache Auf Abruf umschalten | RECHTE UMSCHALT+F | RECHTE UMSCHALT+PUNKTE 1-3-4 |
| Letzten Hinweis wiederholen | RECHTE UMSCHALT+N | RECHTE UMSCHALT+PUNKTE 1-3-4-5 |
| Braille Math Editor starten | PUNKTE 3-4-6-7 CHORD | - |

## Cursor Funktionen

Nutzen Sie diese Kurztasten, um einen Cursor zum Navigieren von JAWS zu wählen.

Tabelle: Eine Tabelle mit der Cursorfunktion in der ersten Spalte, dem Braille-Zeichen in der zweiten Spalte und dem Punktmuster in der dritten Spalte.

| Beschreibung | Braillesymbol | Punktmuster |
| --- | --- | --- |
| JAWS Cursor | J CHORD | PUNKTE 2-4-5 CHORD |
| PC Cursor | P CHORD | PUNKTE 1-2-3-4 CHORD |
| Touch Cursor | PUNKTE 1-2-5-6 CHORD | PUNKTE 1-2-5-6 CHORD |
| Ziehe JAWS zu PC | RECHTE UMSCHALT+PUNKTE 3-6 (Minus-Zeichen) | RECHTE UMSCHALT+PUNKTE 3-6 |
| Ziehe PC zu JAWS | RECHTE UMSCHALT+PLUS-Zeichen | RECHTE UMSCHALT+PUNKTE 3-4-6 |
| Braille folgt Aktivem Cursor | PUNKTE 1-2-6 CHORD | PUNKTE 1-2-6 CHORD |
| Aktiver Cursor folgt Braille | PUNKTE 1-2-7 CHORD | PUNKTE 1-2-7 CHORD |
| Braille Cursor zum PC Cursor ziehen | LINKE UMSCHALT+PUNKTE 3-4-6 | LINKE UMSCHALT+PUNKTE 3-4-6 |
| Ziehe Braillecursor zum Aktiven Cursor | LINKE UMSCHALT+PUNKTE 3-6 | LINKE UMSCHALT+PUNKTE 3-6 |

## Touchcursor Funktionen

Nutzen Sie diese Kurztasten, um mit dem Touchcursor zu navigieren.

Tabelle: Eine Tabelle mit den Touchcursorbefehlen in der ersten Spalte, dem Braille-Zeichen in der zweiten Spalte und dem Punktmuster in der dritten Spalte.

| Beschreibung | Braillesymbol | Punktmuster |
| --- | --- | --- |
| Touch Cursor | PUNKTE 1-2-5-6 CHORD | PUNKTE 1-2-5-6 CHORD |
| Vorheriges Element | PUNKTE 1-2 CHORD | PUNKTE 1-2 CHORD |
| Nächstes Element | PUNKTE 4-5 CHORD | PUNKTE 4-5 CHORD |
| Aktuelles Element ansagen | C CHORD | PUNKTE 1-4 CHORD |
| Nächstes Element nach Typ (wie ausgewählt im Navigationsrotor) | LINKE oder RECHTE KIPPTASTE RUNTER | LINKE oder RECHTE KIPPTASTE RUNTER |
| Vorheriges Element nach Typ (wie ausgewählt im Navigationsrotor) | LINKE oder RECHTE KIPPTASTE RAUF | LINKE oder RECHTE KIPPTASTE RAUF |
| Vorwärts durch die Navigationstypen bewegen | LINKE AUSWAHL+LINKE KIPPTASTE RUNTER , RECHTE AUSWAHL+LINKE KIPPTASTE RUNTER , LINKE AUSWAHL+RECHTE KIPPTASTE RUNTER oder RECHTE AUSWAHL+RECHTE KIPPTASTE RUNTER | LINKE AUSWAHL+LINKE KIPPTASTE RUNTER , RECHTE AUSWAHL+LINKE KIPPTASTE RUNTER , LINKE AUSWAHL+RECHTE KIPPTASTE RUNTER oder RECHTE AUSWAHL+RECHTE KIPPTASTE RUNTER |
| Rückwärts durch die Navigationstypen bewegen | LINKE AUSWAHL+LINKE KIPPTASTE RAUF , RECHTE AUSWAHL+LINKE KIPPTASTE RAUF , LINKE AUSWAHL+RECHTE KIPPTASTE RAUF oder RECHTE AUSWAHL+RECHTE KIPPTASTE RAUF | LINKE AUSWAHL+LINKE KIPPTASTE RAUF , RECHTE AUSWAHL+LINKE KIPPTASTE RAUF , LINKE AUSWAHL+RECHTE KIPPTASTE RAUF oder RECHTE AUSWAHL+RECHTE KIPPTASTE RAUF |
| Gehe zu erstem Element | LINKE LESETASTE+LINKE oder RECHTE AUSWAHL oder L CHORD | LINKE LESETASTE+LINKE oder RECHTE AUSWAHL oder PUNKTE 1-2-3 CHORD |
| Gehe zu letztem Element | RECHTE LESETASTE+LINKE oder RECHTE AUSWAHL oder PUNKTE 4-5-6 CHORD | LINKE LESETASTE+LINKE oder RECHTE AUSWAHL oder PUNKTE 4-5-6 CHORD |
| Aktuelles Element aktivieren | CURSORROUTINGTASTE | CURSORROUTINGTASTE |
| Textlesemodus aktivieren | RECHTE UMSCHALT+PUNKT 7 | RECHTE UMSCHALT+PUNKT 7 |
| Textlesemodus ausschalten | RECHTE UMSCHALT+PUNKT 1 oder X CHORD | RECHTE UMSCHALT+PUNKT 1 oder PUNKTE 1-3-4-6 CHORD |
| Erweiterte Navigation umschalten | RECHTE UMSCHALT+PUNKT 3 oder Cursorroutingtaste drücken und gedrückt halten | RECHTE UMSCHALT+PUNKT 3 oder Cursorroutingtaste drücken und gedrückt halten |

## Hilfsprogramm Funktionen

Nutzen Sie diese Kurztasten für allgemeine Funktionen der Hilfsprogramme.

Tabelle: Eine Tabelle mit der Hilfsprogrammfunktion in der ersten Spalte, dem Kurztastenbefehl in der zweiten Spalte und dem Punktmuster in der dritten Spalte.

| Beschreibung | Braillesymbol | Punktmuster |
| --- | --- | --- |
| JAWS Manager aufrufen | RECHTE UMSCHALT+RUNTERGERUTSCHTE 2 | RECHTE UMSCHALT+PUNKTE 2-3 |
| Linke obere Rahmenecke setzen | RECHTE UMSCHALT+Ö | RECHTE UMSCHALT+PUNKTE 2-4-6 |
| Rechte untere Rahmenecke setzen | RECHTE UMSCHALT+ER-Zeichen | RECHTE UMSCHALT+PUNKTE 1-2-4-5-6 |
| Grafikbezeichner | RECHTE UMSCHALT+G | RECHTE UMSCHALT+PUNKTE 1-2-4-5 |
| JAWS Suchen | RECHTE UMSCHALT+F CHORD | RECHTE UMSCHALT+PUNKTE 1-2-4 CHORD |
| JAWS Weitersuchen | RECHTE UMSCHALT+PUNKTE 2-5 | RECHTE UMSCHALT+PUNKTE 2-5 |

Quelle: Braille_Display_Input_Commands.htm

## Die Elemente der Focus 14, Focus 40 und Focus 80 Blue

Die Focus 14, Focus 40 und Focus 80 Blue Braillezeilen sind mit zwei Navigationskipptasten, zwei Modustasten, zwei Lesetasten, zwei Kippschaltern, zwei Auswahlschaltern, vier Lesekipptasten (nur Focus 80 Blue) und Cursorroutingtasten über jedem Braillemodul ausgestattet.

## Navigationskippschalter und Modusschalter

Mit den Navigationskippschaltern der Focus-Zeilen können Sie schnell durch Dateien, Dialoge, Listen und Menüs navigieren. Sie können sich damit in einer Datei zeilen-, satz- oder absatzweise bewegen oder rückwärts und vorwärts weitergehen. Zum Durchschalten durch die vier Navigationsmodi, drücken Sie die Modustaste, die sich direkt oberhalb der Navigationskippschalter befindet. Sie springen in einem Dialogfenster auf die vorhandenen Steuerelemente und interagieren Sie mit ihnen. Bewegen Sie sich in einem Menü rauf und runter durch die Einträge.

## Lesetasten

Die Focus Lesetasten bewegen die Braillezeile bei jedem Drücken eine Anzeige (14, 40 oder 80 Zellen) nach links oder rechts weiter. Drücken Sie die Lesetaste an der linken, vorderen Ecke der Focus, der Schalter mit einem erhabenem doppelten Pfeil Links Symbol, um nach links zu schwenken; drücken Sie die Lesetaste an der rechten, hinteren Ecke der Focus, der Schalter mit einem erhabenem doppelten Pfeil Rechts Symbol, um nach rechts zu schwenken. Die Funktionen der Lesetasten können vertauscht werden, so dass beim Drücken der linken Lesetaste die Focus nach rechts weiterbewegt und beim Drücken der rechten Lesetaste nach links weiterbewegt wird. Lesen Sie die Hilfe über den [JAWS Tastaturmanager](jkey.chm::/jkey/introduction_to_keyboard_manager.htm) , um Informationen über das Ändern dieser und anderer Elementzuweisungen zu erfahren.

## Kipptasten

Mithilfe der Kipptasten bewegen Sie sich zeilenweise nach oben oder nach unten. Drücken Sie das obere Ende der Kipptaste, um eine Zeile nach oben zu gehen. Drücken Sie das untere Ende der Kipptaste, um eine Zeile nach unten zu gehen. Die Kipptasten in Kombination mit den Lesetasten springen an den Anfang oder das Ende der Zeile, auf dem sich der Cursor befindet. Drücken Sie eine Lesetaste und das obere Ende einer Kipptaste, um an den Zeilenanfang zu springen. Drücken Sie eine Lesetaste und das untere Ende einer Kipptaste, um an das Zeilenende zu springen.

## Auswahltasten

Wenn Sie alleine betätigt werden, steuern die konkav-geformten Auswahltasten das Automatische Weiterbewegen. Wenn Sie in Kombination mit anderen Steuerelementen gedrückt werden, führen die Auswahltasten mehrere Funktionen aus.

## Kipp-Lesetasten (nur Focus 80 Blue)

Die vier Kipp-Lesetasten auf der Focus 80 Blue dienen als zusätzliche Lesetasten. Sie bewegen jedoch auf die gleiche Art wie die Kipptasten. Drücken Sie das obere Ende einer der beiden Kipp-Lesetasten, um nach links zu springen und drücken Sie das untere Ende, um nach rechts zu springen.

## Cursorroutingtasten

Cursorroutingtasten befinden sich über jedem Braillemodul. Drücken Sie eine Cursorroutingtaste, um den Cursor an diesen Punkt zu ziehen, oder um einen Link auf einer Webseite oder in einer E-Mail zu aktivieren. Im Flächenmodus können Sie durch Druck auf eine Cursorroutingtaste ein Menü öffnen oder Menüeinträge auswählen.

## Mehrfach-Funktionen

| Funktion | Taste(n) |
| --- | --- |
| Automatisches Weiterbewegen aktivieren | LINKE+RECHTE AUSWAHLTASTE |
| Geschwindigkeit beim Automatischen Weiterbewegen verringern | LINKE AUSWAHLTASTE |
| Geschwindigkeit beim Automatischen Weiterbewegen erhöhen | RECHTE AUSWAHLTASTE |
| Rechter Mausklick | LESETASTE+CURSORROUTINGTASTE |
| STRG+Linker Mausklick | CURSORROUTINGTASTE+CHORD |
| Seite runter | LINKE oder RECHTE AUSWAHLTASTE+KIPPTASTE RUNTER |
| Seite rauf | LINKE oder RECHTE AUSWAHLTASTE+KIPPTASTE RAUF |
| Dateianfang | LINKE LESETASTE+AUSWAHLSCHALTER oder AUSWAHLTASTE+KIPP-LESE TASTE RAUF |
| Dateiende | RECHTE LESETASTE+AUSWAHLSCHALTER oder AUSWAHLTASTE+KIPP-LESETASTE RUNTER |
| Ende | LESETASTE+KIPPTASTE RUNTER |
| POS1 | LESETASTE+KIPPTASTE RAUF |
| Nächste Zeile | KIPTASTE RUNTER |
| Vorherige Zeile | KIPPTASTE RAUF |
| Nach links bewegen | LINKE LESETASTE |
| Nach rechts bewegen | RECHTE LESETASTE |
| Text markieren | LINKE UMSCHALT+CURSORROUTINGTASTE |
| Block markieren | RECHTE UMSCHALT+CURSORROUTINGTASTE am Blockanfang; am Blockende wiederholen |
| Navigationskippschalter umschalten zwischen An/Aus | LINKER oder RECHTER Modusschalter CHORD |

## Focus Blue Tastatur

Direkt oberhalb der Routingtasten befinden sich 8 Tasten, die denen einer Perkins-Braille-Tastatur entsprechen. Bei den acht Brailletasten handelt es sich von links nach rechts um: 7, 3, 2, 1, 4, 5, 6, und 8. Diese Tasten können für die Texteingabe oder zum Ausführen von Befehlen verwendet werden. An der Vorderkante, direkt unter und mittig der Braillezeile befindet sich eine **LEERTASTE** . Diese Taste wird gemeinsam mit den Brailletasten bei der Eingabe von Befehlen verwendet. Direkt unter der **LEERTASTE** an der Vorderkante der Braillezeile befinden sich zwei **UMSCHALT** Tasten, die auch zum Ausführen von verschiedenen Befehlen genutzt werden. Lesen Sie das Hilfethema [Braillezeilen Eingabebefehle](Braille_Display_Input_Commands.htm) für weitere Informationen zum Ausführen von JAWS und Windows Befehlen mit der Focus Blue.

### Die Perkins-Braille-Tastatur sperren

Wenn Sie Ihre Focus Blue vor der QWERTZ Tastatur Ihres Rechners verwenden, dann können Sie die Perkins-Tastaen auf der Braillezeile sperren, um ein unbeabsichtigtes Drücken und damit die ungewünschte Eingabe von Text oder Befehlen zu vermeiden.

Um die Tastatur der Focus Blue zu sperren, drücken Sie den Power-Schalter, um die Statusinformationen anzuzeigen, und dann gleichzeitig eine Cursorroutingtaste und die linke Modustaste. Um anzuzeigen, dass die Tastatur gesperrt ist, werden PUNKTE 2-3-4-6-7-8 und PUNKTE 1-3-5-6-7-8 in zwei Zellen am rechten Ende der Braillezeile angezeigt, direkt vor dem Verbindungsstatus. Drücken Sie irgendeine andere Taste, um zur normalen Ausführung zurückzukehren. Einmal gesperrt, wird das Drücken der **PUNKTE 1** bis **8** oder der **LEERTASTE** keine Tasten mehr an den Computer senden.

Um die Tastatur wieder zu entsperren, damit Sie wieder Text eingeben oder Befehle über die Focus Blue ausführen können, drücken Sie den Power Schalter, um die Statusinformationen anzuzeigen, und dann gleichzeitig eine Cursorroutingtaste und die rechte Modustaste. Drücken Sie irgendeine andere Taste, um zur normalen Ausführung zurückzukehren und Sie sind wieder in der Lage, über die Tastatur der Focus Blue Text einzugeben.

Quelle: Controls_for_Focus_14_40_and_80_Blue.htm

## Die Elemente der klassischen Focus 40 Blue

Die klassische Focus 40 Blue ist mit zwei Scrollrädern, zwei Lesetasten, zwei Kipptasten, zwei Auswahltasten und Cursorroutingtasten und Navigationstasten über jedem Braillemodul ausgestattet.

## Scrollräder

Mit den Scrollrädern der Focus-Zeilen können Sie schnell durch Dateien, Dialoge, Listen und Menüs navigieren. Sie können sich damit in einer Datei zeilen-, satz- oder absatzweise bewegen oder rückwärts und vorwärts weitergehen. Sie springen in einem Dialogfenster auf die vorhandenen Steuerelemente und interagieren Sie mit ihnen. Bewegen Sie sich in einem Menü rauf und runter durch die Einträge. Weitere Information darüber finden Sie im Hilfethema [Scrollräder](focus_ww_ab_crk.htm#whiz) .

## Lesetasten

Die Focus Lesetasten bewegen die Braillezeile bei jedem Drücken eine Anzeige (40 Zellen) nach links oder rechts weiter. Drücken Sie die Lesetaste an der linken Seite der Focus, um nach links weiterzubewegen; drücken Sie die Lesetaste auf der rechten Seite der Focus, um nach rechts weiterzubewegen. Die Funktionen der Lesetasten können vertauscht werden, so dass beim Drücken der linken Lesetaste die Focus nach rechts weiterbewegt und beim Drücken der rechten Lesetaste nach links weiterbewegt wird. Lesen Sie die Hilfe über den [JAWS Tastaturmanager](jkey.chm::/jkey/introduction_to_keyboard_manager.htm) , um Informationen über das Ändern dieser und anderer Elementzuweisungen zu erfahren.

## Kipptasten

Mithilfe der Kipptasten bewegen Sie sich zeilenweise nach oben oder nach unten. Drücken Sie das obere Ende der Kipptaste, um eine Zeile nach oben zu gehen. Drücken Sie das untere Ende der Kipptaste, um eine Zeile nach unten zu gehen. Die Kipptasten in Kombination mit den Lesetasten springen an den Anfang oder das Ende der Zeile, auf dem sich der Cursor befindet. Drücken Sie eine Lesetaste und das obere Ende einer Kipptaste, um an den Zeilenanfang zu springen. Drücken Sie eine Lesetaste und das untere Ende einer Kipptaste, um an das Zeilenende zu springen.

## Auswahltasten

Wenn Sie alleine betätigt werden, steuern die Auswahltasten das Automatische Weiterbewegen. Wenn Sie in Kombination mit anderen Steuerelementen gedrückt werden, führen die Auswahltasten mehrere Funktionen aus.

## Cursorroutingtasten

Cursorroutingtasten befinden sich über jedem Braillemodul. Drücken Sie eine Cursorroutingtaste, um den Cursor an diesen Punkt zu ziehen, oder um einen Link auf einer Webseite oder in einer E-Mail zu aktivieren. Im Flächenmodus können Sie durch Druck auf eine Cursorroutingtaste ein Menü öffnen oder Menüeinträge auswählen.

Drücken und halten Sie die **RECHTE AUSWAHLTASTE** , während Sie gleichzeitig eine **CURSORROUTINGTASTE** drücken, um einen rechten Mausklick an der Stelle auszuführen.

## Navigationstasten

Direkt hinter den Cursorroutingtasten befinden sich die Navigationstasten. Die Anzahl der Navigationstasten ist identisch mit der Anzahl der Braillemodule auf den Focus Zeilen. Die Funktionstasten haben zwei Funktionen - zehn dienen als Kurztasten, die einen schnellen Zugriff auf Funktionen oder Einstellungen ermöglichen und der Rest dient als zusätzliche Lesetasten.

Direkt hinter den Navigationstasten befinden sich sieben erhabene Markierungen, die zur schnellen Orientierung sowohl für Navigations- als auch Cursorroutingtasten dienen: Die zehn Funktionstasten direkt unter der mittleren Markierung sind Kurztasten und durchnummeriert, zur Linken der mittleren Markierung, 1 bis 5. Die fünf Tasten zur Rechten dieser Markierung sind von links nach rechts mit 6 bis 10 nummeriert. Die restlichen Tasten haben die gleiche Funktion wie die Lesetasten, die auf der linken Seite bewegen zurück, und die auf der rechten Seite bewegen vorwärts.

Tabelle: Diese Tabelle beschreibt die 14 Navigationskurztasten

| Funktion | Tastenkürzel |
| --- | --- |
| Braille Cursor zum PC Cursor ziehen | 1 |
| Aktiver Cursor folgt Braillecursor | 2 |
| Braillecursor folgt Aktivem Cursor | 3 |
| Fensteranfang | 4 |
| UMSCHALT+TAB | 5 |
| TAB | 6 |
| Fensterende | 7 |
| Kurzschriftübersetzung umschalten | 8 |
| Aktuelles Wort ausschreiben | 9 |
| Ziehe Braillecursor zum Aktiven Cursor | 10 |

Außerdem sind die beiden Navigationstasten direkt zur Linken der ersten Kurztaste und die beiden zur Rechten der zehnten Kurztaste folgenden speziellen Funktionen zugewiesen:

Tabelle: Diese Tabelle beschreibt die 14 Navigationskurztasten

| Funktion | Navigationstaste |
| --- | --- |
| Automatisches Weiterbewegen aktivieren | Zweite Taste zur Linken der ersten Kurztaste |
| Letzte Blitzmeldung wiederholen | Erste Taste zur Linken der ersten Kurztaste |
| Geschwindigkeit beim Automatischen Weiterbewegen verringern | Erste Taste zur Rechten der zehnten Kurztaste |
| Geschwindigkeit beim Automatischen Weiterbewegen erhöhen | Zweite Taste zur Rechten der zehnten Kurztaste |

## Mehrfach-Funktionen

| Funktion | Taste(n) |
| --- | --- |
| Automatisches Weiterbewegen aktivieren | LINKE+RECHTE AUSWAHLTASTE |
| Geschwindigkeit beim Automatischen Weiterbewegen verringern | LINKE AUSWAHLTASTE |
| Geschwindigkeit beim Automatischen Weiterbewegen erhöhen | RECHTE AUSWAHLTASTE |
| Linker Mausklick | LESETASTE+CURSORROUTINGTASTE oder KIPP-LESE TASTE RAUF+CURSORROUTINGTASTE oder KIPP-LESE TASTE RUNTER+CURSORROUTINGTASTE |
| STRG+Linker Mausklick | CURSORROUTINGTASTE+CHORD |
| Seite runter | LINKE oder RECHTE AUSWAHLTASTE+KIPPTASTE RUNTER |
| Seite rauf | LINKE oder RECHTE AUSWAHLTASTE+KIPPTASTE RAUF |
| Dateianfang | LINKE LESETASTE+AUSWAHLSCHALTER oder AUSWAHLTASTE+KIPP-LESE TASTE RAUF |
| Dateiende | RECHTE LESETASTE+AUSWAHLSCHALTER oder AUSWAHLTASTE+KIPP-LESETASTE RUNTER |
| Ende | LESETASTE+KIPPTASTE RUNTER |
| POS1 | LESETASTE+KIPPTASTE RAUF |
| Nächste Zeile | KIPTASTE RUNTER |
| Vorherige Zeile | KIPPTASTE RAUF |
| Nach links bewegen | LINKE LESETASTE oder LINKE KIPP-LESETASTE RAUF |
| Nach rechts bewegen | RECHTE LESETASTE oder RECHTE KIPP-LESETASTE RAUF |
| Text markieren | RECHTE AUSWAHLTASTE+CURSORROUTINGTASTE |
| Block markieren | AUSWAHLTASTE+CURSORROUTINGTASTE am Blockanfang; am Blockende wiederholen |
| Scrollräder ein-/ausschalten | LINKES oder RECHTES SCROLLRAD+CHORD |

Quelle: Controls_for_Focus_40_Blue.htm

## Die Elemente der Focus 40 und 80

Die Braillezeilen Focus 40 und 80 sind mit zwei Scrollrädern, zwei Lesetasten, zwei Kipptasten, zwei Auswahltasten, zwei Kipp-Lesetasten (nur Focus 80) und Cursorroutingtasten und Funktionstasten über jedem Braillemodul ausgestattet.

## Scrollräder

Mit den Scrollrädern der Focus-Zeilen können Sie schnell durch Dateien, Dialoge, Listen und Menüs navigieren. Sie können sich damit in einer Datei zeilen-, satz- oder absatzweise bewegen oder rückwärts und vorwärts weitergehen. Sie springen in einem Dialogfenster auf die vorhandenen Steuerelemente und interagieren Sie mit ihnen. Bewegen Sie sich in einem Menü rauf und runter durch die Einträge. Weitere Information darüber finden Sie im Hilfethema [Scrollräder](focus_ww_ab_crk.htm#whiz) .

## Lesetasten

Die Focus Lesetasten bewegen die Braillezeile bei jedem Drücken eine Anzeige (40 oder 80 Zellen) nach links oder rechts weiter. Die beiden Lesetasten haben eine rechteckige Form, so dass sie bequem mit den Daumen betätigt werden können, wenn Ihre Hände auf den Braillemodulen mit Lesen beschäftigt sind. Drücken Sie die Lesetaste an der linken Seite, um nach links zu springen. Drücken Sie die Lesetaste an der rechten Seite, um nach rechts zu springen.

## Kipptasten

Mithilfe der Kipptasten bewegen Sie sich zeilenweise nach oben oder nach unten. Drücken Sie das obere Ende der Kipptaste, um eine Zeile nach oben zu gehen. Drücken Sie das untere Ende der Kipptaste, um eine Zeile nach unten zu gehen. Die Kipptasten in Kombination mit den Lesetasten springen an den Anfang oder das Ende der Zeile, auf dem sich der Cursor befindet. Drücken Sie eine Lesetaste und das obere Ende einer Kipptaste, um an den Zeilenanfang zu springen. Drücken Sie eine Lesetaste und das untere Ende einer Kipptaste, um an das Zeilenende zu springen.

## Auswahltasten

Wenn Sie alleine betätigt werden, steuern die Auswahltasten das Automatische Weiterbewegen. Wenn Sie in Kombination mit anderen Steuerelementen gedrückt werden, führen die Auswahltasten mehrere Funktionen aus.

## Kipp-Lesetasten (nur Focus 80)

Die beiden Kipp-Lesetasten auf der Focus 80 dienen als zusätzliche Lesetasten. Sie bewegen jedoch auf die gleiche Art wie die Kipptasten. Drücken Sie das obere Ende einer der beiden Kipp-Lesetasten, um nach links zu springen und drücken Sie das untere Ende, um nach rechts zu springen.

## Brailletastatur

Zwischen den Braillemodulen und dem vorderen Ende des Gerätes, unter einer abnehmbaren Plastikklappe, befinden sich acht Tasten, die einer Perkins Brailletastatur ähneln. Diese Tasten sind für die Eingabe von Befehlen vorgesehen. Am vorderen Ende der Zeile finden Sie drei Tasten **LINKE UMSCHALT** , **LEERTASTE** und **RECHTE UMSCHALT** . Diese drei Tasten werden zusammen mit den Brailletasten zur Eingabe von Befehlen verwendet.

## Cursorroutingtasten

Über den Braillemodulen befinden sich die Cursorroutingtasten. Drücken Sie eine Cursorroutingtaste, um den Cursor an diesen Punkt zu ziehen, oder um einen Link auf einer Webseite oder in einer E-Mail zu aktivieren. Im Flächenmodus können Sie durch Druck auf eine Cursorroutingtaste ein Menü öffnen oder Menüeinträge auswählen.

Drücken und halten Sie die **RECHTE AUSWAHLTASTE** , während Sie gleichzeitig eine **CURSORROUTINGTASTE** drücken, um einen rechten Mausklick an der Stelle auszuführen.

## Navigationstasten

Direkt hinter den Cursorroutingtasten befinden sich die Navigationstasten. Die Anzahl der Navigationstasten ist identisch mit der Anzahl der Braillemodule auf den Focus Zeilen. Die Navigationstasten haben zwei Funktionen - 14 dienen als Kurztasten, die einen schnellen Zugriff auf Funktionen oder Einstellungen ermöglichen und der Rest dient als zusätzliche Lesetasten.

Die 14 Navigationstasten direkt unter der mittleren Markierung sind die Kurztasten. Sie sind von links beginnend nummeriert und gehen dann bis zur mittleren Markierung als 1 bis 7. Die sieben Tasten von rechts bis zur mittleren Markierung sind von 8 bis 14 nummeriert. Die unten stehende Tabelle enthält eine Beschreibung der Navigationstasten.

Die verbleibenden Navigationstasten verfügen über die gleiche Funktion wie die Tasten zum Weiterbewegen. Die auf der linken Seite springen rückwärts und die auf der rechten Seite vorwärts.

Tabelle: Diese Tabelle beschreibt die 14 Navigationskurztasten

| Funktion | Tastenkürzel |
| --- | --- |
| Automatisches Weiterbewegen aktivieren | 1 |
| Letzte Blitzmeldung wiederholen | 2 |
| Braille Cursor zum PC Cursor ziehen | 3 |
| Aktiver Cursor folgt Braillecursor | 4 |
| Braillecursor folgt Aktivem Cursor | 5 |
| Fensteranfang | 6 |
| UMSCHALT+TAB | 7 |
| TAB | 8 |
| Fensterende | 9 |
| Kurzschriftübersetzung umschalten | 10 |
| Aktuelles Wort ausschreiben | 11 |
| Ziehe Braillecursor zum Aktiven Cursor | 12 |
| Geschwindigkeit beim Automatischen Weiterbewegen verringern | 13 |
| Geschwindigkeit beim Automatischen Weiterbewegen erhöhen | 14 |

## Mehrfach-Funktionen

| Funktion | Taste(n) |
| --- | --- |
| Automatisches Weiterbewegen aktivieren | LINKE+RECHTE AUSWAHLTASTE |
| Geschwindigkeit beim Automatischen Weiterbewegen verringern | LINKE AUSWAHLTASTE |
| Geschwindigkeit beim Automatischen Weiterbewegen erhöhen | RECHTE AUSWAHLTASTE |
| Linker Mausklick | LESETASTE+CURSORROUTINGTASTE |
| STRG+Linker Mausklick | CURSORROUTINGTASTE+CHORD |
| Seite runter | LINKE oder RECHTE AUSWAHLTASTE+KIPPTASTE RUNTER |
| Seite rauf | LINKE oder RECHTE AUSWAHLTASTE+KIPPTASTE RAUF |
| Dateianfang | LINKE LESETASTE+AUSWAHLSCHALTER oder AUSWAHLTASTE+KIPP-LESE TASTE RAUF |
| Dateiende | RECHTE LESETASTE+AUSWAHLSCHALTER oder AUSWAHLTASTE+KIPP-LESETASTE RUNTER |
| Ende | LESETASTE+KIPPTASTE RUNTER |
| POS1 | LESETASTE+KIPPTASTE RAUF |
| Nächste Zeile | KIPTASTE RUNTER |
| Vorherige Zeile | KIPPTASTE RAUF |
| Nach links bewegen | LINKE LESETASTE oder LINKE KIPP-LESETASTE RAUF |
| Nach rechts bewegen | RECHTE LESETASTE oder RECHTE KIPP-LESETASTE RAUF |
| Text markieren | RECHTE AUSWAHLTASTE+CURSORROUTINGTASTE |
| Block markieren | AUSWAHLTASTE+CURSORROUTINGTASTE am Blockanfang; am Blockende wiederholen |
| Scrollräder ein-/ausschalten | LINKES oder RECHTES SCROLLRAD+CHORD |

Quelle: Controls_for_Focus_40_and_80.htm

## Focus Bluetooth-Verbindung

Damit Sie die Focus Blue kabellos mit JAWS über Bluetooth nutzen können, müssen Sie zuerst eine Bluetooth Partnerschaft zwischen der Focus und dem Computer konfigurieren.

Gehen Sie bitte folgendermaßen vor, um eine Bluetooth-Partnerschaft zwischen der Focus Braillezeile und dem Rechner einzurichten:

1. Drücken Sie die **WINDOWSTASTE** , schreiben Sie "Bluetooth" in das Sucheingabefeld und drücken Sie **EINGABE** , um auf die Bluetooth-Einstellungen Ihres Computers zuzugreifen.
2. Drücken Sie **TAB** , um zum Bluetooth-Schalter zu springen und ist dieser deaktiviert, dann schalten Sie ihn mit der **LEERTASTE** ein.
3. Schalten Sie die Focus ein. Die Statusinformationen werden angezeigt.
4. Drücken Sie **UMSCHALT+TAB** , um auf den Schalter Bluetooth. oder anderes Gerät hinzufügen springen und drücken Sie die **LEERTASTE** . Drücken Sie noch einmal die **Leertaste** auf Bluetooth.
5. Drücken Sie **TAB** , um auf die Liste der verfügbaren Geräte zu springen.
6. Verwenden Sie die **PFEILTASTEN** , um Ihre Focus Braillezeile in der Liste auszuwählen und drücken Sie dann **EINGABE** , um das Koppeln der Braillezeile abzuschließen. Wurde die Focus nicht gefunden, dann stellen Sie sicher, dass diese eingeschaltet ist.

Jetzt müssen Sie JAWS für die Nutzung der Bluetooth Verbindung konfigurieren. Beachten Sie, dass es nicht notwendig ist, zuerst eine USB Verbindung herzustellen, um Bluetooth zu nutzen. Wenn Sie bisher noch keine USB Verbindung mit der Focus Braillezeile eingerichtet haben, gehen Sie wie folgt vor:

1. Drücken Sie **JAWS TASTE+J** , um das JAWS Programmfenster zu öffnen.
2. Öffnen Sie mit **ALT+O** das Menü Optionen, gehen Sie auf den Eintrag Braille und drücken Sie EINGABE, um den Dialog Braille Grundeinstellungen zu öffnen.
3. Gehen Sie mit **TAB** auf Braillezeile hinzufügen und drücken Sie **EINGABE** .
4. Wählen Sie Focus in der Liste der Braillezeilen und drücken Sie **LEERTASTE** , um diese auszuwählen, gehen Sie dann auf Weiter.
5. Im kombinierten Eingabefeld für die Ausgabeschnittstelle wählen Sie Bluetooth.
6. Wählen Sie Weiter und stellen Sie sicher, dass die Focus als erste Braillezeile ausgewählt ist.
7. Aktivieren Sie den Schalter Fertigstellen, und Sie werden aufgefordert, JAWS neu zu starten, damit diese Änderungen wirksam werden. Aktivieren Sie den OK Schalter erneut, um diese Meldung zu schließen und noch einmal, um den Dialog Braille Grundeinstellungen zu schließen.
8. Beenden Sie JAWS und starten Sie es erneut, und Ihre Focus Blue kommuniziert jetzt mit JAWS über Bluetooth.

Wenn Sie gegenwärtig die Focus Braillezeile über USB verwenden und Sie möchten die Verbindung auf Bluetooth umschalten, gehen Sie wie folgt vor:

1. Drücken Sie **JAWS TASTE+J** , um das JAWS Programmfenster zu öffnen.
2. Öffnen Sie mit **ALT+O** das Menü Optionen, gehen Sie auf den Eintrag Braille und drücken Sie EINGABE, um den Dialog Braille Grundeinstellungen zu öffnen.
3. Überprüfen Sie, ob in der Ausklappliste Standard Braillezeile Focus steht, dann aktivieren Sie den Schalter Einstellungen ändern.
4. Im kombinierten Eingabefeld für die Ausgabeschnittstelle wählen Sie Bluetooth.
5. Aktivieren Sie den OK Schalter, und Sie werden aufgefordert, JAWS neu zu starten, damit diese Änderungen wirksam werden. Aktivieren Sie den OK Schalter erneut, um diese Meldung zu schließen und noch einmal, um den Dialog Braille Grundeinstellungen zu schließen.
6. Beenden Sie JAWS und starten Sie es erneut, und Ihre Focus Blue kommuniziert jetzt mit JAWS über Bluetooth.

Sobald JAWS für die Kommunikation mit der Focus Blue über Bluetooth konfiguriert ist, können Sie zwischen USB und Bluetooth hin- und herschalten und JAWS erkennt automatisch die Verbindung, ohne das Einstellungen geändert oder JAWS neu gestartet werden müsste. Wenn Sie beispielsweise das USB Kabel verbinden, dann wird die Zeile mit JAWS über USB arbeiten. Wenn Sie das USB Kabel entfernen und dann die Focus Blue einschalten, dann wird die Zeile mit JAWS über Bluetooth arbeiten.

Um den Batteriestatus zu überprüfen, drücken Sie den Ein-/Ausschalter, so dass die verbleibende Batterieleistung angezeigt wird. Die Buchstaben "BT" werden auch am rechten Ende der Braillemodule angezeigt, um auf die aktive Bluetooth-Verbindung hinzuweisen. Drücken Sie eine Cursorroutingtaste, um zum normalen Betrieb zurückzukehren.

Quelle: Focus_Bluetooth_Connection.htm

## Focus

Die Focus Braillezeilen sind eine ideale taktile Schnittstelle zu Ihrem Computer. Die Modelle der ersten Generation gibt es mit 44, 70 oder 84 Braillemodulen. Die Modelle der späteren Generation gibt es mit 14, 40 oder 80 Braillemodulen. Die folgenden Themen behandeln den Einsatz der Focus 14, Focus 40 und Focus 80 Blue, der klassischen Focus 40 Blue, der Focus 40/80 und der Focus 44/70/84 Braillezeilen zusammen mit JAWS.

[Überblick](focus_overview.htm)

[Die Elemente der Focus 14, Focus 40 und Focus 80 Blue](Controls_for_Focus_14_40_and_80_Blue.htm)

[Die Elemente der klassischen Focus 40 Blue](Controls_for_Focus_40_Blue.htm)

[Die Elemente der Focus 40 und 80](Controls_for_Focus_40_and_80.htm)

[Die Elemente der Focus 44, 70 und 84](focus_ww_ab_crk.htm)

[Braillezeilen Eingabebefehle](Braille_Display_Input_Commands.htm)

[Braille Befehle](focus_brl_cmd.htm)

[Windows Befehle](focus_win_cmd.htm)

[JAWS Befehle](focus_jaws_cmd.htm)

[Befehle für verschiedene Anwendungen](focus_app_cmd.htm)

[Focus Bluetooth-Verbindung](Focus_Bluetooth_Connection.htm)

*Siehe auch:*

Quelle: focus.htm

## Focus Braille Befehle

All diese Befehle verwenden die **LEERTASTE** der Focus Braillezeile. Wir verwenden den Begriff Chord, um dies anzuzeigen. Ein Chord ist lediglich eine Folge von Tasten, die zusammen mit der **LEERTASTE** gedrückt werden.

**Hinweis:** Um das Lesen für Sie zu vereinfachen, haben wir sowohl das Braillesymbol als auch die Punktekombination angegeben. Navigieren Sie einfach zu der Spaltenüberschrift der Darstellungsweise, die Sie bevorzugen, und drücken Sie **ALT+STRG+PFEIL RUNTER** , um sich durch die Befehlsliste zu bewegen. Sie hören dann lediglich die Befehlsbeschreibung und entweder das Braillesymbol oder die Punktekombination, nicht jedoch beides. Gibt es für eine Punktekombination kein Braillesymbol, wird die Punktekombination in beiden Spalten angezeigt.

Tabelle: Focus Braille Befehle

| Beschreibung | Braillesymbol | Braille Punktekombination |
| --- | --- | --- |
| Braillezeile auf erste Fensterzeile | L CHORD | PUNKTE 1-2-3 CHORD |
| Braillezeile auf letzte Fensterzeile | PUNKTE 4-5-6 CHORD | PUNKTE 4-5-6 CHORD |
| Aktuelles Wort bei Kurzschriftübersetzung ausschreiben | T CHORD | PUNKTE 2-3-4-5 CHORD |
| Kurzschriftübersetzung | PUNKTE 1-2-4-5-7 CHORD | PUNKTE 1-2-4-5-7 CHORD |
| Zeichen- und Attributmodus umschalten | PUNKTE 1-6 CHORD | PUNKTE 1-6 CHORD |
| Schaltet um zwischen Flächenmodus, strukturiertem Modus und Sprachausgabenmodus. | M CHORD | PUNKTE 1-3-4 CHORD |
| 8-/6-Punkt-Braille umschalten | 8 CHORD | PUNKTE 2-3-6 CHORD |
| Cursorform verändern | PUNKTE 1-4-6 CHORD | PUNKTE 1-4-6 CHORD |
| Braillecursor beschränken | R CHORD | PUNKTE 1-2-3-5 CHORD |

Quelle: focus_brl_cmd.htm

## Weitere Brailleeinstellungen

Die Focus und PAC Mate Braillezeilen ermöglichen es Ihnen, die Position der Statusmodule, wie auch die Festigkeit der Braillestifte auf ihre individuellen Bedürfnisse anzupassen.

Um diese Einstellungen anzupassen, öffnen Sie die Einstellungsverwaltung, erweitern die Braille-Gruppe und wählen die Gruppe Erweitert. Damit sich Änderungen auf alle Anwendungen auswirken, drücken Sie **STRG+UMSCHALT+D** , um die Standardeinstellungen von JAWS zu laden. Damit Änderungen für eine spezielle Anwendung wirksam werden, wählen Sie diese in der Ausklappliste Anwendungen.

## Lage der Statusmodule

Sie können festlegen, ob die Statusmodule einer Focus Braillezeile auf der linken oder rechten Seite der Braillezeile angezeigt werden, oder Sie können sie vollständig abschalten. Standardmäßig werden die Statusmodule auf der linken Seite der Braillezeile angezeigt.

## Punktstärke

Sie können die Festigkeit der Stifte der Focus oder PAC Mate Braillezeile angeben. Es gibt fünf Stufen der Festigkeit. Passen Sie die Anzeige so an, dass sie am ehesten der Sensibilität Ihrer Fingerkuppen entspricht.

Diese Funktion steht für die PAC Mate Braillezeile und alle Focus Braillezeilen Modelle vor der 5. Generation zur Verfügung. Diese Funktion funktioniert auch mit der Focus Braillezeile der 5. Generation, wenn auf dieser eine Firmware vor 5.80.55 installiert ist.

Quelle: focus_config.htm

## Focus Befehle für Webseiten

Um das Lesen für Sie zu vereinfachen, haben wir sowohl das Braillesymbol als auch die Punktekombination angegeben. Navigieren Sie einfach zu der Spaltenüberschrift der Darstellungsweise, die Sie bevorzugen, und drücken Sie **ALT+STRG+PFEIL RUNTER** , um sich durch die Befehlsliste zu bewegen. Sie hören dann lediglich die Befehlsbeschreibung und entweder das Braillesymbol oder die Punktekombination, nicht jedoch beides. Gibt es für eine Punktekombination kein Braillesymbol, wird die Punktekombination in beiden Spalten angezeigt. Verwenden Sie Computerbraille für die Zahlen in der Spalte Braillesymbole.

Tabelle: Focus Internet Explorer Befehle

| Beschreibung | Braillesymbol | Braille Punktschriftmuster |
| --- | --- | --- |
| Auf den nächsten Text ohne Links springen | RECHTE UMSCHALT+PUNKT 8 | RECHTE UMSCHALT+PUNKT 8 |
| Überschrift auswählen | RECHTE UMSCHALT+RUNTERGERUTSCHTE 6 | RECHTE UMSCHALT+PUNKTE 2-3-5 |
| Einen Link auswählen | RECHTE UMSCHALT+RUNTERGERUTSCHTE 7 | RECHTE UMSCHALT+PUNKTE 2-3-5-6 |
| Schalter der Symbolleiste auflisten | RECHTE UMSCHALT+RUNTERGERUTSCHTE 8 | RECHTE UMSCHALT+PUNKTE 2-3-6 |
| Einen Rahmen auswählen | RECHTE UMSCHALT+RUNTERGERUTSCHTE 9 | RECHTE UMSCHALT+PUNKTE 3-5 |

Quelle: focus_ie_cmd.htm

## Focus JAWS Befehle

Alle JAWS Befehle verwenden die **RECHTE UMSCHALT** Taste als Teil des Befehls.

**Hinweis:** Um das Lesen für Sie zu vereinfachen, haben wir sowohl das Braillesymbol als auch die Punktekombination angegeben. Navigieren Sie einfach zu der Spaltenüberschrift der Darstellungsweise, die Sie bevorzugen, und drücken Sie **ALT+STRG+PFEIL RUNTER** , um sich durch die Befehlsliste zu bewegen. Sie hören dann lediglich die Befehlsbeschreibung und entweder das Braillesymbol oder die Punktekombination, nicht jedoch beides. Gibt es für eine Punktekombination kein Braillesymbol, wird die Punktekombination in beiden Spalten angezeigt. Verwenden Sie Computerbraille für die Zahlen in der Spalte Braillesymbole.

## Allgemeine Befehle

Tabelle: Allgemeine JAWS Befehle

| Beschreibung | Braillesymbol | Braille Punktschriftmuster |
| --- | --- | --- |
| JAWS Programmfenster | RECHTE UMSCHALT+J | RECHTE UMSCHALT+PUNKTE 2-4-5 |
| Schnelleinstellung | RECHTE UMSCHALT+V | RECHTE UMSCHALT+PUNKTE 1-2-3-6 |
| Fensterliste öffnen | RECHTE UMSCHALT+RUNTERGERUTSCHTE 0 | RECHTE UMSCHALT+PUNKTE 3-5-6 |
| Symbole des Infobereichs auflisten | RECHTE UMSCHALT+K | RECHTE UMSCHALT+PUNKTE 1-3 |
| Bildschirm neu aufbauen | RECHTE UMSCHALT+Z | RECHTE UMSCHALT+PUNKTE 1-3-5-6 |
| Schriftart ansagen | RECHTE UMSCHALT+F | RECHTE UMSCHALT+PUNKTE 1-2-4 |
| Windows Tastenkombinationen Hilfe | RECHTE UMSCHALT+W | RECHTE UMSCHALT+PUNKTE 2-4-5-6 |
| Aktuelles Fenster lesen | RECHTE UMSCHALT+B | RECHTE UMSCHALT+PUNKTE 1-2 |
| Standard-Schalter in Dialogfeldern | RECHTE UMSCHALT+E | RECHTE UMSCHALT+PUNKTE 1-5 |
| JAWS beenden | RECHTE UMSCHALT+RUNTERGERUTSCHTE 4 | RECHTE UMSCHALT+PUNKTE 2-5-6 |
| Ein Stimmenprofil auswählen | RECHTE UMSCHALT+S | RECHTE UMSCHALT+PUNKTE 2-3-4 |
| Tabellenüberschriften umschalten | RECHTE UMSCHALT+H | RECHTE UMSCHALT+PUNKTE 1-2-5 |
| Tabellenlesen umschalten | RECHTE UMSCHALT+Q | RECHTE UMSCHALT+PUNKTE 2-3-4-6 |

## Cursor Befehle

Tabelle: Cursor Befehle

| Beschreibung | Braillesymbol | Braille Punktschriftmuster |
| --- | --- | --- |
| Ziehe JAWS zu PC | RECHTE UMSCHALT+PUNKTE 3-6 (Minus-Zeichen) | RECHTE UMSCHALT+PUNKTE 3-6 |
| Ziehe PC zu JAWS | RECHTE UMSCHALT+IE-Zeichen | RECHTE UMSCHALT+PUNKTE 3-4-6 |

## Hilfsprogramme

Tabelle: Befehle für JAWS Hilfsprogramme

| Beschreibung | Braillesymbol | Braille Punktschriftmuster |
| --- | --- | --- |
| JAWS Manager aufrufen | RECHTE UMSCHALT+RUNTERGERUTSCHTE 2 | RECHTE UMSCHALT+PUNKTE 2-3 |
| Linke obere Rahmenecke setzen | RECHTE UMSCHALT+Ö | RECHTE UMSCHALT+PUNKTE 2-4-6 |
| Rechte untere Rahmenecke setzen | RECHTE UMSCHALT+ER-Zeichen | RECHTE UMSCHALT+PUNKTE 1-2-4-5-6 |
| Grafikbezeichner | RECHTE UMSCHALT+G | RECHTE UMSCHALT+PUNKTE 1-2-4-6 |
| JAWS Suchen | RECHTE UMSCHALT+F CHORD | RECHTE UMSCHALT+PUNKTE 1-2-4 CHORD |
|  | RECHTE UMSCHALT+PUNKTE 2-5 | RECHTE UMSCHALT+PUNKTE 2-5 |

Quelle: focus_jaws_cmd.htm

## Focus Navigationsbeispiel

# Navigationsbeispiel

1. Drücken Sie **RECHTE UMSCHALT+RUNTERGERUTSCHTE 2** ( **RECHTE UMSCHALT+PUNKTE 2-3** ), um das Dialogfeld JAWS Manager starten zu öffnen.
2. Scrollen Sie mit den Scrollrädern durch die Liste, bis Sie den Tastaturmanager gefunden haben.
3. Drücken Sie **PUNKT 8** für **EINGABE** .
4. Drücken Sie **PUNKTE 4-5** , um mit **TAB** zur Liste der zugewiesenen Tasten zu gelangen.
5. Scrollen Sie mit den Scrollrädern durch die Liste, bis Sie zu der Tastenkombination gelangen, die Sie sich ansehen möchten.
6. Verwenden Sie den Befehl Braillezeile auf letzte Fensterzeile ( **PUNKTE 4-5-6 CHORD** ), um sich die Kurzbeschreibung auf der Statuszeile durchzulesen.
7. Kehren Sie mit dem Befehl Ziehe Braillezeile zu aktivem Cursor, dem Buchstaben **R** auf Ihrer Braillezeile ( **PUNKTE 1-2-3-5** ), zur ausgewählten Tastenkombination zurück.

Wenn Sie dem Beispiel gefolgt sind, haben Sie die Informationen erhalten, ohne zwischen der Tastatur und der Focus Braillezeile hin und her wechseln zu müssen.

Quelle: focus_nav_ex.htm

## Focus Übersicht

Die Focus Braillezeilen verfügen über viele hilfreiche Funktionen, mit denen Sie durch Dokumente wandern, Text markieren, den Cursor auf eine Bildschirmposition bewegen können und vieles mehr. Zusätzlich sind alle Modelle mit einer Brailletastatur ausgestattet, um Text einzugeben und Befehle auszuführen. Weitere Informationen über das Zusammenspiel Ihrer Focus Braillezeile mit JAWS finden Sie in den folgenden Hilfethemen:

[Steuerelemente für Focus 14, Focus 40 und Focus 80 Blue](Controls_for_Focus_14_40_and_80_Blue.htm) [Steuerelemente für die klassische Focus 40 Blue](Controls_for_Focus_40_Blue.htm) [Steuerelemente für Focus 40 und 80](Controls_for_Focus_40_and_80.htm) [Steuerelemente für Focus 44, 70 und 84](focus_ww_ab_crk.htm)

**Hinweis:** Einen Überblick über die Bluetooth-Konfiguration finden Sie unter [Focus Bluetooth-Verbindung](Focus_Bluetooth_Connection.htm) .

Die folgenden Informationen beschreiben, wie die Befehle für JAWS und die Focus Braillezeilen miteinander korrespondieren. Sobald Sie diese Denkweise verstanden haben, müssen Sie sich keine lange Liste von Befehlen mehr merken. Die Befehle sind unterteilt in JAWS Befehle, Windows Befehle und Braille Befehle. Für jede dieser Befehlsarten gibt es nur ein Muster. Die Befehle der Focus Zeilen basieren durchgehend auf JAWS und Windows Befehlen. Wenn Sie also schon mit den Tastaturbefehlen in JAWS und Windows vertraut sind, lernen Sie die Befehle für die Focus sehr schnell. Wenn Sie sich auf der anderen Seite mit den Focus Befehlen vertraut gemacht haben, bereiten Ihnen die JAWS und Windows Tastaturbefehle keine Probleme mehr.

## JAWS Befehle

Wenn Sie bereits mit JAWS vertraut sind, sind diese Befehle einfach zu erlernen. Und wenn Sie gerade beginnen, sich mit Ihrer Focus Braillezeile und JAWS vertraut zu machen, unterstützen diese Befehle Sie auch beim Erlernen der JAWS Tastaturbefehle.

Die **RECHTE UMSCHALT** Taste auf Ihrer Focus Braillezeile entspricht der **EINFÜGEN** Taste auf Ihrer Tastatur. Der JAWS Befehl zum Aktivieren des JAWS-Fensters ist **JAWS TASTE+J** . Der entsprechende Focus Befehl lautet also **RECHTE UMSCHALT+J** ( **RECHTE UMSCHALT+PUNKTE 2-4-5** ).

Viele JAWS Befehle verwenden **EINFÜGEN** zusammen mit den Funktionstasten **F1** bis **F12** . Für Befehle, die **JAWS TASTE+F1** bis **F9** verwenden, drücken Sie einfach die **RECHTE UMSCHALT** und tippen die runtergerutschte Ziffer, die der Funktionstaste entspricht. So ist zum Beispiel der JAWS-Befehl für den Aufruf der JAWS Hilfsprogramme **JAWS TASTE+F2** . Der Focus Befehl lautet also **RECHTE UMSCHALT+2** ( **RECHTE UMSCHALT+PUNKTE 2-3** ).

Lesen Sie bitte hierzu [JAWS Befehle für die Focus Serie](focus_jaws_cmd.htm) .

## Windows Befehle

Die Windows Befehle folgen einer ähnlichen Konvention. Viele Windows Befehle verwenden **STRG** , **ALT** oder **UMSCHALT** als Teil des Befehls. Auf der Focus-Braillezeile wird die **LINKE UMSCHALT** -Taste für diese Befehle verwendet. Der Windows Befehl, um markierten Text in die Zwischenablage zu kopieren, lautet **STRG+C** . Der Focus Befehl lautet also **LINKE UMSCHALT+C** ( **LINKE UMSCHALT+PUNKTE 1-4** ).

Um den Umgang mit den Focus Braillezeilen oder das Erlernen von Windows so einfach wie möglich zu gestalten, werden für die Focus Befehle die gleichen Buchstaben verwendet wie für die Windows Befehle.

Lesen Sie hierzu bitte [Focus Windows-Befehle](focus_win_cmd.htm) .

## Braille Befehle

Vorrangig ändern diese Befehle Einstellungen Ihrer Braillezeile. Diese Tastenkombinationen entstehen aus der Kombination mit der **LEERTASTE** . Sie werden auch als Chord-Befehle bezeichnet. Verwenden Sie die **LEERTASTE** wie andere Umschalter-Tasten ( **UMSCHALT** , **STRG** , **ALT** , usw.). Drücken Sie zuerst die **LEERTASTE** , halten Sie diese gedrückt, und drücken Sie dann die andere Taste oder Tasten, die Bestandteile des Befehls sind. All diese Befehle verändern die Einstellungen, wie Informationen auf Ihrer Braillezeile formatiert, übersetzt oder präsentiert werden.

Lesen Sie bitte hierzu [Focus Braille Befehle](focus_brl_cmd.htm) .

## Ausnahmen

Die Beziehung zwischen den Funktionstasten und den heruntergerutschten Ziffern schließt nicht den Befehl zum Auflisten der Symbole des Infobereichs, **JAWS TASTE+F11** auf der Tastatur, ein. Wir haben diesem Befehl die Tastenkombination **RECHTE UMSCHALT+K** ( **RECHTE UMSCHALT+PUNKTE 1-3** ) zugewiesen.

Der Befehl zum Öffnen der Fensterliste, **JAWS TASTE+F10** , ist **RECHTE UMSCHALT+RUNTERGERUTSCHTE 0** ( **RECHTE UMSCHALT+PUNKTE 3-5-6** ).

Durch Beschränkungen bei der Verfügbarkeit von Tasten gibt es weitere Ausnahmen. Wir haben uns jedoch bemüht, die Konsistenz mit den JAWS oder Windows Befehlen weitestgehend einzuhalten.

## Ein Beispiel

Nachdem Sie sich die Focus Befehle angesehen haben, wählen Sie den nachfolgenden Link [Focus Navigationsbeispiel](focus_nav_ex.htm) , um zu verstehen, wie effizient man mit der Focus Braillezeile navigieren kann.

Quelle: focus_overview.htm

## Focus Befehle für Microsoft PowerPoint

# Focus Befehle für Microsoft Powerpoint

Um das Lesen für Sie zu vereinfachen, haben wir sowohl das Braillesymbol als auch die Punktekombination angegeben. Navigieren Sie einfach zu der Spaltenüberschrift der Darstellungsweise, die Sie bevorzugen, und drücken Sie **ALT+STRG+PFEIL RUNTER** , um sich durch die Befehlsliste zu bewegen. Sie hören dann lediglich die Befehlsbeschreibung und entweder das Braillesymbol oder die Punktekombination, nicht jedoch beides. Gibt es für eine Punktekombination kein Braillesymbol, wird die Punktekombination in beiden Spalten angezeigt. Verwenden Sie Computerbraille für die Zahlen in der Spalte Braillesymbole.

Tabelle: Fokus Powerpoint Befehle

| Beschreibung | Braillesymbol | Braille Punktschriftmuster |
| --- | --- | --- |
| Text Fett | LINKE UMSCHALT+F | LINKE UMSCHALT+PUNKTE 1-2 |
| EINGABE | PUNKT 8 | PUNKT 8 |
| Nächstes Objekt | PUNKTE 4-5 | PUNKTE 4-5 |
| Vorheriges Objekt | B | PUNKTE 1-2 |
| Nächste Folie der Präsentation | LEERTASTE | LEERTASTE |
| Vorherige Folie der Bildschirmpräsentation | PUNKT 7 | PUNKT 7 |
| Hyperlink wählen | RECHTE UMSCHALT+RUNTERGERUTSCHTE 7 | RECHTE UMSCHALT+PUNKTE 2-3-5-6 |
| Gewählten Hyperlink aktivieren | LINKE UMSCHALT+PUNKT 8 | LINKE UMSCHALT+PUNKT 8 |
|  | LINKE UMSCHALT+PUNKT 1 CHORD | LINKE UMSCHALT+PUNKT 1 CHORD |

Quelle: focus_ppt_cmd.htm

## Focus Befehle für Microsoft Word

Um das Lesen für Sie zu vereinfachen, haben wir sowohl das Braillesymbol als auch die Punktekombination angegeben. Navigieren Sie einfach zu der Spaltenüberschrift der Darstellungsweise, die Sie bevorzugen, und drücken Sie **ALT+STRG+PFEIL RUNTER** , um sich durch die Befehlsliste zu bewegen. Sie hören dann lediglich die Befehlsbeschreibung und entweder das Braillesymbol oder die Punktekombination, nicht jedoch beides. Gibt es für eine Punktekombination kein Braillesymbol, wird die Punktekombination in beiden Spalten angezeigt. Verwenden Sie Computerbraille für die Zahlen in der Spalte Braillesymbole.

Tabelle: Focus Word Befehle

| Beschreibung | Braillesymbol | Braille Punktschriftmuster |
| --- | --- | --- |
| Text Fett | LINKE UMSCHALT+F | LINKE UMSCHALT+PUNKTE 1-2 |
| Text Kursiv | LINKE UMSCHALT+K | LINKE UMSCHALT+PUNKTE 2-4 |
| Text Unterstreichen | LINKE UMSCHALT+U | LINKE UMSCHALT+PUNKTE 1-3-6 |
| Text Zentrieren | LINKE UMSCHALT+E | LINKE UMSCHALT+PUNKTE 1-5 |
| Linksbündig | LINKE UMSCHALT+L | LINKE UMSCHALT+PUNKTE 1-2-3 |
| Rechtsbündig | LINKE UMSCHALT+R | LINKE UMSCHALT+PUNKTE 1-2-3-5 |
| Blocksatz | LINKE UMSCHALT+B | LINKE UMSCHALT+PUNKTE 2-4-5 |
| Einrücken | LINKE UMSCHALT+M | LINKE UMSCHALT+PUNKTE 1-3-4 |
| Hängender Einzug | LINKE UMSCHALT+M CHORD | LINKE UMSCHALT+PUNKTE 1-3-4 CHORD |
| Rechtschreibfehler auflisten | LINKE UMSCHALT+E CHORD | LINKE UMSCHALT+PUNKTE 1-2-3 CHORD |
| Grammatikfehler auflisten | LINKE UMSCHALT+G | LINKE UMSCHALT+PUNKTE 1-2-4-5 |
| Links im Dokument auflisten oder Fehler und Vorschlag in Rechtschreibprüfung lesen | RECHTE UMSCHALT+RUNTERGERUTSCHTE 7 | RECHTE UMSCHALT+PUNKTE 2-3-5-6 |
| Kommentare auflisten | LINKE UMSCHALT+PUNKT 3 CHORD | LINKE UMSCHALT+PUNKT 3 CHORD |
| Eingebettete Objekte auflisten | LINKE UMSCHALT+O | LINKE UMSCHALT+PUNKTE 1-3-5 |
| Tabelle auswählen | RECHTE UMSCHALT+T CHORD | RECHTE UMSCHALT+PUNKTE 2-3-4-5 CHORD |
| Formularfelder auflisten | RECHTE UMSCHALT+L CHORD | RECHTE UMSCHALT+PUNKTE 1-2-3 CHORD |
| Nächste Seite | LINKE UMSCHALT+PUNKTE 4-6 CHORD | LINKE UMSCHALT+PUNKTE 4-6 CHORD |
| Vorherige Seite | LINKE UMSCHALT+K CHORD | LINKE UMSCHALT+PUNKTE 1-3 CHORD |
| Ausschnitt wechseln | LINKE UMSCHALT+RUNTERGERUTSCHTE 6 | LINKE UMSCHALT+PUNKTE 2-3-5 |
| Einfüge-/Überschreibmodus umschalten | LINKE UMSCHALT+I CHORD | LINKE UMSCHALT+PUNKTE 2-4 CHORD |

Quelle: focus_wd_cmd.htm

## Focus Windows Befehle

# Windows Befehle

Alle Windows Befehle verwenden die **LINKE UMSCHALT** Taste als Teil des Befehls.

**Hinweis:** Um das Lesen für Sie zu vereinfachen, haben wir sowohl das Braillesymbol als auch die Punktekombination angegeben. Navigieren Sie einfach zu der Spaltenüberschrift der Darstellungsweise, die Sie bevorzugen, und drücken Sie **ALT+STRG+PFEIL RUNTER** , um sich durch die Befehlsliste zu bewegen. Sie hören dann lediglich die Befehlsbeschreibung und entweder das Braillesymbol oder die Punktekombination, nicht jedoch beides. Gibt es für eine Punktekombination kein Braillesymbol, wird die Punktekombination in beiden Spalten angezeigt.

## Navigations- und Bearbeitungsbefehle

Tabelle: Navigations- und Bearbeitungsbefehle

| Beschreibung | Braillesymbol | Braille Punktschriftmuster |
| --- | --- | --- |
| ALT+TAB | LINKE UMSCHALT+PUNKTE 4-5 | LINKE UMSCHALT+PUNKTE 4-5 |
| Aus Zwischenablage einfügen | LINKE UMSCHALT+V | LINKE UMSCHALT+PUNKTE 1-2-3-6 |
| In Zwischenablage kopieren | LINKE UMSCHALT+C | LINKE UMSCHALT+PUNKTE 1-4 |
| In Zwischenablage ausschneiden | LINKE UMSCHALT+X | LINKE UMSCHALT+PUNKTE 1-3-4-6 |
| Rückgängig | LINKE UMSCHALT+Z | LINKE UMSCHALT+PUNKTE 1-3-5-6 |
| Entfernen | LINKE UMSCHALT+D | LINKE UMSCHALT+PUNKTE 1-4-5 |

## Befehle zum Markieren

Tabelle: Befehle zum Markieren

| Beschreibung | Braillesymbol | Braille Punktschriftmuster |
| --- | --- | --- |
| Nächstes Zeichen markieren | LINKE UMSCHALT+PUNKT 6 | LINKE UMSCHALT+PUNKT 6 |
| Vorheriges Zeichen markieren | LINKE UMSCHALT+PUNKT 3 | LINKE UMSCHALT+PUNKT 3 |
| Nächste Zeile markieren | LINKE UMSCHALT+PUNKT 4 | LINKE UMSCHALT+PUNKT 4 |
| Vorherige Zeile markieren | LINKE UMSCHALT+PUNKT 1 | LINKE UMSCHALT+PUNKT 1 |
| Vom Cursor bis Zeilenende markieren | LINKE UMSCHALT+PUNKT 5 | LINKE UMSCHALT+PUNKT 5 |
| Vom Zeilenanfang markieren | LINKE UMSCHALT+PUNKT 2 | LINKE UMSCHALT+PUNKT 2 |
| Vom Dateianfang zum Fokus markieren | LINKE UMSCHALT+L | LINKE UMSCHALT+PUNKTE 1-2-3 |
| Vom Fokus bis Dateiende markieren | LINKE UMSCHALT+PUNKTE 4-5-6 | LINKE UMSCHALT+PUNKTE 4-5-6 |
| Nächste Bildschirmseite markieren | LINKE UMSCHALT+PUNKTE 4-6 | LINKE UMSCHALT+PUNKTE 4-6 |
| Vorherige Bildschirmseite markieren | LINKE UMSCHALT+K | LINKE UMSCHALT+PUNKTE 1-3 |
| Alles markieren | LINKE UMSCHALT+VOLLZEICHEN | LINKE UMSCHALT+PUNKTE 1-2-3-4-5-6 |
| Einen Rahmen auswählen | RECHTE UMSCHALT+RUNTERGERUTSCHTE 9 | RECHTE UMSCHALT+PUNKTE 3-5 |
| Überschrift auswählen | RECHTE UMSCHALT+RUNTERGERUTSCHTE 6 | RECHTE UMSCHALT+PUNKTE 2-3-5 |
| Einen Link auswählen | RECHTE UMSCHALT+RUNTERGERUTSCHTE 7 | RECHTE UMSCHALT+PUNKTE 2-3-5-6 |

### Mit den Cursorroutingtasten markieren

Um Text mit Hilfe der Cursorroutingtasten zu markieren, drücken Sie die **LINKE UMSCHALT** , halten diese gedrückt und drücken die Routingtaste über dem Text, bei dem Sie die Markierung beginnen möchten. Lassen Sie beide Tasten los. Gehen Sie zu dem Punkt, an dem Sie die Markierung beenden möchten, und drücken Sie **LINKE UMSCHALT** plus die Cursorroutingtaste an dieser Stelle. Sie können alle Navigationsbefehle verwenden, um vom Startpunkt der Markierung zum Endpunkt zu gelangen, sogar mit den Scrollrädern. Wenn jedoch das Fenster, das den Text enthält, zu scrollen beginnt, hat dies Auswirkungen darauf, was tatsächlich markiert wird.

Quelle: focus_win_cmd.htm

## Die Elemente der Focus 44, 70 und 84

Die Focus Braillezeilen besitzen zwei Scrollräder, zwei Lesetasten, und Cursorroutingtasten oberhalb jedes Braillemoduls. Zwischen den Lesetasten befinden sich weiterhin zwei Funktionstasten.

## Scrollräder

Mit den Scrollrädern der Focus Zeilen können Sie schnell durch Dateien, Listen und Menüs navigieren. Die Scrollräder garantieren Funktionalität, die Sie dort benötigen, wo Sie gerade sind. Bewegen Sie sich in einer Datei zeilen-, satz- oder absatzweise. Sie springen in einem Dialogfenster auf die vorhandenen Steuerelemente und interagieren Sie mit ihnen. Bewegen Sie sich in einem Menü rauf und runter durch die Einträge.

### Die Scrollräder in Dateien

In Textdateien und Textverarbeitungsdokumenten bewegt man sich mit den Scrollrädern zeilen-, satz- oder absatzweise. Die zwei Scrollräder, von denen sich jeweils eines am linken und rechten Ende des Notizgerätes befindet, können unabhängig voneinander eingestellt werden. Drücken Sie ein Scrollrad nach unten, um es auf zeilen-, satz- oder absatzweises Scrollen einzustellen. Drehen Sie das Scrollrad in Ihre Richtung, um sich abwärts durch eine Datei zu bewegen. Drehen Sie das Scrollrad in die entgegengesetzte Richtung, um sich aufwärts durch eine Datei zu bewegen.

### Die Scrollräder in Menüs

Drehen Sie ein Scrollrad in Ihre Richtung, um abwärts durch ein Menü zu wandern und drehen Sie es von sich weg, um aufwärts zu wandern. Drücken Sie ein Scrollrad nach unten, um einen Menüeintrag auszuwählen.

### Die Scrollräder in Dialogen

In Dialogen drehen Sie ein Scrollrad zu sich hin, um vorwärts auf die Steuerelemente zu springen, und Sie drehen das Scrollrad von sich weg, um in umgekehrter Reihenfolge auf die Steuerelemente zu springen. Wenn Sie ein Scrollrad nach unten drücken, so hat das je nach Steuerelement unterschiedliche Aktionen zur Folge.

Wenn Sie ein Scrollrad nach unten drücken, während Sie sich auf einem Steuerelement befinden, das Elemente auflistet, wie zum Beispiel Listenansichten, Auswahllisten, Auswahlschalter und Strukturansichten, dann aktiviert das Scrollrad den Listen-Modus. In diesem Modus verwenden Sie das Scrollrad, um sich durch die Listenelemente zu bewegen. Drücken Sie erneut auf ein Scrollrad, um den Listenmodus zu verlassen.

Wenn Sie ein Scrollrad nach unten drücken, während Sie sich auf einem Kontrollfeld oder Schalter befinden, so wird der Status des Kontrollfeldes umgeschaltet oder der Schalter wird aktiviert. Wenn sich mehrere Kontrollfelder in einem Gruppenfeld befinden, so wird in den Listenmodus gewechselt, sobald Sie ein Scrollrad nach unten drücken.

Die Scrollräder bieten diese Funktionalität in vielen Bereichen an, zum Beispiel im Windows Explorer, in Outlook, auf Word Symbolleisten und sogar auf dem Windows Desktop.

### Focus Weiterbewegen

Das Focus Weiterbewegen bedeutet, dass Sie mit den Scrollrädern durch Ihre Dokumente wandern, wobei Sie den PC Cursor mit dem Braillecursor verschieben. Diese Funktion ist besonders beim Lesen von langen Dokumenten, zum Beispiel Büchern, sehr hilfreich. Beim Lesen und Weiterbewegen rollt der Bildschirm weiter, so dass Sie ohne Unterbrechung weiterlesen können.

Um das Weiterbewegen zu aktivieren, drücken Sie die Scrollräder so lange nach unten, bis Sie "Focus Weiterbewegen" hören. Danach bewegen Sie die Räder, um im Dokument zu navigieren. Wenn Sie die Räder zu sich hin drehen, wird die Seite nach unten bewegt, drehen Sie die Räder von sich weg, wird die Seite nach oben bewegt.

## Lesetasten

Mit den Lesetasten der Focus Braillezeile können Sie sich durch eine Datei, ein Menü oder eine Liste bewegen, während Sie sich im Flächenmodus befinden. Drücken Sie die **LINKE LESETASTE** , um auf einer Zeile nach links zu springen oder um rückwärts durch ein Dokument zu wandern. Drücken Sie die **RECHTE LESETASTE** , um auf einer Zeile nach rechts zu springen oder um vorwärts durch ein Dokument zu wandern. Drücken Sie beide Lesetasten gleichzeitig, um die zuletzt angezeigte Braille Blitzmeldung zu wiederholen.

## Funktionstasten

Die beiden Funktionstasten befinden sich zwischen den Braillemodulen und der Rückseite jedes Geräts. Drücken Sie **RECHTE FUNKTIONSTASTE+LINKE FUNKTIONSTASTE** , um den Modus Automatisches Weiterbewegen zu starten. Um die Lesegeschwindigkeit während des Automatischen Weiterbewegens zu erhöhen, drücken Sie die **RECHTE FUNKTIONSTASTE** . Um die Lesegeschwindigkeit zu verringern, drücken Sie die **LINKE FUNKTIONSTASTE** .

## Brailletastatur

Zwischen den Braillemodulen und dem vorderen Ende der Zeile befinden sich acht Tasten, die einer Perkins Brailletastatur ähneln. Diese Tasten sind für die Eingabe von Befehlen vorgesehen. Am vorderen Ende der Zeile finden Sie drei Tasten **LINKE UMSCHALT** , **LEERTASTE** und **RECHTE UMSCHALT** . Diese drei Tasten werden zusammen mit den Brailletasten zur Eingabe von Befehlen verwendet.

## Cursorroutingtasten

Über jedem Braillemodul der Focus Braillezeile befindet sich eine Cursorroutingtaste. Drücken Sie eine Cursorroutingtaste, um den Cursor an diesen Punkt zu ziehen, oder um einen Link auf einer Webseite oder in einer E-Mail zu aktivieren. Im Flächenmodus können Sie durch Druck auf eine Cursorroutingtaste ein Menü öffnen oder Menüeinträge auswählen.

Drücken Sie die **RECHTE FUNKTIONSTASTE** zusammen mit einer Cursorroutingtaste, um einen rechten Mausklick an diesem Punkt zu simulieren.

## Mehrfach-Funktionen

Die folgende Liste enthält Befehle, die auf der Focus 40/80 ausführen können.

| Funktion | Steuerungen |
| --- | --- |
| Automatisches Weiterbewegen aktivieren | LINKE FUNKTIONSTASTE+RECHTE FUNKTIONSTASTE |
| Geschwindigkeit beim Automatischen Weiterbewegen verringern | LINKE FUNKTIONSTASTE |
| Geschwindigkeit beim Automatischen Weiterbewegen erhöhen | RECHTE FUNKTIONSTASTE |
| Linker Mausklick | CURSORROUTINGTASTE |
| STRG+Linker Mausklick | CURSORROUTINGTASTE+CHORD |
| Rechter Mausklick | RECHTE FUNKTIONSTASTE+CURSORROUTINGTASTE |
| Scrollräder ein-/ausschalten | LINKES oder RECHTES SCROLLRAD+CHORD |
| Nach links bewegen | LINKE LESETASTE |
| Nach rechts bewegen | RECHTE LESETASTE |
| Letzte Blitzmeldung wiederholen | LINKE LESETASTE+RECHTE LESETASTE |

Quelle: focus_ww_ab_crk.htm

## Focus Befehle für Microsoft Excel

Um das Lesen für Sie zu vereinfachen, haben wir sowohl das Braillesymbol als auch die Punktekombination angegeben. Navigieren Sie einfach zu der Spaltenüberschrift der Darstellungsweise, die Sie bevorzugen, und drücken Sie **ALT+STRG+PFEIL RUNTER** , um sich durch die Befehlsliste zu bewegen. Sie hören dann lediglich die Befehlsbeschreibung und entweder das Braillesymbol oder die Punktekombination, nicht jedoch beides. Gibt es für eine Punktekombination kein Braillesymbol, wird die Punktekombination in beiden Spalten angezeigt. Verwenden Sie Computerbraille für die Zahlen in der Spalte Braillesymbole.

Tabelle: Focus Excel Befehle

| Beschreibung | Braillesymbol | Braille Punktschriftmuster |
| --- | --- | --- |
| Text Fett | LINKE UMSCHALT+F | LINKE UMSCHALT+PUNKTE 1-2 |
| Text Kursiv | LINKE UMSCHALT+K | LINKE UMSCHALT+PUNKTE 2-4 |
| Text Unterstreichen | LINKE UMSCHALT+U | LINKE UMSCHALT+PUNKTE 1-3-6 |
| Gehe zu erster Zelle | L CHORD | PUNKTE 1-2-3 CHORD |
| Gehe zu letzter Zelle | PUNKTE 4-5-6 CHORD | PUNKTE 4-5-6 CHORD |
| Zellen der aktuellen Spalte auflisten | RECHTE UMSCHALT+C CHORD | RECHTE UMSCHALT+PUNKTE 1-4 CHORD |
| Zellen der aktuellen Reihe auflisten | RECHTE UMSCHALT+R CHORD | RECHTE UMSCHALT+PUNKTE 1-2-3-5 CHORD |
| Spalte markieren | LINKE UMSCHALT CHORD | LINKE UMSCHALT CHORD |
| Reihe markieren | RECHTE UMSCHALT CHORD | RECHTE UMSCHALT CHORD |
| Zellen bei Seitenwechseln auflisten | RECHTE UMSCHALT+B CHORD | RECHTE UMSCHALT+PUNKTE 1-2 CHORD |
| Kommentierte Zellen auflisten | RECHTE UMSCHALT+PUNKT 3 CHORD | RECHTE UMSCHALT+PUNKT 3 CHORD |
| Sichtbare Zellen mit Daten auflisten | RECHTE UMSCHALT+D CHORD | RECHTE UMSCHALT+PUNKTE 1-4-5 CHORD |
| Nächstes Arbeitsblatt | LINKE UMSCHALT+PUNKTE 4-6 CHORD | LINKE UMSCHALT+PUNKTE 4-6 CHORD |
| Vorheriges Arbeitsblatt | LINKE UMSCHALT+K CHORD | LINKE UMSCHALT+PUNKTE 1-3 CHORD |
| Gehe zu Arbeitsblatt | RECHTE UMSCHALT+S | RECHTE UMSCHALT+PUNKTE 2-3-4 |
| In die Überwachungszelle springen | RECHTE UMSCHALT+M CHORD | RECHTE UMSCHALT+PUNKTE 1-3-4 CHORD |
| Formelmodus | VOLLZEICHEN | PUNKTE 1-2-3-4-5-6 |
| Auto Summe | LINKE UMSCHALT+VOLLZEICHEN CHORD | LINKE UMSCHALT+PUNKTE 1-2-3-4-5-6 CHORD |
| Status der Gitternetzlinien ansagen | RECHTE UMSCHALT+G CHORD | RECHTE UMSCHALT+PUNKTE 1-2-4-5 CHORD |
| Region auswählen | RECHTE UMSCHALT+RUNTERGERUTSCHTE 8 | RECHTE UMSCHALT+PUNKTE 2-3-6 |
| Objekte des Arbeitsblattes auswählen | RECHTE UMSCHALT+O | RECHTE UMSCHALT+PUNKTE 1-3-5 |
| Aktuelle Uhrzeit | LINKE UMSCHALT+PUNKTE 5-6 | LINKE UMSCHALT+PUNKTE 5-6 |
| Falsch geschriebenes Wort und Vorschläge lesen | RECHTE UMSCHALT+RUNTERGERUTSCHTE 7 | RECHTE UMSCHALT+PUNKTE 2-3-5-6 |

Quelle: focus_xl_cmd.htm

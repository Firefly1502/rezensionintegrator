# Datenschutzerklärung – Textbausteine für das Google-Rezensionen-Widget

**Stand:** 2026-04-21
**Zweck:** Zwei Textblöcke zum Einfügen in die Datenschutzerklärung auf www.fullflightsim.de/datenschutz, bevor das Widget live geht.

Beide Blöcke beschreiben Verarbeitungen, die durch das selbst gehostete Rezensions-Widget entstehen. Die bereits vorhandene Datenschutzerklärung wird damit ergänzt, nicht ersetzt.

---

## Block A – Darstellung von Google-Rezensionen

**Überschrift-Vorschlag:** *Darstellung von Google-Rezensionen auf unserer Website*

Auf unserer Website binden wir öffentlich zugängliche Kundenrezensionen ein, die Nutzerinnen und Nutzer bei Google zu unserem Unternehmen (Google Business Profile „Full Flight Sim", Griesheim bei Darmstadt) hinterlassen haben. Anbieter dieser Rezensionen ist die Google Ireland Limited, Gordon House, Barrow Street, Dublin 4, Irland.

Die Rezensionen werden nicht live aus einem Google-Dienst in Ihren Browser nachgeladen, sondern einmal täglich über die offizielle Google-Schnittstelle („Places API" bzw. „Business Profile API") von uns abgerufen und anschließend in einer eigenen Datei auf unserem Hosting zwischengespeichert. Beim Aufruf unserer Website werden die Rezensionen aus dieser Datei ausgeliefert. Dadurch findet **beim Besuch unserer Website keine direkte Verbindung Ihres Browsers zu Google-Servern statt**, soweit das Widget betroffen ist.

Angezeigt werden – soweit von der jeweiligen Nutzerin bzw. dem jeweiligen Nutzer bei Google selbst öffentlich gemacht – Vorname bzw. Anzeigename, Profilbild, Sternebewertung, Bewertungstext und Bewertungsdatum. Diese Daten sind bei Google ohnehin öffentlich einsehbar.

**Rechtsgrundlage** ist Art. 6 Abs. 1 lit. f DSGVO. Unser berechtigtes Interesse besteht in einer transparenten, übersichtlichen Darstellung von Kundenfeedback zu unserem Flugsimulator-Angebot sowie in der technisch schlanken und datenschutzfreundlichen Einbindung dieser Rezensionen.

Ein „Bewertung schreiben"-Button in unserem Rezensions-Widget führt Sie auf eine Google-Seite. Erst ab dem Klick auf diesen Button bauen Sie eine direkte Verbindung zu Google auf; ab diesem Zeitpunkt gilt die Datenschutzerklärung von Google: <https://policies.google.com/privacy>.

---

## Block B – Hosting der Widget-Dateien über GitHub Pages

**Überschrift-Vorschlag:** *Auslieferung von Widget-Dateien über GitHub Pages*

Die technischen Bestandteile unseres Rezensions-Widgets (Layout-Datei, Skriptdatei, gespeicherte Rezensions-Daten, zwischengespeicherte Profilbilder der Rezensentinnen und Rezensenten) werden über den Dienst „GitHub Pages" der GitHub, Inc., 88 Colin P Kelly Jr St, San Francisco, CA 94107, USA, ausgeliefert. GitHub, Inc. ist eine Tochtergesellschaft der Microsoft Corporation.

Beim Aufruf unserer Website lädt Ihr Browser diese Dateien direkt von einem GitHub-Server. Dabei wird technisch zwingend Ihre IP-Adresse an GitHub übertragen. Weitere Daten, die Ihr Browser üblicherweise bei einem Seitenaufruf übermittelt (z. B. User-Agent, Zeitpunkt des Abrufs, angefragte Ressource), können dabei ebenfalls verarbeitet und kurzfristig in Server-Logfiles gespeichert werden. Eine Auswertung durch uns findet nicht statt; wir erhalten von GitHub keine personenbezogenen Daten zu einzelnen Besucherinnen und Besuchern.

Eine Übertragung in ein Drittland (USA) kann nicht ausgeschlossen werden. Die GitHub, Inc. ist unter dem „EU-U.S. Data Privacy Framework" zertifiziert; ein Angemessenheitsbeschluss der Europäischen Kommission liegt vor (Durchführungsbeschluss (EU) 2023/1795 vom 10. Juli 2023).

**Rechtsgrundlage** ist Art. 6 Abs. 1 lit. f DSGVO. Unser berechtigtes Interesse besteht in einer kostengünstigen, zuverlässigen und wartungsarmen Bereitstellung der Widget-Dateien. Ein eigener Webserver müsste andernfalls zusätzlich zum bestehenden Website-Baukasten betrieben werden.

Weitere Informationen zum Datenschutz bei GitHub Pages finden Sie unter: <https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement>.

---

## Hinweise an Michael (nicht mitkopieren)

1. **Einfügeort in Duda:** Datenschutz-Seite öffnen → die beiden Blöcke als eigene Abschnitte unterhalb bestehender Abschnitte einfügen (z. B. nach „Google Maps", falls vorhanden, sonst am Ende vor dem Abschnitt „Rechte der betroffenen Personen").
2. **Vorab-Check:** Vor dem Go-Live kurz mit einem Juristen oder dem bisherigen Datenschutz-Dienstleister (sofern vorhanden) gegenlesen lassen – die Texte sind sorgfältig formuliert, aber keine Rechtsberatung.
3. **Trigger:** Diese Texte sollten **erst live** sein, wenn auch das Widget auf der Website sichtbar eingebunden ist. Vorher beschreiben sie eine Verarbeitung, die noch nicht stattfindet.
4. **Avatar-Caching** ist bewusst nicht als eigener Abschnitt aufgeführt – es ist bereits in Block A mit abgedeckt („… in einer eigenen Datei auf unserem Hosting zwischengespeichert", „keine direkte Verbindung Ihres Browsers zu Google-Servern").
5. **Wenn später Analytics/Tracking dazukommt** (z. B. Klicks auf „Bewertung schreiben"), braucht es einen zusätzlichen Abschnitt – nicht Teil dieses Entwurfs.

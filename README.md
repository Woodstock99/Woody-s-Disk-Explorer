# Woody's Disk Explorer

Woody's Disk Explorer stellt die physischen Sektoren einer Festplatte 
(HDD/SSD/USB) dar. Die Sektoren können analysiert, überprüft und bei 
Bedarf auch editiert werden. Backup-Funktionen ermöglichen die 
Wiederherstellung von Partitionstabellen, Bootrecords oder auch 
ganzen Sektorblöcken.

Pro Seite werden 128 Sektoren angezeigt, die man entweder mit der 
Maus scrollen oder sektorweise mit den Pfeiltasten <↑↓> durchsuchen 
kann. Die obere Button-Leiste ermöglicht ein schnelles Vor- und 
Zurückblättern.

Das Programm wird immer im Schreibschutz-Modus (read only) gestartet, 
da unsachgemäßes Schreiben in Sektoren evtl. bis zum Totalverlust aller Daten 
führen kann.

Da das Programm direkten Zugriff auf physikalische Sektoren hat, muss es mit 
Root-Rechten gestartet werden.


![alt text](https://github.com/Woodstock99/Woody-s-Disk-Explorer/blob/main/screenshot.png)


### Anforderungen:

- python3
- python3-tk

### Getestet mit:

- Arch Linux 
- Linux Mint

### Lizenz:

- GNU GPL3

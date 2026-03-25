#! /usr/bin/env python3
#
#   Woody's Disk Explorer v1.05
#
##############################################################################################################

import tkinter as tk
import tkinter.filedialog as fdialog
import tkinter.messagebox as message
import os
import datetime

##############################################################################################################

Device = "/dev/sda"
SektNum = 0
SektData = bytearray()
Sekt2Data = bytearray()

Schrift = "Consolas 11"
Vordergrund = "#ffffff"
Hintergrund = "#000066"
EINFUEGEN = True

##############################################################################################################

Master = tk.Tk()
Master.title("Woody's Disk Explorer")
Master.option_add("*Dialog.msg.font", "Helvetica 11")
Master.option_add("*Dialog.msg.wrapLength", "50i")

StatusText = tk.StringVar()
ReadOnly = tk.IntVar() 
ReadOnly.set(1)

##############################################################################################################

def Lese_Sektor(laufwerk, Sektor):

    global SektData
    
    try:
        with open(laufwerk, "rb") as fp:
            fp.seek(Sektor*512)
            SektData = fp.read(512)
            return True
    except:
        return False

##############################################################################################################

def Schreibe_Sektor(laufwerk, Sektor):

    global SektData
    
    try:
        with open(laufwerk, "wb") as fp:
            fp.seek(Sektor*512)
            fp.write(SektData)
            return True
    except:
        return False

##############################################################################################################

def Sektor_Bin2Text(sektnum):

    text = ""

    # 16 Zeilen ausgeben
    for z in range(16):  
        text += "{:012X}".format(sektnum*512+z*32) + "  "

        # 32 Byte in Hex
        for s in range(32):
            if s % 8 == 0:
                text += " "
            text += "{:02X}".format(SektData[z*32+s]) + " "
        text += "  "
        # 32 Byte in Ascii
        for s in range(32):
            if SektData[z*32+s] > 31 and SektData[z*32+s] < 127:
                text += "{:c}".format(SektData[z*32+s])
            else:
                text += "." 
        text += "\n"

    return text

##############################################################################################################

def Zeige_Sektorenblock():

    Haupt_Fenster.configure(state="normal")
    Haupt_Fenster.delete("1.0", "end")
    Haupt_Fenster.insert("end", "   Sektor:   {:<47s}".format(str(SektNum)) + Device + "\n")

    # 128 Sektoren lesen und anzeigen
    for i in range(128):
        if Lese_Sektor(Device, SektNum+i):
            if len(SektData) == 512:
                Haupt_Fenster.insert("end", Sektor_Bin2Text(SektNum+i))
                if i < 127:
                    Haupt_Fenster.insert("end", "   Sektor:   {:<47s}\n".format(str(SektNum+i+1)))

    Haupt_Fenster.configure(state="disabled")
    Haupt_Fenster.focus_set()                     # Focus auf Hauptfenster
    Statusleiste_Anzeigen("")

##############################################################################################################

def Sektoren_Erster():

    global SektNum

    SektNum = 0
    Zeige_Sektorenblock()

##############################################################################################################

def Sektoren_Weiter(nr):

    global SektNum

    if (SektNum + nr) >= 0:    SektNum += nr
    else:                      SektNum = 0
    Zeige_Sektorenblock()
    return "break"                                # eingebaute <Pfeiltaste> ignorieren

##############################################################################################################

def Sektor_Vor():        # <Pfeiltaste runter>

    global SektNum

    if Lese_Sektor(Device, SektNum+128):
        if SektData:     # sonst Fehler bei letztem Sektor + 1
            SektNum += 1
            Haupt_Fenster.configure(state="normal")
            Haupt_Fenster.delete("1.0", "19.0")
            Haupt_Fenster.insert("1.0", "   Sektor:   {:<47s}".format(str(SektNum)) + Device + "\n")
            Haupt_Fenster.insert("end", "   Sektor:   {:<47s}\n".format(str(SektNum+127)))
            Haupt_Fenster.insert("end", Sektor_Bin2Text(SektNum))
            Haupt_Fenster.configure(state="disabled")
            Statusleiste_Anzeigen("")

    return "break"       # eingebaute <Pfeiltaste> ignorieren

##############################################################################################################

def Sektor_Zurueck():    # <Pfeiltaste hoch>

    global SektNum

    if SektNum > 0:
        if Lese_Sektor(Device, SektNum-1):
            SektNum -= 1
            Haupt_Fenster.configure(state="normal")
            Haupt_Fenster.delete("end-18l", "end-1c")
            Haupt_Fenster.delete("1.0", "2.0")    # "Device" in 1.Zeile löschen
            Haupt_Fenster.insert("1.0", "   Sektor:   {:<47s}".format(str(SektNum+1)) + "\n")
            Haupt_Fenster.insert("1.0", Sektor_Bin2Text(SektNum))
            Haupt_Fenster.insert("1.0", "   Sektor:   {:<47s}".format(str(SektNum)) + Device + "\n")
            Haupt_Fenster.configure(state="disabled")
            Statusleiste_Anzeigen("")

    return "break"       # eingebaute <Pfeiltaste> ignorieren

##############################################################################################################

def Sektoren_Letzter():

    global SektNum

    try:
        with open(Device, "rb") as f:
            f.seek(0, os.SEEK_END)
            gesamt_byte = f.tell()
            gesamt_sekt = int(gesamt_byte / 512)
            SektNum = gesamt_sekt - 128           # 128 Sektoren pro Seite
            Zeige_Sektorenblock()
            return True
    except:
        return False

##############################################################################################################

def SektNum_Eingeben(event=None):

    def Neue_Sektoren_Anzeigen(event):

        global SektNum

        Eingabe = Eingabefeld.get()

        if Eingabe.isdecimal():
            SektNum = int(Eingabe)
            Zeige_Sektorenblock()
            Fenster.destroy()

    Fenster = tk.Toplevel(Master)
    Fenster.title(Device)
    Fenster.geometry("+" + str(Master.winfo_x()+630) + "+" + str(Master.winfo_y()+55)) 
    Fenster.resizable(False, False)
    Fenster.wm_attributes("-topmost", 1)

    Eingabefeld = tk.Entry(Fenster, bd=3, width=15, font=Schrift)
    Eingabefeld.pack(padx=50, pady=30)

    Eingabefeld.focus_set()
    Eingabefeld.bind("<Return>", Neue_Sektoren_Anzeigen)
    Fenster.bind("<Escape>", lambda event: Fenster.destroy())

##############################################################################################################

def Device_Auswaehlen(event=None):

    def Neues_Device_Anzeigen(event):

        global Device, SektNum

        Eingabe = Eingabefeld.get()

        if Lese_Sektor(Eingabe, 0):
            Device = Eingabe
            SektNum = 0
            Zeige_Sektorenblock()
            Fenster.destroy()

    Fenster = tk.Toplevel(Master)
    Fenster.title(Device)
    Fenster.geometry("+" + str(Master.winfo_x()+600) + "+" + str(Master.winfo_y()+55)) 
    Fenster.resizable(False, False)
    Fenster.wm_attributes("-topmost", 1)

    Eingabetext = tk.Label(Fenster, text="Device:", font="Helvetica 11")
    Eingabefeld = tk.Entry(Fenster, bd=3, width=10, font=Schrift)
    tk.Label(Fenster).pack(side=tk.LEFT, padx=25, pady=25)
    Eingabetext.pack(side=tk.LEFT, padx=5, pady=30)
    Eingabefeld.pack(side=tk.LEFT, padx=5, pady=30)
    tk.Label(Fenster).pack(side=tk.LEFT, padx=25, pady=25)

    Eingabefeld.insert(0, "/dev/")
    Eingabefeld.focus_set()
    Eingabefeld.bind("<Return>", Neues_Device_Anzeigen)
    Fenster.bind("<Escape>", lambda event: Fenster.destroy())

##############################################################################################################

##############################################################################################################

def Zeige_Partitionstabelle():

    Status = [0,0,0,0]
    Typ = [0,0,0,0]
    Anfang = [0,0,0,0]
    Anzahl = [0,0,0,0]
    Groesse = [0,0,0,0]

    if Lese_Sektor(Device[0:8], 0):

        Fenster = tk.Toplevel(Master)
        Fenster.title(Device[0:8] + " - Partitionstabelle")
        Fenster.geometry("+" + str(Master.winfo_x()+310) + "+" + str(Master.winfo_y()+400)) 
        Fenster.resizable(False, False)
        Fenster.wm_attributes("-topmost", 1)

        for i in range(4):
            Status[i] = int(SektData[0x01BE+16*i])
        for i in range(4):
            Typ[i] = int(SektData[0x01C2+16*i])
        for i in range(4):
            Anfang[i] = int(SektData[0x01C6+16*i] + SektData[0x01C7+16*i]*256 + SektData[0x01C8+16*i]*65536 + SektData[0x01C9+16*i]*16777216)
        for i in range(4):
            Anzahl[i] = int(SektData[0x01CA+16*i] + SektData[0x01CB+16*i]*256 + SektData[0x01CC+16*i]*65536 + SektData[0x01CD+16*i]*16777216)
        for i in range(4):
            Groesse[i] = Anzahl[i]*512/10**9

        PartText = tk.Text(Fenster, width=66, height=8, padx=60, pady=20, font=Schrift)
        PartText.insert("end",   "\n      Boot    Typ          Anfang          Anzahl        Größe\n")
        PartText.insert("end",     "──────────────────────────────────────────────────────────────────\n")
        for i in range(4):
            PartText.insert("end", " {:1d}.    {:02X}      {:02X}  {:14d}  {:14d}  {:11.1f} GB\n".format(i+1, Status[i], Typ[i], Anfang[i], Anzahl[i], Groesse[i]))

        PartText.pack(pady=1, padx=1)
        PartText.configure(state="disabled")
        Fenster.bind("<Escape>", lambda event: Fenster.destroy())
    else:
        message.showwarning(Device, "\nDer MBR von " + Device[0:8] + " konnte nicht gelesen werden!  ")

##############################################################################################################

def Erweiterte_Partitionen():

    Typ = 0
    Anfang = 0
    Anzahl = 0
    Groesse = 0
    Sektor = 0
    Erweitert = 0

    if Lese_Sektor(Device[0:8], 0):

        for i in range(4):
            if SektData[0x01C2+16*i] == 0x0F:      # 0x0F = LBA,  0x05 = CHS Adressierung
                Typ = int(SektData[0x01C2+16*i])
                Anfang = int(SektData[0x01C6+16*i] + SektData[0x01C7+16*i]*256 + SektData[0x01C8+16*i]*65536 + SektData[0x01C9+16*i]*16777216)
                Anzahl = int(SektData[0x01CA+16*i] + SektData[0x01CB+16*i]*256 + SektData[0x01CC+16*i]*65536 + SektData[0x01CD+16*i]*16777216)
                Groesse = Anzahl*512/10**9
                Erweitert = 1
                Sektor = Anfang
                break

        if Erweitert == 1:

            Fenster = tk.Toplevel(Master)
            Fenster.title(Device[0:8] + " - Erweiterte Partitionen")
            Fenster.geometry("+" + str(Master.winfo_x()+360) + "+" + str(Master.winfo_y()+380)) 
            Fenster.resizable(False, False)
            Fenster.wm_attributes("-topmost", 1)

            ErwText = tk.Text(Fenster, width=58, height=15, padx=60, pady=20, font=Schrift)
            ErwText.insert("end", "\n       Typ         Anfang         Anzahl        Größe\n")
            ErwText.insert("end", "──────────────────────────────────────────────────────────\n")
            ErwText.insert("end", "        {:02X} {:14d} {:14d} {:12.1f} GB\n\n".format(Typ, Anfang, Anzahl, Groesse))

            Anfang = 0
            while Typ != 0:
                if Lese_Sektor(Device[0:8], Sektor+Anfang):
                    Typ = int(SektData[0x01C2])
                    Anfang = int(SektData[0x01C6] + SektData[0x01C7]*256 + SektData[0x01C8]*65536 + SektData[0x01C9]*16777216)
                    Anzahl = int(SektData[0x01CA] + SektData[0x01CB]*256 + SektData[0x01CC]*65536 + SektData[0x01CD]*16777216)
                    Groesse = Anzahl*512/10**9
                    ErwText.insert("end", "  {:1d}.    {:02X} {:14d} {:14d} {:12.1f} GB\n".format(Erweitert, Typ, Anfang, Anzahl, Groesse))
                    Typ = int(SektData[0x01C2+16])
                    Anfang = int(SektData[0x01C6+16] + SektData[0x01C7+16]*256 + SektData[0x01C8+16]*65536 + SektData[0x01C9+16]*16777216)
                    Anzahl = int(SektData[0x01CA+16] + SektData[0x01CB+16]*256 + SektData[0x01CC+16]*65536 + SektData[0x01CD+16]*16777216)
                    Groesse = Anzahl*512/10**9
                    ErwText.insert("end", "        {:02X} {:14d} {:14d} {:12.1f} GB\n\n".format(Typ, Anfang, Anzahl, Groesse))
                    Erweitert += 1
            ErwText.pack(pady=1, padx=1)
            ErwText.configure(state="disabled")
            Fenster.bind("<Escape>", lambda event: Fenster.destroy())
        else:
            message.showinfo(Device, "\nKeine erweiterten Partitionen gefunden.  ")
    else:
        message.showwarning(Device, "\nDer MBR von " + Device[0:8] + " konnte nicht gelesen werden!  ")

##############################################################################################################

def EFI_Partitionen():

    Anfang = [0,0,0,0]
    Ende = [0,0,0,0]
    Attrib = [0,0,0,0]
    Anzahl = [0,0,0,0]
    Groesse = [0,0,0,0]

    if Lese_Sektor(Device[0:8], 1):

        if SektData[0:8] == ("EFI PART").encode("utf-8"):

            Fenster = tk.Toplevel(Master)
            Fenster.title(Device[0:8] + " - EFI Partitionstabelle")
            Fenster.geometry("+" + str(Master.winfo_x()+270) + "+" + str(Master.winfo_y()+400)) 
            Fenster.resizable(False, False)
            Fenster.wm_attributes("-topmost", 1)

            Lese_Sektor(Device[0:8], 2)
            for i in range(4):
                Anfang[i] = int(SektData[0x0020+128*i]        + SektData[0x0021+128*i]*256    + SektData[0x0022+128*i]*256**2 + SektData[0x0023+128*i]*256**3) +\
                            int(SektData[0x0024+128*i]*256**4 + SektData[0x0025+128*i]*256**5 + SektData[0x0026+128*i]*256**6 + SektData[0x0027+128*i]*256**7)
            for i in range(4):
                Ende[i]   = int(SektData[0x0028+128*i]        + SektData[0x0029+128*i]*256    + SektData[0x002A+128*i]*256**2 + SektData[0x002B+128*i]*256**3) +\
                            int(SektData[0x002C+128*i]*256**4 + SektData[0x002D+128*i]*256**5 + SektData[0x002E+128*i]*256**6 + SektData[0x002F+128*i]*256**7)
            for i in range(4):
                Attrib[i] = int(SektData[0x0030+128*i]        + SektData[0x0031+128*i]*256    + SektData[0x0032+128*i]*256**2 + SektData[0x0033+128*i]*256**3) +\
                            int(SektData[0x0034+128*i]*256**4 + SektData[0x0035+128*i]*256**5 + SektData[0x0036+128*i]*256**6 + SektData[0x0037+128*i]*256**7)
            for i in range(4):
                Anzahl[i] = (Ende[i]-Anfang[i])
            for i in range(4):
                Groesse[i] = (Ende[i]-Anfang[i])*512/10**9

            PartText = tk.Text(Fenster, width=75, height=8, padx=60, pady=20, font=Schrift)
            PartText.insert("end",   "\n      Typ          Anfang            Ende          Anzahl        Größe\n")
            PartText.insert("end",     "──────────────────────────────────────────────────────────────────────────\n")
            for i in range(4):
                PartText.insert("end", " {:1d}. {:5d}  {:14d}  {:14d}  {:14d}  {:11.1f} GB\n".format(i+1, Attrib[i], Anfang[i], Ende[i], Anzahl[i], Groesse[i]))

            PartText.pack(pady=1, padx=1)
            PartText.configure(state="disabled")
            Fenster.bind("<Escape>", lambda event: Fenster.destroy())
        else:
            message.showinfo(Device, "\nKeine EFI Partition gefunden. ")
    else:
        message.showwarning(Device, "\nDer 2.Sektor von " + Device[0:8] + " konnte nicht gelesen werden!  ")

##############################################################################################################

def Zeige_BPB_FAT32():

    if len(Device) == 8:  xDevice = Device + "1"
    else:                 xDevice = Device

    if Lese_Sektor(xDevice, 0):

        Fenster = tk.Toplevel(Master)
        Fenster.title(xDevice + " - BPB - FAT32")
        Fenster.geometry("+" + str(Master.winfo_x()+530) + "+" + str(Master.winfo_y()+340)) 
        Fenster.resizable(False, False)
        Fenster.wm_attributes("-topmost", 1)

        BiosText = tk.Text(Fenster, width=38, height=19, padx=10, pady=20, font=Schrift, wrap="none")
        try:     BiosText.insert("end", "\n{:>23s} {:s}\n".format("Bezeichnung:", SektData[0x03:0x0B].decode("utf-8").rstrip("\x00")))
        except:  BiosText.insert("end", "{:>23s}\n".format("Bezeichnung:"))
        try:     BiosText.insert("end", "{:>23s} {:s}\n".format("Volume Label:", SektData[0x47:0x52].decode("utf-8").rstrip("\x00")))
        except:  BiosText.insert("end", "{:>23s}\n".format("Volume Label:"))
        try:     BiosText.insert("end", "{:>23s} {:s}\n".format("Dateisystem:", SektData[0x52:0x5A].decode("utf-8").rstrip("\x00")))
        except:  BiosText.insert("end", "{:>23s}\n".format("Dateisystem:"))
        BiosText.insert("end", "{:>23s} {:02X}\n".format("Media Descriptor:", SektData[0x15]))
        BiosText.insert("end", "{:>23s} {:02X}\n".format("Laufwerknummer:", SektData[0x40]))
        BiosText.insert("end", "{:>23s} {:02X}\n".format("Boot Signatur:", SektData[0x42]))
        BiosText.insert("end", "{:>23s} {:d}\n".format("Bytes/Sektor:", SektData[0x0B] + SektData[0x0C]*256))
        BiosText.insert("end", "{:>23s} {:d}\n".format("Sektoren/Cluster:", SektData[0x0D]))
        BiosText.insert("end", "{:>23s} {:d}\n".format("Reservierte Sektoren:", SektData[0x0E] + SektData[0x0F]*256))
        BiosText.insert("end", "{:>23s} {:d}\n".format("Versteckte Sektoren:", SektData[0x1C] + SektData[0x1D]*256 + SektData[0x1E]*256**2 + SektData[0x1F]*256**3))
        BiosText.insert("end", "{:>23s} {:d}\n".format("Anzahl FAT's:", SektData[0x10]))
        BiosText.insert("end", "{:>23s} {:d}\n".format("Sektoren/FAT:", SektData[0x24] + SektData[0x25]*256 + SektData[0x26]*256**2 + SektData[0x27]*256**3))
        BiosText.insert("end", "{:>23s} {:d}\n".format("Cluster RootDir:", SektData[0x2C] + SektData[0x2D]*256 + SektData[0x2E]*256**2 + SektData[0x2F]*256**3))
        BiosText.insert("end", "{:>23s} {:d}\n".format("Anzahl Köpfe:", SektData[0x1A] + SektData[0x1B]*256))
        BiosText.insert("end", "{:>23s} {:d}\n".format("Sektoren/Spur:", SektData[0x18] + SektData[0x19]*256))
        BiosText.insert("end", "{:>23s} {:d}\n".format("Sektoren gesamt:", SektData[0x20] + SektData[0x21]*256 + SektData[0x22]*256**2 + SektData[0x23]*256**3))

        BiosText.pack(pady=2, padx=1)
        BiosText.configure(state="disabled")
        Fenster.bind("<Escape>", lambda event: Fenster.destroy())
    else:
        message.showwarning(Device, "\nDer Bootsektor von " + xDevice + " konnte nicht gelesen werden!  ")

##############################################################################################################

def Zeige_BPB_NTFS():

    if len(Device) == 8:  xDevice = Device + "1"
    else:                 xDevice = Device

    if Lese_Sektor(xDevice, 0):

        Fenster = tk.Toplevel(Master)
        Fenster.title(xDevice + " - BPB - NTFS")
        Fenster.geometry("+" + str(Master.winfo_x()+530) + "+" + str(Master.winfo_y()+340)) 
        Fenster.resizable(False, False)
        Fenster.wm_attributes("-topmost", 1)

        BiosText = tk.Text(Fenster, width=38, height=18, padx=10, pady=20, font=Schrift, wrap="none")
        try:     BiosText.insert("end", "\n{:>23s} {:s}\n".format("Bezeichnung:", SektData[0x03:0x0B].decode("utf-8").rstrip("\x00")))
        except:  BiosText.insert("end", "{:>23s}\n".format("Bezeichnung:"))
        BiosText.insert("end", "{:>23s} {:02X}\n".format("Media Descriptor:", SektData[0x15]))
        BiosText.insert("end", "{:>23s} {:02X}\n".format("Laufwerknummer:", SektData[0x24]))
        BiosText.insert("end", "{:>23s} {:02X}\n".format("Boot Signatur:", SektData[0x26]))
        BiosText.insert("end", "{:>23s} {:d}\n".format("Bytes/Sektor:", SektData[0x0B] + SektData[0x0C]*256))
        BiosText.insert("end", "{:>23s} {:d}\n".format("Sektoren/Cluster:", SektData[0x0D]))
        BiosText.insert("end", "{:>23s} {:d}\n".format("Reservierte Sektoren:", SektData[0x0E] + SektData[0x0F]*256))
        BiosText.insert("end", "{:>23s} {:d}\n".format("Versteckte Sektoren:", SektData[0x1C] + SektData[0x1D]*256 + SektData[0x1E]*256**2 + SektData[0x1F]*256**3))
        BiosText.insert("end", "{:>23s} {:d}\n".format("Erster MFT Cluster:", SektData[0x30] + SektData[0x31]*256 + SektData[0x32]*256**2 + SektData[0x33]*256**3 +\
                                                                         SektData[0x34]*256**4 + SektData[0x35]*256**5 + SektData[0x36]*256**6 + SektData[0x37]*256**7))
        BiosText.insert("end", "{:>23s} {:d}\n".format("Zweiter MFT Cluster:", SektData[0x38] + SektData[0x39]*256 + SektData[0x3A]*256**2 + SektData[0x3B]*256**3 +\
                                                                         SektData[0x3C]*256**4 + SektData[0x3D]*256**5 + SektData[0x3E]*256**6 + SektData[0x3F]*256**7))
        BiosText.insert("end", "{:>23s} {:02X} ({:d})\n".format("Cluster/MFT-Record:", SektData[0x40], 2**(256-SektData[0x40])))
        BiosText.insert("end", "{:>23s} {:d}\n".format("Cluster/Index-Buffer:", SektData[0x44]))
        BiosText.insert("end", "{:>23s} {:d}\n".format("Anzahl Köpfe:", SektData[0x1A] + SektData[0x1B]*256))
        BiosText.insert("end", "{:>23s} {:d}\n".format("Sektoren/Spur:", SektData[0x18] + SektData[0x19]*256))
        BiosText.insert("end", "{:>23s} {:d}\n".format("Sektoren gesamt:", SektData[0x28] + SektData[0x29]*256 + SektData[0x2A]*256**2 + SektData[0x2B]*256**3 +\
                                                                           SektData[0x2C]*256**4 + SektData[0x2D]*256**5 + SektData[0x2E]*256**6 + SektData[0x2F]*256**7))

        BiosText.pack(pady=2, padx=1)
        BiosText.configure(state="disabled")
        Fenster.bind("<Escape>", lambda event: Fenster.destroy())
    else:
        message.showwarning(Device, "\nDer Bootsektor von " + xDevice + " konnte nicht gelesen werden!  ")

##############################################################################################################

def Zeige_EXT4_Info():

    def Hex_String(offset, anzahl):

        text = ""
        for s in range(anzahl):
            text += "{:02X}".format(SektData[offset+s])
        return text


    if len(Device) == 8:  xDevice = Device + "1"
    else:                 xDevice = Device

    if Lese_Sektor(xDevice, 2):

        Fenster = tk.Toplevel(Master)
        Fenster.title(xDevice + " - EXT4 Info")
        Fenster.geometry("+" + str(Master.winfo_x()+470) + "+" + str(Master.winfo_y()+340)) 
        Fenster.resizable(False, False)
        Fenster.wm_attributes("-topmost", 1)

        BiosText = tk.Text(Fenster, width=46, height=23, padx=10, pady=20, font=Schrift, wrap="none")
        BiosText.insert("end", "\n{:>9s} {:s}\n".format("UUID:", Hex_String(0x68, 16)))
        try:     BiosText.insert("end", "\n{:>25s} {:s}\n".format("Datenträgername:", SektData[0x78:0x88].decode("utf-8").rstrip("\x00")))
        except:  BiosText.insert("end", "{:>25s}\n".format("Datenträgername:"))
        try:     BiosText.insert("end", "{:>25s} {:s}\n".format("Einhängepunkt:", SektData[0x88:0xC8].decode("utf-8").rstrip("\x00")))
        except:  BiosText.insert("end", "{:>25s}\n".format("Einhängepunkt:"))
        sekunden = SektData[0x108] + SektData[0x109]*256 + SektData[0x10A]*256**2 + SektData[0x10B]*256**3
        BiosText.insert("end", "{:>25s} {:s}\n".format("Erstellungsdatum:", datetime.datetime.fromtimestamp(sekunden).strftime("%d.%m.%y %H:%M")))
        BiosText.insert("end", "{:>25s} {:02X}{:02X}\n".format("Magic Signatur:", SektData[0x39], SektData[0x38]))
        BiosText.insert("end", "{:>25s} {:d}\n".format("Mount-Zähler:", SektData[0x34] + SektData[0x35]*256))
        BiosText.insert("end", "{:>25s} {:d}\n".format("Anzahl Inodes:", SektData[0x00] + SektData[0x01]*256 + SektData[0x02]*256**2 + SektData[0x03]*256**3))
        BiosText.insert("end", "{:>25s} {:d}\n".format("Freie Inodes:", SektData[0x10] + SektData[0x11]*256 + SektData[0x12]*256**2 + SektData[0x13]*256**3))
        BiosText.insert("end", "{:>25s} {:d}\n".format("Anzahl Blöcke:", SektData[0x04] + SektData[0x05]*256 + SektData[0x06]*256**2 + SektData[0x07]*256**3))
        BiosText.insert("end", "{:>25s} {:d}\n".format("Freie Blöcke:", SektData[0x0C] + SektData[0x0D]*256 + SektData[0x0E]*256**2 + SektData[0x0F]*256**3))
        BiosText.insert("end", "{:>25s} {:d}\n".format("Reservierte Blöcke:", SektData[0x08] + SektData[0x09]*256 + SektData[0x0A]*256**2 + SektData[0x0B]*256**3))
        BiosText.insert("end", "{:>25s} {:d}\n".format("Erster Inode:", SektData[0x54] + SektData[0x55]*256 + SektData[0x56]*256**2 + SektData[0x57]*256**3))
        BiosText.insert("end", "{:>25s} {:d}\n".format("Inode-Größe:", SektData[0x58] + SektData[0x59]*256))
        BiosText.insert("end", "{:>25s} {:d}\n".format("Erster Datenblock:", SektData[0x14] + SektData[0x15]*256 + SektData[0x16]*256**2 + SektData[0x17]*256**3))
        BiosText.insert("end", "{:>25s} {:d}\n".format("Block-Größe:", (SektData[0x18] + SektData[0x19]*256 + SektData[0x1A]*256**2 + SektData[0x1B]*256**3)*2048))
        BiosText.insert("end", "{:>25s} {:d}\n".format("Cluster-Größe:", (SektData[0x1C] + SektData[0x1D]*256 + SektData[0x1E]*256**2 + SektData[0x1F]*256**3)*2048))
        BiosText.insert("end", "{:>25s} {:d}\n".format("Inodes/Gruppe:", SektData[0x28] + SektData[0x29]*256 + SektData[0x2A]*256**2 + SektData[0x2B]*256**3))
        BiosText.insert("end", "{:>25s} {:d}\n".format("Blöcke/Gruppe:", SektData[0x20] + SektData[0x21]*256 + SektData[0x22]*256**2 + SektData[0x23]*256**3))
        BiosText.insert("end", "{:>25s} {:d}\n".format("Cluster/Gruppe:", SektData[0x24] + SektData[0x25]*256 + SektData[0x26]*256**2 + SektData[0x27]*256**3))

        BiosText.pack(pady=2, padx=1)
        BiosText.configure(state="disabled")
        Fenster.bind("<Escape>", lambda event: Fenster.destroy())
    else:
        message.showwarning(Device, "\nDer Sektor 2 konnte nicht gelesen werden!  ")

##############################################################################################################

#############################################################################################################

def Master_Boot_Record_Sichern():

    if Lese_Sektor(Device[0:8], 0):
        datName = "wde_" + Device[5:8] + "__MasterBootRecord.bin"
        with open(datName, "wb") as datei:
            datei.write(SektData)
        message.showinfo(Device, "\nDer MBR wurde in \"" + datName + "\" gesichert.  ")

##############################################################################################################

def Bootsektor_Sichern():

    if len(Device) == 8:    xDevice = Device + "1"
    else:                   xDevice = Device

    if Lese_Sektor(xDevice, 0):
        datName = "wde_" + xDevice[5:9] + "_BootSector.bin"
        with open(datName, "wb") as datei:
            datei.write(SektData)
        message.showinfo(Device, "\nDer Bootsektor wurde in \"" + datName + "\" gesichert.  ")

##############################################################################################################

def Sektorenblock_Sichern():

    def Sektoren_Sichern(e):

        Erster = EingabeErster.get()
        Anzahl = EingabeAnzahl.get()

        if len(Device) == 8:    xDevice = Device + "_"
        else:                   xDevice = Device

        if Erster.isdecimal() and Anzahl.isdecimal():
            datName = "wde_" + xDevice[5:9] + "_x" + Erster + "_n" + Anzahl + ".bin"
            with open(datName, "wb") as datei:
                for i in range(int(Anzahl)):
                    if Lese_Sektor(Device, int(Erster)+i):
                        datei.write(SektData)
            Fenster.destroy()
            message.showinfo(Device, "\nDie Sektoren wurden in \"" + datName + "\" gesichert.  ")

    Fenster = tk.Toplevel(Master)
    Fenster.title(Device)
    Fenster.geometry("+" + str(Master.winfo_x()+580) + "+" + str(Master.winfo_y()+408)) 
    Fenster.resizable(False, False)
    Fenster.wm_attributes("-topmost", 1)

    TextErster = tk.Label(Fenster, text="1.Sektor:", font="Helvetica 11")
    TextAnzahl = tk.Label(Fenster, text="  Anzahl:", font="Helvetica 11")
    EingabeErster = tk.Entry(Fenster, bd=3, width=12, font=Schrift)
    EingabeAnzahl = tk.Entry(Fenster, bd=3, width=12, font=Schrift)
    tk.Label(Fenster).grid(row=0, column=0, padx=20, pady=1)
    TextErster.grid(row=1, column=1, padx=5, pady=3, sticky="w")    # linksbündig
    TextAnzahl.grid(row=2, column=1, padx=5, pady=3)
    EingabeErster.grid(row=1, column=2, padx=5, pady=3)
    EingabeAnzahl.grid(row=2, column=2, padx=5, pady=3)
    tk.Label(Fenster).grid(row=3, column=3, padx=20, pady=1)

    EingabeErster.focus_set()
    EingabeErster.bind("<Return>", Sektoren_Sichern)
    EingabeAnzahl.bind("<Return>", Sektoren_Sichern)
    Fenster.bind("<Escape>", lambda event: Fenster.destroy())

##############################################################################################################

def MBR_Wiederherstellen():

    global SektData

    mbrDatei = "wde*_" + Device[5:8] + "__MasterBootRecord.bin"
    pfadName = fdialog.askopenfilename(title="MasterBootRecord-Backup für " + Device[5:8] + " öffnen",filetypes=[("",mbrDatei),("Binärdateien","*.bin")])

    if pfadName:
        if message.askyesno(Device, "\nSoll der MBR mit \"" + os.path.basename(pfadName) + "\" überschrieben werden?  "):
            if ReadOnly.get() == 0:
                with open(pfadName, "rb") as fp:
                    SektData = fp.read(512)
                Schreibe_Sektor(Device[0:8], 0)
                Zeige_Sektorenblock()
                message.showinfo(Device, "\nDer MasterBootRecord wurde überschrieben.  ")
            else:
                message.showwarning(Device, "\nKonnte nicht schreiben, der Schreibschutz ist aktiviert.  ")

##############################################################################################################

def Bootsektor_Wiederherstellen():

    global SektData

    if len(Device) == 8:    xDevice = Device + "1"
    else:                   xDevice = Device

    bootDatei = "wde*_" + xDevice[5:9] + "_BootSector.bin"
    pfadName = fdialog.askopenfilename(title="Bootsektor-Backup für " + xDevice[5:9] + " öffnen",filetypes=[("",bootDatei),("Binärdateien","*.bin")])

    if pfadName:
        if message.askyesno(xDevice, "\nSoll der Bootsektor mit \"" + os.path.basename(pfadName) + "\" überschrieben werden?  "):
            if ReadOnly.get() == 0:
                with open(pfadName, "rb") as fp:
                    SektData = fp.read(512)
                Schreibe_Sektor(xDevice, 0)
                Zeige_Sektorenblock()
                message.showinfo(xDevice, "\nDer Bootsektor wurde überschrieben.  ")
            else:
                message.showwarning(xDevice, "\nKonnte nicht schreiben, der Schreibschutz ist aktiviert.  ")

##############################################################################################################

def Sektorenblock_Schreiben():

    global SektData

    if len(Device) == 8:
        blockDatei = "wde*_" + Device[5:8] + "__x*_n*.bin"
    else:
        blockDatei = "wde*_" + Device[5:9] + "_x*_n*.bin"

    pfadName = fdialog.askopenfilename(title="Sektorenblock-Datei für " + Device[5:] + " öffnen",filetypes=[("",blockDatei),("Binärdateien","*.bin")])

    if pfadName:
        datName = os.path.splitext(os.path.basename(pfadName))[0]

        if datName[0:3] == "wde" and datName.find("_x") != -1 and datName.find("_n") != -1:
            x1 = datName.find("_x")
            x2 = datName.find("_", x1+2)
            erster = int(datName[x1+2:x2])
            n1 = datName.find("_n")
            anzahl = int(datName[n1+2:])

            if message.askyesno(Device, "\nSollen die Sektoren " + str(erster) + " bis " + str(erster+anzahl-1) + " überschrieben werden?  "):
                if ReadOnly.get() == 0:
                    with open(pfadName, "rb") as fp:
                        for i in range(int(anzahl)):
                            SektData = fp.read(512)
                            Schreibe_Sektor(Device, int(erster)+i)
                    Zeige_Sektorenblock()
                    message.showinfo(Device, "\nDie Sektoren " + str(erster) + " bis " + str(erster+anzahl-1) + " wurden überschrieben.  ")
                else:
                    message.showwarning(Device, "\nKonnte nicht schreiben, der Schreibschutz ist aktiviert.   ")
        else:
            message.showwarning(Device, "\nUnbekannter Dateiname \"" + os.path.basename(pfadName) + "\"  ")

##############################################################################################################

##############################################################################################################

def Musterdatei_Erstellen():

    def Datei_Erstellen(event=None):

        global Sekt2Data

        auswahl = RadioVar.get()
        if auswahl == 1:
            strBytes = bytearray(EingabeAscii.get(), "utf-8")
            datName = EingabeAscii.get()
        else:
            try:
                strBytes = bytearray.fromhex(EingabeHex.get())
                datName = EingabeHex.get()
            except:
                message.showerror(Device, "Kein gültiger Hex-String!")
                return()
            
        Sekt2Data.clear()
        for i in range(int(512/len(strBytes))+1):
            Sekt2Data += strBytes 
        datName = "wde_Muster_" + datName + ".bin"
        try:
            with open(datName, "wb") as fp:
                fp.write(Sekt2Data[0:512])
            Fenster.destroy()
            message.showinfo(Device, "\nDie Musterdatei \"" + datName + "\" wurde erstellt. ")
        except:
            message.showerror(Device, "\nDie Datei \"" + datName + "\" konnte nicht erstellt werden. ", parent=Fenster)
            return

    def Auswahl_Eingabe():
        auswahl = RadioVar.get()
        if auswahl == 1:
            EingabeAscii.config(state="normal")
            EingabeHex.config(state="disabled")
        else:
            EingabeAscii.config(state="disabled")
            EingabeHex.config(state="normal")

#---------------------------------------------------

    Fenster = tk.Toplevel(Master)
    Fenster.title(Device)
    Fenster.geometry("+" + str(Master.winfo_x()+450) + "+" + str(Master.winfo_y()+280)) 
    Fenster.resizable(False, False)
    Fenster.wm_attributes("-topmost", 1)

    RadioVar = tk.IntVar(value=1)

    TextOben = tk.Label(Fenster, text="Gewünschte Muster-Zeichenkette eingeben:", font="Helvetica 11")
    RadioAscii = tk.Radiobutton(Fenster, variable=RadioVar, value=1, command=Auswahl_Eingabe)
    TextAscii = tk.Label(Fenster, text="Ascii-String:", font="Helvetica 11")
    EingabeAscii = tk.Entry(Fenster, bd=3, width=28, font=Schrift)
    RadioHex = tk.Radiobutton(Fenster, variable=RadioVar, value=2, command=Auswahl_Eingabe)
    TextHex = tk.Label(Fenster, text="Hex-String:", font="Helvetica 11")
    EingabeHex = tk.Entry(Fenster, bd=3, width=28, font=Schrift)
    TextHinweis = tk.Label(Fenster, text="Hinweis: Es wird eine Binärdatei mit 512 Byte erstellt.", font="Helvetica 9")
    ButtonErstellen = tk.Button(Fenster, bd=3, text="Erstellen", font="Helvetica 11", command=Datei_Erstellen)
    ButtonAbbrechen = tk.Button(Fenster, bd=3, text="Abbrechen", font="Helvetica 11", command=Fenster.destroy)

    tk.Label(Fenster).grid(row=0, column=0, padx=10)
    TextOben.grid(row=1, column=0, columnspan=7, padx=5, pady=15)
    RadioAscii.grid(row=2, column=1, padx=5, pady=3)
    TextAscii.grid(row=2, column=2, padx=5, pady=3, sticky="e")
    EingabeAscii.grid(row=2, column=3, columnspan=3, padx=1, pady=3)
    RadioHex.grid(row=3, column=1, padx=5, pady=3)
    TextHex.grid(row=3, column=2, padx=5, pady=3, sticky="e")
    EingabeHex.grid(row=3, column=3, columnspan=3, padx=1, pady=3)
    TextHinweis.grid(row=4, column=0, columnspan=7, pady=15)
    ButtonErstellen.grid(row=5, column=0, columnspan=7, padx=80, pady=7, ipadx=28, sticky="w")
    ButtonAbbrechen.grid(row=5, column=0, columnspan=7, padx=80, pady=7, ipadx=15, sticky="e")
    tk.Label(Fenster).grid(row=6, column=6, padx=20)

    EingabeAscii.config(state="normal")
    EingabeHex.config(state="disabled")
    EingabeAscii.focus_set()
    EingabeAscii.bind("<Return>", Datei_Erstellen)
    EingabeHex.bind("<Return>", Datei_Erstellen)
    Fenster.bind("<Escape>", lambda event: Fenster.destroy())

##############################################################################################################

def Muster_Schreiben():

    global SektData

    def Sektoren_Schreiben(e):

        Erster = EingabeErster.get()
        Anzahl = EingabeAnzahl.get()
        Letzter = int(Erster) + int(Anzahl) -1

        if Erster.isdecimal() and Anzahl.isdecimal():
            Fenster.destroy()
            if message.askyesno(Device, "\nSollen die Sektoren " + Erster + " bis " + (str(Letzter)) + " überschrieben werden?  "):
                if ReadOnly.get() == 0:
                    for i in range(int(Anzahl)):
                        Schreibe_Sektor(Device, int(Erster)+i)
                    Zeige_Sektorenblock()
                    message.showinfo(Device, "\nDie Sektoren wurden mit \"" + os.path.basename(pfadName) + "\" überschrieben.  ")
                else:
                    message.showwarning(Device, "\nKonnte nicht schreiben, der Schreibschutz ist aktiviert.  ")

#-----------------------------------

    pfadName = fdialog.askopenfilename(title="Musterdatei (512 Byte) öffnen",filetypes=[("Binärdateien","*.bin"),("Alle Dateien","*")])

    if pfadName:
        Anzahl = os.path.getsize(pfadName)
        if Anzahl == 512:                     # nur Dateien mit 512 Byte zulassen
            with open(pfadName, "rb") as fp:
                SektData = fp.read(512)

            Fenster = tk.Toplevel(Master)
            Fenster.title(Device)
            Fenster.geometry("+" + str(Master.winfo_x()+580) + "+" + str(Master.winfo_y()+408)) 
            Fenster.resizable(False, False)
            Fenster.wm_attributes("-topmost", 1)

            TextErster = tk.Label(Fenster, text="1.Sektor:", font="Helvetica 11")
            TextAnzahl = tk.Label(Fenster, text=" Anzahl :", font="Helvetica 11")

            EingabeErster = tk.Entry(Fenster, bd=3, width=12, font=Schrift)
            EingabeAnzahl = tk.Entry(Fenster, bd=3, width=12, font=Schrift)
            tk.Label(Fenster).grid(row=0, column=0, padx=20, pady=1)
            TextErster.grid(row=1, column=1, padx=5, pady=3, sticky="w")    # linksbündig
            TextAnzahl.grid(row=2, column=1, padx=5, pady=3)
            EingabeErster.grid(row=1, column=2, padx=5, pady=3)
            EingabeAnzahl.grid(row=2, column=2, padx=5, pady=3)
            tk.Label(Fenster).grid(row=3, column=3, padx=20, pady=1)

            EingabeErster.focus_set()
            EingabeErster.bind("<Return>", Sektoren_Schreiben)
            EingabeAnzahl.bind("<Return>", Sektoren_Schreiben)
            Fenster.bind("<Escape>", lambda event: Fenster.destroy())

        else:
            message.showwarning(Device, "\"" + os.path.basename(pfadName) + "\" hat nicht die erforderliche Sektorgröße von 512 Byte.  ")

##############################################################################################################

def Sektoren_Vergleichen():

    global SektData, Sekt2Data

    pfadName = fdialog.askopenfilename(title="Vergleichsdatei öffnen",filetypes=[("Binärdateien","*.bin"),("Alle Dateien","*")])

    if pfadName:
        datName = os.path.splitext(os.path.basename(pfadName))[0]
        if datName[0:3] == "wde":
            if datName.find("MasterBootRecord") != -1 or datName.find("BootSector") != -1:
                erster = 0
                anzahl = 1
                GUELTIG = True
            elif datName.find("_x") != -1 and datName.find("_n") != -1:
                x1 = datName.find("_x")
                x2 = datName.find("_", x1+2)
                erster = int(datName[x1+2:x2])
                n1 = datName.find("_n")
                anzahl = int(datName[n1+2:])
                GUELTIG = True
            else:
                message.showwarning(Device, "\nUnbekannter Dateiname \"" + os.path.basename(pfadName) + "\"  ")
                GUELTIG = False

            if GUELTIG:
                verschiedene = 0
                meldung = ""
                with open(pfadName, "rb") as fp:
                    for x in range(anzahl):
                        Lese_Sektor(Device, erster+x)
                        Sekt2Data = fp.read(512)
                        meldung += "\nSektor: {:d}  -\n".format(erster+x)
                        n = 0
                        for i in range(512):
                            if SektData[i] != Sekt2Data[i]:
                                verschiedene += 1      # veränderte Bytes insgesamt
                                n += 1                 # veränderte Bytes / Sektor
                                if n < 64:
                                    meldung += "{:03X}, ".format(i)
                                    if n % 16 == 0:    meldung += "    \n"
                                if n == 64:            meldung += "..."
                        if n == 0:
                            meldung = meldung[:-1] + "  ok"
                if verschiedene == 0:
                    message.showinfo(Device, "\n>>>>>   I D E N T I S C H   <<<<<     ")
                else:
                    message.showinfo(Device, "\n" + str(verschiedene) + " veränderte Bytes gefunden:  \n" + meldung)
        else:
            message.showwarning(Device, "\nUnbekannter Dateiname \"" + os.path.basename(pfadName) + "\"  ")

##############################################################################################################

def Zeichenkette_Suchen():

    def String_Suchen(event=None):

        auswahl = RadioVar.get()
        if auswahl == 1:    string = EingabeAscii.get()
        else:               string = EingabeHex.get()
        erster = EingabeErster.get()
        anzahl = EingabeAnzahl.get()

        if string != "" and erster.isdecimal() and anzahl.isdecimal():
            if auswahl == 1:
                strBytes = bytearray(string, "utf-8")
            else:
                try:
                    strBytes = bytearray.fromhex(string)
                except:
                    TextErgebnis.delete("1.0", "end")
                    TextErgebnis.insert("end", "Kein gültiger Hex-String!\n")
                    return()

            zahler = 0
            TextErgebnis.delete("1.0", "end")
            try:
                for i in range(int(anzahl)):
                    print("\r" + str(i), end="")                    # Suchverlauf im Terminal anzeigen
                    if Lese_Sektor(Device, int(erster)+i):
                        index = SektData.find(strBytes)
                        if index != -1:
                            TextErgebnis.insert("end", "{:5d}.  Sektor: {:d} - Index: {:d}\n".format(zahler+1, int(erster)+i, index))
                            zahler += 1
                print("")
            except KeyboardInterrupt:
                pass
                TextErgebnis.insert("end", "Durch Benutzer vorzeitig abgebrochen.\n")
            if zahler == 0:
                TextErgebnis.insert("end", "String wurde nicht gefunden.\n")

    def String_Weiter(event=None):
        neuer = int(EingabeErster.get()) + int(EingabeAnzahl.get())
        EingabeErster.delete(0, "end")
        EingabeErster.insert(0, str(neuer))
        String_Suchen()

    def Auswahl_Eingabe():
        auswahl = RadioVar.get()
        if auswahl == 1:
            EingabeAscii.config(state="normal")
            EingabeHex.config(state="disabled")
        else:
            EingabeAscii.config(state="disabled")
            EingabeHex.config(state="normal")

#---------------------------------------------------

    Fenster = tk.Toplevel(Master)
    Fenster.title(Device)
    Fenster.geometry("+" + str(Master.winfo_x()+450) + "+" + str(Master.winfo_y()+55)) 
    Fenster.resizable(False, False)
    Fenster.wm_attributes("-topmost", 1)

    RadioVar = tk.IntVar(value=1)

    RadioAscii = tk.Radiobutton(Fenster, variable=RadioVar, value=1, command=Auswahl_Eingabe)
    TextAscii = tk.Label(Fenster, text="Ascii-String:", font="Helvetica 11")
    EingabeAscii = tk.Entry(Fenster, bd=3, width=28, font=Schrift)
    RadioHex = tk.Radiobutton(Fenster, variable=RadioVar, value=2, command=Auswahl_Eingabe)
    TextHex = tk.Label(Fenster, text="Hex-String:", font="Helvetica 11")
    EingabeHex = tk.Entry(Fenster, bd=3, width=28, font=Schrift)
    TextErster = tk.Label(Fenster, text="1. Sektor:", font="Helvetica 11")
    EingabeErster = tk.Entry(Fenster, bd=3, width=10, font=Schrift)
    TextAnzahl = tk.Label(Fenster, text="Anzahl:", font="Helvetica 11")
    EingabeAnzahl = tk.Entry(Fenster, bd=3, width=10, font=Schrift)
    ScrollVertikal = tk.Scrollbar(Fenster, width=20)
    TextErgebnis = tk.Text(Fenster, width=40, height=22, padx=20, pady=20, yscrollcommand = ScrollVertikal.set, font=Schrift)
    ScrollVertikal.config(command = TextErgebnis.yview)
    ButtonSuchen = tk.Button(Fenster, bd=3, text="Suchen", font="Helvetica 11", command=String_Suchen)
    ButtonWeiter = tk.Button(Fenster, bd=3, text="Weiter", font="Helvetica 11", command=String_Weiter)
    ButtonAbbrechen = tk.Button(Fenster, bd=3, text="Abbrechen", font="Helvetica 11", command=Fenster.destroy)

    tk.Label(Fenster).grid(row=0, column=0, padx=10, pady=1)
    RadioAscii.grid(row=1, column=1, padx=5, pady=3)
    TextAscii.grid(row=1, column=2, padx=5, pady=3, sticky="e")
    EingabeAscii.grid(row=1, column=3, columnspan=3, padx=1, pady=3)
    RadioHex.grid(row=2, column=1, padx=5, pady=3)
    TextHex.grid(row=2, column=2, padx=5, pady=3, sticky="e")
    EingabeHex.grid(row=2, column=3, columnspan=3, padx=1, pady=3)
    TextErster.grid(row=3, column=2, padx=5, pady=10, sticky="e")
    EingabeErster.grid(row=3, column=3, padx=1, pady=10)
    TextAnzahl.grid(row=3, column=4, padx=5, pady=10, sticky="e")
    EingabeAnzahl.grid(row=3, column=5, padx=1, pady=10)
    ScrollVertikal.grid(row=5, column=6, columnspan=1, padx=1, pady=1, sticky="nws")
    TextErgebnis.grid(row=5, column=1, columnspan=5, padx=1, pady=1)
    ButtonSuchen.grid(row=6, column=0, columnspan=7, padx=40, pady=20, ipadx=28, sticky="w")
    ButtonWeiter.grid(row=6, column=0, columnspan=7, padx=1, pady=20, ipadx=33)
    ButtonAbbrechen.grid(row=6, column=0, columnspan=7, padx=40, pady=20, ipadx=15, sticky="e")
    tk.Label(Fenster).grid(row=6, column=6, padx=20, pady=5)

    EingabeErster.insert(0, str(SektNum))
    EingabeAnzahl.insert(0, str(10000))
    EingabeAscii.config(state="normal")
    EingabeHex.config(state="disabled")
    EingabeAscii.focus_set()
    EingabeAscii.bind("<Return>", String_Suchen)
    EingabeHex.bind("<Return>", String_Suchen)
    EingabeErster.bind("<Return>", String_Suchen)
    EingabeAnzahl.bind("<Return>", String_Suchen)
    Fenster.bind("<Escape>", lambda event: Fenster.destroy())

##############################################################################################################

def Part_Tabelle_Editieren():

    def Part_Tabelle_Schreiben(event=None):

        global SektData

        e1 = Eingabe1.get()
        e2 = Eingabe2.get()
        e3 = Eingabe3.get()
        e4 = Eingabe4.get()

        try:
            int(e1,16) + int(e2,16) + int(e3,16) + int(e4,16)     # auf gültigen Hex-String prüfen

            if len(e1) == 32 and len(e2) == 32 and len(e3) == 32 and len(e4) == 32:     # auf richtige Länge prüfen (16 Byte)
                if message.askyesno(Device, "\nSoll die Partitionstabelle von \"" + Device[5:8] + "\" überschrieben werden?  ", parent=Fenster):
                    if ReadOnly.get() == 0:
                        SektData = SektData[0:446] + bytearray.fromhex(e1) + bytearray.fromhex(e2) + bytearray.fromhex(e3) + bytearray.fromhex(e4) + bytearray.fromhex("55aa")
                        if Schreibe_Sektor(Device[0:8], 0):
                            Zeige_Sektorenblock()
                            message.showinfo(Device[0:8], "\nDie Partitionstabelle von \"" + Device[5:8] + "\" wurde überschrieben.  ", parent=Fenster)
                        else:
                            message.showwarning(Device, "\nDer Masterbootsektor konnte nicht überschrieben werden.  ", parent=Fenster)
                    else:
                        message.showwarning(Device, "\nKonnte nicht schreiben, der Schreibschutz ist aktiviert.  ", parent=Fenster)
                Fenster.destroy()
        except:
            pass

    if Lese_Sektor(Device[0:8], 0):

        Fenster = tk.Toplevel(Master)
        Fenster.title(Device[0:8])
        Fenster.geometry("+" + str(Master.winfo_x()+500) + "+" + str(Master.winfo_y()+200)) 
        Fenster.resizable(False, False)
        Fenster.wm_attributes("-topmost", 1)

        TextOben = tk.Label(Fenster, text="Partitionstabelle (4 x 16 Byte):", font="Helvetica 12")
        TextMit1 = tk.Label(Fenster, text=" ├─┼─────┼─┼─────┼───────┼───────┤  ", font=Schrift)
        TextMit2 = tk.Label(Fenster, text=" ├─┼─────┼─┼─────┼───────┼───────┤  ", font=Schrift)
        TextMit3 = tk.Label(Fenster, text=" ├─┼─────┼─┼─────┼───────┼───────┤  ", font=Schrift)
        Eingabe1 = tk.Entry(Fenster, bd=3, width=33, font=Schrift)
        Eingabe2 = tk.Entry(Fenster, bd=3, width=33, font=Schrift)
        Eingabe3 = tk.Entry(Fenster, bd=3, width=33, font=Schrift)
        Eingabe4 = tk.Entry(Fenster, bd=3, width=33, font=Schrift)
        ButtonSpeichern = tk.Button(Fenster, bd=3, text="Speichern", font="Helvetica 11", command=Part_Tabelle_Schreiben)
        ButtonAbbrechen = tk.Button(Fenster, bd=3, text="Abbrechen", font="Helvetica 11", command=Fenster.destroy)

        TextOben.pack(padx=50, pady=25)
        Eingabe1.pack(padx=50, pady=2)
        TextMit1.pack(padx=50, pady=2)
        Eingabe2.pack(padx=50, pady=2)
        TextMit2.pack(padx=50, pady=2)
        Eingabe3.pack(padx=50, pady=2)
        TextMit3.pack(padx=50, pady=2)
        Eingabe4.pack(padx=50, pady=2)
        ButtonSpeichern.pack(padx=70, pady=30, ipadx=23, side="left")
        ButtonAbbrechen.pack(padx=0, pady=30, ipadx=20, side="left")

        Eintrag1 = "".join("{:02X}".format(i) for i in SektData[0x01BE:0x01BE+16])
        Eintrag2 = "".join("{:02X}".format(i) for i in SektData[0x01BE+16:0x01BE+32])
        Eintrag3 = "".join("{:02X}".format(i) for i in SektData[0x01BE+32:0x01BE+48])
        Eintrag4 = "".join("{:02X}".format(i) for i in SektData[0x01BE+48:0x01BE+64])

        Eingabe1.insert(0, Eintrag1)
        Eingabe2.insert(0, Eintrag2)
        Eingabe3.insert(0, Eintrag3)
        Eingabe4.insert(0, Eintrag4)
        Eingabe1.focus_set()
        Eingabe1.bind("<Return>", Part_Tabelle_Schreiben)
        Eingabe2.bind("<Return>", Part_Tabelle_Schreiben)
        Eingabe3.bind("<Return>", Part_Tabelle_Schreiben)
        Eingabe4.bind("<Return>", Part_Tabelle_Schreiben)
        Fenster.bind("<Escape>", lambda event: Fenster.destroy())

##############################################################################################################

def Aktl_Sektor_Editieren():

    def Bin2Hex(sektnum):

        text = ""
        for z in range(32):    # 32 Zeilen
            for s in range(16):
                text += "{:02X}".format(SektData[z*16+s]) + " "
        return text

    def Bin2Ascii(sektnum):

        text = ""
        for z in range(32):    # 32 Zeilen  
            for s in range(16):
                if SektData[z*16+s] > 31 and SektData[z*16+s] < 127:
                    text += "{:c}".format(SektData[z*16+s])
                else:
                    text += "." 
        return text

    def Eingabe_Pruefen():

        global Sekt2Data

        hex_str = Hex_Fenster.get("1.0", tk.END + "-1c")     # ohne letztes LF !!

        if len(hex_str) != 1536:          # Länge prüfen (512*3=1536)
            message.showwarning(Device, "\nUngültiges Format. ", parent=Hex_Fenster)
            return False
        for i in range(0, len(hex_str), 3):
            try:
                int(hex_str[i], 16)       # String mit Basis 16 in Zahl konvertieren
                int(hex_str[i+1], 16)
            except ValueError:
                message.showwarning(Device, "\nUngültige Hex-Zahl. ", parent=Hex_Fenster)
                return False
            if hex_str[i+2] != " ":       # 3.Zeichen prüfen (Leerzeichen)
                message.showwarning(Device, "\nUngültiges Format. ", parent=Hex_Fenster)
                return False

        Sekt2Data = bytearray.fromhex(hex_str.replace(" ", ""))    # Hex-Zahlen-String -> bytearray
        return True

    def Datei_Speichern(event):

        if Eingabe_Pruefen():
            if len(Device) == 8:    xDevice = Device + "_"
            else:                   xDevice = Device
            datName = "wde_" + xDevice[5:9] + "_" + str(SektNum) + ".bin"
            with open(datName, "wb") as Datei:
                Datei.write(Sekt2Data)
            message.showinfo(Device, "\nSektor wurde in Datei " + datName + " gespeichert.  ", parent=Fenster)
            Fenster.destroy()

    def Sektor_Speichern(event):

        if Eingabe_Pruefen():
            if message.askyesno(Device, "\nSoll Sektor " + str(SektNum) + " überschrieben werden?  ", parent=Fenster):
                if ReadOnly.get() == 0:
                    with open(Device, "wb") as fp:
                        fp.seek(SektNum*512)
                        fp.write(Sekt2Data)
                    Zeige_Sektorenblock()
                    Fenster.destroy()
                else:
                    message.showwarning(Device, "\nKonnte nicht schreiben, der Schreibschutz ist aktiviert.  ", parent=Fenster)

    def Einfuegen_Umstellen(event):

        global EINFUEGEN

        if EINFUEGEN:    EINFUEGEN = False
        else:            EINFUEGEN = True


    def Einfuegemodus(event):

        if EINFUEGEN:
            if event.char == event.keysym or event.keysym == "space":    # wenn normale Taste oder Leertaste,
                Hex_Fenster.delete("insert", "insert + 1c")              #  dann lösche Zeichen an der akt. Cursorposition

#---------------------------------------------------

    if Lese_Sektor(Device, SektNum):

        Fenster = tk.Toplevel(Master)
        Fenster.title(Device + " - Sektor: " + str(SektNum))
        Fenster.geometry("+" + str(Master.winfo_x()+405) + "+" + str(Master.winfo_y()+56)) 
        Fenster.resizable(False, False)
        Fenster.wm_attributes("-topmost", True)

        Hex_Fenster = tk.Text(Fenster, width=48, height=32, padx=12, pady=12)
        Hex_Fenster.config(foreground=Vordergrund, background=Hintergrund, font="Consolas 10", undo="TRUE", insertbackground="white")
        Ascii_Fenster = tk.Text(Fenster, width=16, height=32, padx=1, pady=12)
        Ascii_Fenster.config(foreground=Vordergrund, background=Hintergrund, font="Consolas 10")
        Linie_Oben = tk.Label(Fenster, text="|              |              | ", font="Consolas 8")
        Linie_Unten = tk.Label(Fenster, text="|              |              | ", font="Consolas 8")
        Info_Zeile = tk.Label(Fenster, text="<Strg+A> in Datei speichern   <Strg+S> in Sektor speichern   <F9> Einfügemodus   <Esc> Abbrechen")
        Info_Zeile.config(foreground=Vordergrund, background="#000000", font="Helvetica 9", relief="sunken")

        Linie_Oben.grid(row=0, column=1, padx=2, pady=1)
        for i in range(16):
            tk.Label(Fenster, text="{:03X}".format(i*32), font="Consolas 10").grid(row=i+1, column=0, padx=5, pady=3)
        Hex_Fenster.grid(row=1, rowspan=18, column=1, padx=2, pady=0)
        Ascii_Fenster.grid(row=1, rowspan=18, column=2, padx=4, pady=0)
        tk.Label(Fenster).grid(row=1, column=3, padx=6, pady=0)
        Linie_Unten.grid(row=20, column=1, padx=2, pady=0)
        Info_Zeile.grid(row=21, column=0, columnspan=4, padx=0, pady=0, ipadx=1, ipady=7, sticky="ew")

        Hex_Fenster.insert("1.0", Bin2Hex(SektNum))
        Ascii_Fenster.insert("1.0", Bin2Ascii(SektNum))
        Ascii_Fenster.config(state="disabled")

        Hex_Fenster.focus_set()
        Hex_Fenster.mark_set("insert", "1.0")
        Hex_Fenster.bind("<Key>", Einfuegemodus)
        Fenster.bind("<Control-Key-a>", Datei_Speichern)
        Fenster.bind("<Control-Key-s>", Sektor_Speichern)
        Fenster.bind("<F9>", Einfuegen_Umstellen)
        Fenster.bind("<Escape>", lambda event: Fenster.destroy())

#############################################################################################################

##############################################################################################################

def Hilfe_Disk_Devices():

    Fenster = tk.Toplevel(Master)
    Fenster.title("Disk Devices")
    Fenster.geometry("+" + str(Master.winfo_x()+530) + "+" + str(Master.winfo_y()+350)) 
    Fenster.resizable(False, False)
    Fenster.wm_attributes("-topmost", 1)

    DevText = tk.Text(Fenster, width=36, height=13, padx=40, pady=20, font=Schrift)
    DevText.insert("end", "\n HDD - SATA:    sda, sdb, sdc, ...\n")
    DevText.insert("end", " └─ Partition:  sda1, ..2, ..3, ...\n\n")
    DevText.insert("end", " HDD - IDE:     hda, hdb\n")
    DevText.insert("end", " └─ Partition:  hda1, ..2, ..3, ...\n\n")
    DevText.insert("end", " USB - Drive:   sdb, sdc, sdd, ...\n")
    DevText.insert("end", " └─ Partition:  sdb1, ..2, ..3, ...\n\n")
    DevText.insert("end", " DVD - SATA:    sr0, sr1  (cdrom)\n")
    DevText.insert("end", " DVD - IDE:     scd0, scd1  (cdrom)\n")

    DevText.pack(padx=1, pady=1)
    DevText.configure(state="disabled")
    Fenster.bind("<Escape>", lambda event: Fenster.destroy())

##############################################################################################################

def Hilfe_Partitionstypen(event=None):

    Fenster = tk.Toplevel(Master)
    Fenster.title("Partitionstypen")
    Fenster.geometry("+" + str(Master.winfo_x()+560) + "+" + str(Master.winfo_y()+180)) 
    Fenster.resizable(False, False)
    Fenster.wm_attributes("-topmost", 1)

    PartText = tk.Text(Fenster, width=29, height=31, padx=40, pady=20, font=Schrift)
    PartText.insert("end", "\n 01h  =  FAT12\n")
    PartText.insert("end", " 04h  =  FAT16 < 32MB\n")
    PartText.insert("end", " 05h  =  Extended Partition\n")
    PartText.insert("end", " 06h  =  FAT16B\n")
    PartText.insert("end", " 07h  =  NTFS, HPFS, exFAT\n")
    PartText.insert("end", " 08h  =  OS/2, HPFS\n")
    PartText.insert("end", " 0Bh  =  FAT32 (CHS)\n")
    PartText.insert("end", " 0Ch  =  FAT32 (LBA)\n")
    PartText.insert("end", " 0Eh  =  FAT16B (LBA)\n")
    PartText.insert("end", " 0Fh  =  WIN95 Extend (LBA)\n")
    PartText.insert("end", " 12h  =  Compaq Diagnostic\n")
    PartText.insert("end", " 27h  =  Windows Recovery\n")
    PartText.insert("end", " 42h  =  Win LDM (2000/XP)\n")
    PartText.insert("end", " 75h  =  Unix PC/IX\n")
    PartText.insert("end", " 82h  =  Linux Swap\n")
    PartText.insert("end", " 83h  =  Linux ext3 / ext4\n")
    PartText.insert("end", " 84h  =  Intel Rapid Start\n")
    PartText.insert("end", " 85h  =  Linux extended\n")
    PartText.insert("end", " 86h  =  Linux RAID\n")
    PartText.insert("end", " 8Eh  =  Linux LVM\n")
    PartText.insert("end", " 93h  =  Linux hidden\n")
    PartText.insert("end", " ABh  =  Apple Boot\n")
    PartText.insert("end", " AFh  =  Apple RAID\n")
    PartText.insert("end", " C0h  =  HP-UX data, service\n")
    PartText.insert("end", " DEh  =  Dell Utility\n")
    PartText.insert("end", " EDh  =  ESP (Lenova, Sony)\n")
    PartText.insert("end", " EEh  =  GUID (protect MBR)\n")
    PartText.insert("end", " EFh  =  EFI (MBR schema)\n")
    PartText.insert("end", " FDh  =  Linux RAID auto\n")

    PartText.pack(padx=1, pady=1)
    PartText.configure(state="disabled")
    Fenster.bind("<Escape>", lambda event: Fenster.destroy())

##############################################################################################################

def Ueber():

    Fenster = tk.Toplevel(Master)
    Fenster.title("Über")
    Fenster.geometry("400x180+" + str(Master.winfo_x()+560) + "+" + str(Master.winfo_y()+380)) 
    Fenster.resizable(False, False)
    Fenster.wm_attributes("-topmost", 1)

    Label1 = tk.Label(Fenster, text="Woody's Disk Explorer", font="Helvetica 14 bold")
    Label2 = tk.Label(Fenster, text="Version 1.05", font="Helvetica 12")
    Label3 = tk.Label(Fenster, text="Copyright © Woodstock", font="Helvetica 12")

    Label1.pack(padx=10, ipady=14) 
    Label2.pack(padx=10, ipady=14) 
    Label3.pack(padx=10, ipady=14) 
    Fenster.bind("<Escape>", lambda event: Fenster.destroy())

###################################################################################################################

def Statusleiste_Anzeigen(text):

    if ReadOnly.get() == 1:    schutz = "Schreibgeschützt"
    else:                      schutz = "Kein Schreibschutz"
    StatusText.set("  Device: {:s}  |  Sektor: {:d}  |  {:s}  |  {:s}".format(Device, SektNum, schutz, text))

###################################################################################################################

Menuleiste = tk.Menu(Master, activebackground=Hintergrund, activeforeground=Vordergrund, font="Helvetica 11")

Menu_Device = tk.Menu(Menuleiste, tearoff=0, activebackground=Hintergrund, activeforeground=Vordergrund, font="Helvetica 11")
Menu_Device_BPB = tk.Menu(Menuleiste, tearoff=0, activebackground=Hintergrund, activeforeground=Vordergrund, font="Helvetica 11")
Menu_Backup = tk.Menu(Menuleiste, tearoff=0, activebackground=Hintergrund, activeforeground=Vordergrund, font="Helvetica 11")
Menu_Extras = tk.Menu(Menuleiste, tearoff=0, activebackground=Hintergrund, activeforeground=Vordergrund, font="Helvetica 11")
Menu_Hilfe = tk.Menu(Menuleiste, tearoff=0, activebackground=Hintergrund, activeforeground=Vordergrund, font="Helvetica 11")

Menu_Device.add_command(label="  Device auswählen", command=Device_Auswaehlen)
Menu_Device.add_separator()
Menu_Device.add_command(label="  Partitionstabelle", command=Zeige_Partitionstabelle)
Menu_Device.add_command(label="  Erweiterte Partitionen", command=Erweiterte_Partitionen)
Menu_Device.add_command(label="  EFI Partitionen", command=EFI_Partitionen)
Menu_Device_BPB.add_command(label="   FAT32", command=Zeige_BPB_FAT32)
Menu_Device_BPB.add_command(label="   NTFS", command=Zeige_BPB_NTFS)
Menu_Device.add_cascade(label="  BIOS-Parameter-Block", menu=Menu_Device_BPB)
Menu_Device.add_command(label="  EXT4 Informationen", command=Zeige_EXT4_Info)
Menu_Device.add_separator()
Menu_Device.add_command(label="  Beenden", command=Master.destroy)

Menu_Backup.add_command(label="  Master Boot Record sichern", command=Master_Boot_Record_Sichern)
Menu_Backup.add_command(label="  Bootsektor sichern", command=Bootsektor_Sichern)
Menu_Backup.add_command(label="  Sektorenblock sichern", command=Sektorenblock_Sichern)
Menu_Backup.add_separator()
Menu_Backup.add_command(label="  MBR wiederherstellen", command=MBR_Wiederherstellen)
Menu_Backup.add_command(label="  Bootsektor wiederherstellen", command=Bootsektor_Wiederherstellen)
Menu_Backup.add_command(label="  Sektorenblock schreiben", command=Sektorenblock_Schreiben)

Menu_Extras.add_command(label="  Musterdatei erstellen", command=Musterdatei_Erstellen)
Menu_Extras.add_command(label="  Muster in Sektoren schreiben", command=Muster_Schreiben)
Menu_Extras.add_separator()
Menu_Extras.add_command(label="  Sektoren überprüfen", command=Sektoren_Vergleichen)
Menu_Extras.add_command(label="  Zeichenkette suchen", command=Zeichenkette_Suchen)
Menu_Extras.add_separator()
Menu_Extras.add_command(label="  Partitionstabelle editieren", command=Part_Tabelle_Editieren)
Menu_Extras.add_command(label="  Aktuellen Sektor editieren", command=Aktl_Sektor_Editieren)

Menu_Hilfe.add_command(label="  Disk Devices", command=Hilfe_Disk_Devices)
Menu_Hilfe.add_command(label="  Partitionstypen", command=Hilfe_Partitionstypen, accelerator=" <F1> ")
Menu_Hilfe.add_separator()
Menu_Hilfe.add_command(label="  Über", command=Ueber)

Menuleiste.add_cascade(label=" Device", menu=Menu_Device, underline=1)
Menuleiste.add_cascade(label=" Backup", menu=Menu_Backup, underline=1)
Menuleiste.add_cascade(label=" Extras", menu=Menu_Extras, underline=1)
Menuleiste.add_cascade(label=" Hilfe ", menu=Menu_Hilfe, underline=1)
Menuleiste.add_checkbutton(label="Schreibschutz   ", variable=ReadOnly, font="Helvetica 11", background="#aa0000", foreground="white",\
                selectcolor="white", activebackground=Hintergrund, activeforeground=Vordergrund, command=lambda: Statusleiste_Anzeigen(""))
Master.config(menu=Menuleiste)

Button_Frame = tk.Frame(Master, bg=Hintergrund)
Button_Frame.pack(side="top", fill="x", padx=1, pady=1)
But1 = tk.Button(Button_Frame,  text="<<",    font="Helvetica 11", width=6, bd=3, borderwidth=3, command=Sektoren_Erster)
But2 = tk.Button(Button_Frame,  text="< -1G", font="Helvetica 11", width=5, bd=3, borderwidth=3, command=lambda: Sektoren_Weiter(-2048*16*32*32*32))
But3 = tk.Button(Button_Frame,  text="< -32M",font="Helvetica 11", width=5, bd=3, borderwidth=3, command=lambda: Sektoren_Weiter(-2048*16*32*32))
But4 = tk.Button(Button_Frame,  text="< -1M", font="Helvetica 11", width=5, bd=3, borderwidth=3, command=lambda: Sektoren_Weiter(-2048*16*32))
But5 = tk.Button(Button_Frame,  text="< -32K",font="Helvetica 11", width=5, bd=3, borderwidth=3, command=lambda: Sektoren_Weiter(-2048*16))
But6 = tk.Button(Button_Frame,  text="< -2K", font="Helvetica 11", width=5, bd=3, borderwidth=3, command=lambda: Sektoren_Weiter(-2048))
But7 = tk.Button(Button_Frame,  text="< -128",font="Helvetica 11", width=5, bd=3, borderwidth=3, command=lambda: Sektoren_Weiter(-128))
But8 = tk.Button(Button_Frame,  text="Sektor-Nr", font="Helvetica 11", width=16, bd=3, borderwidth=3, command=SektNum_Eingeben)
But9 = tk.Button(Button_Frame,  text="+128 >",font="Helvetica 11", width=5, bd=3, borderwidth=3, command=lambda: Sektoren_Weiter(+128))
But10 = tk.Button(Button_Frame, text="+2K >", font="Helvetica 11", width=5, bd=3, borderwidth=3, command=lambda: Sektoren_Weiter(+2048))
But11 = tk.Button(Button_Frame, text="+32K >",font="Helvetica 11", width=5, bd=3, borderwidth=3, command=lambda: Sektoren_Weiter(+2048*16))
But12 = tk.Button(Button_Frame, text="+1M >", font="Helvetica 11", width=5, bd=3, borderwidth=3, command=lambda: Sektoren_Weiter(+2048*16*32))
But13 = tk.Button(Button_Frame, text="+32M >",font="Helvetica 11", width=5, bd=3, borderwidth=3, command=lambda: Sektoren_Weiter(+2048*16*32*32))
But14 = tk.Button(Button_Frame, text="+1G >", font="Helvetica 11", width=5, bd=3, borderwidth=3, command=lambda: Sektoren_Weiter(+2048*16*32*32*32))
But15 = tk.Button(Button_Frame, text=">>",    font="Helvetica 11", width=6, bd=3, borderwidth=3, command=Sektoren_Letzter)

Navi_Button = [ But1, But2, But3, But4, But5, But6, But7, But8, But9, But10, But11, But12, But13, But14, But15 ]
tk.Label(Button_Frame, bg=Hintergrund).grid(row=1, column=1, padx=1)
for i in range (15):
    Navi_Button[i].grid(row=1, column=i+2, padx=2, pady=4)
Scroll_Balken = tk.Scrollbar(Master, width=20)
Haupt_Fenster = tk.Text(Master, width=148, height=50, padx=6, yscrollcommand = Scroll_Balken.set)
Statusleiste = tk.Label(Master, textvariable=StatusText, relief="sunken", anchor="w", font="Helvetica 11")
Haupt_Fenster.config(bg=Hintergrund, fg=Vordergrund, font="Consolas 10")
Scroll_Balken.config(command = Haupt_Fenster.yview)
Statusleiste.pack(side="bottom", fill="x", padx=2, pady=1)
Haupt_Fenster.pack(side="left", fill="y", padx=1, pady=1)
Scroll_Balken.pack(side="left", fill="y")

Haupt_Fenster.bind("<F1>", Hilfe_Partitionstypen)
Haupt_Fenster.bind("<Key-Up>", lambda event: Sektor_Zurueck())
Haupt_Fenster.bind("<Key-Down>", lambda event: Sektor_Vor())
Haupt_Fenster.bind("<Control-Key-s>", SektNum_Eingeben)
Haupt_Fenster.bind("<Control-Key-d>", Device_Auswaehlen)

##############################################################################################################

if os.environ["USER"] != "root":
    print("Keine Berechtigung - bitte mit sudo starten.")
    raise SystemExit()

Zeige_Sektorenblock()

Master.mainloop()

##############################################################################################################


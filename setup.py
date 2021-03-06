#! /bin/python3

import os
import subprocess
import sys
import tkinter as tk
from tkinter import messagebox
import time

# imporrt the standard to read and write config files
import configparser

#list of required modules
modules=list()
try:
    import vlc
except:
    modules.append("python-vlc")

master=None
# try:
#     import crontab
# except:
#     modules.append("python-crontab")

def createAutostart():
    '''
    create the auto start file gruene_signale.desktop in $HOME/.config/autostart/
    also create intermediate paths if the do not exist
    when the file already exists, nothing is done
    '''
    autostartfile = os.path.expanduser("~/.config/autostart/gruene_signale.desktop")
    whereami = os.path.dirname(os.path.realpath(__file__))
    contents = """[Desktop Entry]
Type=Application
Name=Green Signals Autostart
Comment=Starten der Slideshow von Gruene Signale
NoDisplay=false
Exec=sh -c 'cd %(path)s && /bin/python3 gruene_signale.py'
"""
    if os.path.isfile(autostartfile) == False:
        if os.path.exists(os.path.dirname(autostartfile)) == False:
            os.makedirs(os.path.dirname(autostartfile))
        file=open(autostartfile,"w")
        file.write(contents%{'path':whereami})
        file.close()

def removeAutostart():
    '''
    check if the auto start file exists, and if it does, remove it
    '''
    autostartfile = os.path.expanduser("~/.config/autostart/gruene_signale.desktop")
    if os.path.isfile(autostartfile) == True:
        os.remove(autostartfile)

def checkAutostartfile():
    '''
    check if the auto start file gruene_signale.desktop already exists
    returns True, if it does, False if not
    '''
    autostartfile = os.path.expanduser("~/.config/autostart/gruene_signale.desktop")
    return int(os.path.isfile(autostartfile))

def installModules():
    global modules
    failed=list()
    for module in modules:
        try:
            #subprocess.check_call(["sleep", "5"])
            subprocess.check_call([sys.executable, "-m", "pip", "install", module])
        except:
            print("install module %s failed" % module)
            failed.append(module)
    modules=failed

#the main window
try:
    master=tk.Tk()
except:
    if len(sys.argv)>1:
        # started from command line with arguments
        if "modinst" in sys.argv:
            installModules()
            print("Die Module wurden erfolgreich installiert.")
        if "autostart" in sys.argv:
            createAutostart()
            print("Das Autostart-Objekt wurde erstellt.")
        if "noautostart" in sys.argv:
            removeAutostart()
            print("Das Autostart-Objekt wurde entfernt.")
        
    else:
        print("Es ist ein Tcl-Fehler aufgetreten. Das Skript muss im Desktop-Modus gestartet werden.")
        print("""Folgende Kommandos sind erlaubt:
   modinst:     wenn notwendig werden fehlende Python Module installiert
   autostart:   Das Autostart-Objekt wird geschrieben
   noautostart: Das Autostart-Objekt wird entfernt

Die weiteren Enstellungen koennen in der Datei gruene-signal.conf angepasst werden.""")
    exit(0)

#init variables used in config file and some other places
doAutostart=tk.IntVar()
bild_dauer=tk.IntVar()
DEBUG_PREVIEW=tk.IntVar()
localPath=tk.StringVar()
remoteURL=tk.StringVar()
energyMode=tk.IntVar()
energyStart=tk.StringVar()
energyStop=tk.StringVar()


#when setup can't find the conf file, inited is set to True
inited = False
#URL for the Intro-Screens, use as default, if conf is inited
introURL="https://wolke.netzbegruenung.de/s/2TPGWN5FtWYy2d8/download"

#set "dirty" flag to False
#any change should set it to True, so we can ask on quit to save data
isDirty=False

class Popup(tk.Toplevel):
    """modal window requires a master"""
    def __init__(self, master, **kwargs):
        geo = '%(w)dx%(h)d+%(x)d+%(y)d' % {'x':master.winfo_x()+4,'y':master.winfo_y()+4,'w':master.winfo_width()-8,'h':master.winfo_height()-8}
        print(geo)
        tk.Toplevel.__init__(self, master, **kwargs)
        self.overrideredirect(True)
        self.geometry(geo) # set the position and size of the popup
        self.configure(bg="DarkSeaGreen1")

        lbl = tk.Label(self, text="Module werden installiert.",bg="DarkSeaGreen1")
        lbl.place(relx=.5, rely=.5, anchor='c')

        # The following commands keep the popup on top.
        # Remove these if you want a program with 2 responding windows.
        # These commands must be at the end of __init__
        self.transient(master) # set to be on top of the main window
        self.grab_set() # hijack all commands from the master (clicks on the main window are ignored)

def open_popup():
    if master != None:
        print("OPEN POPUP")
        master.popup = Popup(master)
        master.update()

def close_popup():
    if master != None:
        master.popup.destroy()
        master.update()

def installModulesGUI(i=0,event=None):
    global modules
    open_popup()
    installModules()
    close_popup()
    if len(modules)==0:
        master.installButton.configure(bg="pale green")
        master.installButton.configure(state='disabled')
        master.installButton.configure(text='bereits installiert.')

def validateTimeFields(input,newchar,action,name):
    if action == "focusout":
        if ":" in input:
            hour=int(input.split(":")[0])
            minute=int(input.split(":")[1])
            if hour < 0 or hour > 23 or minute < 0 or minute > 59:
                messagebox.showerror("Eingabefehler", "Bitte geben sie eine gueltige Uhrzeit ein oder die Anzahl der Stunden mit vorangestelltem -")
                master.nametowidget(name).focus()
                return False
            else:
                print(name)
                if ".start" in name:
                    energyStart.set("%(h)d:%(m)02d" % {'h':hour, 'm':minute})
                elif ".stop" in name:
                    energyStop.set("%(h)d:%(m)02d" % {'h':hour, 'm':minute})
                return True
    if newchar == "-" and len(input) < 2:
        setDirty()
        return True
    elif len(input)>0 and input[0] == "-" and newchar in "0123456789":
        setDirty()
        return True
    elif newchar not in '01234567890:.':
        return False
    if action != "forced":
        setDirty()
    return True;

def setDirty(action=None, ign=None):
    #this is called for buttons etc.
    global isDirty
    #print("setDirty() called", sys._getframe().f_back.f_code.co_name, "###", action, "###", ign)
    isDirty = True
    return True

def setEntryDirty(action=None, ign=None):
    #this gets called 
    global isDirty
    #print("setDirty() called", sys._getframe().f_back.f_code.co_name, "###", action, "###", ign)
    if action != None and int(action) >= 0:
        isDirty = True
    return True


def readConfig(configFile=None):
    global bild_dauer, DEBUG_PREVIEW, localPath, remoteURL, isDirty, inited
    global energyStart, energyStop, energyMode
    if configFile == None:
        configFile = os.path.dirname(os.path.realpath(__file__)) + os.sep + "gruene_signale.conf"
    if os.path.exists(configFile) == False:
        inited = True
    config = configparser.ConfigParser()
    config.read(configFile)
    #read bild - dauer
    try:
        bild_dauer.set(int(config.get('bilder', 'dauer')))
    except:
        bild_dauer.set(10)
        isDirty = True

    #read debug - preview
    try:
        val = config.get('debug', 'preview')
    except:
        val = "0"
    if val == "1":
        DEBUG_PREVIEW.set(1)

    #read pfad - lokal
    try:
        val = os.path.realpath(config.get('pfad', 'lokal'))
    except:
        val = os.path.dirname(os.path.realpath(__file__)) + os.sep + "slideshow"
    localPath.set(val)

    #try to read the remote URL, if not given, work offline
    try:
        val = config.get('pfad', 'remote')
        remoteURL.set(val)
    except:
        val = None
        remoteURL.set("")
    
    #read energ - mode
    try:
        energyMode.set(int(config.get('energy','mode')))
    except:
        energyMode.set(0)
    
    #read energy - start
    try:
        val = config.get('energy', 'start')
    except:
        val = ""
    energyStart.set(val)
    
    #read energy - stop
    try:
        val = config.get('energy', 'stop')
    except:
        val = ""
    energyStop.set(val)

def writeConfig(configFile=None):
    if configFile == None:
        configFile = os.path.dirname(os.path.realpath(__file__)) + os.sep + "gruene_signale.conf"
    config = configparser.ConfigParser()
    config.read(configFile)

    required_sections = ['bilder','filme','pfad','debug','energy']
    for sect in required_sections:
        if sect not in config.sections():
            config.add_section( sect )

    config.set('bilder','dauer',"%d" % bild_dauer.get())
    config.set('debug', 'preview',"%d" % DEBUG_PREVIEW.get())
    config.set('pfad', 'lokal',localPath.get().strip())
    config.set('pfad', 'remote',remoteURL.get().strip())
    config.set('energy', 'mode', "%d" % energyMode.get())
    config.set('energy', 'start', energyStart.get())
    config.set('energy', 'stop', energyStop.get())

    with open(configFile, 'w') as file:
        config.write(file)


def save():
    global isDirty,inited
    if isDirty == False:
        return;
    writeConfig()
    if checkAutostartfile() == 1 and doAutostart.get() == 0:
        removeAutostart()
    if checkAutostartfile() == 0 and doAutostart.get() == 1:
        createAutostart()
    isDirty=False
    inited=False

def quit():
    if isDirty == True:
        result = messagebox.askyesno("ungesicherte Daten","Sollen die Einstellungen vor dem Beenden gespeichert werden?")
        if result:
            save()
    master.destroy()
    exit(0)

def buildGUI_1():
    #add button or notification if Python modules (see above) needs to be installed
    row=tk.Frame(master,bd=1,relief=tk.SUNKEN)
    lab=tk.Label(row,text="Python Module",width=30,anchor='w')
    if len(modules) == 0:
        obj=tk.Button(row,text="bereits installiert",bg="pale green",state='disabled')
    else:
        obj=tk.Button(row,text="Installieren",command=installModulesGUI,fg="red")
    master.installButton = obj
    row.pack(side=tk.TOP,padx=dx,pady=dy,expand=tk.YES,fill=tk.X)
    lab.pack(side=tk.LEFT,pady=dy,padx=dx)
    obj.pack(side=tk.RIGHT,expand=tk.YES,fill=tk.X,padx=dx)
    
def buildGUI_2():
    #add autostart checkbox
    doAutostart.set(checkAutostartfile())
    row=tk.Frame(master,bd=1,relief=tk.SUNKEN)
    lab=tk.Label(row,text="Gruene Signale automatisch starten",width=30,anchor='w')
    obj=tk.Checkbutton(row,text="aktiv",variable=doAutostart,command=setDirty)
    row.pack(side=tk.TOP,padx=dx,pady=dy,expand=tk.YES,fill=tk.X)
    lab.pack(side=tk.LEFT,pady=dy,padx=dx)
    obj.pack(side=tk.RIGHT,expand=tk.YES,fill=tk.X,padx=dx)

def buildGUI_3():
    #add entry field for local path
    row=tk.Frame(master,bd=1,relief=tk.SUNKEN)
    lab=tk.Label(row,text="lokaler Pfad",width=30,anchor='w')
    obj=tk.Entry(row,textvariable=localPath,validate="key",validatecommand=(anyEntryCallback, '%d', '%P'))
    row.pack(side=tk.TOP,padx=dx,pady=dy,expand=tk.YES,fill=tk.X)
    lab.pack(side=tk.LEFT,pady=dy,padx=dx)
    obj.pack(side=tk.RIGHT,expand=tk.YES,fill=tk.X,padx=dx)

def buildGUI_4():
    #add entry field for remoteURL
    row=tk.Frame(master,bd=1,relief=tk.SUNKEN)
    lab=tk.Label(row,text="Remote-URL (wenn leer: Offline-Modus)",width=30,anchor='w')
    if inited == True:
        remoteURL.set(introURL)
    obj=tk.Entry(row,textvariable=remoteURL,validate="key",validatecommand=(anyEntryCallback, '%d','%P'))
    row.pack(side=tk.TOP,padx=dx,pady=dy,expand=tk.YES,fill=tk.X)
    lab.pack(side=tk.LEFT,pady=dy,padx=dx)
    obj.pack(side=tk.RIGHT,expand=tk.YES,fill=tk.X,padx=dx)

def buildGUI_5():
    #add scale widget for duration
    row=tk.Frame(master,bd=1,relief=tk.SUNKEN)
    lab=tk.Label(row,text="Anzeigedauer der Bilder (Sekunden)",width=30,anchor='w')
    obj=tk.Scale(row,from_=5,to=120,variable=bild_dauer,orient=tk.HORIZONTAL,command=setDirty)
    row.pack(side=tk.TOP,padx=dx,pady=dy,expand=tk.YES,fill=tk.X)
    lab.pack(side=tk.LEFT,pady=dy,padx=dx)
    obj.pack(side=tk.RIGHT,expand=tk.YES,fill=tk.X,padx=dx)

def buildGUI_6():
    #MARK: add controls for energy savings
    row1=tk.Frame(master,bd=1,relief=tk.SUNKEN)
    row1.pack(side=tk.TOP,padx=dx,pady=dy,expand=tk.YES,fill=tk.X)

    row2=tk.Frame(row1,bd=1,relief=tk.FLAT)
    row2.pack(side=tk.TOP,padx=dx,pady=dy,expand=tk.YES,fill=tk.X)

    row3=tk.Frame(row1,bd=1,relief=tk.FLAT)
    row3.pack(side=tk.TOP,padx=dx,pady=dy,expand=tk.YES,fill=tk.X)
    row4=tk.Frame(row1,bd=1,relief=tk.FLAT)
    row4.pack(side=tk.TOP,padx=dx,pady=dy,expand=tk.YES,fill=tk.X)

    lab=tk.Label(row2,text="Energiesparoptionen",width=30,anchor='w')
    obj0=tk.Radiobutton(row2,text="ohne",variable=energyMode,command=setDirty,value=0)
    obj1=tk.Radiobutton(row2,text="RasPi ausschalten",variable=energyMode,command=setDirty,value=1)
    obj2=tk.Radiobutton(row2,text="Monitor deaktivieren",variable=energyMode,command=setDirty,value=2)
    lab.pack(side=tk.LEFT,pady=dy,padx=dx)
    obj2.pack(side=tk.RIGHT,expand=tk.YES,fill=tk.X,padx=dx)
    obj1.pack(side=tk.RIGHT,expand=tk.YES,fill=tk.X,padx=dx)
    obj0.pack(side=tk.RIGHT,expand=tk.YES,fill=tk.X,padx=dx)

    lab=tk.Label(row3,text="",width=30,anchor='w')
    lab.pack(side=tk.LEFT,pady=dy,padx=dx)
    lab=tk.Label(row3,text="um",width=3,anchor='w')
    lab.pack(side=tk.LEFT,pady=dy,padx=dx)
    obj1=tk.Entry(row3,name="start",textvariable=energyStart,validate="all",validatecommand=(timeEntryCallback, '%P','%S', "%V", "%W"))
    obj1.pack(side=tk.LEFT,fill=tk.X,padx=dx)

    lab=tk.Label(row3,text="bis",width=3,anchor='w')
    lab.pack(side=tk.LEFT,pady=dy,padx=dx)
    obj2=tk.Entry(row3,name="stop",textvariable=energyStop,validate="all",validatecommand=(timeEntryCallback, '%P', '%S', "%V", "%W"))
    obj2.pack(side=tk.LEFT,fill=tk.X,padx=dx)
    
def buildGUI_7():
    #add checkbox for Debug Preview Mode
    row=tk.Frame(master,bd=1,relief=tk.SUNKEN)
    lab=tk.Label(row,text="Debug Preview Modus",width=30,anchor='w')
    obj=tk.Checkbutton(row,text="aktiv",variable=DEBUG_PREVIEW,command=setDirty)
    row.pack(side=tk.TOP,padx=dx,pady=dy,expand=tk.YES,fill=tk.X)
    lab.pack(side=tk.LEFT,pady=dy,padx=dx)
    obj.pack(side=tk.RIGHT,expand=tk.YES,fill=tk.X,padx=dx)

def buildGUI_8():
    #add buttons
    row=tk.Frame(master)
    saveButton=tk.Button(row,text="Speichern",command=save,pady=4,padx=dx)
    saveButton.pack(side=tk.LEFT,pady=dy,padx=dx)
    quitButton=tk.Button(row,text="Beenden",command=quit,pady=4,padx=dx)
    quitButton.pack(side=tk.RIGHT,pady=dy,padx=dx)
    row.pack(side=tk.BOTTOM)

def buildGUI():
    buildGUI_1()
    buildGUI_2()
    buildGUI_3()
    buildGUI_4()
    buildGUI_5()
    buildGUI_6()
    buildGUI_7()
    buildGUI_8()
    
    
readConfig()

master.minsize(600,300)
master.geometry("800x450+560+300")
master.title("Einstellungen: Gruene Signale")
master.option_add('*Dialog.msg.font', 'System 10')

#register callbacks for entry fields
timeEntryCallback = master.register(validateTimeFields)
anyEntryCallback = master.register(setEntryDirty)

#fixed value for pady and padx used by pack() function
dy=2
dx=4

buildGUI()
master.mainloop()

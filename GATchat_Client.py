#! /usr/bin/python

#------------------------------- Différents modules ------------------------------------------------------------------------------------------#

import socket                          # Permet la connexion entre Client et Serveur.
import sys                             # Permet d'utiliser les fonctions systèmes.
import threading                      # Permet d'utiliser plusieurs taches en parrallèle
import time                           # Donne des indications sur le temps ( date / heure ).
import os                              # Permet d'utiliser des fonctions shell ( mkdir ... ).
import platform                       # Reconnait l'environnement (Windows / ubuntu / Mac ... )
import webbrowser
from tkinter import *               # Permet de créer une interface graphique.
from tkinter import ttk
from tkinter.messagebox import * # boîte de dialogue

#---------------------------------------------- Différentes classes --------------------------------------------------------------------------#

# Définitions des classes pour gérer l'émission de messages,
# pour gérer la réception .

def repertory_stock():
    """Cette fonction crée le dossier pour stocker les logs avec les fichiers qui serviront à enregistrer les logs"""
    type_os = platform.system()
    if type_os == "Linux":
        now = time.localtime()
        if not os.path.exists("Log_client/"):
            os.mkdir("Log_client/")
            if not os.path.exists("Log_client/{0}".format(str(now.tm_year))):
                os.mkdir("Log_client/{0}".format(str(now.tm_year)))            
                for i in range(12):
                    if not os.path.exists("Log_client/{0}/{1}".format(str(now.tm_year), str(i+1))):
                        os.mkdir("Log_client/{0}/{1}".format(str(now.tm_year), str(i +1)))
                        for k in range(31):                    
                            if not os.path.isfile("Log_client/{0}/{1}/logdu{2}.txt".format(str(now.tm_year), str(i+1), str(k+1))):
                                logday = open("Log_client/{0}/{1}/logdu{2}.txt".format(str(now.tm_year), str(i+1), str(k+1)), 'w')
                                logday.close()
    else:
        now = time.localtime()
        if not os.path.exists("Log_client"):
            os.mkdir("Log_client")
            if not os.path.exists("Log_client\\{0}".format(str(now.tm_year))):
                os.mkdir("Log_client\\{0}".format(str(now.tm_year)))
                for i in range(12):
                    if not os.path.exists("Log_client\\{0}\\{1}".format(str(now.tm_year), str(i+1))):
                        os.mkdir("Log_client\\{0}\\{1}".format(str(now.tm_year), str(i +1)))                 
                        for k in range(31):
                            if not os.path.isfile("Log_client\\{0}\\{1}\\logdu{2}.txt".format(str(now.tm_year), str(i+1), str(k+1))):
                                logday = open("Log_client\\{0}\\{1}\\logdu{2}.txt".format(str(now.tm_year), str(i+1), str(k+1)), 'w')
                                logday.close()
                
def copylog(messagefromclient):
    """Cette fonction enregistre le message reçu dans le fichier du jour correspondant avec l'heure de reception"""
    now = time.localtime()
    type_os = platform.system()
    if type_os == "Linux":
        log = open("Log_client/{0}/{1}/logdu{2}.txt".format(str(now.tm_year), str(now.tm_mon), str(now.tm_mday)), 'a')
        log.write('{0}:{1}:{2} {3}\n'.format(str(now.tm_hour), str(now.tm_min), str(now.tm_sec), messagefromclient))
    else:
        log = open("Log_client\\{0}\\{1}\\logdu{2}.txt".format(str(now.tm_year), str(now.tm_mon), str(now.tm_mday)), 'a')
        log.write('{0}:{1}:{2} {3}\n'.format(str(now.tm_hour), str(now.tm_min), str(now.tm_sec), messagefromclient))
    log.close()

class ThreadReception(threading.Thread):
    """objet thread gérant la réception des messages"""
    def __init__(self, conn, zone_mess, fenetre, aff_users):
        threading.Thread.__init__(self)
        self.connexion = conn # réf. du socket de connexion
        self.message_recu = ""
        self.zone_mess = zone_mess
        self.aff_users = aff_users
    def run(self):
        global deco_prog
        global ferm_prog
        while 1:
            now = time.localtime()
            self.message_recu = self.connexion.recv(1024).decode("Utf8")
            verif_mess = self.message_recu.split("kjergGKEZJZEN_çà-è_à)-è42112") # On split pour vérifier que c'est la véritable liste selon le code fournit
                                                                                 # par le serveur
            
            if not self.message_recu or self.message_recu == "/quit":
                self.connexion.send(self.message_recu.encode("Utf8"))
                break
            elif len(verif_mess) > 1:
                self.aff_users.config(state = NORMAL)
                self.aff_users.delete(1.0, END)
                self.aff_users.insert(END, "Users connectés :\n")
                self.aff_users.insert(END, verif_mess[1])
                self.aff_users.config(state = DISABLED)
            else:
                copylog(self.message_recu)
                self.message_recu_mod = self.modifmessage(self.message_recu)
                
                self.zone_mess.config(state = NORMAL)
                self.message_recu_heure = "{0}:{1}:{2} ".format(now.tm_hour, now.tm_min, now.tm_sec)
                
                self.zone_mess.insert(END, "\n" + self.message_recu_heure, "vert")
                self.zone_mess.insert(END, "<" + self.message_recu_mod[0] + "> ", "bleu")
                self.zone_mess.insert(END, self.message_recu_mod[1])
                self.zone_mess.yview_moveto(1.0) # Permet d'actualiser la position de la scrollbar à chaque nouveau message
                self.zone_mess.config(state = DISABLED)
            
        print("Client arrêté. Connexion interrompue.")
        self.connexion.close()
        if ferm_prog == False and deco_prog == False:
            self.zone_mess.config(state = NORMAL)
            self.zone_mess.insert(END, "\nLa connexion a été interrompue. Veuillez vous reconnecter.")
            self.zone_mess.config(state = DISABLED)
            test_reco=askyesno("Connexion perdue", "Voulez-vous vous reconnecter ?")
            
            if test_reco == True:
                fenetre_prin.quit()
            else:
                deco_prog = True
                fenetre_chat.deco.destroy()
                fenetre_chat.zone_texte.destroy()
                fenetre_chat.bouton_envoi.destroy()
                fenetre_chat.aff_users_co.destroy()
                fenetre_prin.quit()
    
    def modifmessage(self, mess):
        """Fonction qui sépare le message en 3 parties, l'heure, le pseudo et le message"""
        pseudo = mess.split("<")
        pseudo = pseudo[1]
        pseudo = pseudo.split(">")
        pseudo = pseudo[0]
        
        message = mess.split("> ")
        message_str = ""
        k = 1
        for loop in range(len(message)-1):
            if len(message) > 2 and message[k] == "" and (k == 1 or (k > 1 and k < len(message)-1)):
                message_str = message_str + message[k] + "> "
            elif len(message) > 2 and message[k] != ""  and k < len(message)-1:
                message_str = message_str + message[k] + "> "
            else: 
                message_str = message_str + message[k]
            k += 1
        
        mess_modifie = [pseudo, message_str]
        
        return mess_modifie
        
        
class FenetrePseudo():
    """objet tkinter qui est une fenêtre demandant le pseudo"""
    def __init__(self, fenetre_prin):
        fenetre_prin.minsize(width = 300, height = 50)
        
        self.frame_pseudo = ttk.Frame(fenetre_prin, padding=(5,5,5,5))
        self.frame_pseudo.grid(row = 0, column = 0, sticky = (N, S, W, E))
        
        self.pseudo_message = ttk.Label(self.frame_pseudo, text = "Choisis ton pseudo :")
        self.pseudo_message.grid(row = 0, column = 0, columnspan = 2)

        self.barre_texte = ttk.Entry(self.frame_pseudo)
        self.barre_texte.insert(INSERT, self.stock_pseudo())
        self.barre_texte.bind("<Return>", self.pseudo_envoi)
        self.barre_texte.grid(row = 1, column = 0, sticky = (W, E, S))
        self.barre_texte.focus()
        
        self.bouton_pseudo = ttk.Button(self.frame_pseudo, text = "Envoi")
        self.bouton_pseudo.bind("<Button-1>", self.pseudo_envoi) 
        self.bouton_pseudo.grid(row = 1, column = 1, sticky = (W, E, S))

        self.frame_pseudo.rowconfigure(0, weight=1)
        self.frame_pseudo.rowconfigure(1, weight=100)
        self.frame_pseudo.columnconfigure(0, weight=100)
        self.frame_pseudo.columnconfigure(1, weight=1)
        
        self.mon_pseudo = ""
        
    def pseudo_envoi(self, event):
        pseudo_valide = True
        self.mon_pseudo = self.barre_texte.get()
        
        for caractere in self.mon_pseudo: # Vérification de la présence de '<' et de '>' pour pas interférer dans le sytsème de couleur !
            if caractere == ">" or caractere == "<":
                pseudo_valide = False
                
        if pseudo_valide == True and len(self.mon_pseudo) <= 16: # Vérification de la longueur du pseudo pour pas d'abus sur le chat
            self.barre_texte.delete(0, END)
            connexion.send(self.mon_pseudo.encode("Utf-8"))
            check_pseudo = connexion.recv(1024).decode("Utf-8")
            if check_pseudo == "again":
                showwarning("Pseudonyme","Pseudonyme déjà utilisé ! :/")
            else:
                fenetre_prin.quit()
            fichier_pseudo = open("memoire_pseudo.txt", 'w')
            fichier_pseudo.write(self.mon_pseudo)
            fichier_pseudo.close()
        else:
            showwarning("Pseudonyme","Pseudonyme trop long (16 max) ou caractères interdits ('>' ou '<') !")

    def stock_pseudo(self):
        fichier_pseudo = open("memoire_pseudo.txt", 'r')
        return fichier_pseudo.readline()
        
class FenetreChat():
    """Classe qui va gérer l'interface où l'on va recevoir les messages et les envoyer"""
    def __init__(self, fenetre_prin, conn):
        fenetre_prin.minsize(width = 950, height = 450)
        
        self.frame = ttk.Frame(fenetre_prin, padding=(5, 5, 5, 5))
        self.frame.grid(row = 0, column = 0, sticky=(N, S, E, W))
        
        self.connexion = conn # réf. du socket de connexion
        self.message_recu = ""
        
        self.scrollbar = ttk.Scrollbar(self.frame)
        self.scrollbar.grid(row = 0, column = 1, rowspan = 2, sticky=(N, S, E), pady = 5)
        
        self.zone_mess = Text(self.frame, background = 'ghost white', yscrollcommand = self.scrollbar.set)
        self.zone_mess.grid(row = 0, column = 0, rowspan = 2, sticky=(N, S, E, W), pady = 5)
        self.zone_mess.insert(END, "Bienvenue sur le serveur de chat GATchat 1.0 !")
        self.zone_mess.config(state = DISABLED)
        self.zone_mess.tag_config("vert", foreground = "green")
        self.zone_mess.tag_config("bleu", foreground = "blue")
        
        
        self.scrollbar.config(command = self.zone_mess.yview)
        
        self.zone_texte = ttk.Entry(self.frame)
        self.zone_texte.bind("<Return>", self.SendMess)
        self.zone_texte.grid(row = 2, column = 0, columnspan = 2, sticky=(E, W, S), padx = 5, pady = 5)
        self.zone_texte.focus()
        
        self.bouton_envoi = ttk.Button(self.frame, text = "Envoi")
        self.bouton_envoi.bind("<Button-1>", self.SendMess)
        self.bouton_envoi.grid(row = 2, column = 2, sticky = (W, E, S), padx = 5, pady = 5)

        self.histo = ttk.Button(self.frame, text="Historique")
        self.histo.bind("<Button-1>", self.open_hist)
        self.histo.grid(row = 0, column = 2, sticky = (N, W, E), padx = 5, pady = 5)
        
        self.deco = ttk.Button(self.frame, text="Déconnexion")
        self.deco.bind("<Button-1>", self.deconnexion)
        self.deco.grid(row = 2, column = 3, sticky = (W, E, S), padx = 5, pady = 5)

        self.aff_users_co = Text(self.frame, width = 7, height=5)
        self.aff_users_co.grid(row = 1, column = 2, columnspan = 2, sticky = (N, S, W, E), padx = 5, pady = 5)
        self.aff_users_co.insert(END, "Users connectés :\n")
        self.aff_users_co.config(state = DISABLED)
        
        self.frame.columnconfigure(0, weight=100)
        self.frame.columnconfigure(1, weight=1)
        self.frame.columnconfigure(2, weight=10)
        self.frame.columnconfigure(3, weight=10)
        self.frame.rowconfigure(0, weight=1)
        self.frame.rowconfigure(1, weight=100)
        self.frame.rowconfigure(2, weight=1)
        
        self.th_R = ThreadReception(self.connexion, self.zone_mess, fenetre_prin, self.aff_users_co)
        self.th_R.start()

        self.message_emis = ""
        
    def open_hist(self, event):
        now = time.localtime()
        type_os = platform.system()
        if type_os == "Windows":
            webbrowser.open("Log_client\\{0}\\{1}\\logdu{2}.txt".format(str(now.tm_year), str(now.tm_mon), str(now.tm_mday)))
        else:
            webbrowser.open("Log_client/{0}/{1}/logdu{2}.txt".format(str(now.tm_year), str(now.tm_mon), str(now.tm_mday)))
	    
        
    def deconnexion(self, event):
        global deco_prog
        connexion.send("/quit".encode("Utf-8"))
        deco_prog = True
        fenetre_chat.deco.destroy()
        fenetre_chat.zone_texte.destroy()
        fenetre_chat.bouton_envoi.destroy()
        fenetre_chat.aff_users_co.destroy()
        fenetre_chat.zone_mess.config(state = NORMAL)
        fenetre_chat.zone_mess.insert(END, "\nVous vous êtes déconnecté(e), vous avez toujours accès à l'historique des conversations. Vous pouvez fermer le programme.\nMerci d'utiliser GATchat !")
        fenetre_chat.zone_mess.config(state = DISABLED)
        copylog("Déconnexion du serveur")
        
    def SendMess(self, event):
        self.message_emis = self.zone_texte.get()
        self.connexion.send(self.message_emis.encode("Utf8"))
        self.zone_texte.delete(0, END)
        self.zone_texte.focus()
        
        
        
#------------------------- Programme principal -----------------------------------------------------------

hote = 'gatchat.no-ip.org'
port = 45000

repertory_stock() # Lancement création des dossiers nécessaires pour logs
deco_prog = False
ferm_prog = False



#-------------------------- Interface graphique -------------------------------------------------------------#

# Fenetre pour pseudo

def Fermeture():
    global ferm_prog
    global deco_prog
    ferm_prog = True
    if deco_prog == False:
        connexion.send("/quit".encode("Utf-8"))
        deco_prog = True
        fenetre_prin.quit()
    else:
        fenetre_prin.quit()
    copylog("Déconnexion du serveur")



while 1: # Boucle principale qui gère les reconnexions.
    connexion = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    fenetre_prin = Tk() # Fenêtre principale du chat !
    fenetre_prin.title('GAT Chat 1.0 Alpha.')
    fenetre_prin.columnconfigure(0, weight=1)
    fenetre_prin.rowconfigure(0, weight=1)
    
    try:
        connexion.connect((hote, port)) # Essai de connexion au serveur
    except socket.error:
        print("La connexion a échoué. Tentative de connexion.")
        if askyesno("Connexion perdue", "Voulez-vous vous reconnecter ?"): # Permet si la réponse et oui de revenir au début et recréer un connexion
            fenetre_prin.destroy() # Suppression de la fenêtre pour éviter de dupliquer la fenêtre
            time.sleep(2)
            continue
        else: # Si la réponse est "non", on quitte le programme
            ferm_prog = True
            break
    ban_or_not = connexion.recv(1024).decode("Utf-8")
    if ban_or_not == "ban":
        showwarning("Ban", "Vous avez été bannis de ce serveur !")
        ferm_prog = True
        connexion.close()
        break
    print("Connexion établie avec le serveur.")
    copylog("Connexion établie avec le serveur.")
    
    #showinfo("Pseudonyme", "Vous devez entrez votre pseudo !")
    fenetre_pseudo = FenetrePseudo(fenetre_prin) # Frame qui permet la gestion du pseudo
    fenetre_prin.mainloop()
    fenetre_pseudo.frame_pseudo.destroy()

    fenetre_chat = FenetreChat(fenetre_prin, connexion) # Frame qui permet l'émission et la réception de messages

    fenetre_prin.protocol("WM_DELETE_WINDOW", Fermeture) # Modifie les conditions de fermetures de la feneêtre avec la croix rouge.
    
    fenetre_prin.mainloop() # Boucle principale pendant le temps de l'émission des messages.
    
    if deco_prog == True: # Permet de vérifier si c'est la connexion qui est perdue ou si l'utilisateur a demandé la déconnexion
        break
    fenetre_prin.destroy()

if ferm_prog == False: # Remet en boucle principale la fenêtre si c'est juste une déconnexion.
    fenetre_prin.mainloop()

fenetre_prin.destroy() # Suppression de la fenêtre principale à la fin du programme.

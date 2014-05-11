#! /usr/bin/python

#------------------------------- Différents modules ------------------------------------------------------------------------------------------#

import socket
import sys
import threading
import time
import os
import platform
import select
#---------------------------------------------- Différentes classes --------------------------------------------------------------------------#

def repertory_stock():
    """Cette fonction crée le dossier pour stocker les logs avec les fichiers qui serviront à enregistrer les logs"""
    type_os = platform.system()
    if type_os == "Linux":
        now = time.localtime()
        if not os.path.exists("Log_serveur/"):
            os.mkdir("Log_serveur/")
            if not os.path.exists("Log_serveur/{0}".format(str(now.tm_year))):
                os.mkdir("Log_serveur/{0}".format(str(now.tm_year)))
                for i in range(12):
                    if not os.path.exists("Log_serveur/{0}/{1}".format(str(now.tm_year), str(i+1))):
                        os.mkdir("Log_serveur/{0}/{1}".format(str(now.tm_year), str(i +1)))
                        for k in range(31):
                            if not os.path.isfile("Log_serveur/{0}/{1}/logdu{2}.txt".format(str(now.tm_year), str(i+1), str(k+1))):
                                logday = open("Log_serveur/{0}/{1}/logdu{2}.txt".format(str(now.tm_year), str(i+1), str(k+1)), 'w')
                                logday.close()
    else:
        now = time.localtime()
        if not os.path.exists("Log_serveur"):
            os.mkdir("Log_serveur")
            if not os.path.exists("Log_serveur\\{0}".format(str(now.tm_year))):
                os.mkdir("Log_serveur\\{0}".format(str(now.tm_year)))
                for i in range(12):
                    if not os.path.exists("Log_serveur\\{0}\\{1}".format(str(now.tm_year), str(i+1))):
                        os.mkdir("Log_serveur\\{0}\\{1}".format(str(now.tm_year), str(i +1)))
                        for k in range(31):
                            if not os.path.isfile("Log_serveur\\{0}\\{1}\\logdu{2}.txt".format(str(now.tm_year), str(i+1), str(k+1))):
                                logday = open("Log_serveur\\{0}\\{1}\\logdu{2}.txt".format(str(now.tm_year), str(i+1), str(k+1)), 'w')
                                logday.close()

def copylog(pseudo, messagefromclient):
    """Cette fonction enregistre le message reçu dans le fichier du jour correspondant avec l'heure de reception"""
    now = time.localtime()
    type_os = platform.system()
    if type_os == "Linux":
        log = open("Log_serveur/{0}/{1}/logdu{2}.txt".format(str(now.tm_year), str(now.tm_mon), str(now.tm_mday)), 'a')
        log.write('{0}:{1}:{2} <{3}> {4}\n'.format(str(now.tm_hour), str(now.tm_min), str(now.tm_sec), pseudo, messagefromclient))
    else:
        log = open("Log_serveur\\{0}\\{1}\\logdu{2}.txt".format(str(now.tm_year), str(now.tm_mon), str(now.tm_mday)), 'a')
        log.write('{0}:{1}:{2} <{3}> {4}\n'.format(str(now.tm_hour), str(now.tm_min), str(now.tm_sec), pseudo, messagefromclient))
    log.close()

def liste_users(utilisateurs_conn):
    """Fonction qui permet de retourner la liste des utilisateurs connectés"""
    liste_envoi = "kjergGKEZJZEN_çà-è_à)-è42112" # Utilisation d'un certain code pour que le client puisse filtrer ce message en tant que liste des utilisateurs connectés
    for utilisateur in utilisateurs_conn:
        liste_envoi = liste_envoi + "* " + utilisateur + "\n"
    for utilisateur in utilisateurs_conn:
        utilisateurs_conn[utilisateur].send(liste_envoi.encode("Utf-8"))    
    
# Définitions des classes pour gérer la connexion client,
# pour gérer des commandes.

class ThreadClient(threading.Thread):
    '''Dérivation d'un objet thread pour gérer la connexion avec un client'''
    def __init__(self, connexion, pseudo):
        """Fonction qui construit la classe héritant du module Thread"""
        threading.Thread.__init__(self)
        self.connexion = connexion
        self.pseudo = pseudo

    def run(self):
        """Fonction qui sert à définir le code à lancer en parallèle"""
        # Dialogue avec le client
        time.sleep(1) # Attente de la connexion de l'utilisateur, pour ne pas avoir d'erreur
        liste_users(utilisateurs_conn) # Envoi de la liste des utilisateurs à tout les utilisateurs connectés
        while 1: # Attente permanente du message et si c'est commande /quit, on sort de boucle et déconnexion de l'utilisateur
            msgClient = self.connexion.recv(1024).decode("Utf8")
            if msgClient == "/quit":
                break # Permet de sortir de la boucle de réception des messages en cas de /quit
            message = "<{0}> {1}".format(self.pseudo, msgClient) 
            copylog(self.pseudo, msgClient)
            now = time.localtime()
            print("{0}:{1}:{2}".format(str(now.tm_hour), str(now.tm_min), str(now.tm_sec)), message)
            for utilisateur in utilisateurs_conn: # Faire suivre le message à l'utilisateur et à tous les autres clients :
                utilisateurs_conn[utilisateur].send(message.encode("Utf8"))

        # Fermeture de la connexion :
        self.connexion.close() # Couper la connexion côté serveur
        time.sleep(0.5)           # Timer pour attendre l'envoi des messages de fin à tous les utilisateurs pour le supprimer du dictionnaire sinon erreur.
        del utilisateurs_conn[self.pseudo]        # Supprimer son entrée dans le dictionnaire par rapport à son pseudo
        del registre_adresses_users[self.pseudo] # Utilisation
        print("Client {0} déconnecté.".format(self.pseudo))
        copylog("Serveur", "Client {0} déconnecté.".format(self.pseudo))
        if comm_kick == False and comm_stop == False:
            for utilisateur in utilisateurs_conn:
                utilisateurs_conn[utilisateur].send("<Serveur> {0} s'est déconnecté(e).".format(self.pseudo).encode("Utf8"))
        time.sleep(0.5)
        liste_users(utilisateurs_conn)
        

class Commandes(threading.Thread):
    """ Dérivation objet thread qui gére les commandes côté serveur """
    def __init__(self):
        """Fonction qui construit la classe héritant du module Thread"""
        threading.Thread.__init__(self)

    def run(self):
        """Fonction qui sert à définir le code à lancer en parallèle"""
        global registre_adresses_users # Permet d'avoir accès au variable définit dans le code principal
        global comm_kick
        global comm_stop
        
        while 1: # Attente permanente de commande avec test pour savoir laquelle est-ce
            commande = input()

        # Commande pour kicker toutes les personnes sur le server ( utile pour les MaJ ).

            if commande == "/kickall": # Commande qui déconnecte tous les utilsateurs
                comm_kick = True
                for utilisateur in utilisateurs_conn: # Envoi à tous les utilisateurs connectés '/quit' pour sortir de la boucle côté client
                    utilisateurs_conn[utilisateur].send("/quit".encode("Utf8"))
                time.sleep(2)
                print("Tous les utilisateurs ont été kickés")

        # Commande pour stopper le server.

            if commande == "/stop": # En plus de déconnecter tout le monde, arrêt du serveur grâce à une simulation de connexion pour sortir boucle principale
                comm_stop = True
                socket_fin = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # On crée une connexion en local dans le but de sortir de la boucle principale de réception des connexions
                socket_fin.connect(('127.0.0.1', Port))
                socket_fin.send("Aegklerg1556442".encode("Utf-8")) # Envoi d'un pseudo difficile à trouver pour ne pas couper le serveur intentionnellement
                time.sleep(0.5)
                socket_fin.close()
                time.sleep(1)
                for utilisateur in utilisateurs_conn:
                    utilisateurs_conn[utilisateur].send("/quit".encode("Utf8"))
                time.sleep(2)
                print("Tous les utilisateurs ont été kickés et le serveur va s'arrêter !")
                copylog("Serveur", "Fermeture du serveur.")
                break

        # Commande pour bannir un utilisateur du server.
            if commande == "/ban":
                pseudo_ban = input("Personne à ban : ")
                try:
                    for user in registre_adresses_users:
                        if user == pseudo_ban:
                            if registre_adresses_users[user] == "127.0.0.1":
                                print("On ne peut ban l'utilisateur local")
                                break
                            adresse_ban = registre_adresses_users[user]
                            black_list = open("blacklist.txt", "a")
                            black_list.write(adresse_ban + "\n")
                            black_list.close()
                            utilisateurs_conn[user].send("/quit".encode("Utf8"))
                            print("L'utilisateur {0} a bien été banni !".format(pseudo_ban))
                            break
                    print("Utilisateur {0} introuvable".format(pseudo_ban))
                except:
                    print("Aucun utilisateur n'est connecté !")


#-------------------------- Programme principal -------------------------------------------------------------#

print("    Serveur chat gérant plusieurs connexions simultanées\n")

# Initialisation du serveur - Mise en place du socket :

Hote = ''
Port = 45000
socketServeur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socketServeur.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Permet de réutiliser le socket tout de suite après fermeture

# Essai de liaison avec l'adresse et le port
try:
    socketServeur.bind((Hote, Port))
    print("Serveur prêt, en attente d'utilisateurs ...\n")
except socket.error:
    print("La liaison du socket à l'adresse choisie a échoué.")
    sys.exit()

socketServeur.listen(5)

utilisateurs_conn = {}                # dictionnaire des utilisateurs connectés par pseudo avec la référence du socket connexion_avec_client
registre_adresses_users = {} # Dictionnaire qui ne conserve que l'adresse IP de l'utilisateur 
comm = Commandes()
comm.start()        # Lancement thread qui gére les commandes

repertory_stock() # Lancement création des dossiers nécessaires pour les logs
check_pseudo = "again" # Variable initialisation pour vérification de pseudos
pseudo = "" # Utilisation d'un pseudo vide si l'utilisateur n'a pas entré de pseudo
ban_or_not = False # Initialisation 
comm_kick = False
comm_stop = False
# Boucle qui gère toutes les connexions entrantes :

copylog("Serveur", "Mise en route du serveur !")
while 1:
    connexion_avec_client, adresse_port = socketServeur.accept() # Retourne la référence du socket ainsi que l'adresse et le port de l'utilisateur

    black_list = open("blacklist.txt", "r")
    black_list.seek(0)

    for ip in black_list: # On vérifie si l'adresse de la connexion entrante est dans la blacklist auquel cas, on met la variable sur True
        if ip == (adresse_port[0] + "\n"):
            ban_or_not = True

    black_list.close()

    if ban_or_not == True: # Si la variable est sur True on envoie à la connexion qu'elle est bannit
        connexion_avec_client.send("ban".encode("Utf-8"))
        connexion_avec_client.close()
        ban_or_not = False # On remet la variable sur False pour les prochaines connexions et on revient au début de la boucle
        continue

    else:
        connexion_avec_client.send("autorisé".encode("Utf-8")) # Autorisation de se connecter

    while check_pseudo == "again": # Boucle vérif. pseudos
        check_lecture, wlist, xlist = select.select([connexion_avec_client], [], [], 30) # Permet d'attendre une réponse du client et s'il n'en donne pas avant 30 secondes, il est kické
        if len(check_lecture) > 0: # check_lecture est la liste des sockets qui ont envoyé une réponse donc si il n'y en a pas, on ne demande pas le pseudo
            try: # Test si pas de pseudo on break
                pseudo = connexion_avec_client.recv(1024).decode("Utf-8") #Réception du pseudo
            except:
                break
        else:
            connexion_avec_client.close()
            pseudo = ""
            break
        check_pseudo = "good" # Changement état pour sortir de la boucle si pseudo existe pas
        if pseudo == "Aegklerg1556442": # Sert pour /stop, c'est le pseudo de la connexion entrante qui permet la sortie de cette boucle
            break
        for name in utilisateurs_conn: # Parcours de la liste des pseudos et on remet "again" pour relancer la boucle si pseudo présent
            if name == pseudo or name == "Serveur":
                check_pseudo = "again"

        connexion_avec_client.send(check_pseudo.encode("Utf-8")) # Renvoie de "again" ou de "good" au client pour sortir ou nom de la boucle lui aussi
    check_pseudo = "again" # Quand la vérification est terminée on remet sur again pour relancer la boucle à la prochaine connexion
    if pseudo == "": # Test après le break pour vérifier si la personne n'a pas rentré de pseudo suite à sa connexion et dans ce cas on se remet en attente de connexion
        continue
    if pseudo == "Aegklerg1556442": # Sert pour /stop, c'est le pseudo de la connexion entrante qui permet la sortie de cette boucle
        if utilisateurs_conn == {}:
            break
        else:
            for utilisateur in utilisateurs_conn:
                utilisateurs_conn[utilisateur].send("<Serveur> Vous avez été déconnecté(e), le serveur s'est arrêté.".encode("Utf-8"))
            connexion_avec_client.close()
            break

    for utilisateur in utilisateurs_conn:
        utilisateurs_conn[utilisateur].send("<Serveur> {0} est maintenant connecté(e)".format(pseudo).encode("Utf-8"))
    thread_client = ThreadClient(connexion_avec_client, pseudo)
    thread_client.start() # Créer un nouvel objet thread pour gérer la connexion :
    utilisateurs_conn[pseudo] = connexion_avec_client # Entrée de la connexion dans le dictionnaire avec son pseudo comme clé
    registre_adresses_users[pseudo] = adresse_port[0] #Entrée de l'adresse de l'utilisateur dans le dictionnaire pour pouvoir le ban si besoin
    info_connexion = "Client {0} connecté, adresse IP {1}, port {2}.".format(pseudo, adresse_port[0], adresse_port[1])
    print(info_connexion)
    copylog("Serveur", info_connexion)
    msg ="<Serveur> Vous êtes connecté(e) au serveur de chat GATchat."
    connexion_avec_client.send(msg.encode("Utf8"))

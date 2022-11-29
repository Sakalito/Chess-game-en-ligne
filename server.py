import socket
from _thread import *
from board import Board
import pickle
import time
#serveur
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server = "localhost"
port = 5555
server_ip = socket.gethostbyname(server)
try:
    s.bind((server, port))
except socket.error as e:
    print(str(e))
#ecoute du serveur
s.listen()
print("Attente de connexions ...")
#initialisation des connexions client
connections = 0
#initialisation du plateau
games = {0:Board(8, 8)}
# spectateurs
spectartor_ids = [] 
specs = 0
def read_specs():
    global spectartor_ids
    spectartor_ids = []
    try:
        with open("specs.txt", "r") as f:
            for line in f:
                spectartor_ids.append(line.strip())
    except:
        print("Pas de spectateurs...")
        open("specs.txt", "w")
#thread 
def threaded_client(conn, game, spec=False):
    global pos, games, currentId, connections, specs
    #si pas de joueur > créer joueur et jouer
    if not spec:
        name = None
        bo = games[game]
        if connections % 2 == 0:
            currentId = "w"
        else:
            currentId = "b"
        bo.start_user = currentId
        # Pickle l'objet et envoie au serveur
        data_string = pickle.dumps(bo)
        #si ts les joueurs sont là, lancer le timer sinon, incrémenter de 1 le nombre de connecté
        if currentId == "b":
            bo.ready = True
            bo.startTime = time.time()
        conn.send(data_string)
        connections += 1
        #boucle while pour recevoir les données envoyé par le client
        while True:
            if game not in games:
                break
            try:
                d = conn.recv(8192 * 3)
                data = d.decode("utf-8")
                if not d:
                    break
                else:
                    #si la selection d'un pion est possible, jouer
                    if data.count("select") > 0:
                        all = data.split(" ")
                        col = int(all[1])
                        row = int(all[2])
                        color = all[3]
                        bo.select(col, row, color)
                    #joueur 2 gagne
                    if data == "winner b":
                        bo.winner = "b"
                        print("Le joueur b gagne la partie! Félicitations!!", game)
                    #joueur 1 gagne
                    if data == "winner w":
                        bo.winner = "w"
                        print("Le joueur a gagne la partie! Félicitations!!", game)
                    #mis à jour mouvement
                    if data == "update moves":
                        bo.update_moves()
                    #nom des joueurs 
                    if data.count("name") == 1:
                        name = data.split(" ")[1]
                        if currentId == "b":
                            bo.p2Name = name
                        elif currentId == "w":
                            bo.p1Name = name
                    #tour du joueur blanc > activer le timer sinon activer le timer du joueur noir
                    if bo.ready:
                        if bo.turn == "w":
                            bo.time1 = 900 - (time.time() - bo.startTime) - bo.storedTime1
                        else:
                            bo.time2 = 900 - (time.time() - bo.startTime) - bo.storedTime2
                    sendData = pickle.dumps(bo)
                conn.sendall(sendData)
            except Exception as e:
                print(e)
        connections -= 1
        #il y a plus de jeu, print qqle chose dans la console
        try:
            del games[game]
            print("Le jeu ", game, "est fini")
        except:
            pass
        print("Le joueur ", name, "a quitté la partie", game)
        conn.close()
    #sinon mettre en spectateur
    else:
        available_games = list(games.keys())
        game_ind = 0
        bo = games[available_games[game_ind]]
        bo.start_user = "s"
        data_string = pickle.dumps(bo)
        conn.send(data_string)
        while True:
            available_games = list(games.keys())
            bo = games[available_games[game_ind]]
            try:
                d = conn.recv(128)
                data = d.decode("utf-8")
                if not d:
                    break
                else:
                    try:
                        if data == "forward":
                            print("Avancement du jeu...")
                            game_ind += 1
                            if game_ind >= len(available_games):
                                game_ind = 0
                        elif data == "back":
                            print("Retour au jeu...")
                            game_ind -= 1
                            if game_ind < 0:
                                game_ind = len(available_games) -1
                        bo = games[available_games[game_ind]]
                    except:
                        print("Jeu invalide reçu du spectateur...")
                    sendData = pickle.dumps(bo)
                    conn.sendall(sendData)
            except Exception as e:
                print(e)
        print("Le spectateur à quitté la partie", game)
        specs -= 1
        conn.close()
#accepter les connexions + affichage de nombre de joueur connecté dans une session & nb de session dans la console
while True:
    if connections < 6:
        conn, addr = s.accept()
        spec = False
        g = -1
        print("Nouvelle connexion...")
        for game in games.keys():
            if games[game].ready == False:
                g=game
        if g == -1:
            try:
                g = list(games.keys())[-1]+1
                games[g] = Board(8,8)
            except:
                g = 0
                games[g] = Board(8,8)
        print("Nombre de connectés:", connections+1)
        print("Nombre de parties:", len(games))
        start_new_thread(threaded_client, (conn,g,spec))
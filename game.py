import pygame
import os
import time
from client import Client
import pickle
pygame.font.init()

# INITIALISATION DU JEU 
board = pygame.transform.scale(pygame.image.load(os.path.join("img","board_alt.png")), (750, 750))
ChessSet = pygame.image.load(os.path.join("img", "ChessSet.jpg"))
rect = (113,113,525,525)
#INITIALISATION DE A QUI LE TOUR (BLANC) EN FIRST
turn = "w"

#ECRAN DU MENU
def menu_screen(win, name):
    global bo, ChessSet
    run = True
    offline = False
    #tant que le menu est ouvert, 
    while run:
        win.blit(ChessSet, (0, 0))
        small_font = pygame.font.SysFont("comicsans", 50)
        #si le serveur est eteint, l'écrire sur la fenetre
        if offline:
            off = small_font.render(
                "Le serveur est off !", 1, (255, 0, 0))
            win.blit(off, (width / 2 - off.get_width() / 2, 500))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                run = False
            #connexion au serveur de jeu
            if event.type == pygame.MOUSEBUTTONDOWN:
                offline = False
                try:
                    bo = connect()
                    run = False
                    main()
                    break
                #print sur la console le serveur est off 
                except:
                    print("Le serveur est off !")
                    offline = True

# MIS A JOUR DU JEU
def redraw_gameWindow(win, bo, p1, p2, color, ready):
    win.blit(board, (0, 0))
    bo.draw(win, color)

    formatTime1 = str(int(p1//60)) + ":" + str(int(p1%60))
    formatTime2 = str(int(p2 // 60)) + ":" + str(int(p2 % 60))
    if int(p1%60) < 10:
        formatTime1 = formatTime1[:-1] + "0" + formatTime1[-1]
    if int(p2%60) < 10:
        formatTime2 = formatTime2[:-1] + "0" + formatTime2[-1]

    font = pygame.font.SysFont("comicsans", 30)
    try:
        txt = font.render(bo.p1Name + "\'s Time: " + str(formatTime2), 1, (255, 255, 255))
        txt2 = font.render(bo.p2Name + "\'s Time: " + str(formatTime1), 1, (255,255,255))
    except Exception as e:
        print(e)
    win.blit(txt, (520,10))
    win.blit(txt2, (520, 700))
    
    txt = font.render("Appuyez sur q pour quitter", 1, (255, 255, 255))
    win.blit(txt, (10, 20))

    if color == "s":
        txt3 = font.render("MODE SPECTATEUR", 1, (255, 0, 0))
        win.blit(txt3, (width/2-txt3.get_width()/2, 10))

    if not ready:
        show = "ATtente de joueurs..."
        if color == "s":
            show = "Attente de joueurs..."
        font = pygame.font.SysFont("comicsans", 80)
        txt = font.render(show, 1, (255, 0, 0))
        win.blit(txt, (width/2 - txt.get_width()/2, 300))
    #annonce la couleur des joueur + annonce quand c'est le tour  d'un joueur
    if not color == "s":
        font = pygame.font.SysFont("comicsans", 30)
        if color == "w":
            txt3 = font.render("TU JOUES LES BLANCS", 1, (255, 0, 0))
            win.blit(txt3, (width / 2 - txt3.get_width() / 2, 10))
        else:
            txt3 = font.render("TU JOUES LES NOIRS", 1, (255, 0, 0))
            win.blit(txt3, (width / 2 - txt3.get_width() / 2, 10))

        if bo.turn == color:
            txt3 = font.render("C'EST TON TOUR", 1, (255, 0, 0))
            win.blit(txt3, (width / 2 - txt3.get_width() / 2, 700))
        else:
            txt3 = font.render("C'EST SON TOUR", 1, (255, 0, 0))
            win.blit(txt3, (width / 2 - txt3.get_width() / 2, 700))

    pygame.display.update()

# ECRAN DE LA FIN DU JEU
def end_screen(win, text):
    pygame.font.init()
    font = pygame.font.SysFont("comicsans", 80)
    txt = font.render(text,1, (255,0,0))
    win.blit(txt, (width / 2 - txt.get_width() / 2, 300))
    pygame.display.update()

    pygame.time.set_timer(pygame.USEREVENT+1, 3000)

    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
                run = False
            elif event.type == pygame.KEYDOWN:
                run = False
            elif event.type == pygame.USEREVENT+1:
                run = False


def click(pos):
    """
    :return: pos (x, y) in range 0-7 0-7
    """
    x = pos[0]
    y = pos[1]
    if rect[0] < x < rect[0] + rect[2]:
        if rect[1] < y < rect[1] + rect[3]:
            divX = x - rect[0]
            divY = y - rect[1]
            i = int(divX / (rect[2]/8))
            j = int(divY / (rect[3]/8))
            return i, j

    return -1, -1

#connexion au client
def connect():
    global n
    n = Client()
    return n.board

#main
def main():
    # INITIALISATION DES VARAIBLES
    global turn, bo, name
    color = bo.start_user
    count = 0
    #envoie l'état des mouvements au serveur
    bo = n.send("update_moves")
    #envoie le nom au serveur
    bo = n.send("name " + name)
    clock = pygame.time.Clock()
    run = True
    #TANT QUE LE JEU TOURNE, JOUER 
    while run:
        if not color == "s":
            p1Time = bo.time1
            p2Time = bo.time2
            if count == 60:
                bo = n.send("get")
                count = 0
            else:
                count += 1
            clock.tick(30)
        # METTRE A JOUR LE JEU
        try:
            redraw_gameWindow(win, bo, p1Time, p2Time, color, bo.ready)
        except Exception as e:
            print(e)
            end_screen(win, "Ton adversaire a quitté la partie !")
            run = False
            break
        #SI LE TEMPS EST ECOULER/ECHEC ET MATH DU COTE WHITE ALORS LE BLACK GG SIONON CONTRAIRE
        if not color == "s":
            if p1Time <= 0:
                bo = n.send("winner b")
            elif p2Time <= 0:
                bo = n.send("winner w")

            if bo.check_mate("b"):
                bo = n.send("winner b")
            elif bo.check_mate("w"):
                bo = n.send("winner w")
        #AFFICHE SUR L ECRAN LE WINNER
        if bo.winner == "w":
            end_screen(win, "White is the Winner!")
            run = False
        elif bo.winner == "b":
            end_screen(win, "Black is the winner")
            run = False
        #quitte le jeu
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

            #ENVOIE AU SERVEUR LES DATA DEQUI A GG
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q and color != "s":
                    if color == "w":
                        bo = n.send("winner b")
                    else:
                        bo = n.send("winner w")
                #AVANCER LE JEU (spectateur)
                if event.key == pygame.K_RIGHT:
                    bo = n.send("forward")
                #RECULER LE JEU (spectateur)
                if event.key == pygame.K_LEFT:
                    bo = n.send("back")

            #ENVOIE LES DONNEES DES MOUVEMENTS AU SERVEUR
            if event.type == pygame.MOUSEBUTTONUP and color != "s":
                if color == bo.turn and bo.ready:
                    pos = pygame.mouse.get_pos()
                    bo = n.send("update moves")
                    i, j = click(pos)
                    bo = n.send("select " + str(i) + " " + str(j) + " " + color)
    #deconnexion 
    n.disconnect()
    bo = 0
    menu_screen(win)

#nom dans la console
name = input("Entrez votre nom : ")
#taille de l'écran
width = 750
height = 750
# DECLARE LA VARIABLE WIN
win = pygame.display.set_mode((width, height))
# TITRE DE L APPLICATION
pygame.display.set_caption("Chess Game")
menu_screen(win, name)

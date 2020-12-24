import random, pygame, sys, operator, os, time
from pygame.locals import *

vitezaJoc = 30
lungimeFereastra = 1700 #x
latimeFereastra = 1000 #y
marimeCelula = 50 #lungimea si latimea ferestrei trebuie sa se imparta la marimea celuluei fara rest
lungimeCelula = int(lungimeFereastra / marimeCelula)
latimeCelula = int(latimeFereastra / marimeCelula)

#             R    G    B
WHITE     = (255, 255, 255)
GREY      = (200, 200, 200)
PINK      = (198, 134, 156)
BLACK     = ( 17,  18,  13)
RED       = (255,   0,   0)
GREEN     = (  0, 255,   0)
DARKGREEN = (  0, 155,   0)
DARKGRAY  = ( 40,  40,  40)
ORANGE    = (255, 155, 111)
backgroundColour = WHITE

UP = 'up'
DOWN = 'down'
LEFT = 'stanga'
RIGHT = 'dreapta'



CAP = 0 #dam capului sarpelui index 0

def main():
    #variabile pe care le vom folosi mai tarziu
    global ceasFPS, afisareSuprafata, f0nt
    global peretiCoord1,peretiCoord2
    peretiCoord1 = []
    peretiCoord2 = []
    peretiCoord2 = gasireSoftPereti()
    peretiCoord1 = gasirePereti()
    #nitializam pygame si fereastra de joc
    pygame.init()
    ceasFPS = pygame.time.Clock()
    afisareSuprafata = pygame.display.set_mode((lungimeFereastra, latimeFereastra))
    f0nt = pygame.font.Font('freesansbold.ttf', 18)
    pygame.display.set_caption('Proiect de An Midrigan&Pelin')
    #incepem jocul
    while True:
        start()
        afisareJoc()


def start():
    global asteptare
    asteptare = False
    nrAsteptari = -1
    # se randomizeaza coordonatele de inceput.
    startx = random.randint(5, lungimeCelula - 6) #coordonata de start x e random
    starty = random.randint(5, latimeCelula - 6) #coordonata de start y e random
    sarpeCoordonate = [{'x': startx + 6, 'y': starty},
                  {'x': startx + 5, 'y': starty},
                  {'x': startx + 4, 'y': starty},
                  ]

    directie = RIGHT
    directionList = [RIGHT]
    CALE = []

    # Se randomizeaza coordonatele marului.
    apple = gasireLocatieRandom(sarpeCoordonate)
    lastApple = {'x':startx-1,   'y': starty -1}
    #calculam prima cale
    CALE = calculamCalea(sarpeCoordonate,apple,True)
    directionList = calcDirection(CALE)
    ultimulPerete = 0

    while True: # main game loop
        for event in pygame.event.get(): # event handling loop
            if event.type == QUIT:
                terminate()
            elif event.type == KEYDOWN:
                  if event.key == K_ESCAPE:
                      terminate()
        # check if the sarpe has hit itself or the edge
        if sarpeCoordonate[CAP]['x'] == -1 or sarpeCoordonate[CAP]['x'] == lungimeCelula or sarpeCoordonate[CAP]['y'] == -1 or sarpeCoordonate[CAP]['y'] == latimeCelula:
            terminate()
            return # game over

        for wormBody in sarpeCoordonate[1:]:
            if wormBody['x'] == sarpeCoordonate[CAP]['x'] and wormBody['y'] == sarpeCoordonate[CAP]['y']:
                terminate()
                return # game over
        # verificam daca marul a fost mancat
        if sarpeCoordonate[CAP]['x'] == apple['x'] and sarpeCoordonate[CAP]['y'] == apple['y']:
            # in caz ca a fost mancat nu stergem ultima celula din sarpe
            lastApple = apple
            apple = gasireLocatieRandom(sarpeCoordonate) # gasim coordonate random a unui alt mar
            drawMar(apple,lastApple)
            CALE = calculamCalea(sarpeCoordonate,apple,True) #calculam din nou calea catre mar
            if not CALE:
              asteptare = True
              nrAsteptari = 10000
            elif CALE == 'stall':
              asteptare = True
              nrAsteptari = int(len(sarpeCoordonate)/2)
            else:
              directionList = calcDirection(CALE)
        else:
            del sarpeCoordonate[-1] # stergem ultima celula din corpul sarpelui


        ultimaDirectie = directie

        #gasim directie noua
        if asteptare and not directionList:
          onlyDirection = calcDoarDirectia(sarpeCoordonate)
          if onlyDirection and onlyDirection == ultimaDirectie:
            directionList.append(onlyDirection)
            print('only directie:', directie)
          else:
            if drumLiber(sarpeCoordonate,directie,ultimulPerete):
              directionList.append(directie)      #continuam ultima directie
            elif (not gasireCapNou(directie,sarpeCoordonate) in sarpeCoordonate) or (gasireCapNou(directie,sarpeCoordonate) in peretiCoord1):
              directionList.append(directie)
            else:
              ultimaDirectie = directie
              #verificam daca se gaseste o cale mai buna, daca nu ramanea cea veche
              CALE = calculamCalea(sarpeCoordonate,apple,False)
              if CALE != [] and CALE != 'stall':
                asteptare = False
                nrAsteptari = -1
                directionList = calcDirection(CALE)
              else:
                if verificaUltimPerete(sarpeCoordonate):
                  ultimulPerete = verificaUltimPerete(sarpeCoordonate)
                directionList.extend(gasireDirectieMaiBuna(sarpeCoordonate,directie,ultimulPerete))
                if calcAria(gasireCapNou(directionList[0],sarpeCoordonate), sarpeCoordonate, ultimulPerete)<3:
                  directionList = [ultimaDirectie]
            nrAsteptari = nrAsteptari - 1
            if nrAsteptari < 1:
              asteptare = False
              prevLastWall = ultimulPerete
              ultimulPerete = 0
              directionList.append(ultimaDirectie)
              CALE = calculamCalea(sarpeCoordonate,apple,True) #calculate CALE to go
              if not CALE:
                asteptare = True
                nrAsteptari = 10000
                ultimulPerete = prevLastWall
              elif CALE == 'stall':
                asteptare = True
                nrAsteptari = int(len(sarpeCoordonate)/2)
                ultimulPerete = prevLastWall
              else:
                directionList = calcDirection(CALE)
        nextHead = gasireCapNou(directionList[0],sarpeCoordonate)
        if asteptare:
          if AriaEstePreaMica(lungimeCelula,nextHead, sarpeCoordonate, ultimulPerete):      #returneaza true daca Aria este prea mica
            ultimulPerete = 0
            directionList = gasimUrmatoareaDirectie(sarpeCoordonate, directionList[0],0)


        directie = directionList.pop(0)
        newCap = gasireCapNou(directie, sarpeCoordonate)
        sarpeCoordonate.insert(0, newCap)
        afisareSuprafata.fill(backgroundColour)
        drawSuprafata()
        drawSarpe(sarpeCoordonate)
        drawMar(apple,lastApple)
        drawScor(len(sarpeCoordonate) - 3)
        pygame.display.update()
        ceasFPS.tick(vitezaJoc)

def calcDoarDirectia(sarpe):
    count = 4
    ways = gasireInVecinatate(sarpe[0])
    theWay = 0
    for each in ways:
      if each in sarpe:
        count = count - 1
      else:
        theWay = each
    if count == 1:
      return calcDirection([sarpe[0],theWay])
    else:
      return 0

def determinareaCoordonateUrmatorPerete(ultimulPerete):
    pereti = []
    loopcount = 0
    for _ in range(latimeCelula):
      if ultimulPerete == RIGHT:
        pereti.append({'x':0, 'y':loopcount})
      if ultimulPerete == LEFT:
        pereti.append({'x':lungimeCelula-1, 'y':loopcount})
      loopcount = loopcount + 1
    loopcount = 0
    for _ in range(lungimeCelula):
      if ultimulPerete == DOWN:
        pereti.append({'x':loopcount, 'y':0})
      if ultimulPerete == UP:
        pereti.append({'x':loopcount, 'y':latimeCelula-1})
      loopcount = loopcount + 1
    return pereti

def drumLiber(sarpe,directie,ultimulPerete):
    listaDeCelule = peretiCoord1 + sarpe
    listaDeCelule.extend(determinareaCoordonateUrmatorPerete(ultimulPerete))
    cap = sarpe[0]
    fata = sarpe[0]
    fataStanga = sarpe[0]
    fataDreapta = sarpe[0]
    stanga = sarpe[0]
    dreapta = sarpe[0]
    if directie == UP:
        newCap = {'x': sarpe[CAP]['x'], 'y': sarpe[CAP]['y'] - 1}
        fata = {'x': sarpe[CAP]['x'], 'y': sarpe[CAP]['y'] - 2}
        fataStanga = {'x': sarpe[CAP]['x']-1, 'y': sarpe[CAP]['y'] - 1}
        fataDreapta = {'x': sarpe[CAP]['x']+1, 'y': sarpe[CAP]['y'] - 1}
        stanga = {'x': sarpe[CAP]['x']-1, 'y': sarpe[CAP]['y']}
        dreapta = {'x': sarpe[CAP]['x']+1, 'y': sarpe[CAP]['y']}
    elif directie == DOWN:
        newCap = {'x': sarpe[CAP]['x'], 'y': sarpe[CAP]['y'] + 1}
        fata = {'x': sarpe[CAP]['x'], 'y': sarpe[CAP]['y'] + 2}
        fataStanga = {'x': sarpe[CAP]['x']-1, 'y': sarpe[CAP]['y'] + 1}
        fataDreapta = {'x': sarpe[CAP]['x']+1, 'y': sarpe[CAP]['y'] + 1}
        stanga = {'x': sarpe[CAP]['x']-1, 'y': sarpe[CAP]['y']}
        dreapta = {'x': sarpe[CAP]['x']+1, 'y': sarpe[CAP]['y']}
    elif directie == LEFT:
        newCap = {'x': sarpe[CAP]['x'] - 1, 'y': sarpe[CAP]['y']}
        fata = {'x': sarpe[CAP]['x'] - 2, 'y': sarpe[CAP]['y']}
        fataStanga = {'x': sarpe[CAP]['x']-1, 'y': sarpe[CAP]['y'] + 1}
        fataDreapta = {'x': sarpe[CAP]['x']-1, 'y': sarpe[CAP]['y'] - 1}
        stanga = {'x': sarpe[CAP]['x'], 'y': sarpe[CAP]['y']+1}
        dreapta = {'x': sarpe[CAP]['x'], 'y': sarpe[CAP]['y']-1}
    elif directie == RIGHT:
        newCap = {'x': sarpe[CAP]['x'] + 1, 'y': sarpe[CAP]['y']}
        fata = {'x': sarpe[CAP]['x'] + 2, 'y': sarpe[CAP]['y']}
        fataStanga = {'x': sarpe[CAP]['x']+1, 'y': sarpe[CAP]['y'] - 1}
        fataDreapta = {'x': sarpe[CAP]['x']+1, 'y': sarpe[CAP]['y'] + 1}
        stanga = {'x': sarpe[CAP]['x'], 'y': sarpe[CAP]['y']-1}
        dreapta = {'x': sarpe[CAP]['x'], 'y': sarpe[CAP]['y']+1}
    if (fataStanga in listaDeCelule and not stanga in listaDeCelule) or (fataDreapta in listaDeCelule and not dreapta in listaDeCelule):
      return False
    if newCap in listaDeCelule:
      return False
    moduriDeDeplasare = []
    moduriDeDeplasare = gasireInVecinatate(newCap)
    count = len(moduriDeDeplasare)
    for each in moduriDeDeplasare:
      if each in listaDeCelule:
        count = count - 1
    if count < 1:
      return False
    elif count < 2 and not (fata in listaDeCelule):
      return False
    else:
      return True

def verificaUltimPerete(sarpe):
    x = sarpe[0]['x']
    y = sarpe[0]['y']
    if x == 0:
      return LEFT
    elif x == lungimeCelula - 1:
      return RIGHT
    elif y == 0:
      return UP
    elif y == latimeCelula -1:
      return DOWN
    else:
      return 0

def verificareIntoarcere(sarpe,listaDeCelule,direction1,direction2):
    if direction1 == UP or direction1 == DOWN:
      if direction2 == RIGHT:
        if {'x': sarpe[CAP]['x']+3, 'y': sarpe[CAP]['y']} in listaDeCelule and (not {'x': sarpe[CAP]['x']+2, 'y': sarpe[CAP]['y']} in listaDeCelule):
          return True
        else:
          return False
      if direction2 == LEFT:
        if {'x': sarpe[CAP]['x']-3, 'y': sarpe[CAP]['y']} in listaDeCelule and (not {'x': sarpe[CAP]['x']-2, 'y': sarpe[CAP]['y']} in listaDeCelule):
          return True
        else:
          return False
    if direction1 == LEFT or direction1 == RIGHT:
      if direction2 == UP:
        if {'x': sarpe[CAP]['x'], 'y': sarpe[CAP]['y']-3} in listaDeCelule and (not {'x': sarpe[CAP]['x'], 'y': sarpe[CAP]['y']-2} in listaDeCelule):
          return True
        else:
          return False
      if direction2 == DOWN:
        if {'x': sarpe[CAP]['x'], 'y': sarpe[CAP]['y']+3} in listaDeCelule and (not {'x': sarpe[CAP]['x'], 'y': sarpe[CAP]['y']+2} in listaDeCelule):
          return True
        else:
          return False

def gasireDirectieMaiBuna(sarpe, directie,ultimulPerete):
    listaDeCelule = list(sarpe)
    smartTurn = False   #dont kill yourself in the corner
    if directie == UP:
        areaLeft = calcAria({'x': sarpe[CAP]['x']-1, 'y': sarpe[CAP]['y']},sarpe,ultimulPerete)
        areaRight = calcAria({'x': sarpe[CAP]['x']+1, 'y': sarpe[CAP]['y']},sarpe,ultimulPerete)
        if areaLeft == 0 and areaRight == 0:
          return [directie]
        ariaDreapta = calcAria({'x': sarpe[CAP]['x'], 'y': sarpe[CAP]['y']-1},sarpe,ultimulPerete)
        maxAria = max(areaLeft,areaRight,ariaDreapta)
        print ('Options:', 'stanga:',areaLeft,'dreapta:',areaRight,'straight:',ariaDreapta)
        if maxAria == ariaDreapta:
          return [directie]
        elif maxAria == areaLeft:
          if verificareIntoarcere(sarpe,listaDeCelule,directie,LEFT):
            print('Smart Turn Enabled')
            return [LEFT, LEFT]
          else:
            return [LEFT, DOWN]
        else:
          if verificareIntoarcere(sarpe,listaDeCelule,directie,RIGHT):
            print('Smart Turn Enabled')
            return [RIGHT, RIGHT]
          else:
            return [RIGHT,DOWN]

    if directie == DOWN:
        areaLeft = calcAria({'x': sarpe[CAP]['x']-1, 'y': sarpe[CAP]['y']},sarpe,ultimulPerete)
        areaRight = calcAria({'x': sarpe[CAP]['x']+1, 'y': sarpe[CAP]['y']},sarpe,ultimulPerete)
        if areaLeft == 0 and areaRight == 0:
          return [directie]
        ariaDreapta = calcAria({'x': sarpe[CAP]['x'], 'y': sarpe[CAP]['y']+1},sarpe,ultimulPerete)
        maxAria = max(areaLeft,areaRight,ariaDreapta)
        print ('Options:','stanga:',areaLeft,'dreapta:',areaRight,'straight:',ariaDreapta)
        if maxAria == ariaDreapta:
          return [directie]
        elif areaLeft == maxAria:
          if verificareIntoarcere(sarpe,listaDeCelule,directie,LEFT):
            print('Smart Turn Enabled')
            return [LEFT, LEFT]
          else:
            return [LEFT, UP]
        else:
          if verificareIntoarcere(sarpe,listaDeCelule,directie,RIGHT):
            print('Smart Turn Enabled')
            return [RIGHT, RIGHT]
          else:
            return [RIGHT,UP]

    elif directie == LEFT:
        areaUp = calcAria({'x': sarpe[CAP]['x'], 'y': sarpe[CAP]['y'] - 1},sarpe,ultimulPerete)
        areaDown = calcAria({'x': sarpe[CAP]['x'], 'y': sarpe[CAP]['y'] + 1},sarpe,ultimulPerete)
        if areaUp == 0 and areaDown == 0:
          return [directie]
        ariaDreapta = calcAria({'x': sarpe[CAP]['x']-1, 'y': sarpe[CAP]['y']},sarpe,ultimulPerete)
        maxAria = max(ariaDreapta,areaUp,areaDown)
        print ('Options:','up:',areaUp,'down:',areaDown,'straight:',ariaDreapta)
        if maxAria == ariaDreapta:
          return [directie]
        elif maxAria == areaUp:
          if verificareIntoarcere(sarpe,listaDeCelule,directie,UP):
            print('Smart Turn Enabled')
            return [UP, UP]
          else:
            return [UP,RIGHT]
        else:
          if verificareIntoarcere(sarpe,listaDeCelule,directie,DOWN):
            print('Smart Turn Enabled')
            return [DOWN, DOWN]
          else:
            return [DOWN,RIGHT]

    elif directie == RIGHT:
        areaUp = calcAria({'x': sarpe[CAP]['x'], 'y': sarpe[CAP]['y'] - 1},sarpe,ultimulPerete)
        areaDown = calcAria({'x': sarpe[CAP]['x'], 'y': sarpe[CAP]['y'] + 1},sarpe,ultimulPerete)
        if areaUp == 0 and areaDown == 0:
          return [directie]
        ariaDreapta = calcAria({'x': sarpe[CAP]['x']+1, 'y': sarpe[CAP]['y']},sarpe,ultimulPerete)
        maxAria = max(ariaDreapta,areaUp,areaDown)
        if maxAria == ariaDreapta:
          return [directie]
        elif areaUp ==maxAria:
          if verificareIntoarcere(sarpe,listaDeCelule,directie,UP):
            return [UP, UP]
          else:
            return [UP,LEFT]
        else:
          if verificareIntoarcere(sarpe,listaDeCelule,directie,DOWN):
            return [DOWN, DOWN]
          else:
            return [DOWN,LEFT]

def gasimUrmatoareaDirectie(sarpe, directie,ultimulPerete):
    listaDeCelule = list(sarpe)
    areaLeft = calcAria({'x': sarpe[CAP]['x']-1, 'y': sarpe[CAP]['y']},sarpe,ultimulPerete)
    areaRight = calcAria({'x': sarpe[CAP]['x']+1, 'y': sarpe[CAP]['y']},sarpe,ultimulPerete)
    areaUp = calcAria({'x': sarpe[CAP]['x'], 'y': sarpe[CAP]['y'] - 1},sarpe,ultimulPerete)
    areaDown = calcAria({'x': sarpe[CAP]['x'], 'y': sarpe[CAP]['y'] + 1},sarpe,ultimulPerete)
    maxAria = max(areaLeft,areaRight,areaUp,areaDown)
    if maxAria == areaUp:
      return [UP]
    elif maxAria == areaDown:
      return [DOWN]
    elif maxAria == areaLeft:
      return [LEFT]
    else:
      return [RIGHT]

def calcAria(punct, sarpe, ultimulPerete):
    urmatorPerete = determinareaCoordonateUrmatorPerete(ultimulPerete)
    if punct in sarpe or punct in peretiCoord1 or punct in urmatorPerete:
      return 0
    bonusLaCoada = 0
    q = []
    cautarePuncte = []
    cautarePuncte.append(punct)
    while (cautarePuncte):
      i = cautarePuncte.pop()
      for each in gasireInVecinatate(i):
        if not each in q:
          if not (each in sarpe or each in peretiCoord1 or punct in urmatorPerete):
            cautarePuncte.append(each)
        if each == sarpe[-1]:
          bonusLaCoada = 200
      q.append(i)
    return len(q)+bonusLaCoada

def AriaEstePreaMica(bound,punct, sarpe, ultimulPerete):
    urmatorPerete = determinareaCoordonateUrmatorPerete(ultimulPerete)
    if punct in sarpe or punct in peretiCoord1 or punct in urmatorPerete:
      return True
    bonusLaCoada = 0
    q = []
    cautarePuncte = []
    cautarePuncte.append(punct)
    while (cautarePuncte):
      i = cautarePuncte.pop()
      for each in gasireInVecinatate(i):
        if not each in q:
          if not (each in sarpe or each in peretiCoord1 or punct in urmatorPerete):
            cautarePuncte.append(each)
        if each == sarpe[-1]:
          bonusLaCoada = 200
      q.append(i)
      if (len(q) + bonusLaCoada) > bound:
        return False
    return True

def calcCost(punct,sarpe):
    neighbors = gasireInVecinatate(punct)
    for each in neighbors:
      if each in sarpe[1:]:
        return sarpe.index(each)
    return 999

def calcDirection(CALE):
    ultimulPunct = CALE[0]
    directii = []
    nextDirection = ''
    for punctulCurent in CALE:
      if (punctulCurent['x'] > ultimulPunct['x']):
        nextDirection = RIGHT
      elif (punctulCurent['x'] < ultimulPunct['x']):
        nextDirection = LEFT
      else:
        if (punctulCurent['y'] > ultimulPunct['y']):
          nextDirection = DOWN
        elif (punctulCurent['y'] < ultimulPunct['y']):
          nextDirection = UP
        else:
          continue
      ultimulPunct = punctulCurent
      directii.append(nextDirection)
    return directii

def calculamCalea(sarpe,apple,softCalculation):
  oldSarpe = list(sarpe)

  CALE = calcululPrincipal(sarpe,apple,softCalculation)
  if not CALE:
    return []
  else:
    copieCalea = list(CALE)
    copieCalea.reverse()
    newSarpe = copieCalea + oldSarpe
    caleOut = calcululPrincipal(newSarpe,newSarpe[-1],False)
    if not caleOut:
    #nu am gasit o cale deci nu mergem dupa mar
      return 'stall'
    else:
    #s-a gasit o cale catre mar
      return CALE

def calcululPrincipal(sarpe,apple,softCalculation):
  punctePanaLaCale= []
  margini = []
  puncteNoi = []
  puncteFolosite = []
  nrDePuncte = 1         #daca toate sunt testate ne intoarcem la alt punct
  gasireaCaii = True
  listaDeCelule = getListOfNo(sarpe)
  softListOfNo = getSoftListOfNo(sarpe)
  softListOfNo.extend(peretiCoord2)
  margini.append(sarpe[0])
  puncteFolosite.append(sarpe[0])
  ultimulPunct = margini[-1]
  punctePanaLaCale.append(ultimulPunct)

  if (apple in peretiCoord2) or (apple in softListOfNo):
    softCalculation = False

  #calculam calea
  while(gasireaCaii and softCalculation):
    ultimulPunct = margini[-1]
    puncteNoi = gasireInVecinatate(ultimulPunct)
    puncteNoi = sorted(puncteNoi, key = lambda k: calcDistance(k,apple), reverse = True)  #sort puncteNoi
    nrDePuncte = len(puncteNoi)
    for punct in puncteNoi:
      if punct in softListOfNo:
        nrDePuncte = nrDePuncte -1
      elif punct in puncteFolosite:
        nrDePuncte = nrDePuncte -1
      else:
        margini.append(punct)
        punctePanaLaCale.append(ultimulPunct)
        puncteFolosite.append(ultimulPunct)

    if nrDePuncte == 0:
      puncteFolosite.append(margini.pop())
      puncteFolosite.append(punctePanaLaCale.pop())
    if apple in margini:
      gasireaCaii = 0
    if not margini:
      softCalculation = False
      break

  if not softCalculation:
    punctePanaLaCale= []
    margini = []
    puncteNoi = []
    puncteFolosite = []
    nrDePuncte = 1
    gasireaCaii = True
    listaDeCelule = getListOfNo(sarpe)
    margini.append(sarpe[0])
    puncteFolosite.append(sarpe[0])
    ultimulPunct = margini[-1]
    punctePanaLaCale.append(ultimulPunct)

    while(gasireaCaii):
      ultimulPunct = margini[-1]
      puncteNoi = gasireInVecinatate(ultimulPunct)
      puncteNoi = sorted(puncteNoi, key = lambda k: calcDistance(k,apple), reverse = True)  #sort puncteNoi
      nrDePuncte = len(puncteNoi)
      for punct in puncteNoi:
        if punct in listaDeCelule:
          nrDePuncte = nrDePuncte -1
        elif punct in puncteFolosite:
          nrDePuncte = nrDePuncte -1
        else:
          margini.append(punct)
          punctePanaLaCale.append(ultimulPunct)
          puncteFolosite.append(ultimulPunct)
      if nrDePuncte == 0:
        puncteFolosite.append(margini.pop())
        puncteFolosite.append(punctePanaLaCale.pop())
      if apple in margini:
        gasireaCaii = 0
      if not margini:
        return []
  punctePanaLaCale.append(apple)
  return punctePanaLaCale

def gasireInVecinatate(punct):
  invecinari = []
  if punct['x'] < lungimeCelula:
    invecinari.append({'x':punct['x']+1,'y':punct['y']})
  if punct['x'] > 0:
    invecinari.append({'x':punct['x']-1,'y':punct['y']})
  if punct['y'] < latimeCelula:
    invecinari.append({'x':punct['x'],'y':punct['y']+1})
  if punct['y'] >0:
    invecinari.append({'x':punct['x'],'y':punct['y']-1})
  return invecinari

def calcDistance(punct, apple):
  distanta = abs(punct['x'] - apple['x']) + abs(punct['y'] - apple['y'])
  return distanta

def getSoftListOfNo(sarpe):
  listaDeCelule = []
  listaDeCelule.extend(celuleDeLangaSarpe(sarpe))
  return listaDeCelule


def celuleDeLangaSarpe(sarpe):
  listaDeCelule = []
  capX = sarpe[0]['x']
  capY = sarpe[0]['y']
  count = 0
  for each in sarpe:
    if count == 0:
      listaDeCelule.append(each)
    else:
      dist = abs (each['x'] - capX) + abs(each['y']-capY)
      nrDinSpate = len(sarpe) - count
      if dist < (nrDinSpate+1):
        listaDeCelule.append(each)
        listaDeCelule.append({'x':each['x']+1,'y':each['y']})
        listaDeCelule.append({'x':each['x']-1,'y':each['y']})
        listaDeCelule.append({'x':each['x'],'y':each['y']+1})
        listaDeCelule.append({'x':each['x'],'y':each['y']-1})
        listaDeCelule.append({'x':each['x']+1,'y':each['y']+1})
        listaDeCelule.append({'x':each['x']-1,'y':each['y']-1})
        listaDeCelule.append({'x':each['x']-1,'y':each['y']+1})
        listaDeCelule.append({'x':each['x']+1,'y':each['y']-1})
    count = count + 1
  seen = set()
  newList = []
  for d in listaDeCelule:
    t = tuple(d.items())
    if t not in seen:
        seen.add(t)
        newList.append(d)
  return newList



def getListOfNo(sarpe):
  listaDeCelule = []
  capX = sarpe[0]['x']
  capY = sarpe[0]['y']
  count = 0
  for each in sarpe:
    dist = abs (each['x'] - capX) + abs(each['y']-capY)
    nrDinSpate = len(sarpe) - count
    count = count + 1
    if dist < (nrDinSpate+1):
      listaDeCelule.append(each)
  listaDeCelule.extend(peretiCoord1)
  return listaDeCelule


def gasirePereti():
  pereti = []
  loopcount = 0
  for _ in range(latimeCelula):
    pereti.append({'x':-1       , 'y':loopcount})
    pereti.append({'x':lungimeCelula, 'y':loopcount})
    loopcount = loopcount + 1
  loopcount = 0
  for _ in range(lungimeCelula):
    pereti.append({'x':loopcount, 'y':-1})
    pereti.append({'x':loopcount, 'y':latimeCelula})
    loopcount = loopcount + 1
  return pereti

def gasireSoftPereti():
  pereti = []
  loopcount = 0
  for _ in range(latimeCelula):
    pereti.append({'x':0       , 'y':loopcount})
    pereti.append({'x':lungimeCelula-1, 'y':loopcount})
    loopcount = loopcount + 1
  loopcount = 0
  for _ in range(lungimeCelula):
    pereti.append({'x':loopcount, 'y':0})
    pereti.append({'x':loopcount, 'y':latimeCelula-1})
    loopcount = loopcount + 1
  return pereti


def drawMarginileFerestrei(points):
    for punct in points:
        x = punct['x'] * marimeCelula
        y = punct['y'] * marimeCelula
        wormSegmentRect = pygame.Rect(x, y, marimeCelula, marimeCelula)
        pygame.draw.rect(afisareSuprafata, ORANGE, wormSegmentRect)
    lastPointRect = pygame.Rect(points[-1]['x']*marimeCelula, points[-1]['y']*marimeCelula, marimeCelula, marimeCelula)
    pygame.draw.rect(afisareSuprafata, (255,255,255), wormSegmentRect)

def gasireCapNou(directie,sarpeCoordonate):
    if directie == UP:
        newCap = {'x': sarpeCoordonate[CAP]['x'], 'y': sarpeCoordonate[CAP]['y'] - 1}
    elif directie == DOWN:
        newCap = {'x': sarpeCoordonate[CAP]['x'], 'y': sarpeCoordonate[CAP]['y'] + 1}
    elif directie == LEFT:
        newCap = {'x': sarpeCoordonate[CAP]['x'] - 1, 'y': sarpeCoordonate[CAP]['y']}
    elif directie == RIGHT:
        newCap = {'x': sarpeCoordonate[CAP]['x'] + 1, 'y': sarpeCoordonate[CAP]['y']}
    return newCap


def verificDacaSeApasaButon():
    if len(pygame.event.get(QUIT)) > 0:
        terminate()

    keyUpEvents = pygame.event.get(KEYUP)
    if len(keyUpEvents) == 0:
        return None
    if keyUpEvents[0].key == K_ESCAPE:
        terminate()
    return keyUpEvents[0].key

def terminate():
    print('AI MURIT!')
    pygame.quit()
    sys.exit()


def gasireLocatieRandom(sarpe):
    locatie = {'x': random.randint(0, lungimeCelula - 1), 'y': random.randint(0, latimeCelula - 1)}
    while(locatie in sarpe):
        locatie = {'x': random.randint(0, lungimeCelula - 1), 'y': random.randint(0, latimeCelula - 1)}
    return locatie


def afisareJoc():
    gameOverFont = pygame.font.Font('freesansbold.ttf', 150)
    gameSurf = gameOverFont.render('Game', True, WHITE)
    overSurf = gameOverFont.render('Over', True, WHITE)
    gameRect = gameSurf.get_rect()
    overRect = overSurf.get_rect()
    gameRect.midtop = (lungimeFereastra / 2, 10)
    overRect.midtop = (lungimeFereastra / 2, gameRect.height + 10 + 25)

    afisareSuprafata.blit(gameSurf, gameRect)
    afisareSuprafata.blit(overSurf, overRect)
    pygame.display.update()
    pygame.time.wait(500)
    verificDacaSeApasaButon()

    while True:
        if verificDacaSeApasaButon():
            pygame.event.get()
            return

def drawScor(score):
    scoreSurf = f0nt.render('Scor: %s' % (score), True, BLACK)
    scoreRect = scoreSurf.get_rect()
    scoreRect.topleft = (lungimeFereastra - 120, 10)
    afisareSuprafata.blit(scoreSurf, scoreRect)

def drawSarpe(sarpeCoordonate):
    for coord in sarpeCoordonate:
        x = coord['x'] * marimeCelula
        y = coord['y'] * marimeCelula
        if(coord == 1):
            wormInnerSegmentRect = pygame.Rect(x + 1, y + 1, marimeCelula - 2, marimeCelula - 2)
            pygame.draw.rect(afisareSuprafata, RED, wormInnerSegmentRect)
        else:
            wormInnerSegmentRect = pygame.Rect(x + 1, y + 1, marimeCelula - 2, marimeCelula - 2)
            pygame.draw.rect(afisareSuprafata, BLACK, wormInnerSegmentRect)

def drawMar(coord,lastApple):
    x = coord['x'] * marimeCelula
    y = coord['y'] * marimeCelula
    appleRect = pygame.Rect(x, y, marimeCelula, marimeCelula)
    pygame.draw.rect(afisareSuprafata, RED, appleRect)

def drawSuprafata():
    return
    for x in range(0, lungimeFereastra, marimeCelula): # draw vertical lines
        pygame.draw.line(afisareSuprafata, DARKGRAY, (x, 0), (x, latimeFereastra))
    for y in range(0, latimeFereastra, marimeCelula): # draw horizontal lines
        pygame.draw.line(afisareSuprafata, DARKGRAY, (0, y), (lungimeFereastra, y))


if __name__ == '__main__':
    main()

import pygame, time, random, sys
from pygame.locals import*
WINDOWWIDTH  = 800
WINDOWHEIGHT = 680
LEFTMARGIN   = 130
RIGHTMARGIN  = 340
TOPMARGIN    = 10
BOXSIZE      = 33
BOARDHEIGHT  = 20
BOARDWIDTH   = 10
DOWNFREQ     = 0.1
SIDEWAYSFREQ = 0.1
FPS = 30

WHITE       =   (255,255,255)
BLACK       =   (  0,  0,  0)
ALTBLACK    =   ( 10, 10, 10)
RED         =   (150,  0,  0)
GREEN       =   (  0,150,  0)
BLUE        =   (  0,  0,150)
YELLOW      =   (150,150,  0)
TURQUOISE   =   (  0,150,150)
PURPLE      =   (150,  0,150)
BGCOLOR     =   (255,255,  0)
COLORS      =   (GREEN, BLUE, YELLOW, TURQUOISE, PURPLE)

#templates are for the 7 shapes below
  ##   ##  ##         #      #    #
  ##  ##    ##  ####  ###  ###   ###


BLANK = '.'
TEMPLATEWIDTH = 5
TEMPLATEHEIGHT = 5
SHAPE_1 =   [['.....',
              '.....',
              '.00..',
              '.00..',
              '.....']]
SHAPE_2 =   [['.....',
              '.....',
              '.00..',
              '..00.',
              '.....'],
             ['.....',
              '..0..',
              '.00..',
              '.0...',
              '.....']]
SHAPE_3 =   [['.....',
              '.....',
              '..00.',
              '.00..',
              '.....'],
             ['.....',
              '..0..',
              '..00.',
              '...0.',
              '.....']]
SHAPE_4 =   [['..0..',
              '..0..',
              '..0..',
              '..0..',
              '.....'],
             ['.....',
              '.....',
              '0000.',
              '.....',
              '.....']]
SHAPE_5 =   [['.....',
              '..0..',
              '..0..',
              '.00..',
              '.....',],
             ['.....',
              '.0...',
              '.000.',
              '.....',
              '.....'],
             ['.....',
              '..00.',
              '..0..',
              '..0..',
              '.....'],
             ['.....',
              '.....',
              '.000.',
              '...0.',
              '.....']]
SHAPE_6 =   [['.....',
              '..0..',
              '..0..',
              '..00.',
              '.....'],
             ['.....',
              '.....',
              '.000.',
              '.0...',
              '.....'],
             ['.....',
              '..00.',
              '...0.',
              '...0.',
              '.....'],
             ['.....',
              '...0.',
              '.000.',
              '.....',
              '.....']]
SHAPE_7 =   [['.....',
              '..0..',
              '.000.',
              '.....',
              '.....'],
             ['.....',
              '..0..',
              '..00.',
              '..0..',
              '.....'],
             ['.....',
              '.....',
              '.000.',
              '..0..',
              '.....'],
             ['.....',
              '..0..',
              '.00..',
              '..0..',
              '.....']]

SHAPES = {'O':      SHAPE_1,
          'S':      SHAPE_2,
          'Z':      SHAPE_3,
          'I':      SHAPE_4,
          'J':      SHAPE_5,
          'L':      SHAPE_6,
          'T':      SHAPE_7}



def main():
    global DISPLAYSURF, FPSCLOCK, SMALLFONT, LARGEFONT
    pygame.init()
    pygame.display.set_caption('Tetris')
    SMALLFONT = pygame.font.Font('freesansbold.ttf', 25)
    LARGEFONT = pygame.font.Font('freesansbold.ttf', 120)
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    FPSCLOCK = pygame.time.Clock()
    introScreen()

def game():
    board = newBoard()
    score = 0
    level = 1
    highScore = getHighScore()
    currentPiece = generatePiece()
    nextPiece = generatePiece()
    lastSidewaysTime = time.time()
    lastDownTime = time.time()
    lastDropTime = time.time()
    movDown = False
    movLeft = False
    movRight = False
    level, dropFreq = getLevelAndSpeed(score)
    pygame.mixer.music.load('maintheme.mid')
    pygame.mixer.music.play(-1, 0.0)
    while True:
        if currentPiece == None:
         # piece has landed, current piece becomes next and next is regenerated
            currentPiece = nextPiece
            nextPiece = generatePiece()
            lastDropTime = time.time()
            # game over check
            if not isValidPosition(board, currentPiece):
                isHighScore = highScoreCheck(score, highScore)
                gameOver(score, isHighScore)
        for event in pygame.event.get():
            # event handling
            if event.type == QUIT:
                terminate()
            elif event.type == KEYDOWN:
                #return to homescreen if escape key is pressed
                if event.key == K_ESCAPE:
                    pygame.mixer.music.stop()
                    introScreen()
                    
                # pause the game if 'p' key is pressed
                elif event.key == K_p:
                    movLeft = False
                    movRight = False
                    movDown = False
                    pauseScreen()

                # handling events if direction keys are pressed
                # move left if left key is pressed and valid
                elif event.key == K_LEFT and isValidPosition(board, currentPiece, adjX=-1):
                    movLeft = True
                    movRight = False
                    movDown = False
                    currentPiece['x'] -= 1
                    lastSidewaysTime = time.time()
                # move right if right arrow is pressed and valid
                elif event.key == K_RIGHT and isValidPosition(board, currentPiece, adjX=1):
                    movLeft = False
                    movRight = True
                    movDown = False
                    currentPiece['x'] += 1
                    lastSidewaysTime = time.time()
                    
                # fall faster if down key is held and valid
                elif event.key == K_DOWN:
                    movLeft = False
                    movRight = False
                    movDown = True
                    if isValidPosition(board, currentPiece, adjY=1):
                        currentPiece['y'] += 1
                    lastDownTime = time.time()
                    
                # rotate piece if space is pressed and valid
                elif event.key == K_SPACE:
                    currentPiece['rotation'] = (currentPiece['rotation'] + 1) % len(SHAPES[currentPiece['shape']])
                    if not isValidPosition(board, currentPiece):
                        currentPiece['rotation'] = (currentPiece['rotation'] - 1) % len(SHAPES[currentPiece['shape']])

            # stop moving if key is released            
            elif event.type == KEYUP:
                if event.key == K_LEFT:
                    movLeft = False
                elif event.key == K_RIGHT:
                    movRight = False
                elif event.key == K_DOWN:
                    movDown = False
                    
        # moving directionally if conditions are met         
        if movLeft and time.time() - lastSidewaysTime > SIDEWAYSFREQ:
            if isValidPosition(board, currentPiece, adjX =-1):
                currentPiece['x'] -= 1
            lastSidewaysTime = time.time()
        if movRight and time.time() - lastSidewaysTime > SIDEWAYSFREQ:
            if isValidPosition(board, currentPiece, adjX=1):
                currentPiece['x'] += 1
            lastSidewaysTime = time.time()
        if movDown and time.time() - lastDownTime > DOWNFREQ:
            if isValidPosition(board, currentPiece, adjY=1):
                currentPiece['y'] += 1
            lastDownTime = time.time()
                    
        # piece falling naturally     
        if time.time() - lastDropTime > dropFreq:
            # piece has landed, add to board and begin next piece
            if  hasLanded(board, currentPiece, adjY=1):
                # make piece permanent board placement
                placeOnBoard(currentPiece, board)
                scoreToAdd = deleteFullLines(board)
                score = score + scoreToAdd
                level, dropFreq = getLevelAndSpeed(score)
                currentPiece = None
            else:
                currentPiece['y'] += 1
                lastDropTime = time.time()

                
        DISPLAYSURF.fill(BGCOLOR)
        drawBoard(board)
        drawNextPiece(nextPiece)
        drawStatus(score, level, highScore)
        # if current piece is still active, redraw
        if currentPiece != None:
            addBlock(currentPiece)
        pygame.display.update()
        FPSCLOCK.tick(FPS)
        
def getHighScore():
    # opens file to return current high score
    with open ('highScore.txt', mode = 'r') as my_file:
        for line in my_file:
            score = line
    return score


def gameOver(score, highScore):
    # plays sound effect once, then loops game over music
    # waits for key press before returning to home screen
    pygame.mixer.music.stop()
    pygame.mixer.music.load('faileffect.wav')
    pygame.mixer.music.play(1, 0.0)
    pygame.time.wait(1500)
    pygame.mixer.music.load('gameover.mid')
    pygame.mixer.music.play(-1, 0.0)
    DISPLAYSURF.fill(BLACK)
    highScoreTime = time.time()
    highScoreColors = (RED, TURQUOISE)
    colorCount = 0
    addText('GAME OVER', LARGEFONT, WINDOWWIDTH/2, WINDOWHEIGHT/2-200, WHITE)
    addText('FINAL SCORE: ' + str(score), SMALLFONT, WINDOWWIDTH/2, WINDOWHEIGHT/2, WHITE)
    addText('Press any key to return to main menu', SMALLFONT, WINDOWWIDTH/2, WINDOWHEIGHT-50, YELLOW)
    while isKeyPressed() == None:
        if highScore and time.time() - highScoreTime > 0.5:
            addText('NEW HIGH SCORE', SMALLFONT, WINDOWWIDTH/2, 500, highScoreColors[colorCount])
            colorCount += 1
            colorCount = colorCount % 2
            highScoreTime = time.time()
        pygame.display.update()
        FPSCLOCK.tick()
    pygame.mixer.music.stop()
    introScreen()

def highScoreCheck(score, highScore):
    # checks if current score has beaten highScore and if so overwrites it
    highScore = int(highScore)
    score = int(score)
    newHighScore = False
    if score <= highScore:
        return
    with open ('highScore.txt', mode='w') as my_file:
        highScore = str(score)
        my_file.write(highScore)
    newHighScore = True
    return newHighScore
    
def getLevelAndSpeed(score):
    # calculates current level and piece fall speed based on current player score
    level = int(score/10+1)
    speed = 0.35 - (level*0.02)
    return level, speed
    
def drawStatus(score, level, highScore):
    # adds the score, level and highScore information to the display
    score = str(score)
    level = str(level)
    highScore = str(highScore)
    addText(('SCORE:    ' + score), SMALLFONT, 645, 330, BLACK)
    addText(('LEVEL:    ' + level), SMALLFONT, 645, 360, BLACK)
    addText(('HIGHSCORE:     ' + highScore), SMALLFONT, 630, 660, BLACK)

def drawNextPiece(piece):
    # draw the next piece in a box at the top right of display
    pygame.draw.rect(DISPLAYSURF, RED, (515, 100, 250, 200))
    pygame.draw.rect(DISPLAYSURF, BLACK, (520, 105, 240, 190))
    addText('NEXT', SMALLFONT, 640, 80, BLACK)
    addBlock(piece, pixelx=560, pixely=130)


def deleteFullLines(board):
    # checks each line on board, starting at the bottom, for any blank spaces
    # if there is no blank spaces in the line, the line above becomes identical
    # to the one above, and each line above it does the same. the very top
    # line of the board becomes blank before the current line is checked again
    # if the line contains any blank squares, the loop iterates up to the next
    # line up until it reaches the top of the board
    cleared = 0
    y = BOARDHEIGHT - 1
    while y >= 0:
        if lineFull(board, y):
            for copy in range(y,0,-1):
                for x in range(BOARDWIDTH):
                    board[x][copy] = board[x][copy-1]
            for x in range(BOARDWIDTH):
                board[x][0] = BLANK
            cleared += 1
        else:
            y -= 1
    return cleared
            

def lineFull(board,y):
    # returns False if any blocks on a board are blank, else returns true
    for x in range(BOARDWIDTH):
        if board[x][y] == BLANK:
            return False
    return True


def isValidPosition(board, piece, adjX=0, adjY=0):
    # first gets current x,y of piece
    # then do a loop of the template and get the x,y of all blocks that arent blank
    # add both together and you have the board coordinates of your block
    # then + the adjusted x,y to these coordinates to check the board for obstacles
    # if there is none the the move is legal
    for x in range(TEMPLATEWIDTH):
        for y in range(TEMPLATEHEIGHT):
            isAboveBoard = y + piece['y'] + adjY < 0
            if isAboveBoard:
                continue
            if SHAPES[piece['shape']][piece['rotation']][y][x] != BLANK:
                if (x + piece['x'] + adjX) < 0:
                    return False
                if (x + piece['x'] + adjX) >= BOARDWIDTH:
                    return False
                if (y + piece['y'] + adjY) >= BOARDHEIGHT:
                    return False
                if board[x + piece['x'] + adjX][y + piece['y'] + adjY] != BLANK:
                    return False
    return True
def hasLanded(board, piece, adjX=0, adjY=0):
     # Return True if the piece is within the board and not colliding
    for x in range(TEMPLATEWIDTH):
        for y in range(TEMPLATEHEIGHT):
            isAboveBoard = y + piece['y'] + adjY < 0
            if isAboveBoard or SHAPES[piece['shape']][piece['rotation']][y][x] == BLANK:
                continue
            if (y + piece['y'] + adjY) >= BOARDHEIGHT:
                return True
            if board[x + piece['x'] + adjX][y + piece['y'] + adjY] != BLANK:
                return True
    return False




    
def introScreen():
    # brings up the intro screen, with the options of start game, controls
    # screen of quit via spacebar, ctrl and esc keys respectively
    DISPLAYSURF.fill(BLACK)
    tetrisTitle = pygame.image.load('tetris_title.png')
    DISPLAYSURF.blit(tetrisTitle,(0, 100))
    addText('press Esc to Quit', SMALLFONT, WINDOWWIDTH/2, WINDOWHEIGHT-100, WHITE)
    addText('press SPACE to Play', SMALLFONT, WINDOWWIDTH/4, WINDOWHEIGHT-175, WHITE)
    addText('press Ctrl for controls', SMALLFONT, WINDOWWIDTH/2 + 175, WINDOWHEIGHT-175, WHITE)
    pygame.display.update() 
    while True:
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if (event.key == K_RCTRL) or (event.key == K_LCTRL):
                    controlsScreen()
                elif (event.key == K_ESCAPE):
                    terminate()
                elif (event.key == K_SPACE):
                    game()
    FPSCLOCK.tick(FPS)


def pauseScreen():
    # brings up pause screen which blocks current board and stays up until a key is pressed
    DISPLAYSURF.fill(BLACK)
    addText('PAUSED', LARGEFONT, WINDOWWIDTH/2, WINDOWHEIGHT/2,  WHITE)
    addText('press any key to return       ',SMALLFONT, WINDOWWIDTH/2, WINDOWHEIGHT-100, YELLOW)
    while isKeyPressed() == None:
        pygame.display.update()
        FPSCLOCK.tick()
    

def controlsScreen():
    # brings up list of controls
    DISPLAYSURF.fill(BLACK)
    addText('LEFT ARROW          MOVE BLOCK LEFT        ', SMALLFONT, WINDOWWIDTH/2, 50,  WHITE)
    addText('RIGHT ARROW         MOVE BLOCK RIGHT       ', SMALLFONT, WINDOWWIDTH/2, 130, WHITE)
    addText('DOWN ARROW          MOVE BLOCK DOWN(FASTER)', SMALLFONT, WINDOWWIDTH/2, 210, WHITE) 
    addText('SPACEBAR            ROTATE SHAPE           ', SMALLFONT, WINDOWWIDTH/2, 290, WHITE)
    addText('"P"                 PAUSE GAME             ', SMALLFONT, WINDOWWIDTH/2, 370, WHITE)
    addText('Esc                 QUIT TO MAIN MENU      ', SMALLFONT, WINDOWWIDTH/2, 450, WHITE)
    addText('press any key to return       ',SMALLFONT, WINDOWWIDTH/2, WINDOWHEIGHT-100, YELLOW)
    while isKeyPressed() == None:
        pygame.display.update()
        FPSCLOCK.tick()
    introScreen()

def addText(text, font, x, y, color):
    # adds text to the screen at current coordinates and font
    textSurf = font.render(text, True, color)
    surfRect = textSurf.get_rect()
    surfRect.center = (x,y)
    DISPLAYSURF.blit(textSurf, surfRect)
    
def isKeyPressed():
    # returns true if any key is pressed
    for event in pygame.event.get():
        if event.type == KEYDOWN:
            return event.key
    return None
    
def generatePiece():
    # create a totally random(shape, rotation, color)block
    shape = random.choice(list(SHAPES.keys()))
    attributes = {'shape':shape,
                  'rotation': random.randint(0, len(SHAPES[shape]) -1),
                  'x': int(BOARDWIDTH / 2) - int(TEMPLATEWIDTH / 2),
                  'y': -2, # start above board
                  'color': random.randint(0, len(COLORS)-1)}
    return attributes


def terminate(): 
    pygame.quit()
    sys.exit() 

def drawBoard(board):
    # rim of board
    pygame.draw.rect(DISPLAYSURF, RED, (LEFTMARGIN - 5, TOPMARGIN - 5, (BOARDWIDTH * BOXSIZE) + 10, (BOARDHEIGHT * BOXSIZE) +10))
    # fill the board
    pygame.draw.rect(DISPLAYSURF, BLACK, (LEFTMARGIN, TOPMARGIN, (BOARDWIDTH * BOXSIZE), (BOARDHEIGHT * BOXSIZE)))
    # passes board coordinates into the drawBox function 
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            drawBox(x, y, board[x][y])

def addBlock(block, pixelx = None, pixely = None):
    # adds the current block to the board data structure permanently
    blockToAdd = SHAPES[block['shape']][block['rotation']]
    if pixelx == None and pixely == None:
        pixelx, pixely = getPixels(block['x'], block['y'])
    for x in range (TEMPLATEWIDTH):
        for y in range (TEMPLATEHEIGHT):
            if blockToAdd[y][x] != BLANK:
                drawBox(None, None, block['color'], pixelx + (x * BOXSIZE), pixely + (y * BOXSIZE))

def drawBox(x, y, color, pixelX=None, pixelY=None):
    # draws the boxes on the board based on the color number in the board
    # data structure
    # if the number =='.' then it is returned, else a box whose color is
    # determined by the corresponding is drawn with a black outline
    if color == BLANK:
        return
    if pixelX == None:
        pixelX, pixelY = getPixels(x, y)
    pygame.draw.rect(DISPLAYSURF, BLACK, (pixelX, pixelY, BOXSIZE, BOXSIZE))
    pygame.draw.rect(DISPLAYSURF, COLORS[color], (pixelX - 1, pixelY - 1, BOXSIZE -2, BOXSIZE - 2))


def placeOnBoard(block, board):
    # temporarily draws the block on the board while it is still falling
    for x in range(TEMPLATEWIDTH):
        for y in range(TEMPLATEHEIGHT):
            if SHAPES[block['shape']][block['rotation']][y][x] != BLANK:
                board[x + block['x']][y + block['y']] = block['color']


def getPixels(boxX, boxY):
    # gets the pixel coordinates of box from its x,y coordinates for drawing purposes
    return (LEFTMARGIN + (boxX * BOXSIZE)), (TOPMARGIN + (boxY * BOXSIZE))
    
def newBoard():
    # create a blank data structure that will be our empty board
    board = []
    for i in range (BOARDWIDTH):
        board.append([BLANK] * BOARDHEIGHT)
    return board    

main()

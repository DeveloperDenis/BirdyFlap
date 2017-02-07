import pygame
import random

pygame.mixer.pre_init(0,0,0,1024)
pygame.init()


#constants
TITLE = 0
PLAYING = 1
GAME_OVER = 2

GRAV_ACCEL = 0.1
SCALE_FACTOR = 4
GROUND_WIDTH = 32
#the width of the game before scaling
INTERNAL_WIDTH = 320
SPAWN_OBSTACLE = pygame.USEREVENT
OBSTACLE_SPACING = 16*3
OBSTACLE_RANGE = 144-OBSTACLE_SPACING-8
OBSTACLE_FREQUENCY = 125

#class initialization
class GameObject(object):

    def __init__(self, startX, startY, fileName):
        self.image = pygame.image.load(fileName)
        self.image = self.image.convert_alpha()
        self.rect = pygame.Rect(startX, startY, self.image.get_width(), self.image.get_height())

    #simple setter methods
    def setX(self, x):
        self.rect.x = x
    def setY(self, y):
        self.rect.y = y
        
    #simple getter methods
    def getTop(self):
        return self.rect.top
    def getBot(self):
        return self.rect.bottom
    def getLeft(self):
        return self.rect.left
    def getRight(self):
        return self.rect.right

class Player(GameObject):
    falling = True
    flapping = False
    animating = True
    ySpeed = 0
    currentFrame = 0
    maxFrames = 3
    delay = 0

    def __init__(self, startX, startY, fileName):
        self.image = pygame.image.load(fileName)
        self.image = self.image.convert_alpha()
        self.rect = self.image.get_rect(x = startX, y = startY)

        self.animRect = pygame.Rect(0,0,16,16)

    def update(self):
        if self.falling or self.flapping:
            
            self.rect.y += self.ySpeed
            self.ySpeed += GRAV_ACCEL

            if self.ySpeed > 0 and self.flapping:
                self.flapping = False
                self.falling = True

        if self.animating and self.delay >= 10:
            if self.currentFrame >= 3:
                self.currentFrame = 0
            else:
                self.currentFrame += 1

            self.animRect.x = self.currentFrame * self.animRect.width
            self.delay = 0

        self.delay += 1

    def flap(self):
        self.ySpeed = -1.5

#game wide important stuff
screen = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("Birdy Flap")
canvas = pygame.Surface((int(screen.get_width()/SCALE_FACTOR), int(screen.get_height()/SCALE_FACTOR)))
running = True
currentState = TITLE
fpsTimer = pygame.time.Clock()
#making the game actually random each time (more or less)
random.seed()
points = 0
highscore = 0
mouseFlag = False

#game objects
player = Player(50, 50, "birdSheet.png")
obstacleArray = []
groundArray = []
pointFont = pygame.font.Font("PressStart2P-Regular.ttf", 32)
pointDisplay = pointFont.render(str(points), False, (255,255,255))
pointCounter = INTERNAL_WIDTH
obstacleCounter = INTERNAL_WIDTH
gameOverBoard = GameObject(100, 50, "gameOverBoard.png")
retryButton = GameObject(gameOverBoard.getLeft()+5, gameOverBoard.getBot()-20, "retryButton.png")
quitButton = GameObject(retryButton.getRight() + 18, retryButton.getTop(), "quitButton.png")
gameOverFont = pygame.font.Font("PressStart2P-Regular.ttf", 12)
bestText = gameOverFont.render("Best:", False, (255,255,255))
titleText = GameObject(INTERNAL_WIDTH/2-20, 25, "titleText.png")
playButton = GameObject(titleText.getLeft()+15, 50, "playButton.png")
flapSound = pygame.mixer.Sound("jump.wav")
hitSound = pygame.mixer.Sound("hit.wav")
pointSound = pygame.mixer.Sound("point.wav")

for i in range(0, 11):
    groundArray.append(GameObject(i*GROUND_WIDTH, canvas.get_height()-36, "ground.png"))

background = GameObject(0, 0, "background.png")

#functions
def updateObstacles():
    i = 0
    while (i < len(obstacleArray)):
        obstacleArray[i].rect.x -= 1

        if obstacleArray[i].rect.right <= 0:
            obstacleArray.pop(i)
            i -= 1
        i += 1
            

def updateGround():
    for groundObject in groundArray:
        groundObject.rect.x -= 1

        if groundObject.rect.right <= 0:
            groundObject.rect.x = INTERNAL_WIDTH
    

def resetPlayer():

    player.setX(50)
    player.setY(100)
    player.ySpeed = 0
    player.falling = True

def restartFlappy():
    global currentState
    global points
    global mouseFlag
    global player
    global obstacleArray
    global pointDisplay
    global pointCounter
    global obstacleCounter
    
    currentState = PLAYING
    points = 0
    mouseFlag = False

    player.setX(50)
    player.setY(50)
    player.animating = True
    player.falling = True
    player.flapping = False
    player.ySpeed = 0
    player.currentFrame = 0
    player.delay = 0

    obstacleArray = []

    pointDisplay = pointFont.render(str(points), False, (255,255,255))
    pointCounter = obstacleCounter = INTERNAL_WIDTH

def gameOver():
    global currentState
    global player
    global highscore
    global points
    global bestScoreText

    currentState = GAME_OVER
    player.animating = False
    
    if points > highscore:
        highscore = points

    bestScoreText = gameOverFont.render(str(highscore), False, (255,255,255))

while running:
    #refresh screen
    canvas.fill((100,100,100))
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONUP and currentState == GAME_OVER:
            if event.button == 1 and quitButton.rect.collidepoint(event.pos[0]/4, event.pos[1]/4):
                running = False
            elif event.button == 1 and retryButton.rect.collidepoint(event.pos[0]/4, event.pos[1]/4):
                restartFlappy()
        elif event.type == pygame.MOUSEBUTTONUP and currentState == TITLE:
            if event.button == 1 and playButton.rect.collidepoint(event.pos[0]/4, event.pos[1]/4):
                player.falling = True
                currentState = PLAYING
    
    if currentState == TITLE:

        canvas.blit(background.image, background.rect)
        canvas.blit(player.image, player.rect, player.animRect)

        for groundObject in groundArray:
            canvas.blit(groundObject.image, groundObject.rect)

        canvas.blit(titleText.image, titleText.rect)
        canvas.blit(playButton.image, playButton.rect)

        player.falling = False
        player.flapping = False

        player.update()
        updateGround()
    
    elif currentState == PLAYING:

        obstacleCounter += 1
        if obstacleCounter >= OBSTACLE_FREQUENCY:
            randomY = random.random()*OBSTACLE_RANGE+52
            
            obstacleArray.append(GameObject(INTERNAL_WIDTH, randomY, "obstacle.png"))
            flippedObstacle = GameObject(INTERNAL_WIDTH, randomY-obstacleArray[0].rect.height - OBSTACLE_SPACING, "obstacle.png")
            flippedObstacle.image = pygame.transform.flip(flippedObstacle.image, False, True)
            obstacleArray.append(flippedObstacle)
            obstacleCounter = 0
        
        if len(obstacleArray) > 0:
            pointCounter -= 1

        if pointCounter <= player.getLeft():
            pointSound.play()
            pointCounter = 175 #hard-coded position of next obstacle after you pass one
            points += 1
            pointDisplay = pointFont.render(str(points), False, (255,255,255))
        
        player.update()
        updateGround()
        updateObstacles()

        for groundObject in groundArray:
            if player.getBot() >= groundObject.getTop():
                hitSound.play()
                player.falling = False
                player.setY(groundObject.getTop()-player.rect.height)
                gameOver()

        for obstacle in obstacleArray:
            tempRect = player.rect.copy()
            tempRect.width = tempRect.width/4
            if tempRect.colliderect(obstacle.rect):
                hitSound.play()
                gameOver()

        if pygame.mouse.get_pressed()[0]:
            mouseFlag = True
        elif mouseFlag and player.getBot() > 2:
            player.flap()
            player.flapping = True
            flapSound.play()
            mouseFlag = False
        elif player.getTop() <= 0 and player.flapping:
            player.falling = True
            player.ySpeed = 0
        
        #game object drawing
        canvas.blit(background.image, background.rect)

        #obstacle drawing
        for i in range(0, len(obstacleArray)):
            canvas.blit(obstacleArray[i].image, obstacleArray[i].rect)
            #print(obstacleArray[i].rect.x, obstacleArray[i+1].rect.x)
        
        canvas.blit(player.image, player.rect, player.animRect)

        #drawing the ground
        for groundObject in groundArray:
            canvas.blit(groundObject.image, groundObject.rect)

        canvas.blit(pointDisplay, pointDisplay.get_rect(center=(INTERNAL_WIDTH/2, 25)))

    elif currentState is GAME_OVER:

        ''' DRAWING '''
        canvas.blit(background.image, background.rect)
        
        for i in range(0, len(obstacleArray)):
            canvas.blit(obstacleArray[i].image, obstacleArray[i].rect)
        
        canvas.blit(player.image, player.rect, player.animRect)
        
        for groundObject in groundArray:
            canvas.blit(groundObject.image, groundObject.rect)

        canvas.blit(gameOverBoard.image, gameOverBoard.rect)
        canvas.blit(retryButton.image, retryButton.rect)
        canvas.blit(quitButton.image, quitButton.rect)
        canvas.blit(bestText, bestText.get_rect(x=gameOverBoard.getLeft()+5, y=gameOverBoard.getTop()+5))
        canvas.blit(bestScoreText, (gameOverBoard.getLeft()+45, gameOverBoard.getTop()+23))
        
    ''' END IF '''
    
    #scale screen up
    screen.blit(pygame.transform.scale(canvas, (canvas.get_width()*SCALE_FACTOR, canvas.get_height()*SCALE_FACTOR)), (0,0))
    #update screen
    pygame.display.flip()

    #keep fps 60
    fpsTimer.tick_busy_loop(60)

pygame.quit()

import pygame,sys
from pygame.locals import *
from ctypes import windll; windll.user32.SetProcessDPIAware()
from random import seed,randint

class LineOfText(pygame.sprite.Sprite):
    __slots__ = ('game','text','x','y','size','font','color','static','textid','image','rect','istouched','ishit','align')
    def __init__(self,game,text,x,y,size,font,color,static=0,textid="0",align="center"):
        self.text,self.x,self.y,self.size,self.color,self.static,self.textid,self.istouched,self.ishit,self.align = text,int(x),int(y),size,color,static,textid,0,0,align
        self.font = game.filepath+font+".ttf"
        pygame.sprite.Sprite.__init__(self,game.texts)
        self.image = pygame.font.Font(self.font,self.size).render(self.text,True,color)
        self.refresh()
    def touch(self): self.istouched = 1; self.image = pygame.font.Font(self.font,int(self.size*1.5)).render(self.text,True,(255,255,0)); self.refresh()
    def untouch(self): self.istouched = 0; self.image = pygame.font.Font(self.font,int(self.size)).render(self.text,True,self.color); self.refresh()
    def update(self, newtext): self.text = newtext; self.image = pygame.font.Font(self.font,self.size).render(self.text,True,self.color); self.refresh()
    def refresh(self):
        if self.align == "center": self.rect = self.image.get_rect(**{"center":(int(self.x),int(self.y))})

class Program:
    def __init__(self):
        self.window = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
        pygame.event.set_allowed([QUIT,KEYUP,KEYDOWN,MOUSEBUTTONDOWN,MOUSEBUTTONUP])
        self.clock = pygame.time.Clock(); pygame.display.set_caption('Collaboration game')
        self.sounds = [pygame.mixer.Sound("click.wav"),pygame.mixer.Sound("lightsout.wav"),pygame.mixer.Sound("step.wav"),pygame.mixer.Sound("win.wav"),pygame.mixer.Sound("lose.wav")]
        self.window_w,self.window_h = pygame.display.get_surface().get_size()
        self.filepath = sys._MEIPASS+'\\' if getattr(sys,'frozen',False) else ''
        self.texts = pygame.sprite.Group()
        self.menu,self.display,self.key,self.inputboxtimer,self.down,self.playerlocation,self.playercount,self.landminechance,self.timerlength,self.mapx,self.mapy = "seed",0,"",0,0,[0,0],3,2,240,64,33

    def findavailable(self,x,y):
        data = []
        if y != 1 and self.map[y-1][x] == 0 and self.map[y-2][x] == 0 and self.map[y-2][x-1] == 0 and self.map[y-2][x+1] == 0: data.append([x,y-1])
        if y != len(self.map)-2 and self.map[y+1][x] == 0 and self.map[y+2][x] == 0 and self.map[y+2][x-1] == 0 and self.map[y+2][x+1] == 0: data.append([x,y+1])
        if x != 1 and self.map[y][x-1] == 0 and self.map[y][x-2] == 0 and self.map[y-1][x-2] == 0 and self.map[y+1][x-2] == 0: data.append([x-1,y])
        if x != len(self.map[0])-2 and self.map[y][x+1] == 0 and self.map[y][x+2] == 0 and self.map[y-1][x+2] == 0 and self.map[y+1][x+2] == 0: data.append([x+1,y])
        return data

    def run(self):
        self.clock.tick(15)
        if self.menu != "game": self.window.fill((227,19,19))
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit();sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DELETE: pygame.quit();sys.exit()
                elif self.menu in ["seed","setting3","setting4","mapsize2"]: self.key = event.key
                elif event.key == pygame.K_ESCAPE:
                    if self.menu == "game": pygame.mixer.Sound.stop(self.sounds[1]); self.menu = "home"
                    elif self.menu.startswith("setting") or self.menu.startswith("about"): self.menu = "home"
                    elif self.menu == "home": self.menu = "seed"
                    elif self.menu == "seed": pygame.quit();sys.exit()
                elif event.key == pygame.K_w: self.seed += 1
                elif event.key == pygame.K_s: self.seed -= 1
                elif event.key == pygame.K_r:
                    if self.menu == "game": self.menu = "loading"
                    self.display = ""
                elif self.menu == "game":
                    if event.key == pygame.K_UP and self.map[self.playerlocation[1]-1][self.playerlocation[0]] != 0 and self.player == 1: self.playerlocation[1] -= 1; pygame.mixer.Sound.play(self.sounds[2])
                    elif event.key == pygame.K_DOWN and self.map[self.playerlocation[1]+1][self.playerlocation[0]] != 0 and self.player == 1: self.playerlocation[1] += 1; pygame.mixer.Sound.play(self.sounds[2])
                    elif event.key == pygame.K_LEFT and self.map[self.playerlocation[1]][self.playerlocation[0]-1] != 0 and self.player == 1: self.playerlocation[0] -= 1; pygame.mixer.Sound.play(self.sounds[2])
                    elif event.key == pygame.K_RIGHT and self.map[self.playerlocation[1]][self.playerlocation[0]+1] != 0 and self.player == 1: self.playerlocation[0] += 1; pygame.mixer.Sound.play(self.sounds[2])
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: self.down = 1
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1: self.down = 0

        if self.display != self.menu:
            self.display = self.menu
            if self.menu == "seed":
                self.ask("Enter a seed","This is a number you and your friends have chosen to share within your game.","input")
            elif self.menu == "setting1":
                self.ask("Choose how many people will be playing","This will determine the noise of the map.","selection",[[[["Player count","Category"]]+[[str(x)+" player",str(x)+"player"] for x in range(2,7)]]])
            elif self.menu == "setting2":
                self.ask("How frequent should landmines be?","","selection",[[[["Frequency","Category"]]+[[x,"landmine"+str(i)]
                    for i,x in enumerate(["Very frequent","Pretty frequent","Kinda frequent","Kinda infrequent","Pretty infrequent","Very infrequent","Disable landmines"])]]])
            elif self.menu == "setting3": self.ask("Enter a time (in seconds)","This is how long you have to try and complete the maze!","input")
            elif self.menu == "setting4": self.ask("Enter the amount of blocks wide you'd like the map to be","Note this game is built for maps of in ratio (16:9) - (0,3)","input")
            elif self.menu == "mapsize2": self.ask("Enter the amount of blocks tall you'd like the map to be","We reccomend sticking to the (16:9) - (0,3) ratio and not a square","input")
            elif self.menu == "areyousure":
                self.ask("Are you sure you'd like to use this map size?","You've used a size known to be buggy.","selection",
                    [[[["Choose:","Category"],["Yes, save choices","setting4yes"],["No, keep previous choice","setting4no"]]]])
            elif self.menu == "about0":
                self.ask("What is this game?","New to the experience? This is the place to be!","about",[["Test 1","Test 2"],["Test1","Test2"]])
            elif self.menu == "home":
                self.ask("Which player would you like to be?","The seed is currently "+str(self.seed),"selection",
                    [[[["Player selection","Category"],
                        ["Player 1 - Controls the character","player1"]]+
                        [["Player "+str(x)+" - Sees"+['',' half',' a third of',' a quarter of',' a fifth of'][self.playercount-2]+" the map","player"+str(x)] for x in range(2,self.playercount+1)],
                    [["Settings","Category"],
                        ["Change the seed","setting0"],
                        ["Player count : "+str(self.playercount),"setting1"],
                        ["Landmine chance","setting2"],
                        ["Timer length : "+str(self.timerlength),"setting3"],
                        ["Map size : "+str(self.mapx)+"x"+str(self.mapy),"setting4"]],
                    [["About","Category"],
                        ["What is this game?","about0"],
                        ["How do I play?","about1"],
                        ["What are the different tiles?","about2"],
                        ["What are the controls?","about3"],
                        ["Who made this?","about4"]]]])
            elif self.menu == "loading":
                self.singletext("Loading...")
                self.map = [[0 for x in range(self.mapx)] for x in range(self.mapy)]
                seed(self.seed); self.startpoint = [0,randint(1,len(self.map)-2)]
                for i in range(3): self.map[self.startpoint[1]][i] = 1
                lastspot = [2,self.startpoint[1]]
                while lastspot != "stop":
                    available1 = self.findavailable(lastspot[0],lastspot[1])
                    if available1 == []: 
                        addpath = False
                        for row in self.map[1:-1]:
                            if 1 not in row: addpath = True
                        for i in range(0,len(self.map[0])-2):
                            found = False
                            for row in self.map:
                                if row[i] == 1: found = True
                            if not found: addpath = True
                        testspot = []
                        if addpath:
                            while testspot != "stop":
                                testspot = [randint(1,len(self.map[0])-2),randint(1,len(self.map)-2)]
                                if self.map[testspot[1]][testspot[0]] == 1: lastspot = testspot; testspot = "stop"
                        else:
                            while testspot != "stop":
                                testspot = [randint(1,len(self.map[0])-2),randint(1,len(self.map)-2)]
                                if self.map[testspot[1]][testspot[0]] == 1:
                                    touching = 0
                                    if self.map[testspot[1]-1][testspot[0]] in [1,3]: touching += 1
                                    if self.map[testspot[1]+1][testspot[0]] in [1,3]: touching += 1
                                    if self.map[testspot[1]][testspot[0]-1] in [1,3]: touching += 1
                                    if self.map[testspot[1]][testspot[0]+1] in [1,3]: touching += 1
                                    if touching == 1: self.map[testspot[1]][testspot[0]] = 2; testspot = "stop"
                                    elif self.landminechance != 6 and randint(1,self.landminechance+1) == 1:
                                        available2 = self.findavailable(testspot[0],testspot[1])
                                        if len(available2) >= 1:
                                            available2 = available2[randint(0,len(available2)-1)]
                                            self.map[available2[1]][available2[0]] = 3
                            lastspot = "stop"
                    else: lastspot = available1[randint(0,len(available1)-1)]; self.map[lastspot[1]][lastspot[0]] = 1

                self.menu,self.texts = "game",pygame.sprite.Group()
                self.blockwidth,self.blockheight = int(self.window_w/(len(self.map[0]))),int(self.window_h/(len(self.map)+3))
                self.window.fill((0,0,0))
                if self.player != 1:
                    if self.playercount >= 3:
                        for row in range(0,len(self.map)):
                            for block in range(0,len(self.map[0])):
                                if randint(1,self.playercount-1) != self.player-1 and row != len(self.map)-1 and row != 0 and block != len(self.map[0])-1 and block != 0: self.map[row][block] = -1
                    self.bricktexture = pygame.transform.scale(pygame.image.load(self.filepath+"brick.png"),(self.blockwidth,self.blockheight))
                    self.groundtexture = pygame.transform.scale(pygame.image.load(self.filepath+"ground.png"),(self.blockwidth,self.blockheight))
                    self.landminetexture = pygame.transform.scale(pygame.image.load(self.filepath+"landmine.png"),(self.blockwidth,self.blockheight))
                    self.startarrow = pygame.transform.scale(pygame.image.load(self.filepath+"startarrow.png"),(self.blockwidth,self.blockheight))
                    self.endflag = pygame.transform.scale(pygame.image.load(self.filepath+"endflag.png"),(self.blockwidth,self.blockheight))
                    for y,row in enumerate(self.map):
                        for x,block in enumerate(row):
                            if block == 0: texture = self.bricktexture
                            elif block == 1: texture = self.groundtexture
                            elif block == 2: texture = self.endflag
                            elif block == 3: texture = self.landminetexture
                            if block != -1: self.window.blit(texture,(x*self.blockwidth,(y+3)*self.blockheight))
                    self.window.blit(self.startarrow,(0,int((self.startpoint[1]+3)*self.blockheight)))
                    self.window.blit(self.bricktexture,(self.blockwidth,self.blockheight))
                    LineOfText(self,"Boundary / wall",self.blockwidth*2+4,self.blockheight,self.blockheight-4,"Arial",(255,255,255),align="left")
                    self.window.blit(self.groundtexture,(int((self.window_w-2*self.blockwidth)/5+4),self.blockheight))
                    LineOfText(self,"Ground / path",(self.window_w-2*self.blockwidth)/5+self.blockwidth+4,self.blockheight,self.blockheight-4,"Arial",(255,255,255),align="left")
                    self.window.blit(self.landminetexture,(int((self.window_w-2*self.blockwidth)/5*2+4),self.blockheight))
                    LineOfText(self,"Landmine",(self.window_w-2*self.blockwidth)/5*2+self.blockwidth+4,self.blockheight,self.blockheight-4,"Arial",(255,255,255),align="left")
                    self.window.blit(self.startarrow,(int((self.window_w-2*self.blockwidth)/5*3+4),self.blockheight))
                    LineOfText(self,"Start",(self.window_w-2*self.blockwidth)/5*3+self.blockwidth+4,self.blockheight,self.blockheight-4,"Arial",(255,255,255),align="left")
                    self.window.blit(self.endflag,(int((self.window_w-2*self.blockwidth)/5*4+4),self.blockheight))
                    LineOfText(self,"End / goal",(self.window_w-2*self.blockwidth)/5*4+self.blockwidth+4,self.blockheight,self.blockheight-4,"Arial",(255,255,255),align="left")
                else:
                    self.playertexture = pygame.transform.scale(pygame.image.load(self.filepath+"player.png"),(self.blockwidth,self.blockheight))
                    self.playerlocation = self.startpoint
                    pygame.mixer.Sound.play(self.sounds[1])
            elif self.menu == "win": pygame.mixer.Sound.stop(self.sounds[1]); pygame.mixer.Sound.play(self.sounds[3]); self.singletext("You win!"); self.menu = "home"
            elif self.menu == "lose": pygame.mixer.Sound.stop(self.sounds[1]); self.singletext("You lost :("); self.menu = "home"

        if self.menu == "seed" and self.key != "":
            if self.key >= 48 and self.key <= 57 and len(self.userinput) <= 15: self.userinput += str(self.key-48)
            elif self.key == pygame.K_BACKSPACE: self.userinput = self.userinput[0:-1]
            elif self.key == pygame.K_RETURN and self.userinput != "": self.menu = "home"; self.seed = int(self.userinput)
            self.key = ""
        elif self.menu == "setting3" and self.key != "":
            if self.key >= 48 and self.key <= 57 and len(self.userinput) <= 15: self.userinput += str(self.key-48)
            elif self.key == pygame.K_BACKSPACE: self.userinput = self.userinput[0:-1]
            elif self.key == pygame.K_RETURN and self.userinput != "" and int(self.userinput) >= 4: self.menu = "home"; self.timerlength = int(self.userinput)
            self.key = ""
        elif self.menu == "setting4" and self.key != "":
            if self.key >= 48 and self.key <= 57 and len(self.userinput) <= 15: self.userinput += str(self.key-48)
            elif self.key == pygame.K_BACKSPACE: self.userinput = self.userinput[0:-1]
            elif self.key == pygame.K_RETURN and self.userinput != "":
                self.tempinputx,self.menu,self.areyousure = int(self.userinput),"mapsize2",False
                if self.tempinputx < 32: self.singletext("Widths lower than 32 are known to be buggy!"); self.areyousure = True
                if self.tempinputx > 128: self.singletext("Widths higher than 128 take a while to load and are hard to see!"); self.areyousure = True
                if self.tempinputx % 16 != 0: self.singletext("This width cannot but put in a 16:9 ratio and may be buggy!"); self.areyousure = True
            self.key = ""
        elif self.menu == "mapsize2" and self.key != "":
            if self.key >= 48 and self.key <= 57 and len(self.userinput) <= 15: self.userinput += str(self.key-48)
            elif self.key == pygame.K_BACKSPACE: self.userinput = self.userinput[0:-1]
            elif self.key == pygame.K_RETURN and self.userinput != "":
                self.tempinputy = int(self.userinput)
                if self.tempinputx/16*9-3 != self.tempinputy: self.singletext("This map size is not in a (16:9) - (0,3) ratio!"); self.areyousure = True
                if self.areyousure: self.menu = "areyousure"
                else: self.mapx,self.mapy = self.tempinputx,self.tempinputy
            self.key = ""
        elif self.menu == "game" and self.player == 1:
            self.window.fill((0,0,0))
            self.window.blit(self.playertexture,(self.playerlocation[0]*self.blockwidth,(self.playerlocation[1]+3)*self.blockheight))
            if self.map[self.playerlocation[1]][self.playerlocation[0]] == 2: self.menu = "win"
            elif self.map[self.playerlocation[1]][self.playerlocation[0]] == 3: self.menu = "lose"

        for text in self.texts:
            if text.align == "center":
                if text.rect.collidepoint(pygame.mouse.get_pos()) and text.static == 0: text.touch()
                elif not text.rect.collidepoint(pygame.mouse.get_pos()) and text.static == 0 and text.istouched == 1 and text.ishit == 0: text.untouch()
                if text.istouched == 1 and self.down == 1: text.ishit = 1
                elif self.down == 0 and text.ishit == 1:
                    text.ishit = 0
                    print(text.textid)
                    pygame.mixer.Sound.play(self.sounds[0])
                    if text.textid.startswith("player"): self.player = int(text.textid[-1:]); self.menu = "loading"
                    elif text.textid.endswith("player"): self.playercount = int(text.textid[0]); self.menu = "home"
                    elif text.textid == "setting4yes": self.mapx,self.mapy = self.tempinputx,self.tempinputy; self.menu = "home"
                    elif text.textid == "setting4no": self.tempinputx,self.tempinputy = self.mapx,self.mapy; self.menu = "home"
                    elif text.textid == "setting0": self.menu = "seed"
                    elif text.textid.startswith("setting"): self.menu = "setting"+text.textid[-1:]
                    elif text.textid.startswith("about"): self.menu = "about"+text.textid[-1:]
                    elif text.textid.startswith("landmine"): self.landminechance = int(text.textid[-1:]); self.menu = "home"

            if text.textid == "userinput":
                self.inputboxtimer += 1
                if self.inputboxtimer == 30:
                    if text.text[len(text.text)-1] == "_": text.update(self.userinput+"  ")
                    else: text.update(self.userinput+"_")
                    self.inputboxtimer = 0
                elif text.text != self.userinput: text.update(self.userinput+text.text[len(text.text)-1])
            if text.align == "center": self.window.blit(text.image,(text.rect.x,text.rect.y))
            else: self.window.blit(text.image,(text.x,text.y))
        pygame.display.update()

    def ask(self,question,information,asktype,other=""):
        self.texts = pygame.sprite.Group()
        LineOfText(self,question,self.window_w/2,24,48,"Impact",(255,255,255),1)
        LineOfText(self,information,self.window_w/2,64,32,"Arial",(196,196,196),1)

        if asktype == "selection":
            for iterate0,rowofanswers in enumerate(other):
                for iterate1,groupofanswers in enumerate(rowofanswers):
                    for iterate2,answer in enumerate(groupofanswers):
                        x = self.window_w/(len(rowofanswers)+1)*(iterate1+1)
                        y = self.window_h/(len(other)+1)*(iterate0+1)-46*(len(groupofanswers)/2-iterate2)
                        if iterate2 == 0: LineOfText(self,answer[0],x,y,32,"Impact",(255,255,255),1,answer[1])
                        else: LineOfText(self,answer[0],x,y,32,"Arial",(255,255,255),textid=answer[1])
        elif asktype == "input":
            self.userinput,self.key = "",""
            LineOfText(self,other,self.window_w/2,self.window_h-60,14,"Arial",(255,255,255),1)
            LineOfText(self,"_",self.window_w/2,self.window_h/2,32,"Impact",(255,255,255),textid="userinput")
            LineOfText(self,"Press [ENTER] to confirm your choice",self.window_w/2,96,24,"Arial",(196,196,196),1)
        elif asktype == "about":
            for iterate0,group in enumerate(other):
                for iterate1,line in enumerate(group):
                    x = self.window_w/(len(other)+1)*(iterate0+1)
                    y = self.window_h/2-23*(len(group))+46*iterate1
                    if len(other) > 1 and iterate1 == 0: LineOfText(self,line,x,y,32,"Impact",(255,255,255))
                    else: LineOfText(self,line,x,y,32,"Arial",(255,255,255))
            LineOfText(self,"Press [ESC] to go back!",self.window_w/2,self.window_h-32,40,"Arial",(255,255,255))

    def singletext(self,text):
        self.texts = pygame.sprite.Group(); self.window.fill((227,19,19))
        LineOfText(self,text,self.window_w/2,self.window_h/2,64,"Impact",(255,255,255))
        for text in self.texts: self.window.blit(text.image,(text.rect.x,text.rect.y))
        pygame.display.update()
        pygame.time.delay(5000)

pygame.mixer.init(buffer=2)
pygame.init(); g = Program()
while True: g.run()
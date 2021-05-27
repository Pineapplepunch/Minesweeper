#!/usr/bin/env python3

import sys,os,re,random,time
from datetime import datetime
from stat import S_IREAD,S_IWRITE
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox
import webbrowser

'''
| event                 | name                  |
| Ctrl-c                | Control-c             |
| Ctrl-/                | Control-slash         |
| Ctrl-\                | Control-backslash     |
| Ctrl+(Mouse Button-1) | Control-1             |
| Ctrl-1                | Control-Key-1         |
| Enter key             | Return                |
|                       | Button-1              |
|                       | ButtonRelease-1       |
|                       | Home                  |
|                       | Up, Down, Left, Right |
|                       | Configure             |
| window exposed        | Expose                |
| mouse enters widget   | Enter                 |
| mouse leaves widget   | Leave                 |
|                       | Key                   |
|                       | Tab                   |
|                       | space                 |
|                       | BackSpace             |
|                       | KeyRelease-BackSpace  |
| any key release       | KeyRelease            |
| escape                | Escape                |
|                       | F1                    |
|                       | Alt-h                 |


'''
#from tkinter import *
#from tkinter import ttk
#from tkinter import messagebox
#Guide
#0-8 are the number of mines around a cell
#9 is a mine
#10 is a cleared cell

#clean this code
class Window(tk.Frame):
    def __init__(self,master=None):
        tk.Frame.__init__(self,master)
        self.master=master
        self.master.eval("tk::PlaceWindow %s center"% self.master.winfo_pathname(self.master.winfo_id()))
        self.master.title("MineSweeper")
        try:
            self.master.iconphoto(True,tk.PhotoImage(file='mine.png'))
        except:
            pass
        
        self.sizes={#MinesXcolumnsXrows
            'Small' :'10x9x9',
            'Medium':'40x16x16',
            'Large' :'99x30x16',
            'Custom':'10x9x9'}
        
        self.styles={#window.#border.#CellOG.#CellCl.#MineCl.#FontFG.#DisableFont.#activeBG
            'Light' :"#EEEEEE.#FFFFFF.#EEEEEE.#E6E6E6.#FF0000.#000000.#000000.#FFFFFF",
            'Dark'  :"#333333.#111111.#000000.#222222.#FF0000.#FFFFFF.#FFFFFF.#000000",
            'Ocean' :"#2211DD.#00DDDD.#22BBFF.#0344BB.#00FFBB.#FFFFFF.#FFFFFF.#FFFFFF",
            'Fall'  :"#EE7700.#EE6600.#EE5500.#773F00.#FF0000.#FFFFFF.#FFFFFF.#FFFFFF",
            'Spring':"#99FF99.#00FF00.#119933.#009900.#FFCC00.#000000.#000000.#FFFFFF",
            'Winter':"#FFFFFF.#FFFFFF.#FFFFFF.#FFFFFF.#FFFFFF.#FFFFFF.#FFFFFF.#FFFFFF"}
        
        
        
        #config variables
        self.create_menu()
        self.colours=self.styles[self.board_style_val.get()].split('.')
        #[0]window background
        #[1]frame background
        #[2]cell background
        #[3]clicked cell background
        #[4]clicked mine background
        #[5]font foreground
        #[6]Disabled Foreground
        
        #split the size value into the following
        self.mines = int(self.sizes[self.board_size_val.get()].split('x')[0])
        self.dimensions = [int(self.sizes[self.board_size_val.get()].split('x')[1]),int(self.sizes[self.board_size_val.get()].split('x')[2])]
        #calculate the size of the window with 20pixel borders(20*2=40) with the square size being 28
        #windows
        if os.name=='nt':
            self.window_geometry = f'{(28*self.dimensions[0])+40}x{(28*self.dimensions[1])+61}' #self.sizes[self.board_size_val.get()].split('-')[2][:-2]+"20"#first time open
        else:
            self.window_geometry = f'{(32*self.dimensions[0])+40}x{(32*self.dimensions[1])+61}'
        
        self.configure(background=self.colours[0])
        #self.master.resizable(0,0)
        self.pack(fill=tk.BOTH,expand=1)
        self.master.geometry(self.window_geometry)
        timerframe = tk.Frame(self,width=80,height=20,relief='raised')#,borderwidth=2)
        timerframe.grid(row=0,column=0)
        timerframe.pack_propagate(0)
        self.timer=0
        self.board = tk.Frame(self,borderwidth=3,background=self.colours[1],relief='raised')
        self.timer_label = tk.Label(timerframe,text=self.timer)#,width=4)
        self.timer_label.pack()
        
        self.create_board(self.dimensions[0],self.dimensions[1])
        
        self.board.grid(row=1,column=0,padx=17)
        self.board_grid=[[ 0 for x in range(self.dimensions[0])] for y in range(self.dimensions[1])]
        self.first_move=True
        self.master.protocol("WM_DELETE_WINDOW",lambda:os._exit(1))
        if self.allow_first_turn_loss.get() == True:
            self.start_game_random_start()

    def create_menu(self):
        def toGitHub():
            webbrowser.open_new('https://github.com/Pineapplepunch/Minesweeper')
            
        self.board_style_val = tk.StringVar()
        self.board_size_val = tk.StringVar()
        self.allow_qmark = tk.BooleanVar()
        self.allow_first_turn_loss = tk.BooleanVar()
        self.load_user_settings()
        self.prev_size = self.board_size_val.get()
        
        
        self.menubar = tk.Menu(self)
        self.game_menu = tk.Menu(self.menubar,tearoff=0)
        self.help_menu = tk.Menu(self.menubar,tearoff=0)
        self.board_size_menu = tk.Menu(self.game_menu,tearoff=0)
        self.board_style_menu = tk.Menu(self.game_menu,tearoff=0)

        self.menubar.add_cascade(label='Game',menu=self.game_menu)
        self.menubar.add_cascade(label='Help',menu=self.help_menu)
        #self.menubar.add_command(label='Debug')
        
        self.game_menu.add_command(label='New Game',accelerator='F2',command=self.start_new_game)
        self.game_menu.add_separator()
        self.game_menu.add_command(label='Statistics',accelerator='F4',command=self.show_statistics_window)
        self.game_menu.add_command(label='Options',accelerator='F5',command=self.options_window)
        self.game_menu.add_separator()
        
        #self.game_menu.add_command(label='Change Appearance',accelerator='F7',command=self.change_board_style)
        self.game_menu.add_cascade(label='Change Appearance',menu=self.board_style_menu)#,command=self.change_board_style)
        for style in self.styles:
            self.board_style_menu.add_radiobutton(label=style,variable=self.board_style_val,command=self.change_board_style)
        
        self.game_menu.add_cascade(label='Change Board',menu=self.board_size_menu)
        for size in self.sizes:
            self.board_size_menu.add_radiobutton(label=size,variable=self.board_size_val,command=self.change_board_size)

        self.game_menu.add_separator()
        self.game_menu.add_command(label='Exit',command= lambda: os._exit(1))
        
        self.help_menu.add_command(label='Link to Github', command=toGitHub )
        
        self.master.bind('<KeyPress-F2>',lambda e: self.start_new_game())
        self.master.bind('<KeyPress-F4>',lambda e: self.show_statistics_window())
        self.master.bind('<KeyPress-F5>',lambda e: self.options_window())
        #self.master.bind('<KeyPress-F7>',lambda e: self.change_board_style())
        
        self.master.config(menu=self.menubar)
    
    def str_to_bool(self,str):return str=='True'
    
    def load_user_settings(self):
        if not os.path.isfile('ms_settings.ini'):
            with open('ms_settings.ini','w') as fw:
                fw.write('size:Small\n')
                fw.write('style:Light\n')
                fw.write('custom_dimension:10x9x9\n')
                fw.write('first_turn_loss:False\n')
                fw.write('allow_question_mark:True\n')
                self.board_size_val.set('Small')
                self.board_style_val.set('Light')
                self.sizes['Custom']='10x9x9'
                self.allow_first_turn_loss.set(False)
                self.allow_qmark.set(False)
        else:
            with open('ms_settings.ini','r')as fr:
                lines=fr.readlines()
            for line in lines:
                if re.search('size',line):
                    self.board_size_val.set(line.split(':')[1].strip())
                if re.search('style',line):
                    self.board_style_val.set(line.split(':')[1].strip())
                if re.search('custom_dimension',line):
                    self.sizes['Custom'] = line.split(':')[1].strip() 
                    self.sanitize_saved_custom_size()
                if re.search('first_turn_loss',line):
                    self.allow_first_turn_loss.set(self.str_to_bool(line.split(':')[1].strip()))
                if re.search('allow_question_mark',line):
                    self.allow_qmark.set(self.str_to_bool(line.split(':')[1].strip()))
            self.on_settings_change()
            
    def sanitize_saved_custom_size(self):
        arr = self.sizes['Custom'].split('x')
        if len(arr) < 3:
            self.sizes['Custom'] = '10x9x9'
        else:    
            if not int(arr[0]) in range(10,661):
                arr[0]=10
            if not int(arr[1]) in range(9,31):
                arr[1]=9
            if not int(arr[2]) in range(9,25):
                arr[2]=9
            if int(arr[0]) > int(arr[1])*int(arr[2]):
                arr[0] = (arr[1]*arr[2])-1
            self.sizes['Custom']='x'.join(map(str,arr))

    def change_board_style(self):
        self.colours=self.styles[self.board_style_val.get()].split('.')
        self.configure(background=self.colours[0])
        self.board.configure(background=self.colours[1])
        
        for row in self.button_board:
            for button in row:
                button.configure(image=None)
                if button['state']=='disabled':
                    button.configure(background=self.colours[3])
                    button.configure(disabledforeground=self.colours[6])
                else:
                    button.configure(background=self.colours[2])
                    button.configure(foreground=self.colours[5])
        self.on_settings_change()
        
    def change_board_size(self):
        if not self.first_move:
            self.after_cancel(self._job)
            yn = messagebox.askyesno('Really change Size?',"If you change sizes this game\nwill reset and count as a loss")
            if yn:
                self.restart()
                for row in self.button_board:
                    for button in row:
                        button.destroy()
                self.mines = int(self.sizes[self.board_size_val.get()].split('x')[0])
                self.dimensions = [int(self.sizes[self.board_size_val.get()].split('x')[1]),int(self.sizes[self.board_size_val.get()].split('x')[2])]
                if os.name=='nt':
	                self.window_geometry = f'{(28*self.dimensions[0])+40}x{(28*self.dimensions[1])+41}' #self.sizes[self.board_size_val.get()].split('-')[2][:-2]+"20"#first time open
                else:
                    self.window_geometry = f'{(37*self.dimensions[0])+25}x{(34*self.dimensions[1])+15}'

                
                self.master.geometry(self.window_geometry)
                self.create_board(self.dimensions[0],self.dimensions[1])
                self.board_grid=[[ 0 for x in range(self.dimensions[0])] for y in range(self.dimensions[1])]
                self.first_move=True
                self.prev_size = self.board_size_val.get()
            else:
                self.board_size_val.set(self.prev_size)
                self.update_timer()
        else:
            self.restart()
            for row in self.button_board:
                for button in row:
                    button.destroy()
                
            self.mines = int(self.sizes[self.board_size_val.get()].split('x')[0])
            self.dimensions = [int(self.sizes[self.board_size_val.get()].split('x')[1]),int(self.sizes[self.board_size_val.get()].split('x')[2])]
            self.window_geometry = f'{(28*self.dimensions[0])+40}x{(28*self.dimensions[1])+41}' #self.sizes[self.board_size_val.get()].split('-')[2][:-2]+"20"#first time open
                
            self.master.geometry(self.window_geometry)
            self.create_board(self.dimensions[0],self.dimensions[1])
            self.board_grid=[[ 0 for x in range(self.dimensions[0])] for y in range(self.dimensions[1])]
            self.first_move=True
            self.prev_size = self.board_size_val.get()
        self.on_settings_change()
    
    def on_settings_change(self):
        with open('ms_settings.ini','r')as file:
            lines = file.readlines()
            if not lines[0].split(':')[1].strip()==self.board_size_val.get():
                lines[0] = lines[0][:5]+self.board_size_val.get()+'\n'
            if not lines[1].split(':')[1].strip()==self.board_style_val.get():
                lines[1] = lines[1][:6]+self.board_style_val.get()+'\n'
            if not lines[2].split(':')[1].strip()==self.sizes['Custom']:
                lines[2] = lines[2][:17]+self.sizes['Custom']+'\n'
            if not lines[3].split(':')[1].strip()==self.allow_first_turn_loss.get():
                lines[3] = lines[3][:16]+str(self.allow_first_turn_loss.get())+'\n'
            if not lines[4].split(':')[1].strip()==self.allow_qmark.get():
                lines[4] = lines[4][:20]+str(self.allow_qmark.get())+'\n'
        with open('ms_settings.ini','w')as file:
            file.writelines(lines)
    
    def update_timer(self):
        self.timer+=1
        self.timer_label['text']=self.timer
        self._job = self.master.after(1000,self.update_timer)
        
    def printb(self):
        for x in self.board_grid:
            for y in x:
                print(y,end=" ")
            print()        
        
    def create_board(self,rows,columns):
        self.button_board=[]
        self.onepixel = tk.PhotoImage()
        self.onepixel.blank()
        for x in range(columns):
            self.button_board.append([])
            for y in range(rows):
                #https://stackoverflow.com/questions/46284901/how-do-i-resize-buttons-in-pixels-tkinter
                #one pixel image
                # 2+20+2
                b = tk.Button(self.board,text=" ",borderwidth=2,relief='raised',background=self.colours[2],foreground=self.colours[5],disabledforeground=self.colours[6],command= lambda x=x,y=y: self.clicked_cell(x,y))
                b.configure(width=20,height=20,image=self.onepixel,compound=tk.CENTER)
                if os.name!='nt':
                    b.configure(width=1,height=15,image=self.onepixel,compound=tk.CENTER)
                b.bind('<Button-2>',lambda event, y=y,x=x: self.flagged_cell(x,y))
                b.bind('<Button-3>',lambda event, y=y,x=x: self.exclude_cell(x,y))
                b.grid(row=x+1,column=y+1,sticky='nesw',padx=0,pady=0)
                self.button_board[x].append(b)
    
    def is_valid(self,x,y):return (x>=0) and (x<self.dimensions[1]) and (y>=0) and (y<self.dimensions[0])
    
    def place_mine(self,x,y):
        randx = random.randint(0,self.dimensions[0]-1)#random row
        randy = random.randint(0,self.dimensions[1]-1)#random column
        if not self.board_grid[randy][randx]==9 and randx!=x and randy!=y and randx!=self.frow and randy!=self.frow: #if the board is not already a min and if the random row and column is not the clicked cell
            self.board_grid[randy][randx]=9#set the cell as a mine
        else:
            #print("location already contains mine")
            self.place_mine(x,y)#else continue to attempt placing mines
    
    def start_game_random_start(self):
        randx = random.randint(0,self.dimensions[0]-1)#random row
        randy = random.randint(0,self.dimensions[1]-1)#random column
        self.start_game(randx,randy)
        
    def start_game(self,x,y):
        #print("Clicked:",x,y)
        self.fcol=y
        self.frow=x
        for i in range(self.mines):#for each allowed mine
            self.place_mine(x,y)#sets mine on non player clicked cell
        #print("Mines have been set")
        #self.printb()
        counter=0    
        #generates the hints on the board using a hidden logical board
        
        for i in range(len(self.board_grid)):
            for j in range(len(self.board_grid[i])):
                if self.board_grid[i][j]!=9:
                    if self.is_valid(i-1,j)   and self.board_grid[i-1][j]==9: counter+=1   #N
                    if self.is_valid(i-1,j-1) and self.board_grid[i-1][j-1]==9: counter+=1 #NW
                    if self.is_valid(i-1,j+1) and self.board_grid[i-1][j+1]==9: counter+=1 #NE
                    if self.is_valid(i+1,j)   and self.board_grid[i+1][j]==9: counter+=1   #S
                    if self.is_valid(i+1,j-1) and self.board_grid[i+1][j-1]==9: counter+=1 #SW
                    if self.is_valid(i+1,j+1) and self.board_grid[i+1][j+1]==9: counter+=1 #SE
                    if self.is_valid(i,j-1)   and self.board_grid[i][j-1]==9: counter+=1   #W
                    if self.is_valid(i,j+1)   and self.board_grid[i][j+1]==9: counter+=1   #E
                    self.board_grid[i][j]=counter
                counter=0
        #print("Set Hints")
        #self.printb()
       
    def check_adjacent(self,x,y):   
        if self.button_board[x][y]['relief']=='raised':#if tile covered
            self.button_board[x][y]['relief']='sunken'#uncover tile
            self.button_board[x][y]['state']='disabled'
            self.button_board[x][y].configure(bg=self.colours[3])#colour cell to theme
            self.button_board[x][y].configure(disabledforeground=self.colours[6])
            if self.board_grid[x][y] in range(1,8):#if cell has surround mine
                self.button_board[x][y]['text'] = self.board_grid[x][y]#set text on cell
            else: #else no surrounding mine
                if self.button_board[x][y]['text']!=' ':
                    self.button_board[x][y]['text']=' '
                if x > 0:
                    self.check_adjacent(x-1,y)
                if x < len(self.board_grid)-1:
                    self.check_adjacent(x+1,y)
                if y > 0:
                    self.check_adjacent(x,y-1)
                if y < len(self.board_grid[x])-1:
                    self.check_adjacent(x,y+1)
               
    def clicked_cell(self,row,column):
        #change to allow loss on first turn
        #self.printb()
        if self.allow_first_turn_loss.get() == True and self.timer==0:
            self.update_timer()
            self.first_move=False
            
        if self.first_move == False:#first move will never end the game
            if self.button_board[row][column]['text']=='(X)':#if X do not proceed
                print("locked")
            else: 
                if self.board_grid[row][column]==9:#if the tile clicked is a mine
                    self.after_cancel(self._job)#stop timer
                    self.button_board[row][column]['relief']='sunken'#uncover tile
                    for i in range(len(self.button_board)):
                        for j in range(len(self.button_board[i])):
                            if self.button_board[i][j]['text'] == "(X)":
                               self.button_board[i][j]['text'] = " X " 
                            else:#Clean up lose animation 
                                if self.board_grid[i][j] == 0 :
                                    self.button_board[i][j]['relief']='sunken'#self.board_grid[i][j]#force all buttons open
                                    self.button_board[i][j].configure(bg=self.colours[3])#colour cell to light grey            
                                elif self.board_grid[i][j] !=0 and self.board_grid[i][j]!=9:
                                    self.button_board[i][j]['text']=self.board_grid[i][j]#force all buttons open
                            if self.board_grid[i][j]== 9:
                                if self.button_board[i][j]['text']!=" X ": self.button_board[i][j]['text']='☼'
                                self.button_board[i][j].configure(bg=self.colours[4],fg=self.colours[5])
                            self.button_board[i][j]['state']='disabled'#game ends
                    self.game_end(False)
                else:#if the tile clicked is not a mine
                    try:
                        self.check_adjacent(row,column)
                    except Exception as e:
                        print(e,row,column)                 
                    win_count=0
                    for i in range(len(self.button_board)):
                        for j in range(len(self.button_board[i])):
                            if self.button_board[i][j]['state']=='disabled':win_count+=1
                    if win_count == (len(self.button_board)*len(self.button_board[1])-self.mines):
                        self.after_cancel(self._job)
                        self.game_end(True)
        elif self.first_move==True:
            self.first_move=False#Flag disabled game will now start
            self.start_game(row,column)#Spawns mines over the board
            self.clicked_cell(row,column)#recalls the method to start the game
            self.update_timer()#starts the game timer
  
    def flagged_cell(self,row,column):
        if self.allow_qmark.get()==True:
            if self.button_board[row][column]['state']!= 'disabled':
                if self.button_board[row][column]['text'] !="(X)":#if not X change to ?
                    self.button_board[row][column]['text']="(?)"
                elif self.button_board[row][column]['text']=="(?)":
                    self.button_board[row][column]['text']=" "
        
    def exclude_cell(self,row,column):
        if self.button_board[row][column]['state']!= 'disabled':
            if self.button_board[row][column]['text'] !="(X)":#if not X change to X
                self.button_board[row][column]['text']="(X)"
            elif self.button_board[row][column]['text'] =="(?)":#if ? change to X
                self.button_board[row][column]['text']="(X)"
            elif self.button_board[row][column]['text'] =="(X)":#if X change to blank
                self.button_board[row][column]['text']=" "
    
    def log(self,is_win):
        if not os.path.isfile('stats'):
            with open('stats','w+') as f:
                losses = 1 if not is_win else 0
                wins = 1 if is_win else 0
                f.write('1|{}|{}\n'.format(losses,wins))
            os.chmod('stats',S_IREAD)
        else:
            os.chmod('stats',S_IREAD| S_IWRITE)
            with open('stats','r+')as f:
                stats = list(map(int,f.readline().strip().split('|')))
                scores=f.readlines()
            os.chmod('stats',S_IREAD)
            #scores.pop(0)
            #scores = scores[:1]
            stats[0] += 1
            stats[1] += 1 if not is_win else 0
            stats[2] += 1 if is_win else 0
            stats= '{}|{}|{}\n'.format(stats[0],stats[1],stats[2])
            if is_win:
                scores.append('{}|{}|{} Seconds\n'.format(self.board_size_val.get(),datetime.now().strftime('%m/%d/%Y'),str(self.timer)))
            os.chmod('stats',S_IREAD| S_IWRITE)
            with open('stats','w+')as f:
                f.write(stats)
                f.writelines(scores)
            os.chmod('stats',S_IREAD)
            shortest_time=99999
            for i in scores:
                if re.search(self.board_size_val.get(),i):
                    temp = int(i.split('|')[-1].split(' ')[0])
                    if temp < shortest_time: shortest_time=temp
            return shortest_time  

    def game_end(self,is_win):
        self.end = tk.Toplevel(self)
        self.end.resizable(0,0)
        self.end.geometry(f'+{self.master.winfo_x()}+{self.master.winfo_y()}')
        self.end.grab_set()
        self.log(is_win)
        stats,topscores = self.get_saved_stats()
        
        message = 'You Lost, Try again?' if is_win==False else 'Congratulations, You Won the Game!'
        
        
        game_end_message = tk.Label(self.end,text=message,font=('Consolas',15))
        time_taken = tk.Label(self.end,text=f'Time: {self.timer} Seconds')
        date = tk.Label(self.end,text=f'Date: {datetime.now().strftime("%m/%d/%Y")}')
        s_best_time = tk.Label(self.end,text=f'Best Time(Small): {topscores[0]} Seconds')
        m_best_time = tk.Label(self.end,text=f'Best Time(Medium): {topscores[1]} Seconds')
        l_best_time = tk.Label(self.end,text=f'Best Time(Large): {topscores[2]} Seconds')
        games_won = tk.Label(self.end,text=f'Games Won: {stats[2]}')
        games_played = tk.Label(self.end,text=f'Games Played: {stats[0]}')
        percentage = tk.Label(self.end,text=f'Win Percentage: {(stats[2]/stats[0])*100:0.02f}%')
        
        playagain = tk.Button(self.end,text='Play Again?',command=lambda: [self.restart(),self.exit_sub_window(self.end)])
        exit_game = tk.Button(self.end,text='Exit Game',command= lambda: os._exit(1))
        
        game_end_message.grid(row=0,column=0,columnspan=2,sticky='nwse',padx=50,pady=10)
        time_taken.grid(row=1,column=0,sticky='w',padx=15)
        date.grid(row=1,column=1,sticky='w',padx=15)
        tk.Label(self.end).grid(row=2)
        
        s_best_time.grid(row=3,column=0,sticky='w',padx=15)
        m_best_time.grid(row=4,column=0,sticky='w',padx=15)
        l_best_time.grid(row=5,column=0,sticky='w',padx=15)
        tk.Label(self.end).grid(row=6)
        
        games_played.grid(row=7,column=0,sticky='w',padx=15)
        games_won.grid(row=8,column=0,sticky='w',padx=15)
        percentage.grid(row=8,column=1,sticky='w',padx=15)
        tk.Label(self.end).grid(row=9)
        
        playagain.grid(row=10,column=0,sticky='n')
        exit_game.grid(row=10,column=1,sticky='n')
        tk.Label(self.end).grid(row=11)
    
    '''    Better one made
    def end_game(self,is_win):
        s_time = self.log(is_win)
        best_game=''
        if not s_time == 99999:
            best_game = 'Your best time was: {} for the {} board\n'.format(s_time,self.board_size_val.get())
        if is_win:#Incorporate a quickest time completion, using log() and return
            yn = messagebox.askyesno('You Win','You Won!\nYour time: '+str(self.timer)+" Seconds\n"+best_game+"Play again?")
        else:
            yn = messagebox.askyesno('You Lose','You Lost!\nPlay Again?')
        if yn:
            self.restart()
        else:
            os._exit(1)'''
          
    def restart(self):
        self.first_move=True
        self.timer=0
        self.timer_label['text']=0
        for i in range(len(self.board_grid)):
            for j in range(len(self.board_grid[i])):
                self.button_board[i][j]['text']=" "
                self.button_board[i][j]['relief']="raised"
                self.button_board[i][j]['state']="normal"
                self.button_board[i][j].configure(bg=self.colours[2])
                self.board_grid[i][j]=0
        if self.allow_first_turn_loss.get() == True:
            self.start_game_random_start()
        
    def start_new_game(self):
        if self.timer!=0:#self.first_move==False:
            self.game_end(False)
        self.after_cancel(self._job)
        self.restart()
    
    def options_window(self):
        if self.timer!=0:#self.first_move==False:
            self.after_cancel(self._job)

        def callback():
            if self.board_size_val.get()=='Custom':
                rows['state']='normal'
                columns['state']='normal'
                mines['state']='normal'
                r_label['state']='normal'
                c_label['state']='normal'
                m_label['state']='normal'

            elif self.board_size_val.get() !='Custom':
                rows['state']='disabled'
                columns['state']='disabled'
                mines['state']='disabled'
                r_label['state']='disabled'
                c_label['state']='disabled'
                m_label['state']='disabled'
        def stylecallback():
            pass
        self.options_window = tk.Toplevel(self)
        self.options_window.grab_set()
        self.options_window.resizable(0,0)
        self.options_window.geometry(f'+{self.master.winfo_x()}+{self.master.winfo_y()}')
        
#        self.options_window.geometry('350x350')
        size_grouping = tk.LabelFrame(self.options_window,text='Size',padx=5,pady=5)
        size_grouping.grid(columnspan=2,padx=20,pady=20)
        style_grouping = tk.LabelFrame(self.options_window,text='Style',padx=10,pady=10)
        style_grouping.grid(row=1,column=0,columnspan=2,padx=20)
        
        #radio button board_size
        
        
        
        defaults = tk.Frame(size_grouping)
        defaults.grid(row=0,column=0)
        
        stylelist = tk.Frame(style_grouping)
        stylelist.grid(row=0,column=1)
        
        small_grid = tk.Radiobutton(defaults,text='Small\n10 Mines\n9x9 Grid',variable=self.board_size_val,value='Small',command=callback)
        medium_grid = tk.Radiobutton(defaults,text='Medium\n40 Mines\n16x16 Grid',variable=self.board_size_val,value='Medium',command=callback)
        large_grid = tk.Radiobutton(defaults,text='Large\n99 Mines\n16x30 Grid',variable=self.board_size_val,value='Large',command=callback)
        small_grid.grid(column=0,sticky='w')
        medium_grid.grid(column=0,sticky='w')
        large_grid.grid(column=0,sticky='w')
        
        inputframe = tk.Frame(size_grouping)
        inputframe.grid(row=0,column=1,sticky='nw',pady=15)
        
        self.cust_row_v = tk.StringVar()
        self.cust_col_v = tk.StringVar()
        self.cust_mine_v = tk.StringVar()
        
        self.cust_mine_v.set(self.sizes['Custom'].split('x')[0])
        self.cust_col_v.set(self.sizes['Custom'].split('x')[1])
        self.cust_row_v.set(self.sizes['Custom'].split('x')[2])
       
        custom_grid = tk.Radiobutton(inputframe,text='Custom',variable=self.board_size_val,value='Custom',command=callback)
        custom_grid.grid(sticky='w')
       
        r_label=tk.Label(inputframe,text='Rows(9-24)',state='disabled')
        r_label.grid(row=1,column=0,sticky='w')
        c_label=tk.Label(inputframe,text='Columns(9-30)',state='disabled')
        c_label.grid(row=2,column=0,sticky='w')
        m_label=tk.Label(inputframe,text='Mines(10-660)',state='disabled')
        m_label.grid(row=3,column=0,sticky='w')
        rows= tk.Entry(inputframe,textvariable=self.cust_row_v,state='disabled',width=4)
        columns= tk.Entry(inputframe,textvariable=self.cust_col_v,state='disabled',width=4)
        mines= tk.Entry(inputframe,textvariable=self.cust_mine_v,state='disabled',width=4)
        
        rows.grid(row=1,column=1)
        columns.grid(row=2,column=1)
        mines.grid(row=3,column=1)
        
        
        
        style_arr=[]
        count=1
        for _key,_value in self.styles.items():
            rb = tk.Radiobutton(stylelist,text=_key,value=_key,variable=self.board_style_val,command=stylecallback)
            rb.grid(row=count,sticky='w')
            arr = _value.split('.')
            for i,color in enumerate(arr):
                tk.Button(stylelist,width=2,state='disabled',background=color).grid(row=count,column=i+1)
            style_arr.append(rb)
            count+=1
        
        tk.Label(self.options_window).grid()
        qmark_box = tk.Checkbutton(self.options_window,justify='left',text='Allow the (?) Flag on cells\n(middle mouse button)',variable=self.allow_qmark)
        qmark_box.grid(row=4,sticky='w',padx=15,columnspan=2)
        
        osp = tk.Checkbutton(self.options_window,justify='left',text='Allow loss on first turn',variable=self.allow_first_turn_loss)
        osp.grid(row=6,columnspan=2,sticky='w',padx=15)
        tk.Label(self.options_window).grid()
        
        confirm_changes = tk.Button(self.options_window,text='Confirm',width=10,command=lambda:self.save_settings(self.options_window))
        cancel_changes = tk.Button(self.options_window,text='Cancel',width=10,command=lambda:self.revert_settings(self.options_window))
        confirm_changes.grid(row=8,column=0)
        cancel_changes.grid(row=8,column=1)
        tk.Label(self.options_window).grid()
    
        callback()
    
    def revert_settings(self,window):
        #open file and load settings
        self.load_user_settings()
        self.exit_sub_window(window)
    def save_settings(self,window):
        if self.validate_custom_size():
            #self.c_size_change = f'{self.cust_mine_v.get()}x{self.cust_row_v.get()}x{self.cust_col_v.get()}'
            self.sizes['Custom'] = f'{self.cust_mine_v.get()}x{self.cust_col_v.get()}x{self.cust_row_v.get()}'
            self.change_board_size()
            self.change_board_style()    
            self.exit_sub_window(window)
        else:
            messagebox.showerror('Error','Custom Grid is not valid\nMines: 10-660\nRows: 9-24\nColumns: 9-30')
    def validate_custom_size(self):
        return int(self.cust_mine_v.get()) in range(10,661) and int(self.cust_col_v.get()) in range(9,31) and int(self.cust_row_v.get()) in range(9,25) and int(self.cust_mine_v.get()) < (int(self.cust_row_v.get())*int(self.cust_row_v.get()))
            
    
    def show_statistics_window(self):
        if self.timer!=0:#self.first_move==False:
            self.after_cancel(self._job)
        
        stats,topscores = self.get_saved_stats()
        self.stats_window = tk.Toplevel(self)
        self.stats_window.grab_set()
        #self.stats_window.geometry('210x235')
        self.stats_window.resizable(0,0)
        self.stats_window.geometry(f'+{self.master.winfo_x()}+{self.master.winfo_y()}')
        
        f= tk.Frame(self.stats_window)
        #f.pack(fill=tk.BOTH,expand=1)
        f.grid(row=0,column=0,sticky='nwse')
        f.grid_rowconfigure(0,weight=1)
        f.grid_columnconfigure(0,weight=1)

        lf = ('Ariel',20)
        tk.Label(f,text='Minesweeper',font = lf).grid(row=0,column=0,columnspan=2,sticky='we')
        
        for title in ('Total Games:','Wins:','Losses:','Win/Losses:'):
            tk.Label(f,text=title).grid(sticky='e',padx=20)
        
        self.games_played = tk.Label(f,text=stats[0])
        self.losseslabel = tk.Label(f,text=stats[1])
        self.winslabel = tk.Label(f,text=stats[2])
        self.percentlabel = tk.Label(f,text=f'{(stats[2]/stats[0])*100:0.2f}%')
        
        self.games_played.grid(row=1,column=1,padx=20,sticky='w')
        self.losseslabel.grid(row=3,column=1,padx=20,sticky='w')
        self.winslabel.grid(row=2,column=1,padx=20,sticky='w')
        self.percentlabel.grid(row=4,column=1,padx=20,sticky='w')
        #self.stats_window.grid_rowconfigure(0,weight=1)
        self.stats_window.grid_columnconfigure(0,weight=1)
        
        tk.Label(f,text='Best Times',font=('Ariel',12)).grid(sticky='nwse',columnspan=2)
        
        for title in ('Small: ','Medium: ','Large: ','Custom:'):
            tk.Label(f,text=title).grid(sticky='e',padx=20)
            
        self.small_best = tk.Label(f,text=f'{topscores[0]} seconds')
        self.medium_best = tk.Label(f,text=f'{topscores[1]} seconds')
        self.large_best = tk.Label(f,text=f'{topscores[2]} seconds')
        self.custom_best = tk.Label(f,text=f'{topscores[2]} seconds')
        
        self.small_best.grid(row=6,column=1,padx=20,sticky='w')
        self.medium_best.grid(row=7,column=1,padx=20,sticky='w')
        self.large_best.grid(row=8,column=1,padx=20,sticky='w')
        self.custom_best.grid(row=9,column=1,padx=20,sticky='w')
        
        self.exit_stats_button = tk.Button(f,text='Continue',command=lambda:self.exit_sub_window(self.stats_window))
        self.exit_stats_button.grid(columnspan=2,sticky='nwse')
        
    def get_saved_stats(self):
        if not os.path.isfile('stats'):
            with open('stats','w') as f:
                f.write('0|0|0\n')
            
        os.chmod('stats',S_IREAD|S_IWRITE)
        with open('stats','r+') as f:
            stats = list(map(int,f.readline().strip().split('|')))
            wins= f.readlines()
        os.chmod('stats',S_IREAD)
        topscores=['na','na','na','na']
        for score in wins:
            temp = int(score.split('|')[-1].split(' ')[0])
            if re.search('Small',score):
                if topscores[0]=='na' or temp < topscores[0]:topscores[0] = temp
            elif re.search('Medium',score):
                if topscores[1]=='na' or temp < topscores[1]:topscores[1] = temp
            elif re.search('Large',score):
                if topscores[2]=='na' or temp < topscores[2]:topscores[2] = temp
            elif re.search('Custom',score):
                if topscores[3]=='na' or temp < topscores[3]:topscores[3] = temp
            #print(int(score.split('|')[-1].split(' ')[0]))
        for i,ts in enumerate(topscores):
            if ts=='na':
                topscores[i]=0
        return stats,topscores
   
    def exit_sub_window(self,window):
        if self.timer!=0: #self.first_move==False:
            self.update_timer()
        window.destroy()


        
if __name__ =='__main__': 
    root = tk.Tk()
    app = Window(root)
    root.mainloop()

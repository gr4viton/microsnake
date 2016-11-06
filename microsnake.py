import pyb
from pyb import I2C 

import math

import os
#import random
import gc

#from main import move_arrow_pressed
#from machine import Pins
#move_arrow_pressed = None
#from shared_globals import move_arrow_pressed 
import shared_globals

class MicroSnakeGame():

    def __init__(q, disp_field_function):
        q.disp_field = disp_field_function
#        q.move_arrow_pressed = move_arrow_pressed

        q.init_game()
        q.printing = False

    def init_game(q):

        MicroSnakeGame.turned = False
        MicroSnakeGame.turn_time = 0
        MicroSnakeGame.turn_delay = 200

        q.pos_min = [0, 0]
        q.pos_max = [16,8]
#        vel = [1,0]
        
        q.vels = [[1,0], [0,1], [-1,0], [0,-1]]

        q.way_vel = {}
        def add_ways(ways):
            d = { way: i for way, i in zip(ways, range(len(ways)))}
            q.way_vel.update(d)
        add_ways('left down right up'.split())
        add_ways(list('ldru'))
        add_ways(range(len(q.vels)))

        

        q.vel = 0

        q.start_length = 5
        q.snake = [[i, 0] for i in range(q.start_length)]

        q.head = q.start_length-1
        q.tail = 0

        q.null_char, q.head_char, q.tail_char, q.dot_char = \
            list(' o x')

        w, h = q.pos_max
        q.field = [[q.null_char for x in range(w)] for y in range(h)] 
        
        q.dot_pos = [pos-1 for pos in q.pos_max]
        
        q.update_chars = []
        for pos in q.snake:
            q.print_char(pos, q.head_char)


        q.step = 0
        


        shared_globals.field = q.field
        shared_globals.line_max = q.pos_max[1]
        q.update_field_dict()
        
        q.last_sent_field = q.field
#        shared_globals.field_lines = 
#        shared_globals.bytefield = q.byte_field

        shared_globals.line_range = range(len(q.field))
#        shared_globals.char_range = range(len(q.field[0]))
        
        pyb.delay(200)

    def run(q):
        q.game_loop()


    def update_field_dict(q):
        field_dict = {}

        for line_num in range(len(q.field)):
            line = q.field[line_num]
            lcd_line_num = line_num % 2
            
            lcd_num = math.floor(line_num/2) % 4

            
            field_dict.update({line_num : [line, lcd_num, lcd_line_num]})
#            q.lcds[lcd_num].disp(line, lcd_line_num)


        shared_globals.field_dict = field_dict
    
    def get_lcd_coords(q, line_num, i):
        lcd_line_num = line_num % 2
            
        lcd_num = math.floor(line_num/2) % 4
        return lcd_num, lcd_line_num

    def send_udpate_chars(q, update_chars=[]):
        print(q.field)
        print(q.last_sent_field)
        for line_num in range(len(q.field)):
            for i in range(len(q.field[line_num])):
#                print(q.field)
                new_char = q.field[line_num][i]

                if new_char != q.last_sent_field[line_num][i]:

                    lcd_num, lcd_line_num = q.get_lcd_coords(line_num, i)
                    char = [lcd_num, lcd_line_num, i, new_char]
                    update_chars.append(char)

        print(update_chars)
        shared_globals.update_chars.extend(update_chars)
        print(shared_globals.update_chars)




    def update_field_lines(q):
        
        field_lines = []
        for line_num in range(len(q.field)):
            field_lines.append( ''.join(q.field[line_num]) )
            
        shared_globals.field_lines = field_lines


    def turn(q, heading=1):
        if heading == 'left':
            heading = 1
        elif heading == 'right':
            heading = -1
        
        if heading != 1 and heading != -1:
            q.print('Not turning! Use "left", "right" or 1, -1 as params!')
            return
        q.vel = (q.vel+dir) % (len(q.vels)-1)
        MicroSnakeGame.turned = False 

    def go_way(q, way='r'):
            
        q.vel = q.vels[q.way_vel[way]]
#        game.go_way('r')

#        player.vel = 


    def print_char(q, pos, new_char):
        q.field[pos[1]][pos[0]] = new_char
        
        lcd_num, lcd_line_num = q.get_lcd_coords(*pos)
        char = [lcd_num, lcd_line_num, pos[1], new_char]
        q.update_chars.append(char)


    def print_head(q):
        q.print_char(q.snake[q.head], q.head_char)
    
    def print_tail(q):
        q.print_char(q.snake[q.tail], q.tail_char)
    
    def print_dot(q):
        q.print_char(q.dot_pos, q.dot_char)
    


    def move(q, pos):
        new_pos = [0,0]
        for i in range(len(pos)):
            new_pos[i] = pos[i] + q.vels[q.vel][i]
            if new_pos[i] >= q.pos_max[i]:
                new_pos[i] = q.pos_min[i]
            elif new_pos[i] < q.pos_min[i]:
                new_pos[i] = q.pos_max[i]-1
        
        q.print('new_pos', new_pos)
        return new_pos

    def set_random_dot(q):
        #
        q.dot_pos = [pyb.rng() % pos_max for pos_max in q.pos_max]
        #q.dot_pos = [random.randrange(max_pos) for max_pos in q.max_pos]

    def check_dot(q, pos):
        got = True
        for i in range(len(pos)):
            if pos[i] != q.dot_pos[i]:
                got = False
        if got:
            q.print('got, new_pos, dot', got, pos, q.dot_pos)
            q.set_random_dot()
        return got

    def handle_input(q):
        move_arrow_pressed = shared_globals.move_arrow_pressed
        q.print('handle_input=', move_arrow_pressed)
        if move_arrow_pressed is not None:
            q.print('TURNED!, ', move_arrow_pressed)
#            q.vel = q.vels[move_arrow_pressed]
            q.vel = move_arrow_pressed
            move_arrow_pressed = None

    def print(q, thing, *args, **kwargs):
        if q.printing:
            print(thing, args, kwargs)

        # DECORATOR!!! USE

    def game_loop(q):
        q.running = True
        while(q.running):
 #           pos = move(pos)
            q.last_sent_field = q.field.copy()
            q.handle_input()
            q.send_udpate_chars(q.update_chars)
            print('last\n', q.last_sent_field)

#            continue
            print('>'*42, 'Step>>', q.step )
#            print('Step>>', q.step)
            q.print('vels[vel] = ', q.vels[q.vel])
            q.print('head,tail = ', q.head, q.tail)
            q.print(q.snake)
            
            q.print('MicroSnakeGame.turned', MicroSnakeGame.turned)
#            if MicroSnakeGame.turned:
 #               print('turning')
  #              q.turn()
            q.handle_input()

            q.print_dot()

            if not 1:
                q.print_tail() 
                q.snake[q.tail] = q.snake[q.head]
                q.snake[q.head] = q.move(q.snake[q.head])
                q.print_head()
                q.tail = (q.tail+1) % (len(q.snake)-2)

            new_pos = q.move(q.snake[q.head])
            got = q.check_dot(new_pos)
            if not got:
                q.print_tail() 
                q.snake[q.tail] = new_pos
            else:
                q.snake.append(q.snake[q.tail])
                q.snake[q.tail] = new_pos

            q.print_head()
            q.head = q.tail
            q.tail = (q.tail+1) % len(q.snake)
            
            q.print('after update')
            
            q.print('head,tail = ', q.head, q.tail)
            q.print(q.snake)
            

            if q.step > q.start_length:
#                print_tail()
                pass

#            q.field = field
#            q.disp_field(q.field)
#            q.preprint_field(q.field)
#            q.update_field_dict()

#            lcd.line('no_map',1)
            q.step += 1

            gc.collect()
            pyb.delay(50)


if __name__ == '__main__':
#    m = MicroSnakeGame()
    print('End of microsnake program!')



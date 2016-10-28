import pyb
from pyb import I2C 

import staccel
import math

import os
import gc # garbage collection for writing?

import lcd_i2c

try: 
    print('try importing pins')
    import pins
except ImportError:
    print('pins not found')

#from machine import Pins

class Machine():
    n = 0
    leds = None

    def on_press(self):
        print('pressed!')
#        print('Machine.turned', Machine.turned)
        act = pyb.millis()
        if (act - Machine.turn_time) > Machine.turn_delay:
            Machine.turned = True
            Machine.turn_time = act
        print('Machine.turned', Machine.turned)

        # print(self.ac.xyz()) # MemoryError:
    def on_tim4(self):
        #lambda t:pyb.LED(3).toggle()
        try:
            n = Machine.n        
            n = (n + 2) % 2
    
            Machine.leds[n].toggle()
            Machine.n = n
        except TypeError as ex:
            #print(ex.strerror)
            print('error')
    
    def __init__(self):
        Machine.turned = False
        Machine.turn_time = 0
        Machine.turn_delay = 200

        Machine.n = 0
        self.init_button()
        #self.show_gpio()

        self.init_lcd()
#        self.demo_lcd()
#        lcd.lcd_init()


        #self.main_loop()
#        self.game_loop()

    def main_loop(self):
        a = 0
        while(1):
            a += 1
            self.demo2_lcd()    
            if a % 100000 == 0:
                #self.demo_lcd()
                pass
            if a == 1000000:
                print(str(a) + 'cycles')
                a = 0
            pass

    def game_loop(self):


        pos_min = [0, 0]
        pos_max = [16,8]
#        vel = [1,0]
        
        vels = [[1,0], [0,1], [-1,0], [0,-1]]
        vel = 0

        start_length = 5
        snake = [[i,0] for i in range(start_length)]

#        head = [start_length-1, 0] # x,y
#        tail = [0, 0]
        head = start_length-1
        tail = 0
#        snake_lenth = start_length

#        line = ['_']*pos_max[0]
#        field = [line] for i in range(pos_max[1])
#        field = [line[:]]*pos_max[1]
        null_char = ' '
#        field = list(pos_max[0], pos_max[1])
        w, h = pos_max
        field = [[null_char for x in range(w)] for y in range(h)] 
#        for x in range(pos_max[0]):
#            for y in range(pos_max[1]):
#                field[x][y] = null

        head_char = 'o'
        tail_char = null_char
#        tail_char = '_'
        get_char = 'x'
        
        get = [pos-1 for pos in pos_max]


        def print_char(pos, char):
            field[pos[1]][pos[0]] = char

        def print_head():
            print_char(snake[head], head_char)
        
        def print_tail():
            print_char(snake[tail], tail_char)
        
        def print_get():
            print_char(get, get_char)
        
        def turn(dir=1):
            if dir == 'left':
                dir = 1
            elif dir == 'right':
                dir = -1
            
            if dir != 1 and dir != -1:
                print('Not turning! Use "left", "right" or 1, -1 as params!')
                return
            vel = (vel+dir) % (len(vels)-1)
            Machine.turned = False 

        def move(pos):
            new_pos = [0,0]
            for q in range(len(pos)):
                new_pos[q] = pos[q] + vels[vel][q]
                if new_pos[q] >= pos_max[q]:
                    new_pos[q] = pos_min[q]
                elif new_pos[q] < pos_min[q]:
                    new_pos[q] = pos_max[q]-1
            
            print('new_pos', new_pos)
            return new_pos

        def check_get(pos):
            got =  True
            for q in range(len(pos)):
                if pos[q] != get[q]:
                    got = False
            
            print('got,new_pos,get',got,pos,get)
            return got

        for pos in snake:
            print_char(pos, head_char)


        running = True
        step = 0
        while(running):
 #           pos = move(pos)

            print('Step>>', step)
            print('vels[vel] = ', vels[vel])
            print('head,tail = ',head, tail)
            print(snake)
            
            print('Machine.turned', Machine.turned)
            if Machine.turned:
                print('turning')
                turn()

            print_get()

            if not 1:
                print_tail() 
                snake[tail] = snake[head]
                snake[head] = move(snake[head])
                print_head()
                tail = (tail+1) % (len(snake)-2)

            new_pos = move(snake[head])
            got = check_get(new_pos)
            if not got:
                print_tail() 
                snake[tail] = new_pos
            else:
                snake.append(snake[tail])
                snake[tail] = new_pos
            print_head()
            head = tail
            tail = (tail+1) % len(snake)
            
            print('after update')
            
            print('head,tail = ',head, tail)
            print(snake)

            if step > start_length:
#                print_tail()
                pass

            for line_num in range(pos_max[1]):
                line = ''.join(field[line_num])
                lcd_line_num = line_num % 2
                lcd_num = (line_num/2) % 4
                self.lcds[lcd_num].disp(line, lcd_line_num)
#            lcd.line('no_map',1)
            step += 1
            pyb.delay(150)

    def init_i2c(self, bus=2, role=I2C.MASTER, baudrate=115200, self_addr=0x42):
        self.i2c = I2C(bus)

        self.addr = self_addr
        self.br = baudrate
        self.i2c.init(role, addr=self.addr, baudrate=self.br)          
                
        print('I2C initialized: self_addr=0x{0:02X} = {0} dec, br={1}'.\
                format(self.addr, self.br))

    def char_range(self, c1, c2):
        """Generates the characters from `c1` to `c2`, inclusive."""
        for c in range(ord(c1), ord(c2)+1):
            yield chr(c)

    def init_lcd(self):

        self.init_i2c()

        scan = self.i2c.scan()
        print('Scanned addresses [dec]:', scan)

        lcd_as = scan
        self.lcds = []
#        self.lcds = [ for as in lcd_as]
        for lcd_a in lcd_as:
            new_lcd = lcd_i2c.lcd1602(self.i2c, lcd_a)
            self.lcds.append(new_lcd)
        

        for i, lcd in enumerate(self.lcds):
            txt = 'Loading...lcd[{}]'.format(i)
            lcd.disp(txt, 0)

        for i, ch in enumerate(self.char_range('a', 'Z')):
            lcd_num = i % len(self.lcds)
            lcd = self.lcds[lcd_num]
            txt = 'lcd[{}] = {}'.format(lcd_num, ch)
            lcd.disp(txt, 0)
            pyb.delay(300)
        
        self.lcd_a = scan[0]
        print('i2c initialization ended.')

    def show_gpio(self):

        print('>> dir(pyb.Pin.board)', dir(pyb.Pin.board))
        print('>> dir(pyb.Pin.cpu)', dir(pyb.Pin.cpu))
        
        try:
            print('>> pins.pins()')
            pins.pins()
            print('>> pins.af()')
            pins.af()
        except:
            print('pins not imported')


    def scan_br(self):
        self.brs = []   
        br_num = 1
        brs = [50, 100, 200, 250, 400,500,800]
        brs = [br*1000 for br in brs]
        brs = range(115200, 9600, -100)
#            brs = range(9600, 115200, 400)    

        print('Scanning {} baudrates'.format(len(brs)))
        for br in brs:
#                br = br
            print(br)
            self.i2c.init(I2C.MASTER,  addr=self.addr, baudrate=br)
            scan = self.i2c.scan()
    #        print(scan)
            if len(scan) > 0:
                print('New functional baudrate {}'.format(br))
                self.brs.append(br)
                if len(self.brs) >= br_num:
                    break
        print('{} functional baudrates < than 115201:\n{}'.format(
            br_num, self.brs))
        self.br = self.brs[-1]
        
        with open(self.file_br, 'w') as f:
            f.write(str(self.br))
            print('Functional baudrate {}, saved to file {}.'.format(
                    self.br, self.file_br))

    def scan_as(self):        
        base = 0x00
        max_a = 16*16*16
        ass = range(0, max_a)
        self.lcd_a = None
        self.ass = []

        print('Scanning {} addresses'.format(len(ass)))
        for offset in ass:
            a = base + offset
            #print('0x{:02X}'.format(a))
            try:
                self.i2c.send(0, addr=a)
                self.i2c.send(0, addr=a)
                print('Address without error: 0x{:02X}'.format(a))
                self.ass.append(a)
            except Exception as ex:
                #print('Some error occured! \n{}'.format(str(ex)))
                pass
            
        if len(self.ass) > 0:
            print('Responsive addresses < {}:\n{}'.format(max_a, 
                ['0x{:02X}'.format(a) for a in self.ass]))
            self.lcd_a = self.ass[0]

            #print(os.listdir())
            with open(self.file_as, 'w') as f:
                f.write(self.lcd_a)
                print('Responsive address 0x{0:02X} = {0} dec, saved to file {1}.'.format(self.lcd_a, self.file_as))

            #print(os.listdir())
            gc.collect()
        else:
            print('No responsive address found!')



    def no_config_scan(self):
        scan_br = True
        try:
            with open(self.file_br, 'r') as f:
                br = int(f.read())
                if br > 0:
                    self.br = br
                    scan_br = False
        except:
            scan_br = True

        if scan_br:
            self.scan_br()

        scan_as = True
        try:
            with open(self.file_as, 'r') as f:
                br = int(f.read())
                if br > 0:
                    self.br = br
                    scan_as = False
        except:
            scan_as = True
        
        scan_as = True
        if scan_as:
            self.scan_as()

    def init_accel(self):
        
        self.ac = staccel.STAccel()
        ac = self.ac


        #from pyb import Accel

        #accel = pyb.Accel()

    def init_button(self):
        
        sw = pyb.Switch()
        # sw.callback(lambda:print('press!'))

        sw.callback(self.on_press)



if __name__ == '__main__':
    m = Machine()
    print('End of machine program!')


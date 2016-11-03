import pyb
from pyb import I2C 

import staccel
import math

import os
#import gc # garbage collection for writing?

#import microsnake
from microsnake import MicroSnakeGame as Game
#from microsnake import move_arrow_pressed
import shared_globals

#from shared_globals import move_arrow_pressed as move_arrow_pressed


import lcd_i2c

import micropython
micropython.alloc_emergency_exception_buf(100)

try: 
    print('try importing pins')
    import pins
except ImportError:
    print('pins not found')

#from machine import Pins



#x = [0,1,2,3]
#move_arrow_pressed = None
#micropython
#microsnake.move_arrow_pressed = move_arrow_pressed

class Machine():
    n = 0
    leds = None
#    move_arrow_pressed = None

    def on_press(q):
        print('pressed!')
#        print('Machine.turned', Machine.turned)
        act = pyb.millis()
        if (act - Machine.turn_time) > Machine.turn_delay:
            Machine.turned = True
            Machine.turn_time = act
        print('Machine.turned', Machine.turned)

        # print(q.ac.xyz()) # MemoryError:
    def on_tim4(q):
        #lambda t:pyb.LED(3).toggle()
        try:
            n = Machine.n        
            n = (n + 2) % 2
    
            Machine.leds[n].toggle()
            Machine.n = n
        except TypeError as ex:
            #print(ex.strerror)
            print('error')
    
    
    def __init__(q):
#        q.show_gpio()
        q.init_buttons()
        q.init_leds()


        q.init_lcd()
#        q.demo_lcd()
#        lcd.lcd_init()
        q.init_game()

        q.main_loop()


    def init_game(q):
        q.game = Game(q.disp_field)
        


#        q.game_logic_timer = pyb.Timer(3)

        tim4 = pyb.Timer(4)


        tim4.callback(lambda x: q.disp_field())
        tim4.init(freq=10)
        q.game_disp_timer = tim4

        q.game.run()

    def main_loop(q):
        a = 0
        while(1):
            a += 1
            if a % 100000 == 0:
                #q.demo_lcd()
                pass
            if a == 1000000:
                print(str(a) + 'cycles')
                a = 0
            pass
        #pyb.wfi() # https://docs.micropython.org/en/latest/pyboard/library/pyb.html
        #pyb.standby()
        pyb.info()

    def init_leds(q):
        q.leds = []
        for i in range(4):
            q.leds.append(pyb.LED(i+1))

    def go_way(q, way='r'):

#        game.go_way('r')

#        player.vel = 
        pass
   

    def init_buttons(q):
        
        sw = pyb.Switch()
        sw.callback(q.on_press)
        
        # sw.callback(lambda:print('press!'))
        pins = ['A' + str(i) for i in range(1, 8, 2)]
#        pins = ['D' + str(i) for i in range(0, 7, 2)]
#        pins = ['A7']

        print('Initializing buttons:', pins)

        q.on_btn_press = {}
        q.btns = []

        bs = []
        mapper = range(len(pins))
#        bs.append(lambda x: print(mapper[0], ': line', x))
#        bs.append(lambda x: print(mapper[1], ': line', x))
#        bs.append(lambda x: print(mapper[2], ': line', x))
#        bs.append(lambda x: print(mapper[3], ': line', x))  

        def on_arrow_button(mapped, line):
            shared_globals.move_arrow_pressed = mapped
#            print('on_arrow_button=', mapped)
#            print('mapped var', mapped, ': line', line)

        bs.append(lambda x: on_arrow_button(mapper[0], x))
        bs.append(lambda x: on_arrow_button(mapper[1], x))
        bs.append(lambda x: on_arrow_button(mapper[2], x))
        bs.append(lambda x: on_arrow_button(mapper[3], x))


        for i, pin_id in enumerate(pins):

            new_callback = bs[i]
            new_btn = pyb.ExtInt(pin_id, pyb.ExtInt.IRQ_FALLING, 
                    pyb.Pin.PULL_UP, new_callback)

            q.btns.append(new_btn)
        


    def disp_field(q):
#        field = shared_globals.field
#        char_range = shared_globals.char_range
        line_range = shared_globals.line_range 
#        bytefield = shared_globals.bytefield
#        num_lines = len(field)
#        line_range = range(num_lines)
        line_num = 0
#        for line_num in line_range:
        while line_num < 8:

            #bytefield
#            line = ''.join(field[line_num])
            print(1)
            line = shared_globals.field_lines[line_num]
            print(2)
            lcd_line_num = line_num % 2
            print(3)
            lcd_num = int(line_num/2) % 4
            print(4)
            q.lcds[lcd_num].disp(line, lcd_line_num)

#            q.lcds[int(line_num/2) % 4].disp( 
#                    shared_globals.field_lines[line_num], 
#                    line_num % 2)

            line_num += 1

    def init_i2c(q, bus=2, role=I2C.MASTER, baudrate=115200, self_addr=0x42):
        q.i2c = I2C(bus)

        q.addr = self_addr
        q.br = baudrate
        q.i2c.init(role, addr=q.addr, baudrate=q.br)          
                
        print('I2C initialized: self_addr=0x{0:02X} = {0} dec, br={1}'.\
                format(q.addr, q.br))

    def char_range(q, c1, c2):
        """Generates the characters from `c1` to `c2`, inclusive."""
        for c in range(ord(c1), ord(c2)+1):
            yield chr(c)

    def init_lcd(q):

        q.init_i2c()

        scan = q.i2c.scan()
        print('Scanned addresses [dec]:', scan)

        lcd_as = scan
        q.lcds = []
#        q.lcds = [ for as in lcd_as]
        for lcd_a in lcd_as:
            new_lcd = lcd_i2c.lcd1602(q.i2c, lcd_a)
            q.lcds.append(new_lcd)
        

        for i, lcd in enumerate(q.lcds):
            txt = 'Loading...lcd[{}]'.format(i)
            lcd.disp(txt, 0)

        for i, ch in enumerate(q.char_range('a', 'Z')):
            lcd_num = i % len(q.lcds)
            lcd = q.lcds[lcd_num]
            txt = 'lcd[{}] = {}'.format(lcd_num, ch)
            lcd.disp(txt, 0)
            pyb.delay(300)
        
        q.lcd_a = scan[0]
        print('i2c initialization ended.')

    def show_gpio(q):

        print('>> dir(pyb.Pin.board)', dir(pyb.Pin.board))
        print('>> dir(pyb.Pin.cpu)', dir(pyb.Pin.cpu))
        
        try:
            print('>> pins.pins()')
            pins.pins()
            print('>> pins.af()')
            pins.af()
        except:
            print('pins not imported')


    def scan_br(q):
        q.brs = []   
        br_num = 1
        brs = [50, 100, 200, 250, 400,500,800]
        brs = [br*1000 for br in brs]
        brs = range(115200, 9600, -100)
#            brs = range(9600, 115200, 400)    

        print('Scanning {} baudrates'.format(len(brs)))
        for br in brs:
#                br = br
            print(br)
            q.i2c.init(I2C.MASTER,  addr=q.addr, baudrate=br)
            scan = q.i2c.scan()
    #        print(scan)
            if len(scan) > 0:
                print('New functional baudrate {}'.format(br))
                q.brs.append(br)
                if len(q.brs) >= br_num:
                    break
        print('{} functional baudrates < than 115201:\n{}'.format(
            br_num, q.brs))
        q.br = q.brs[-1]
        
        with open(q.file_br, 'w') as f:
            f.write(str(q.br))
            print('Functional baudrate {}, saved to file {}.'.format(
                    q.br, q.file_br))
        pyb.sync()


    def scan_as(q):        
        base = 0x00
        max_a = 16*16*16
        ass = range(0, max_a)
        q.lcd_a = None
        q.ass = []

        print('Scanning {} addresses'.format(len(ass)))
        for offset in ass:
            a = base + offset
            #print('0x{:02X}'.format(a))
            try:
                q.i2c.send(0, addr=a)
                q.i2c.send(0, addr=a)
                print('Address without error: 0x{:02X}'.format(a))
                q.ass.append(a)
            except Exception as ex:
                #print('Some error occured! \n{}'.format(str(ex)))
                pass
            
        if len(q.ass) > 0:
            print('Responsive addresses < {}:\n{}'.format(max_a, 
                ['0x{:02X}'.format(a) for a in q.ass]))
            q.lcd_a = q.ass[0]

            #print(os.listdir())
            with open(q.file_as, 'w') as f:
                f.write(q.lcd_a)
                print('Responsive address 0x{0:02X} = {0} dec, saved to file {1}.'.format(q.lcd_a, q.file_as))

            #print(os.listdir())
#            gc.collect()
            pyb.sync()
        else:
            print('No responsive address found!')



    def no_config_scan(q):
        scan_br = True
        try:
            with open(q.file_br, 'r') as f:
                br = int(f.read())
                if br > 0:
                    q.br = br
                    scan_br = False
        except:
            scan_br = True

        if scan_br:
            q.scan_br()

        scan_as = True
        try:
            with open(q.file_as, 'r') as f:
                br = int(f.read())
                if br > 0:
                    q.br = br
                    scan_as = False
        except:
            scan_as = True
        
        scan_as = True
        if scan_as:
            q.scan_as()

    def init_accel(q):
        
        q.ac = staccel.STAccel()
        ac = q.ac


        #from pyb import Accel

        #accel = pyb.Accel()




if __name__ == '__main__':
    m = Machine()
    print('End of machine program!')


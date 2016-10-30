import pyb
from pyb import I2C 

import staccel
import math

import os
#import gc # garbage collection for writing?

from microsnake import MicroSnakeGame as Game
import lcd_i2c

import micropython
micropython.alloc_emergency_exception_buf(100)

try: 
    print('try importing pins')
    import pins
except ImportError:
    print('pins not found')

#from machine import Pins



x = [0,1,2,3]


class Machine():
    n = 0
    leds = None
    move_arrow_pressed = None

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
#        self.show_gpio()
        self.init_buttons()
        self.init_leds()


        self.init_lcd()
#        self.demo_lcd()
#        lcd.lcd_init()
        self.init_game()

        self.main_loop()


    def init_game(self):
        self.game = Game(self.disp_field)

#        self.game.run()

    def main_loop(self):
        a = 0
        while(1):
            a += 1
            if a % 100000 == 0:
                #self.demo_lcd()
                pass
            if a == 1000000:
                print(str(a) + 'cycles')
                a = 0
            pass
        #pyb.wfi() # https://docs.micropython.org/en/latest/pyboard/library/pyb.html
        #pyb.standby()
        pyb.info()

    def init_leds(self):
        self.leds = []
        for i in range(4):
            self.leds.append(pyb.LED(i+1))

    def go_way(self, way='r'):

#        game.go_way('r')

#        player.vel = 
        pass
    

    def init_buttons(self):
        
        sw = pyb.Switch()
        sw.callback(self.on_press)
        
        # sw.callback(lambda:print('press!'))
        pins = ['A' + str(i) for i in range(1, 8, 2)]
#        pins = ['D' + str(i) for i in range(0, 7, 2)]
#        pins = ['A7']

        print('Initializing buttons:', pins)

        self.on_btn_press = {}
        self.btns = []

        bs = []
        mapper = [1,2,3,4]
        bs.append(lambda x: print(mapper[0], ': line', x))
        bs.append(lambda x: print(mapper[1], ': line', x))
        bs.append(lambda x: print(mapper[2], ': line', x))
        bs.append(lambda x: print(mapper[3], ': line', x))  


        def on_arrow_button(btn_index, line):
            Machine.move_arrow_pressed = btn_index
            print('btn_index', btn_index, ': line', line)

        for i, pin_id in enumerate(pins):

            new_callback = bs[i]
#            new_callback = on_arrow_button
            new_btn = pyb.ExtInt(pin_id, pyb.ExtInt.IRQ_FALLING, 
                    pyb.Pin.PULL_UP, new_callback)


#            new_btn = pyb.Pin(pin_id, pyb.Pin.IN, Pin.PULL_UP)
            

            self.btns.append(new_btn)
        


    def disp_field(self, field):
        num_lines = len(field)
        for line_num in range(num_lines):
            line = ''.join(field[line_num])
            lcd_line_num = line_num % 2
            lcd_num = int(line_num/2) % 4
            self.lcds[lcd_num].disp(line, lcd_line_num)

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
        pyb.sync()


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
#            gc.collect()
            pyb.sync()
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




if __name__ == '__main__':
    m = Machine()
    print('End of machine program!')


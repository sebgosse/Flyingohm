from ST7735 import TFT, TFTColor
from sysfont import sysfont
from machine import SPI,Pin,ADC,PWM
import time
import uasyncio

spi = SPI(0, baudrate=20000000, polarity=0, phase=0,
          sck=Pin(2), mosi=Pin(19), miso=None) #sck / tx
tft=TFT(spi,16,17,18) #Rx/Csn/SCK
tft.initr()
tft.rgb(True)
tft.rotation(2)
tft.fill(TFT.WHITE)
pwm_low_us = 1000 # # durée en us du signal pwm pour être à 0%
pwm_scale_us = 1000 # durée en us entre la position 0% et 100%

# Configurer la broche du bouton en entrée avec une résistance de tirage vers le haut
bouton = machine.Pin(15, machine.Pin.IN, machine.Pin.PULL_UP)
bouton_led = PWM(Pin(14, mode=Pin.OUT))
#bouton_led.freq(10)
#bouton_led.duty_u16(65535)

potentiometer = ADC(machine.Pin(27, mode=Pin.IN))  # potentiometer connected to A1, power & ground
pwm = PWM(Pin(0, mode=Pin.OUT))
pwm.freq(50)
pwm.duty_u16(0)

def draw_bmp():
    f=open('INTRO_LOGO.bmp', 'rb')
    if f.read(2) == b'BM':  #header
        print("A")
        dummy = f.read(8) #file size(4), creator bytes(4)
        print("B")        
        offset = int.from_bytes(f.read(4), 'little')
        hdrsize = int.from_bytes(f.read(4), 'little')
        width = int.from_bytes(f.read(4), 'little')
        height = int.from_bytes(f.read(4), 'little')
        if int.from_bytes(f.read(2), 'little') == 1: #planes must be 1
            depth = int.from_bytes(f.read(2), 'little')
            if depth == 24 and int.from_bytes(f.read(4), 'little') == 0:#compress method == uncompressed
                print("Image size:", width, "x", height)
                rowsize = (width * 3 + 3) & ~3
                if height < 0:
                    height = -height
                    flip = False
                else:
                    flip = True
                w, h = width, height
                if w > 128: w = 128
                if h > 160: h = 160
                tft._setwindowloc((0,0),(w - 1,h - 1))
                for row in range(h):
                    if flip:
                        pos = offset + (height - 1 - row) * rowsize
                    else:
                        pos = offset + row * rowsize
                    if f.tell() != pos:
                        dummy = f.seek(pos)
                    for col in range(w):
                        bgr = f.read(3)
                        tft._pushcolor(TFTColor(bgr[2],bgr[1],bgr[0]))
        tft.text((80, 140), "V0.1", TFT.BLACK, sysfont, 2, nowrap=True)


def testfillrects(color1, color2):
    tft.fill(TFT.WHITE);
    for x in range(tft.size()[0],0,-6):
        tft.fillrect((tft.size()[state_machine0]//2 - x//2, tft.size()[1]//2 - x/2), (x, x), color1)
        tft.rect((tft.size()[0]//2 - x//2, tft.size()[1]//2 - x/2), (x, x), color2)

async def detecter_appui_court():
    print("detecter_appui_court")    
    # Attendre que le bouton soit relâché
    while bouton.value() == 0:
        await uasyncio.sleep_ms(5)
        pass
    print("bouton laché")    
    # Attendre que le bouton soit appuyé    
    while bouton.value() == 1:
        await uasyncio.sleep_ms(5)        
        pass    
    print("bouton appuyé")    
    sm.transition("ARMED_TO_DISARMED") 
    return True


async def display_potentiometer():
    print("display_potentiometer")
    prec_val = 0
    
    while True :
        #print("pot")
        val = potentiometer.read_u16()
        #print(val)      # Display value
        if (val != prec_val):
            print(val)
            y = 128*(val/65535)
            tft.fillrect((0,25),(y,5),TFT.BLACK)
            tft.fillrect((y +1 ,25),(128,5),TFT.WHITE)            
            tmp = (val/65535)*pwm_scale_us
            val = pwm_low_us + int(tmp)
            print(val)
            pwm.duty_ns(val*1000) #x1000 car c'est en ns
        prec_val = val
        await uasyncio.sleep_ms(5)




async def detecter_appui_court_long():

    print("detecter_appui_court_long")
    while True :
        # Attendre que le bouton soit relâché
        while bouton.value() == 1:
            await uasyncio.sleep_ms(5)
            pass
        # Attendre l'appui court
        debut_appui_court = time.ticks_us()
        while bouton.value() == 0:
            await uasyncio.sleep_ms(5)
            pass
        fin_appui_court = time.ticks_us()
        
        if (time.ticks_diff(fin_appui_court, debut_appui_court) < 200000):
        
            # Attendre que le bouton soit relâché
            while bouton.value() == 1:
                await uasyncio.sleep_ms(5)                
                pass
            
            # Attendre l'appui long
            debut_appui_long = time.ticks_us()
            # Si plus de 600ms entre appui court et appui long, on en fait rien.
            if (time.ticks_diff(debut_appui_long, debut_appui_court) > 600000):
                return False
            
            # On affiche la barre de progression bleue
            y = 0
            while bouton.value() == 0:
                tft.fillrect((0,150),(y,10),TFT.BLUE)
                y = y+5
                if (y>128):
                    break
                await uasyncio.sleep_ms(5)                
                pass
            fin_appui_long= time.ticks_us()

            # On efface la barre de progression
            tft.fillrect((0,150),(128,10),TFT.WHITE)

            # Vérifier si la séquence d'appui a été détectée
            if time.ticks_diff(fin_appui_court, debut_appui_court) < 200000 and time.ticks_diff(fin_appui_long, debut_appui_long) > 1500000:
                sm.transition("DISARMED_TO_ARMED")
                return True

class StateMachine:
    def __init__(self):
        self.state = "INIT"
        print("INIT State")
        
    def transition(self, event):
        if self.state == "INIT" and event == "INIT_TO_DISARMED":
            self.state = "DISARMED"
            #White Screen
            tft.fill(TFT.WHITE)
            self.display_state()
            uasyncio.create_task(detecter_appui_court_long())            
            uasyncio.create_task(display_potentiometer())            
            print("Transition from INIT to DISARMED")
        elif self.state == "DISARMED" and event == "DISARMED_TO_ARMED":
            self.state = "ARMED"
            tft.fill(TFT.WHITE)
            uasyncio.create_task(detecter_appui_court())                        
            print("Transition from DISARMED to ARMED")
        elif self.state == "ARMED" and event == "ARMED_TO_DISARMED":
            self.state = "DISARMED"
            tft.fill(TFT.WHITE)
            uasyncio.create_task(detecter_appui_court_long())               
            print("Transition from ARMED to DISARMED")
        else:
            print("Invalid transition")
                
    def read_potentiometre(self):
        # Setup the potentiometer input
        #potentiometer = analogio.AnalogIn(board.A0)
        print("Potentiometer read")
        time.sleep_ms(1)  # Wait for 1ms before reading again
    
    def display_info(self):
        if (self.state == "ARMED"):
            info="Appui court puis long pour armer"
        elif (self.state == "DISARMED"):
            info="Appui court pour désarmer"
        else:
            info=""
        tft.text((0, 40), info , TFT.BLACK, sysfont, 2, nowrap=True)
            
            
    def display_state(self):
        if (self.state == "ARMED"):
            color=TFT.RED
        elif (self.state == "DISARMED"):
            color=TFT.BLUE
        else:
            color=TFT.BLACK
        tft.text((0, 0), self.state , color, sysfont, 3, nowrap=True)

    async def run(self):
        while True:
            if self.state == "INIT":
                draw_bmp()
                await uasyncio.sleep(1)
                self.transition("INIT_TO_DISARMED")

            elif self.state == "DISARMED":
                self.display_state()                
                await uasyncio.sleep_ms(1)

            elif self.state == "ARMED":
                self.display_state()
                await uasyncio.sleep_ms(1)                    


if __name__ == "__main__":
    sm = StateMachine()
    uasyncio.run(sm.run())


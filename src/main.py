import time
import asyncio
import board, busio
import pwmio
from analogio import AnalogIn
import terminalio
from adafruit_simplemath import map_range

import displayio
from adafruit_st7735r import ST7735R
from adafruit_display_text import label
from adafruit_display_shapes.rect import Rect
from adafruit_display_shapes.line import Line

from digitalio import DigitalInOut, Direction, Pull
import vectorio
from adafruit_bitmap_font import bitmap_font
from utils import constant
from utils.enum import SmStatus

MODE_FONT = bitmap_font.load_font("fonts/ic8x8u.bdf")


class Timer:
    def __init__(self):
        self.seconds = 0
        self.start_seconds = 0

    async def start_timer(self) -> None:
        while True:
            if sm.state == SmStatus.ARMED:
                flying_time_s = int(time.monotonic()) - self.start_seconds
                screen.timer_text.text = (
                    f"{str(flying_time_s // 3600)}:"
                    + "{:02d}".format((flying_time_s // 60) % 60)
                    + ":"
                    + "{:02d}".format(flying_time_s % 60)
                )
            await asyncio.sleep_ms(100)

    def reset_timer(self) -> None:
        self.start_seconds = int(time.monotonic())


class Button:
    def __init__(self):
        self.pin = DigitalInOut(board.GP15)
        self.pin.direction = Direction.INPUT
        self.pin.pull = Pull.UP

    # Short pressed button detection (armed to disarmed state)
    async def short_pressed_disarm(self) -> bool:
        # Wait for button release
        while self.pin.value == 0:
            await asyncio.sleep_ms(100)

        # Wait for button press
        while self.pin.value == 1:
            await asyncio.sleep_ms(100)

        sm.transition("ARMED_TO_DISARMED")
        return True

    # Long pressed button detection (disarmed to armed state)
    async def long_pressed_arm(self) -> bool:
        nb_cycles = 30  # Number of 100ms cycle needed to switch to armed mode
        while True:
            # Wait for button release
            while self.pin.value:
                await asyncio.sleep_ms(100)
            y = 0
            while not self.pin.value:
                screen.rect_arming.width = int(128 * (y / nb_cycles))
                y = y + 1
                if y > nb_cycles:
                    break
                await asyncio.sleep_ms(100)

            screen.rect_arming.width = 0
            if y > nb_cycles:
                sm.transition("DISARMED_TO_ARMED")
                return True


class Buzzer:
    def __init__(self):
        pass

    #         self.pwm = PWM(Pin(12))
    #         self.buzzer_off_delay = 2000 #Durée du bip lorsque le moteur est armé (en ms)
    #         self.buzzer_on_delay = 100 #Durée du silence lorsque le moteur est armé (en ms)

    def playtone(self, frequency: int) -> None:
        self.pwm.duty_u16(5000)
        self.pwm.freq(frequency)

    def bequiet(self) -> None:
        self.pwm.duty_u16(0)

    async def playsong(self) -> None:
        tone_state = 1
        while True:
            try:
                if tone_state == 0:
                    self.bequiet()
                    tone_state = 1
                    await asyncio.sleep_ms(self.buzzer_off_delay)
                else:
                    self.playtone(500)
                    tone_state = 0
                    await asyncio.sleep_ms(self.buzzer_on_delay)
            except asyncio.core.CancelledError:
                self.bequiet()
                return
        self.bequiet()  # ! This is unbound


class Esc:
    def __init__(self):
        self.pwm = pwmio.PWMOut(
            board.GP0, frequency=constant.pwm_frequency, duty_cycle=0
        )
        # Set 0% Power
        self.pwm.duty_cycle = int(constant.pwm_low)
        print(constant.pwm_low)

    async def send_PWM(self) -> None:
        while True:
            val = potentiometer.value
            power = int(map_range(val, 0, 65535, constant.pwm_low, constant.pwm_high))
            # Set Power regarding potentiometer
            self.pwm.duty_cycle = power
            await asyncio.sleep_ms(20)

    def send_PWM_0(self) -> None:
        self.pwm.duty_cycle = int(constant.pwm_low)


class Display:
    def __init__(self):
        mosi_pin = board.GP11
        clk_pin = board.GP10
        reset_pin = board.GP17
        cs_pin = board.GP18
        dc_pin = board.GP16

        displayio.release_displays()
        spi = busio.SPI(clock=clk_pin, MOSI=mosi_pin)
        display_bus = displayio.FourWire(
            spi, command=dc_pin, chip_select=cs_pin, reset=reset_pin
        )
        self.display = ST7735R(
            display_bus, width=128, height=160, bgr=True, auto_refresh=True
        )
        splash = displayio.Group()
        self.display.show(splash)

        ###########
        ## FIRST GROUP : MODE AND POWER BAR
        ###########

        # Draw power bar and arming bar
        palette = displayio.Palette(1)
        palette[0] = 0xFF0000
        self.rect_power = vectorio.Rectangle(
            pixel_shader=palette, width=1, height=5, x=0, y=14
        )
        self.rect_arming = vectorio.Rectangle(
            pixel_shader=palette, width=1, height=5, x=0, y=8
        )
        # Draw Mode (Armed/Disarmed)
        text_mode = "INIT"
        first_group = displayio.Group(scale=1, x=11, y=24)
        self.text_area = label.Label(MODE_FONT, text=text_mode, color=0xFFFFFF, scale=2)
        first_group.append(self.text_area)  # Subgroup for text scaling
        first_group.append(self.rect_arming)
        first_group.append(self.rect_power)
        first_group.append(Line(0, 20, 128, 20, 0xFFFFFF))
        self.rect_arming.width = 0

        ###########
        ## SECOND GROUP : AUTONOMY
        ###########

        autonomy = "100%"
        second_group = displayio.Group(scale=1, x=11, y=70)
        self.text_autonomy = label.Label(
            MODE_FONT, x=10, text=autonomy, color=0xFFFFFF, scale=3
        )
        second_group.append(self.text_autonomy)  # Subgroup for text scaling
        second_group.append(Line(0, 20, 128, 20, 0xFFFFFF))

        ###########
        ## THIRD GROUP : CONSUMPTION
        ###########

        consumption = "0W"
        third_group = displayio.Group(scale=1, x=11, y=100)
        self.text_consumption = label.Label(
            MODE_FONT, x=40, y=5, text=consumption, color=0xFFFFFF, scale=2
        )
        third_group.append(self.text_consumption)  # Subgroup for text scaling
        third_group.append(Line(0, 20, 128, 20, 0xFFFFFF))

        ###########
        ## FOURTH GROUP : TIMER
        ###########

        # Draw timer
        fourth_group = displayio.Group(scale=1, x=11, y=130)
        text_timer = "0:00:00"
        self.timer_text = label.Label(
            MODE_FONT, text=text_timer, color=0xFFFFFF, scale=2
        )
        self.timer_text.y = 15
        fourth_group.append(self.timer_text)  # Subgroup for text scaling

        splash.append(first_group)
        splash.append(second_group)
        splash.append(third_group)
        splash.append(fourth_group)


class Potentiometer:
    def __init__(self):
        self.adc = AnalogIn(board.A1)
        self.value = 0

    # Potentiometer reading
    async def read(self) -> None:
        while True:
            self.value = self.adc.value
            # Update Power Bar on screen
            screen.rect_power.width = int((self.value / 65536) * 128)
            await asyncio.sleep_ms(20)


class StateMachine:
    def __init__(self):
        self.state = SmStatus.ARMED
        asyncio.create_task(potentiometer.read())
        self.start_timer_task = asyncio.create_task(timer.start_timer())
        print("INIT State")

    def transition(self, event: str) -> None:
        if self.state == SmStatus.ARMED and event == "INIT_TO_DISARMED":
            self.state = SmStatus.DISARMED
            print("_INIT_TO_DISARM")
            self.display_state_and_create_task("Transition from INIT to DISARMED")
        elif self.state == SmStatus.DISARMED and event == "DISARMED_TO_ARMED":
            self.arme_state_machine()
        elif self.state == SmStatus.ARMED and event == "ARMED_TO_DISARMED":
            self.state = SmStatus.DISARMED
            self.send_pwm_task.cancel()
            esc.send_PWM_0()
            self.display_state_and_create_task("Transition from ARMED to DISARMED")
        else:
            print("Invalid transition")

    def arme_state_machine(self) -> None:
        self.state = SmStatus.ARMED
        self.display_state()
        timer.reset_timer()
        asyncio.create_task(button.short_pressed_disarm())
        self.send_pwm_task = asyncio.create_task(esc.send_PWM())
        print("Transition from DISARMED to ARMED")

    def display_state_and_create_task(self, text: str) -> None:
        self.display_state()
        asyncio.create_task(button.long_pressed_arm())
        print(text)

    def display_state(self) -> None:
        if self.state == SmStatus.ARMED:
            self.update_screen(20, 0xFF0000, "ACTIF")
        elif self.state == SmStatus.DISARMED:
            self.update_screen(0, 0x00FF00, "INACTIF")
        else:
            self.update_screen(0, 0xFFFFFF, "UNKNOWN")

    def update_screen(
        self, text_position: int, text_color: int, screen_status: str
    ) -> None:
        screen.text_area.x = text_position
        screen.text_area.color = text_color
        screen.text_area.text = screen_status

    async def run(self):
        while True:
            if self.state == SmStatus.ARMED:
                # screen.draw_bmp()
                print("INIT")
                self.transition("INIT_TO_DISARMED")
                print("INIT TO DISARM")
            await asyncio.sleep_ms(100)


if __name__ == "__main__":
    timer = Timer()
    esc = Esc()
    potentiometer = Potentiometer()
    screen = Display()
    button = Button()
    buzzer = Buzzer()
    sm = StateMachine()
    asyncio.run(sm.run())

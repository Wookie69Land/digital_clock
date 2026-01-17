from machine import Pin, I2C, RTC
import time

# ===========================================================================
# 1. STEROWNIK LCD
# ===========================================================================
class I2cLcd:
    def __init__(self, i2c, i2c_addr, num_lines, num_columns):
        self.i2c = i2c
        self.i2c_addr = i2c_addr
        self.i2c.writeto(self.i2c_addr, bytearray([0]))
        self.i2c.writeto(self.i2c_addr, bytearray([64]))
        time.sleep(0.020)
        self.num_lines = num_lines
        self.num_columns = num_columns
        self.backlight_val = 0x08
        self.display_val = 0x04
        self.bk_light(True)
        self.init_display()

    def init_display(self):
        self.write_byte(0x33, 0)
        self.write_byte(0x32, 0)
        self.write_byte(0x06, 0)
        self.write_byte(0x0C, 0)
        self.write_byte(0x28, 0)
        self.clear()

    def clear(self):
        self.write_byte(0x01, 0)
        time.sleep(0.002)

    def bk_light(self, on):
        self.backlight_val = 0x08 if on else 0x00
        self.expander_write(0)

    def write_byte(self, byte, mode):
        high_nib = byte & 0xF0
        low_nib = (byte << 4) & 0xF0
        self.expander_write(high_nib | mode | self.backlight_val)
        self.expander_write(low_nib | mode | self.backlight_val)

    def expander_write(self, byte):
        self.i2c.writeto(self.i2c_addr, bytearray([byte | 0x04]))
        self.i2c.writeto(self.i2c_addr, bytearray([byte & ~0x04]))

    def putstr(self, string):
        for char in string:
            self.write_byte(ord(char), 1)

    def move_to(self, col, row):
        offsets = [0x00, 0x40, 0x14, 0x54]
        self.write_byte(0x80 | (offsets[row] + col), 0)

# ===========================================================================
# 2. KONFIGURACJA SPRZĘTU
# ===========================================================================
i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)
lcd = I2cLcd(i2c, 0x27, 2, 16)
rtc = RTC() # Zegar czasu rzeczywistego (pobiera czas z komputera w Wokwi)

# Przyciski (Pull Up -> aktywne stanem 0)
btn_mode  = Pin(15, Pin.IN, Pin.PULL_UP)
btn_up    = Pin(14, Pin.IN, Pin.PULL_UP)
btn_down  = Pin(13, Pin.IN, Pin.PULL_UP)
btn_reset = Pin(12, Pin.IN, Pin.PULL_UP) # NOWY GUZIK

# ===========================================================================
# 3. ZMIENNE GLOBALNE
# ===========================================================================
# Czas zegara
hours = 12
minutes = 0
seconds = 0

# Stany: 0=Clock, 1=Edit Hour, 2=Edit Min, 3=STOPWATCH (Stoper)
state = 0 

# Zmienne Stopera
sw_running = False
sw_start_time = 0  # Czas startu w ms
sw_accumulated = 0 # Czas zgromadzony z poprzednich cykli start/stop

# ===========================================================================
# 4. FUNKCJE POMOCNICZE
# ===========================================================================
def debounce(pin):
    if pin.value() == 0:
        time.sleep(0.2)
        return True
    return False

def sync_time_from_system():
    """Pobiera czas z RTC (systemu) i ustawia w zmiennych"""
    global hours, minutes, seconds
    # rtc.datetime() zwraca: (year, month, day, weekday, hours, minutes, seconds, subseconds)
    t = rtc.datetime()
    hours = t[4]
    minutes = t[5]
    seconds = t[6]

# Na start pobierz czas z systemu (Warszawa/PC time)
sync_time_from_system()

# Ekran powitalny
lcd.clear()
lcd.putstr("Clock & Stopwtch")
lcd.move_to(0, 1)
lcd.putstr("System Ready...")
time.sleep(1)
lcd.clear()

last_tick = time.ticks_ms()

# ===========================================================================
# 5. GŁÓWNA PĘTLA
# ===========================================================================
while True:
    current_ms = time.ticks_ms()

    # --- LOGIKA ZEGARA (Co 1 sekunda) ---
    if time.ticks_diff(current_ms, last_tick) >= 1000:
        last_tick = current_ms
        if state != 3: # W trybie stopera też liczymy czas w tle, ale nie odświeżamy tak często
            seconds += 1
            if seconds >= 60:
                seconds = 0
                minutes += 1
            if minutes >= 60:
                minutes = 0
                hours += 1
            if hours >= 24:
                hours = 0
        
        # Odświeżanie ekranu (tylko w trybach Zegara)
        if state < 3:
            lcd.move_to(0, 0)
            lcd.putstr("Czas: {:02d}:{:02d}:{:02d}".format(hours, minutes, seconds))
            
            lcd.move_to(0, 1)
            if state == 0:   lcd.putstr("Tryb: NORMALNY  ")
            elif state == 1: lcd.putstr("USTAW: GODZINA  ")
            elif state == 2: lcd.putstr("USTAW: MINUTA   ")

    # --- LOGIKA STOPERA (Odświeżanie szybkie) ---
    if state == 3:
        # Obliczanie czasu stopera
        if sw_running:
            now = time.ticks_ms()
            diff = time.ticks_diff(now, sw_start_time)
            total_ms = sw_accumulated + diff
        else:
            total_ms = sw_accumulated
            
        # Konwersja ms na min:sec:ms
        s_ms = int((total_ms % 1000) / 10) # Setne sekundy (0-99)
        s_sec = int((total_ms / 1000) % 60)
        s_min = int((total_ms / 60000) % 60)
        
        # Wyświetlanie stopera
        lcd.move_to(0, 0)
        lcd.putstr("STOPER:         ")
        lcd.move_to(0, 1)
        # Format MM:SS:ms
        lcd.putstr("{:02d}:{:02d}:{:02d}        ".format(s_min, s_sec, s_ms))


    # --- OBSŁUGA PRZYCISKÓW ---

    # 1. Przycisk MODE (Zmiana trybów)
    if debounce(btn_mode):
        state += 1
        if state > 3: state = 0 # 0, 1, 2, 3 -> 0
        lcd.clear() # Czyść ekran przy zmianie trybu
        last_tick = 0 # Wymuś odświeżenie zegara
    
    # 2. Przycisk RESET CLOCK (Działa tylko w trybach zegara)
    if debounce(btn_reset):
        if state != 3:
            sync_time_from_system() # Reset do czasu warszawskiego
            lcd.move_to(0, 1)
            lcd.putstr("! SYNC SYSTEM ! ") # Potwierdzenie
            time.sleep(0.5)
            last_tick = 0 # Wymuś odświeżenie

    # 3. Przycisk UP (Zmienne działanie)
    if debounce(btn_up):
        if state == 1: # Godzina ++
            hours = (hours + 1) % 24
            last_tick = 0
        elif state == 2: # Minuta ++
            minutes = (minutes + 1) % 60
            seconds = 0
            last_tick = 0
        elif state == 3: # STOPER START/STOP
            if sw_running:
                # Zatrzymaj
                sw_running = False
                sw_accumulated += time.ticks_diff(time.ticks_ms(), sw_start_time)
            else:
                # Wystartuj
                sw_running = True
                sw_start_time = time.ticks_ms()

    # 4. Przycisk DOWN (Zmienne działanie)
    if debounce(btn_down):
        if state == 1: # Godzina --
            hours = (hours - 1) % 24
            last_tick = 0
        elif state == 2: # Minuta --
            minutes = (minutes - 1) % 60
            seconds = 0
            last_tick = 0
        elif state == 3: # STOPER RESET
            if not sw_running: # Tylko jak zatrzymany
                sw_accumulated = 0
                lcd.move_to(0, 1)
                lcd.putstr("00:00:00        ")

    time.sleep(0.01) # Lekki oddech dla procesora
#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <RTClib.h>

LiquidCrystal_I2C lcd(0x27, 16, 2);  // Adres I2C LCD
RTC_DS1307 rtc;  // Lub RTC_DS3231 rtc;

int btnHourUp = 2, btnHourDown = 3, btnMinUp = 4, btnMinDown = 5, btnMode = 1;
int buzzer = 6;
int alarmHour = 12, alarmMin = 0;  // Domyślny alarm
bool alarmMode = false;  // Tryb edycji alarmu
unsigned long buttonPressStart = 0;  // Czas startu naciśnięcia btnMode
bool buttonPressed = false;  // Flaga naciśnięcia
unsigned long inactivityTimeout = 0;  // Timeout dla trybu alarmu
int prevSecond = -1;  // Śledzenie poprzedniej sekundy dla alarmu
bool alarmActive = false;  // Flaga aktywnego alarmu

void setup() {
  Wire.begin();
  lcd.init();
  lcd.backlight();
  
  rtc.begin();
  if (!rtc.isrunning()) {  // Sprawdź i ustaw czas
    lcd.setCursor(0,1);
    lcd.print("Setting time...");
    rtc.adjust(DateTime(F(__DATE__), F(__TIME__)));
  }

  pinMode(btnHourUp, INPUT_PULLUP);
  pinMode(btnHourDown, INPUT_PULLUP);
  pinMode(btnMinUp, INPUT_PULLUP);
  pinMode(btnMinDown, INPUT_PULLUP);
  pinMode(btnMode, INPUT_PULLUP);
  pinMode(buzzer, OUTPUT);
}

void loop() {
  DateTime now = rtc.now();
  int currentSecond = now.second();
  
  // Wyświetlanie czasu lub alarmu w zależności od trybu
  lcd.setCursor(0, 0);
  if (alarmMode) {
    lcd.print("Alarm: ");
    if (alarmHour < 10) lcd.print("0");
    lcd.print(alarmHour); lcd.print(':');
    if (alarmMin < 10) lcd.print("0");
    lcd.print(alarmMin); lcd.print("   ");
  } else {
    lcd.print("Czas: ");
    if (now.hour() < 10) lcd.print("0");
    lcd.print(now.hour(), DEC); lcd.print(':');
    if (now.minute() < 10) lcd.print("0");
    lcd.print(now.minute(), DEC); lcd.print(':');
    if (now.second() < 10) lcd.print("0");
    lcd.print(now.second(), DEC);
  }

  // Detekcja naciśnięcia btnMode
  if (digitalRead(btnMode) == LOW) {
    if (!buttonPressed) {
      buttonPressed = true;
      buttonPressStart = millis();
    }
  } else {
    if (buttonPressed) {
      unsigned long pressDuration = millis() - buttonPressStart;
      buttonPressed = false;
      
      if (pressDuration < 1000) {  // Krótki press: Reset czasu lub wyjście z alarmu
        if (alarmMode) {
          alarmMode = false;  // Wyjście z trybu alarmu
          tone(buzzer, 500, 100);
        } else {
          rtc.adjust(DateTime(F(__DATE__), F(__TIME__)));  // Reset do rzeczywistego
          lcd.setCursor(0,1);
          lcd.print("Time reset!    ");
          tone(buzzer, 800, 200);  // Sygnał resetu
          delay(1000);
          lcd.clear();  // Pełne czyszczenie LCD
        }
      } else {  // Długi press: Toggle trybu alarmu
        alarmMode = !alarmMode;
        inactivityTimeout = millis() + 5000;  // 5s timeout
        tone(buzzer, 500, 100);  // Sygnał
      }
    }
  }

  // Obsługa przycisków w zależności od trybu + reset alarmu
  bool anyButtonPressed = (digitalRead(btnHourUp) == LOW || digitalRead(btnHourDown) == LOW ||
                           digitalRead(btnMinUp) == LOW || digitalRead(btnMinDown) == LOW ||
                           digitalRead(btnMode) == LOW);

  if (anyButtonPressed && alarmActive) {
    alarmActive = false;  // Reset alarmu po naciśnięciu przycisku
    noTone(buzzer);
    lcd.clear();
  }

  if (alarmMode) {
    if (digitalRead(btnHourUp) == LOW) { alarmHour = (alarmHour + 1) % 24; delay(200); inactivityTimeout = millis() + 5000; }
    if (digitalRead(btnHourDown) == LOW) { alarmHour = (alarmHour == 0 ? 23 : alarmHour - 1); delay(200); inactivityTimeout = millis() + 5000; }
    if (digitalRead(btnMinUp) == LOW) { alarmMin = (alarmMin + 1) % 60; delay(200); inactivityTimeout = millis() + 5000; }
    if (digitalRead(btnMinDown) == LOW) { alarmMin = (alarmMin == 0 ? 59 : alarmMin - 1); delay(200); inactivityTimeout = millis() + 5000; }
    
    // Wyjście z trybu po timeout
    if (millis() > inactivityTimeout) {
      alarmMode = false;
      tone(buzzer, 500, 100);  // Sygnał wyjścia
    }
  } else {
    // Normalny tryb: Nastawianie czasu
    if (digitalRead(btnHourUp) == LOW) { rtc.adjust(rtc.now() + TimeSpan(0,1,0,0)); delay(200); }
    if (digitalRead(btnHourDown) == LOW) { rtc.adjust(rtc.now() - TimeSpan(0,1,0,0)); delay(200); }
    if (digitalRead(btnMinUp) == LOW) { rtc.adjust(rtc.now() + TimeSpan(0,0,1,0)); delay(200); }
    if (digitalRead(btnMinDown) == LOW) { rtc.adjust(rtc.now() - TimeSpan(0,0,1,0)); delay(200); }
  }

  // Sprawdzenie i kontynuacja alarmu
  if (!alarmMode && now.hour() == alarmHour && now.minute() == alarmMin && currentSecond == 0 && prevSecond != 0) {
    alarmActive = true;  // Aktywuj alarm
    Serial.println("Alarm triggered!");
  }

  if (alarmActive) {
    lcd.setCursor(0,1);
    lcd.print("ALARM!         ");
    tone(buzzer, 1000 + (millis() % 200), 500);  // Zmieniający ton buzzer
  }

  prevSecond = currentSecond;

  delay(50);  // Odświeżanie
}
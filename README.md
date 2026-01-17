# Projekt: Zegar Cyfrowy - Systemy Wbudowane

**Autor:** Łukasz Krajewski  
**Nr indeksu:** 335077  
**Przedmiot:** Systemy Wbudowane (Test 4)

## 📋 Opis Projektu

Celem projektu było zaprojektowanie i implementacja zegara cyfrowego z możliwością nastawy czasu. Projekt został zrealizowany na dwóch alternatywnych, nowoczesnych platformach w środowisku symulacyjnym WOKWI:

1.  **Arduino Uno** (Język C++) – wersja z obsługą sprzętowego RTC i Alarmu.
2.  **Raspberry Pi Pico** (MicroPython) – wersja ze Stoperem i synchronizacją czasu systemowego.

Oba rozwiązania wykorzystują wyświetlacz LCD 16x2 (I2C) oraz przyciski do sterowania interfejsem.

---

## 📂 Zawartość Repozytorium

* `digital_clock.c` – Kod źródłowy dla platformy Arduino Uno.
* `digital_clock.py` – Kod źródłowy dla platformy Raspberry Pi Pico.
* `README.md` – Dokumentacja projektu.

---

## 🛠️ Wersja 1: Arduino Uno (C++)

Implementacja niskopoziomowa wykorzystująca biblioteki `Wire`, `LiquidCrystal_I2C` oraz `RTClib`. Projekt symuluje użycie zewnętrznego modułu czasu rzeczywistego (RTC DS1307).

### Funkcje:
* 🕒 **Zegar:** Wyświetlanie czasu (HH:MM:SS) pobieranego z modułu RTC.
* ⚙️ **Nastawa:** Niezależna regulacja godzin i minut za pomocą dedykowanych przycisków.
* 🔔 **Alarm:** Możliwość ustawienia godziny alarmu (sygnalizacja dźwiękowa buzzerem + komunikat na LCD).
* 🔄 **Reset:** Szybki powrót do czasu kompilacji.

### Podłączenie (Pinout):
| Element | Pin Arduino | Funkcja |
| :--- | :--- | :--- |
| **LCD SDA** | A4 | Komunikacja I2C |
| **LCD SCL** | A5 | Komunikacja I2C |
| **Btn Hour+** | D2 | Zwiększ godzinę |
| **Btn Hour-** | D3 | Zmniejsz godzinę |
| **Btn Min+** | D4 | Zwiększ minutę |
| **Btn Min-** | D5 | Zmniejsz minutę |
| **Btn Mode** | D1 | Tryb Alarmu / Reset |
| **Buzzer** | D6 | Sygnał dźwiękowy |

🔗 **Symulacja online:** [WOKWI Project - Arduino Version](https://wokwi.com/projects/453250596509913089)

---

## 🐍 Wersja 2: Raspberry Pi Pico (MicroPython)

Implementacja wysokopoziomowa w języku Python. Wykorzystuje wbudowany RTC mikrokontrolera oraz autorską klasę do obsługi wyświetlacza LCD.

### Funkcje:
* 🕒 **Zegar:** Wyświetlanie czasu z systemową synchronizacją (czas hosta).
* ⏱️ **Stoper:** Funkcja start/stop/reset z dokładnością do milisekund.
* ⚙️ **Menu:** Zmiana trybów jednym przyciskiem (Zegar -> Edycja Godziny -> Edycja Minuty -> Stoper).
* 🌍 **Sync:** Przycisk resetu synchronizujący czas z czasem systemowym (np. strefa Warsaw).

### Podłączenie (Pinout):
| Element | Pin Pico (GP) | Funkcja |
| :--- | :--- | :--- |
| **LCD SDA** | GP0 | Komunikacja I2C |
| **LCD SCL** | GP1 | Komunikacja I2C |
| **Btn Mode** | GP15 | Zmiana trybu (Zegar/Edit/Stoper) |
| **Btn Up** | GP14 | Plus / Start Stopera |
| **Btn Down** | GP13 | Minus / Reset Stopera |
| **Btn Reset**| GP12 | Synchronizacja czasu (System Time) |

🔗 **Symulacja online:** [WOKWI Project - Pi Pico Version](https://wokwi.com/projects/453391438665750529)

---

## 🚀 Jak uruchomić

### Wymagania:
* Symulator online **WOKWI** (rekomendowane, nie wymaga instalacji).
* LUB fizyczny sprzęt (Arduino Uno / Pi Pico + LCD I2C + przyciski).

### Instrukcja (WOKWI):
1.  Wejdź w jeden z linków do symulacji powyżej.
2.  Kliknij zielony przycisk **Play** w symulatorze.
3.  Używaj wirtualnych przycisków w oknie podglądu, aby sterować zegarem.

### Instrukcja (Lokalnie):
* **Arduino:** Otwórz plik `.c` w Arduino IDE, zainstaluj biblioteki `LiquidCrystal_I2C` oraz `RTClib`, a następnie wgraj na płytkę.
* **Pico:** Wgraj firmware MicroPython na Pico, otwórz plik `.py` w Thonny IDE i zapisz go na urządzeniu jako `main.py`.

---

Copyright © 2026 Łukasz Krajewski.
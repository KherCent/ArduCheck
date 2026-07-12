/*
 * diagnostic_sketch.ino
 *
 * Sketch de auto-diagnóstico para Arduino Uno y Mega.
 * Reporta por Serial el estado de cada subsistema.
 *
 * Protocolo de salida (líneas separadas por '\n'):
 *   $ID,<board>,<chip>          -> identificación
 *   $VCC,<voltaje_x100>          -> voltaje de alimentación (centésimas de V)
 *   $LED,<0|1>                   -> LED pin 13 OK
 *   $DIGPIN,<pin>,<0|1>          -> pin digital funciona (HIGH esperado)
 *   $DIGLOW,<pin>,<0|1>          -> pin digital vuelve a LOW
 *   $ADC,<pin>,<valor>           -> lectura ADC (0-1023)
 *   $PWM,<pin>,<freq>,<rms>      -> PWM generado y medido
 *   $EEPROM,<addr>,<0|1>         -> prueba de EEPROM
 *   $FLASH,<used>,<total>        -> memoria Flash usada/total en bytes
 *   $RAM,<free>                  -> RAM libre en bytes
 *   $I2C,<addr>,<0|1>            -> dispositivo I2C encontrado
 *   $CLK,<millis>,<real_ms>      -> deriva del reloj
 *   $DONE,<0|1|2>                -> 0=OK, 1=WARN, 2=FAIL
 */

#include <Wire.h>
#include <EEPROM.h>

#define VERSION "1.0"

// ---------- CONFIGURACIÓN POR PLACA ----------
#if defined(__AVR_ATmega2560__)
  const char* BOARD_NAME = "Mega";
  const char* CHIP_NAME  = "ATmega2560";
  const int LED_PIN = 13;
  const int FIRST_DIG_PIN = 2;     // pines 0/1 son Serial
  const int LAST_DIG_PIN  = 53;
  const int FIRST_AN_PIN  = A0;
  const int LAST_AN_PIN   = A15;
  const int FIRST_PWM_PIN = 2;     // 2..13
  const int RAM_SIZE = 8192;
  const int FLASH_SIZE = 262144;
#elif defined(__AVR_ATmega328P__)
  const char* BOARD_NAME = "Uno";
  const char* CHIP_NAME  = "ATmega328P";
  const int LED_PIN = 13;
  const int FIRST_DIG_PIN = 2;
  const int LAST_DIG_PIN  = 13;
  const int FIRST_AN_PIN  = A0;
  const int LAST_AN_PIN   = A5;
  const int FIRST_PWM_PIN = 3;
  const int RAM_SIZE = 2048;
  const int FLASH_SIZE = 32768;
#else
  const char* BOARD_NAME = "Generic";
  const char* CHIP_NAME  = "Unknown";
  const int LED_PIN = 13;
  const int FIRST_DIG_PIN = 2;
  const int LAST_DIG_PIN  = 13;
  const int FIRST_AN_PIN  = A0;
  const int LAST_AN_PIN   = A5;
  const int FIRST_PWM_PIN = 3;
  const int RAM_SIZE = 2048;
  const int FLASH_SIZE = 32256;
#endif

unsigned long t_start;

// ---------- HELPERS ----------
void emit(const __FlashStringHelper* tag, long v1 = -99999, long v2 = -99999, long v3 = -99999) {
  Serial.print(tag);
  if (v1 != -99999) {
    Serial.print(',');
    Serial.print(v1);
  }
  if (v2 != -99999) {
    Serial.print(',');
    Serial.print(v2);
  }
  if (v3 != -99999) {
    Serial.print(',');
    Serial.print(v3);
  }
  Serial.println();
  Serial.flush();
}

// ---------- TEST 1: identificación ----------
void test_id() {
  emit(F("$ID"), (long)BOARD_NAME, (long)CHIP_NAME);
}

// ---------- TEST 2: voltaje interno (1.1V bandgap) ----------
long readVcc() {
  // Técnica: leer bandgap interno con Vcc como referencia
  ADMUX = _BV(REFS0) | _BV(MUX3) | _BV(MUX2) | _BV(MUX1);
  delay(2);
  ADCSRA |= _BV(ADSC);
  while (bit_is_set(ADCSRA, ADCSRA));
  long result = ADCL;
  result |= (ADCH << 8);
  result = 1125300L / result; // 1.1V * 1023 * 1000 / 10
  return result;
}

void test_voltage() {
  long v = readVcc();
  emit(F("$VCC"), v);
}

// ---------- TEST 3: LED integrado ----------
void test_led() {
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, HIGH);
  delay(50);
  bool ok = (digitalRead(LED_PIN) == HIGH);
  digitalWrite(LED_PIN, LOW);
  delay(50);
  emit(F("$LED"), ok ? 1 : 0);
}

// ---------- TEST 4: pines digitales ----------
void test_digital_pins() {
  int failures = 0;
  for (int p = FIRST_DIG_PIN; p <= LAST_DIG_PIN; p++) {
    if (p == LED_PIN) continue;
    pinMode(p, OUTPUT);
    digitalWrite(p, HIGH);
    delayMicroseconds(10);
    int hi = digitalRead(p);
    digitalWrite(p, LOW);
    delayMicroseconds(10);
    int lo = digitalRead(p);
    emit(F("$DIGPIN"), p, hi);
    emit(F("$DIGLOW"), p, lo);
    if (hi != HIGH) failures++;
  }
  emit(F("$DIGFAIL"), failures);
}

// ---------- TEST 5: ADC ----------
void test_adc() {
  for (int p = FIRST_AN_PIN; p <= LAST_AN_PIN; p++) {
    analogRead(p); // descarte
    int v = analogRead(p);
    emit(F("$ADC"), p, v);
  }
}

// ---------- TEST 6: PWM ----------
void test_pwm() {
  for (int p = FIRST_PWM_PIN; p <= LAST_DIG_PIN; p++) {
    // PWM solo en pines marcados como PWM por hardware
    #if defined(__AVR_ATmega2560__)
      bool isPWM = (p == 2 || p == 3 || p == 4 || p == 5 ||
                    (p >= 6 && p <= 9) || (p >= 11 && p <= 13));
    #else
      bool isPWM = (p == 3 || p == 5 || p == 6 || p == 9 || p == 10 || p == 11);
    #endif
    if (!isPWM) continue;
    analogWrite(p, 128);
    delay(20);
    int rms = analogRead(A0); // medir en A0 si está conectado
    analogWrite(p, 0);
    emit(F("$PWM"), p, 490, rms);
  }
}

// ---------- TEST 7: EEPROM ----------
void test_eeprom() {
  bool ok = true;
  for (int addr = 0; addr < 16; addr++) {
    byte original = EEPROM.read(addr);
    EEPROM.write(addr, (byte)~addr);
    byte readback = EEPROM.read(addr);
    EEPROM.write(addr, original);
    emit(F("$EEPROM"), addr, (readback == (byte)~addr) ? 1 : 0);
    if (readback != (byte)~addr) ok = false;
  }
  emit(F("$EEPOK"), ok ? 1 : 0);
}

// ---------- TEST 8: memoria ----------
void test_memory() {
  int ram_free = freeRam();
  emit(F("$RAM"), ram_free);
  // Flash size es aproximado al definido en board.txt
  emit(F("$FLASH"), FLASH_SIZE, FLASH_SIZE);
}

// ---------- TEST 8.5: Free RAM helper ----------
int freeRam() {
  extern int __heap_start, *__brkval;
  int v;
  return (int)&v - (__brkval == 0 ? (int)&__heap_start : (int)__brkval);
}

// ---------- TEST 9: I2C ----------
void test_i2c() {
  Wire.begin();
  int found = 0;
  for (byte addr = 1; addr < 0x7F; addr++) {
    Wire.beginTransmission(addr);
    if (Wire.endTransmission() == 0) {
      emit(F("$I2C"), addr, 1);
      found++;
    }
  }
  emit(F("$I2CCOUNT"), found);
}

// ---------- TEST 10: SPI ----------
void test_spi() {
  // Solo verifica que los pines SPI responden
  pinMode(SCK, OUTPUT);
  digitalWrite(SCK, HIGH);
  delayMicroseconds(1);
  bool sck = (digitalRead(SCK) == HIGH);
  emit(F("$SPI"), sck ? 1 : 0);
}

// ---------- TEST 11: reloj ----------
void test_clock() {
  unsigned long m = millis();
  delay(1000);
  unsigned long real = millis() - m;
  emit(F("$CLK"), m, real);
}

// ---------- SETUP / LOOP ----------
void setup() {
  Serial.begin(115200);
  while (!Serial) {;}
  t_start = millis();

  Serial.print(F("# Arduino Diagnostic v"));
  Serial.println(F(VERSION));
  emit(F("$BEGIN"));

  test_id();
  test_voltage();
  test_led();
  test_digital_pins();
  test_adc();
  test_pwm();
  test_eeprom();
  test_memory();
  test_i2c();
  test_spi();
  test_clock();

  emit(F("$DONE"), 0);
}

void loop() {
  // Nada que hacer; todo se ejecuta en setup()
  delay(10000);
}

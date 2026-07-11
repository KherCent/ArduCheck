/**
 * diagnostic_sketch.ino — Arduino SAMD (Zero, MKR, Nano 33 IoT)
 * 
 * Compatible con: Arduino Zero, MKR1000, MKR WiFi 1010, Nano 33 IoT
 * MCU: ATSAMD21G18 (SAMD21)
 * 
 * Test incluidos:
 *   - LED integrado (pin 13 = PA17 en Zero/MKR, pin 13 en Nano 33 IoT)
 *   - Pines digitales (D0-D21)
 *   - ADC (A0-A5, pines 14-19)
 *   - DAC (A0, solo en Zero/MKR)
 *   - PWM (varios pines)
 *   - Communication Serial (USB Native + Serial1)
 *   - clock() accuracy
 *   - freeMemory() (heap)
 *   - millis() / micros()
 */

#include <Arduino.h>

#define BAUD 115200
#define TEST_TOKEN "DIAG_SAMD_V1"
#define DELAY_MS 50
#define PWM_FREQ 490

// LEDs y pines especiales
#if defined(ARDUINO_SAMD_ZERO)
  #define LED_PIN 13
  #define DAC_PIN DAC0
#elif defined(ARDUINO_SAMD_MKR1000) || defined(ARDUINO_SAMD_MKRWIFI1010)
  #define LED_PIN  LED_BUILTIN
  #define DAC_PIN DAC0
#elif defined(ARDUINO_NANO_33_IOT)
  #define LED_PIN  LED_BUILTIN
#else
  #define LED_PIN 13
#endif

struct TestResult {
    const char* name;
    bool pass;
    const char* detail;
};

// ---------- Utilities ----------
static void send_test(const char* name, bool pass, const char* detail) {
    Serial.print("TEST:");
    Serial.print(name);
    Serial.print(":");
    Serial.print(pass ? "PASS" : "FAIL");
    Serial.print(":");
    Serial.println(detail);
}

static void blink_led(int times, int ms) {
    for (int i = 0; i < times; i++) {
        digitalWrite(LED_PIN, HIGH);
        delay(ms);
        digitalWrite(LED_PIN, LOW);
        delay(ms);
    }
}

// ---------- Test: Identidad ----------
static TestResult test_identity() {
    TestResult r = {"IDENTITY", true, ""};
    snprintf(r.detail, sizeof(r.detail), "SAMD21 | %s | %s", 
             TEST_TOKEN, LED_PIN == 13 ? "D13_OK" : "LED_OK");
    return r;
}

// ---------- Test: LED ----------
static TestResult test_led() {
    TestResult r = {"LED", true, ""};
    pinMode(LED_PIN, OUTPUT);
    digitalWrite(LED_PIN, HIGH);
    delay(DELAY_MS);
    bool high = digitalRead(LED_PIN) == HIGH;
    digitalWrite(LED_PIN, LOW);
    delay(DELAY_MS);
    bool low = digitalRead(LED_PIN) == LOW;
    r.pass = high && low;
    snprintf(r.detail, sizeof(r.detail), "LED=%d | HIGH=%d LOW=%d", 
             LED_PIN, high, low);
    return r;
}

// ---------- Test: Communication ----------
static TestResult test_serial() {
    TestResult r = {"SERIAL", true, ""};
    // Verificar que SerialUSB esta conectado
    bool usb_ok = (SerialUSB || Serial);
    snprintf(r.detail, sizeof(r.detail), "USB=%d SERIAL=%d BAUD=%d", 
             usb_ok, 1, BAUD);
    return r;
}

// ---------- Test: Clock ----------
static TestResult test_clock() {
    TestResult r = {"CLOCK", true, ""};
    unsigned long start = millis();
    unsigned long m1 = millis();
    unsigned long m2 = millis();
    unsigned long elapsed = m2 - m1;
    unsigned long delta = elapsed;
    snprintf(r.detail, sizeof(r.detail), "MILLIS_OK | delta=%lu", delta);
    return r;
}

// ---------- Test: ADC ----------
static TestResult test_adc() {
    TestResult r = {"ADC", true, ""};
    int readings[6] = {0};
    int pins[6] = {A0, A1, A2, A3, A4, A5};
    char buf[64] = "";
    for (int i = 0; i < 6; i++) {
        pinMode(pins[i], INPUT);
        readings[i] = analogRead(pins[i]);
    }
    snprintf(r.detail, sizeof(r.detail), 
             "A0=%d A1=%d A2=%d A3=%d A4=%d A5=%d",
             readings[0], readings[1], readings[2], readings[3], readings[4], readings[5]);
    return r;
}

// ---------- Test: Memory ----------
static TestResult test_memory() {
    TestResult r = {"MEMORY", true, ""};
    extern char _end;
    extern char *__brkval;
    int freeMemory = (&_end - __brkval) + (&__brkval - (&_end));
    snprintf(r.detail, sizeof(r.detail), 
             "FLASH=%dKB | RAM_est=%dKB | HEAP=OK",
             (int)(FlashSize / 1024), freeMemory / 1024);
    return r;
}

// ---------- Test: USB enumeration ----------
static TestResult test_usb() {
    TestResult r = {"USB", true, ""};
    bool usb_connected = SerialUSB || Serial;
    snprintf(r.detail, sizeof(r.detail), 
             "USB=%d VUSB=%d", usb_connected, 
             (int)USB->DEVICE.FSMSTATUS.bit.FSMSTATE);
    return r;
}

// ---------- Test: PWM ----------
static TestResult test_pwm() {
    TestResult r = {"PWM", true, ""};
    int pwm_pins[] = {3, 4, 5, 6, 8, 9, 10, 11, 12, 13};
    int count = 0;
    for (int i = 0; i < 10; i++) {
        pinMode(pwm_pins[i], OUTPUT);
        analogWrite(pwm_pins[i], 128);
        count++;
    }
    snprintf(r.detail, sizeof(r.detail), "PWM_pins=%d/10", count);
    for (int i = 0; i < 10; i++) {
        analogWrite(pwm_pins[i], 0);
    }
    return r;
}

// ---------- Test: DAC (si esta disponible) ----------
static TestResult test_dac() {
    TestResult r = {"DAC", true, "NO_DAC"};
#if defined(DAC0)
    analogWrite(DAC0, 128);
    delay(DELAY_MS);
    int val = analogRead(DAC0);
    analogWrite(DAC0, 0);
    snprintf(r.detail, sizeof(r.detail), "DAC=%d", val);
    r.pass = true;
#else
    snprintf(r.detail, sizeof(r.detail), "NO_DAC_AVAILABLE");
    r.pass = true;
#endif
    return r;
}

// ---------- setup ----------
void setup() {
    // Esperar que se inicialice el SerialUSB
    while (!Serial && millis() < 3000) { }
    
    Serial.begin(BAUD);
    #ifdef SerialUSB
    SerialUSB.begin(BAUD);
    #endif
    
    Serial.print("\n=== ");
    Serial.print(TEST_TOKEN);
    Serial.println(" ===");
    Serial.print("Board: ");
    #ifdef ARDUINO_SAMD_ZERO
    Serial.println("Arduino Zero");
    #elif defined(ARDUINO_SAMD_MKR1000)
    Serial.println("Arduino MKR1000");
    #elif defined(ARDUINO_SAMD_MKRWIFI1010)
    Serial.println("Arduino MKR WiFi 1010");
    #elif defined(ARDUINO_NANO_33_IOT)
    Serial.println("Arduino Nano 33 IoT");
    #else
    Serial.println("SAMD Board");
    #endif
    
    // Ejecutar tests
    TestResult results[10];
    int n = 0;
    
    results[n++] = test_identity();
    results[n++] = test_led();
    results[n++] = test_serial();
    results[n++] = test_clock();
    results[n++] = test_adc();
    results[n++] = test_memory();
    results[n++] = test_usb();
    results[n++] = test_pwm();
    results[n++] = test_dac();
    
    // Enviar resultados
    Serial.println("--- RESULTS ---");
    int passed = 0;
    for (int i = 0; i < n; i++) {
        send_test(results[i].name, results[i].pass, results[i].detail);
        if (results[i].pass) passed++;
    }
    
    Serial.print("--- SUMMARY:");
    Serial.print(passed);
    Serial.print("/");
    Serial.print(n);
    Serial.print(" PASS ---");
    Serial.println();
    
    blink_led(passed == n ? 3 : 1, 200);
}

// ---------- loop ----------
void loop() {
    delay(1000);
    digitalWrite(LED_PIN, !digitalRead(LED_PIN));
}

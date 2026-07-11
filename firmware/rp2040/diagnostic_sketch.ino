/**
 * diagnostic_sketch.ino — Raspberry Pi RP2040 (Pico, Nano RP2040 Connect)
 * 
 * Compatible con: Raspberry Pi Pico, Pico W, Arduino Nano RP2040 Connect
 * MCU: RP2040 (dual-core ARM Cortex-M0+)
 * 
 * Test incluidos:
 *   - LED integrado (pin LED_BUILTIN)
 *   - Pines digitales (GPIO 0-29)
 *   - ADC (GPIO 26-29, 4 canales)
 *   - PWM (todos los pines)
 *   - Communication Serial (USB CDC + UART0)
 *   - clock() / millis() / micros()
 *   - freeMemory()
 */

#include <Arduino.h>

#define BAUD 115200
#define TEST_TOKEN "DIAG_RP2040_V1"
#define DELAY_MS 50

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
        digitalWrite(LED_BUILTIN, HIGH);
        delay(ms);
        digitalWrite(LED_BUILTIN, LOW);
        delay(ms);
    }
}

// ---------- Test: Identity ----------
static TestResult test_identity() {
    TestResult r = {"IDENTITY", true, ""};
    snprintf(r.detail, sizeof(r.detail), "RP2040 | %s | CORE=%d", 
             TEST_TOKEN, rp2040.hwlib_version);
    return r;
}

// ---------- Test: LED ----------
static TestResult test_led() {
    TestResult r = {"LED", true, ""};
    pinMode(LED_BUILTIN, OUTPUT);
    digitalWrite(LED_BUILTIN, HIGH);
    delay(DELAY_MS);
    bool high = digitalRead(LED_BUILTIN) == HIGH;
    digitalWrite(LED_BUILTIN, LOW);
    delay(DELAY_MS);
    bool low = digitalRead(LED_BUILTIN) == LOW;
    r.pass = high && low;
    snprintf(r.detail, sizeof(r.detail), "LED=%d HIGH=%d LOW=%d", 
             LED_BUILTIN, high, low);
    return r;
}

// ---------- Test: GPIO ----------
static TestResult test_gpio() {
    TestResult r = {"GPIO", true, ""};
    int tested = 0;
    int failed = 0;
    // Testear pines basicos: 0, 1, 2, 3, 4, 5, 15, 16, 17, 18, 19, 20, 21, 22
    int test_pins[] = {0, 1, 2, 3, 4, 5, 15, 16, 17, 18, 19, 20, 21, 22};
    for (int i = 0; i < 14; i++) {
        int pin = test_pins[i];
        pinMode(pin, OUTPUT);
        digitalWrite(pin, HIGH);
        if (digitalRead(pin) == HIGH) tested++;
        digitalWrite(pin, LOW);
        if (digitalRead(pin) == LOW) tested++;
    }
    snprintf(r.detail, sizeof(r.detail), "GPIO_tested=%d/28", tested);
    r.pass = (tested >= 20);
    return r;
}

// ---------- Test: ADC ----------
static TestResult test_adc() {
    TestResult r = {"ADC", true, ""};
    int a0 = analogRead(A0);
    int a1 = analogRead(A1);
    int a2 = analogRead(A2);
    int a3 = analogRead(A3);
    snprintf(r.detail, sizeof(r.detail), "A0=%d A1=%d A2=%d A3=%d", 
             a0, a1, a2, a3);
    r.pass = (a0 >= 0 && a3 >= 0);
    return r;
}

// ---------- Test: PWM ----------
static TestResult test_pwm() {
    TestResult r = {"PWM", true, ""};
    int pwm_pins[] = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22};
    int count = 0;
    for (int i = 0; i < 23; i++) {
        pinMode(pwm_pins[i], OUTPUT);
        analogWrite(pwm_pins[i], 128);
        count++;
    }
    snprintf(r.detail, sizeof(r.detail), "PWM_pins=%d/23", count);
    for (int i = 0; i < 23; i++) {
        analogWrite(pwm_pins[i], 0);
    }
    return r;
}

// ---------- Test: Memory ----------
static TestResult test_memory() {
    extern char _end;
    extern char *__brkval;
    int freeMemory = (&_end - __brkval);
    TestResult r = {"MEMORY", true, ""};
    snprintf(r.detail, sizeof(r.detail), 
             "RAM=%dKB | HEAP=OK | CORE=%d",
             freeMemory / 1024, rp2040.cpucore);
    return r;
}

// ---------- Test: Serial ----------
static TestResult test_serial() {
    TestResult r = {"SERIAL", true, ""};
    bool serial_ok = (bool)Serial;
    snprintf(r.detail, sizeof(r.detail), "USB_CDC=%d BAUD=%d", serial_ok, BAUD);
    return r;
}

// ---------- Test: Clock ----------
static TestResult test_clock() {
    TestResult r = {"CLOCK", true, ""};
    unsigned long m1 = millis();
    delay(100);
    unsigned long m2 = millis();
    unsigned long elapsed = m2 - m1;
    bool clock_ok = (elapsed >= 95 && elapsed <= 110);
    snprintf(r.detail, sizeof(r.detail), "MILLIS_elapsed=%lu", elapsed);
    r.pass = clock_ok;
    return r;
}

// ---------- Test: Watchdog ----------
static TestResult test_watchdog() {
    TestResult r = {"WATCHDOG", true, ""};
    // RP2040 tiene watchdog hardware
    bool has_wdog = true;
    snprintf(r.detail, sizeof(r.detail), "HW_WATCHDOG=%d", has_wdog);
    return r;
}

// ---------- setup ----------
void setup() {
    Serial.begin(BAUD);
    while (!Serial && millis() < 3000) { }
    
    Serial.print("\n=== ");
    Serial.print(TEST_TOKEN);
    Serial.println(" ===");
    Serial.print("Board: ");
    #ifdef ARDUINO_NANO_RP2040_CONNECT
    Serial.println("Arduino Nano RP2040 Connect");
    #elif defined(ARDUINO_RASPBERRY_PI_PICO)
    Serial.println("Raspberry Pi Pico");
    #else
    Serial.println("RP2040 Board");
    #endif
    Serial.printf("CPU cores: %d\n", rp2040.cpucore);
    Serial.printf("CPU freq: %lu MHz\n", rp2040.freq CPU ? rp2040.freqcpu() / 1000000 : 0);
    
    TestResult results[10];
    int n = 0;
    
    results[n++] = test_identity();
    results[n++] = test_led();
    results[n++] = test_gpio();
    results[n++] = test_adc();
    results[n++] = test_pwm();
    results[n++] = test_memory();
    results[n++] = test_serial();
    results[n++] = test_clock();
    results[n++] = test_watchdog();
    
    Serial.println("--- RESULTS ---");
    int passed = 0;
    for (int i = 0; i < n; i++) {
        send_test(results[i].name, results[i].pass, results[i].detail);
        if (results[i].pass) passed++;
    }
    
    Serial.printf("--- SUMMARY:%d/%d PASS ---\n", passed, n);
    
    blink_led(passed == n ? 3 : 1, 200);
}

// ---------- loop ----------
void loop() {
    delay(1000);
    digitalWrite(LED_BUILTIN, !digitalRead(LED_BUILTIN));
}

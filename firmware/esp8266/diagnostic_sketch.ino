/**
 * diagnostic_sketch.ino — ESP8266 (NodeMCU, Wemos D1 Mini, etc.)
 * 
 * Compatible con: NodeMCU V2/V3, Wemos D1 Mini, ESP-12E/F, 
 *                y cualquier placa basada en ESP8266
 * MCU: Tensilica Xtensa LX106
 * 
 * Test incluidos:
 *   - LED integrado (GPIO 2 en la mayoria)
 *   - Communication Serial (USB CDC)
 *   - WiFi scan
 *   - ADC (A0 = TOUT)
 *   - free memory / heap
 *   - CPU frequency
 */

#include <Arduino.h>

#define BAUD 115200
#define TEST_TOKEN "DIAG_ESP8266_V1"
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
    int led = LED_BUILTIN; // GPIO 2 en la mayoria
    pinMode(led, OUTPUT);
    for (int i = 0; i < times; i++) {
        digitalWrite(led, LOW);  // LED invertido en D1 Mini
        delay(ms);
        digitalWrite(led, HIGH);
        delay(ms);
    }
}

// ---------- Test: Identity ----------
static TestResult test_identity() {
    TestResult r = {"IDENTITY", true, ""};
    snprintf(r.detail, sizeof(r.detail), "ESP8266 | %s | SDK=%s", 
             TEST_TOKEN, ESP.getSdkVersion());
    return r;
}

// ---------- Test: LED ----------
static TestResult test_led() {
    TestResult r = {"LED", true, ""};
    int led = LED_BUILTIN;
    pinMode(led, OUTPUT);
    digitalWrite(led, LOW);  // Many D1 Mini boards have inverted LED
    delay(DELAY_MS);
    bool state1 = digitalRead(led);
    digitalWrite(led, HIGH);
    delay(DELAY_MS);
    bool state2 = digitalRead(led);
    r.pass = (state1 != state2);
    snprintf(r.detail, sizeof(r.detail), "LED=%d STATE1=%d STATE2=%d", 
             led, state1, state2);
    return r;
}

// ---------- Test: ADC ----------
static TestResult test_adc() {
    TestResult r = {"ADC", true, ""};
    int adc0 = analogRead(A0);  // A0 = TOUT pin
    snprintf(r.detail, sizeof(r.detail), "A0=%d (TOUT)", adc0);
    r.pass = (adc0 >= 0 && adc0 <= 1024);
    return r;
}

// ---------- Test: Memory ----------
static TestResult test_memory() {
    TestResult r = {"MEMORY", true, ""};
    size_t heap = ESP.getFreeHeap();
    uint32_t flash = ESP.getFlashChipSize();
    uint8_t chip = ESP.getChipRevision();
    snprintf(r.detail, sizeof(r.detail), 
             "HEAP=%dKB FLASH=%dKB CHIP_REV=%d",
             heap / 1024, flash / 1048576, chip);
    r.pass = (heap > 10000);
    return r;
}

// ---------- Test: Serial ----------
static TestResult test_serial() {
    TestResult r = {"SERIAL", true, ""};
    bool ok = (bool)Serial;
    snprintf(r.detail, sizeof(r.detail), "USB=%d BAUD=%d", ok, BAUD);
    return r;
}

// ---------- Test: Clock ----------
static TestResult test_clock() {
    TestResult r = {"CLOCK", true, ""};
    unsigned long m1 = millis();
    delay(100);
    unsigned long m2 = millis();
    unsigned long elapsed = m2 - m1;
    unsigned long freq = ESP.getCpuFreqMHz();
    bool clock_ok = (elapsed >= 95 && elapsed <= 115);
    snprintf(r.detail, sizeof(r.detail), "MILLIS=%lu FREQ=%luMHz", elapsed, freq);
    r.pass = clock_ok;
    return r;
}

// ---------- Test: WiFi ----------
static TestResult test_wifi() {
    TestResult r = {"WIFI", true, "NO_SCAN"};
    int networks = WiFi.scanNetworks();
    snprintf(r.detail, sizeof(r.detail), "WIFI_scan=%d networks", networks);
    WiFi.scanDelete();
    return r;
}

// ---------- Test: Reset ----------
static TestResult test_reset() {
    TestResult r = {"RESET", true, ""};
    rst_reasons reason = ESP.getResetReason();
    snprintf(r.detail, sizeof(r.detail), "REASON=%d", (int)reason);
    return r;
}

// ---------- Test: Flash ----------
static TestResult test_flash() {
    TestResult r = {"FLASH", true, ""};
    uint32_t realSize = ESP.getFlashChipRealSize();
    uint32_t IDESize = ESP.getFlashChipSize();
    bool match = (realSize == IDESize);
    snprintf(r.detail, sizeof(r.detail), 
             "REAL=%luKB IDE=%luKB MATCH=%d",
             realSize / 1024, IDESize / 1024, match);
    r.pass = match;
    return r;
}

// ---------- Test: System ----------
static TestResult test_system() {
    TestResult r = {"SYSTEM", true, ""};
    uint32_t up = micros();
    uint32_t vcc = ESP.getVcc();
    snprintf(r.detail, sizeof(r.detail), "VCC=%umV UPTIME=%lu", vcc, up / 1000000);
    return r;
}

// ---------- setup ----------
void setup() {
    Serial.begin(BAUD);
    delay(500);
    
    Serial.print("\n=== ");
    Serial.print(TEST_TOKEN);
    Serial.println(" ===");
    Serial.printf("Chip ID: %08X\n", ESP.getChipId());
    Serial.printf("Flash size: %lu KB (IDE: %lu KB)\n", 
                  ESP.getFlashChipRealSize() / 1024, 
                  ESP.getFlashChipSize() / 1024);
    Serial.printf("Free heap: %lu bytes\n", ESP.getFreeHeap());
    Serial.printf("CPU freq: %lu MHz\n", ESP.getCpuFreqMHz());
    Serial.printf("SDK: %s\n", ESP.getSdkVersion());
    Serial.printf("Mac: %s\n", WiFi.macAddress().c_str());
    
    TestResult results[10];
    int n = 0;
    
    results[n++] = test_identity();
    results[n++] = test_led();
    results[n++] = test_serial();
    results[n++] = test_memory();
    results[n++] = test_clock();
    results[n++] = test_adc();
    results[n++] = test_wifi();
    results[n++] = test_reset();
    results[n++] = test_flash();
    results[n++] = test_system();
    
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
    int led = LED_BUILTIN;
    digitalWrite(led, !digitalRead(led));
}

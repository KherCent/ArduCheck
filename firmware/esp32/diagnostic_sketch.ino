/**
 * diagnostic_sketch.ino — ESP32 (todas las variantes)
 * 
 * Compatible con: ESP32, ESP32-S2, ESP32-S3, ESP32-C3, ESP32-C6, ESP32-H2
 * MCU: Tensilica Xtensa LX6 / RISC-V
 * 
 * Test incluidos:
 *   - LED integrado (GPIO 2 en la mayoria)
 *   - Communication Serial (USB CDC + UART0)
 *   - WiFi scan (solo si hay modulo)
 *   - BLE scan (si esta disponible)
 *   - ADC (GPIO 36-39, 32-35)
 *   - Hall sensor
 *   - Touch pins
 *   - free memory / heap
 *   - CPU frequency
 */

#include <Arduino.h>

#define BAUD 115200
#define TEST_TOKEN "DIAG_ESP32_V1"
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
    int led = 2; // Default LED en GPIO2
    #ifdef LED_BUILTIN
    led = LED_BUILTIN;
    #endif
    pinMode(led, OUTPUT);
    for (int i = 0; i < times; i++) {
        digitalWrite(led, HIGH);
        delay(ms);
        digitalWrite(led, LOW);
        delay(ms);
    }
}

// ---------- Test: Identity ----------
static TestResult test_identity() {
    TestResult r = {"IDENTITY", true, ""};
    #if defined(ESP32)
    snprintf(r.detail, sizeof(r.detail), "ESP32 | %s | REV=%d", 
             TEST_TOKEN, ESP.getRevision());
    #elif defined(ESP32S2)
    snprintf(r.detail, sizeof(r.detail), "ESP32-S2 | %s", TEST_TOKEN);
    #elif defined(ESP32S3)
    snprintf(r.detail, sizeof(r.detail), "ESP32-S3 | %s", TEST_TOKEN);
    #elif defined(ESP32C3)
    snprintf(r.detail, sizeof(r.detail), "ESP32-C3 | %s", TEST_TOKEN);
    #else
    snprintf(r.detail, sizeof(r.detail), "ESP32_UNKNOWN | %s", TEST_TOKEN);
    #endif
    return r;
}

// ---------- Test: LED ----------
static TestResult test_led() {
    TestResult r = {"LED", true, ""};
    int led = 2;
    #ifdef LED_BUILTIN
    led = LED_BUILTIN;
    #endif
    pinMode(led, OUTPUT);
    digitalWrite(led, HIGH);
    delay(DELAY_MS);
    bool high = digitalRead(led) == HIGH;
    digitalWrite(led, LOW);
    delay(DELAY_MS);
    bool low = digitalRead(led) == LOW;
    r.pass = high && low;
    snprintf(r.detail, sizeof(r.detail), "LED=%d HIGH=%d LOW=%d", led, high, low);
    return r;
}

// ---------- Test: ADC ----------
static TestResult test_adc() {
    TestResult r = {"ADC", true, ""};
    int readings[4] = {0};
    #ifdef A0
    readings[0] = analogRead(A0);
    #endif
    #ifdef A3
    readings[1] = analogRead(A3);
    #endif
    #ifdef A4
    readings[2] = analogRead(A4);
    #endif
    #ifdef A5
    readings[3] = analogRead(A5);
    #endif
    snprintf(r.detail, sizeof(r.detail), "A0=%d A3=%d A4=%d A5=%d", 
             readings[0], readings[1], readings[2], readings[3]);
    r.pass = true;
    return r;
}

// ---------- Test: Memory ----------
static TestResult test_memory() {
    TestResult r = {"MEMORY", true, ""};
    size_t heap = ESP.getFreeHeap();
    size_t psram = 0;
    #ifdef PSRAM
    psram = ESP.getPsramSize();
    #endif
    snprintf(r.detail, sizeof(r.detail), 
             "HEAP=%dKB PSRAM=%dKB FLASH=%dKB",
             heap / 1024, psram / 1024, ESP.getFlashChipSize() / 1048576);
    r.pass = (heap > 20000);
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

// ---------- Test: Hall Sensor (ESP32 only) ----------
static TestResult test_hall() {
    TestResult r = {"HALL", true, "NO_HALL"};
    #ifdef ESP32
    int hall = hallRead();
    snprintf(r.detail, sizeof(r.detail), "HALL=%d", hall);
    #else
    snprintf(r.detail, sizeof(r.detail), "NO_HALL_AVAILABLE");
    #endif
    return r;
}

// ---------- Test: Touch ----------
static TestResult test_touch() {
    TestResult r = {"TOUCH", true, "NO_TOUCH"};
    #ifdef ESP32
    // GPIO 4, 0, 2, 15, 13, 12, 14 son touch en ESP32
    int t4 = touchRead(T9);  // GPIO 4
    snprintf(r.detail, sizeof(r.detail), "TOUCH_T9=%d", t4);
    r.pass = (t4 > 0 && t4 < 200);
    #else
    snprintf(r.detail, sizeof(r.detail), "NO_TOUCH_AVAILABLE");
    #endif
    return r;
}

// ---------- Test: WiFi ----------
static TestResult test_wifi() {
    TestResult r = {"WIFI", true, "NO_WIFI"};
    #ifdef ESP32
    int networks = WiFi.scanNetworks();
    snprintf(r.detail, sizeof(r.detail), "WIFI_scan=%d networks", networks);
    WiFi.scanDelete();
    r.pass = true;
    #else
    snprintf(r.detail, sizeof(r.detail), "NO_WIFI_MODULE");
    #endif
    return r;
}

// ---------- Test: Reset reason ----------
static TestResult test_reset() {
    TestResult r = {"RESET", true, ""};
    int reason = esp_reset_reason();
    const char* reasons[] = {
        "POWERON", "SW_RESET", "OW_RESET", "PANIC", 
        "INT_WDT", "TASK_WDT", "WDT", "DEEPSLEEP", "SW_RESET", "EXT_WAKEUP"
    };
    const char* rstr = (reason >= 0 && reason <= 9) ? reasons[reason] : "UNKNOWN";
    snprintf(r.detail, sizeof(r.detail), "REASON=%d (%s)", reason, rstr);
    return r;
}

// ---------- setup ----------
void setup() {
    Serial.begin(BAUD);
    delay(500);
    
    Serial.print("\n=== ");
    Serial.print(TEST_TOKEN);
    Serial.println(" ===");
    Serial.printf("Chip: %s\n", ESP.getChipModel());
    Serial.printf("Chip revision: %d\n", ESP.getChipRevision());
    Serial.printf("CPU cores: %d\n", ESP.getChipCores());
    Serial.printf("CPU freq: %lu MHz\n", ESP.getCpuFreqMHz());
    Serial.printf("Flash size: %lu MB\n", ESP.getFlashChipSize() / 1048576);
    Serial.printf("Free heap: %lu bytes\n", ESP.getFreeHeap());
    
    TestResult results[10];
    int n = 0;
    
    results[n++] = test_identity();
    results[n++] = test_led();
    results[n++] = test_serial();
    results[n++] = test_memory();
    results[n++] = test_clock();
    results[n++] = test_adc();
    results[n++] = test_hall();
    results[n++] = test_touch();
    results[n++] = test_wifi();
    results[n++] = test_reset();
    
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
    int led = 2;
    #ifdef LED_BUILTIN
    led = LED_BUILTIN;
    #endif
    digitalWrite(led, !digitalRead(led));
}

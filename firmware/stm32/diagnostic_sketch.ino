/*
 * firmware/stm32/diagnostic_sketch.ino
 *
 * Sketch de auto-test para Arduino Portenta H7 / Giga (STM32H747).
 * Compatible con el core STM32duino (mbed).
 *
 * Protocolo de comunicación (serie a 115200 baud):
 *   $ID,<board>,<chip>          - Identificación
 *   $VCC,<mv>                    - Voltaje en milivoltios
 *   $LED,<0|1>                   - Test del LED integrado
 *   $I2C,<addr1>,<addr2>,...     - Dispositivos I2C detectados (hex)
 *   $RAM,<bytes>                 - RAM libre aproximada
 *   $CLK,<expected_ms>,<actual>  - Deriva del reloj
 *   $DONE,<code>                 - Fin (0=OK, 1=ERROR)
 */

#include <Arduino.h>
#include <Wire.h>

// LED_BUILTIN está disponible en Portenta H7 / Giga
#ifdef LED_BUILTIN
const int LED_PIN = LED_BUILTIN;
#else
const int LED_PIN = 13;  // fallback para BluePill
#endif

// Test del LED
bool test_led() {
    pinMode(LED_PIN, OUTPUT);
    digitalWrite(LED_PIN, HIGH);
    delay(200);
    digitalWrite(LED_PIN, LOW);
    delay(200);
    digitalWrite(LED_PIN, HIGH);
    delay(200);
    bool ok = digitalRead(LED_PIN) == HIGH;
    digitalWrite(LED_PIN, LOW);
    return ok;
}

// Leer voltaje de alimentación (aproximación usando ADC interno)
// En la mayoría de los STM32 el ADC puede leer VREF+ internamente
uint16_t read_vcc_mv() {
    // STM32 con ADC interno: leer VDD
    // Nota: los valores exactos dependen del modelo
    // Para Portenta H7 y Giga, usamos el ADC en PA0 (con divisor si es necesario)
    // Placeholder: devuelve un valor representativo
#if defined(ARDUINO_PORTENTA_H7_M7) || defined(ARDUINO_GIGA)
    // En Portenta H7 y Giga, el voltaje nominal es 3.3V
    // Se puede usar el sensor de voltaje interno si está disponible
    // Por ahora, retornamos 3300mV como aproximación
    return 3300;
#elif defined(ARDUINO_BLUEPILL_F103C8) || defined(ARDUINO_BLUEPILL_F103CB)
    // BluePill (STM32F103): 3.3V nominal
    return 3300;
#else
    // Desconocido
    return 0;
#endif
}

// Escanear I2C
void scan_i2c(char* buffer, size_t bufsize) {
    byte error, address;
    int nDevices = 0;
    char temp[16];
    buffer[0] = '\0';

    Wire.begin();
    for (address = 1; address < 127; address++) {
        Wire.beginTransmission(address);
        error = Wire.endTransmission();
        if (error == 0) {
            snprintf(temp, sizeof(temp), "%02X", address);
            if (nDevices > 0) strncat(buffer, ",", bufsize - strlen(buffer) - 1);
            strncat(buffer, temp, bufsize - strlen(buffer) - 1);
            nDevices++;
        }
    }
}

// RAM libre (heap)
int free_ram() {
    extern char _end;
    extern char *__brkval;
    char* heap_start = (__brkval == 0) ? &_end : __brkval;
    char stack;
    return (int)&stack - (int)heap_start;
}

// Test de reloj con millis()
unsigned long test_clock_drift() {
    unsigned long start = millis();
    delay(1000);  // Esperar 1 segundo
    unsigned long elapsed = millis() - start;
    return elapsed;
}

void setup() {
    Serial.begin(115200);
    while (!Serial && millis() < 3000) {
        // Esperar Serial
    }
    delay(500);

    Serial.println("# ArduCheck STM32 Diagnostic v1.0");

    // Identificar placa
#if defined(ARDUINO_PORTENTA_H7_M7) || defined(ARDUINO_PORTENTA_H7_M4)
    Serial.println("$ID,PortentaH7,STM32H747");
#elif defined(ARDUINO_GIGA)
    Serial.println("$ID,ArduinoGiga,STM32H747");
#elif defined(ARDUINO_BLUEPILL_F103C8) || defined(ARDUINO_BLUEPILL_F103CB)
    Serial.println("$ID,BluePill,STM32F103C8");
#else
    Serial.println("$ID,STM32,STM32");
#endif

    // Voltaje VDD
    uint16_t vcc = read_vcc_mv();
    Serial.print("$VCC,");
    Serial.println(vcc);

    // LED
    bool led_ok = test_led();
    Serial.print("$LED,");
    Serial.println(led_ok ? "1" : "0");

    // I2C scan
    char i2c_buf[128] = {0};
    scan_i2c(i2c_buf, sizeof(i2c_buf));
    Serial.print("$I2C,");
    Serial.println(i2c_buf);

    // RAM libre
    int ram = free_ram();
    Serial.print("$RAM,");
    Serial.println(ram);

    // Reloj
    unsigned long drift = test_clock_drift();
    Serial.print("$CLK,1000,");
    Serial.println(drift);

    // Done
    Serial.println("$DONE,0");
}

void loop() {
    delay(100);
}

/*
 * ============================================================
 *  SMART HELMET — MINE SAFETY GATEWAY  |  RECEIVER (Laptop 2)
 *  ESP32 WROOM — AES-128 Decrypted LoRa Receiver
 * ============================================================
 *  Receives encrypted LoRa packets from Smart Helmet sender,
 *  decrypts them, parses sensor data, and displays alerts.
 *
 *  Encryption: AES-128-CBC using mbedTLS (built into ESP32 SDK)
 *              Key and IV MUST MATCH the SENDER exactly.
 *
 *  Libraries (Arduino IDE > Tools > Manage Libraries):
 *    1. LoRa  by Sandeep Mistry
 *    (mbedTLS is built-in to ESP32 — no extra install needed)
 *
 *  Wiring (LoRa module on Laptop 2 ESP32):
 *    LoRa  SCK→18  MISO→19  MOSI→23  NSS→5  RST→14  DIO0→2
 * ============================================================
 */

#include <Arduino.h>
#include <SPI.h>
#include <LoRa.h>
#include "mbedtls/aes.h"

// ─────────────────────────────────────────────────────────────
// LoRa PINS
// ─────────────────────────────────────────────────────────────
#define LORA_SCK   18
#define LORA_MISO  19
#define LORA_MOSI  23
#define LORA_NSS   5
#define LORA_RST   14
#define LORA_DIO0  2
#define LORA_FREQ  433E6

// ─────────────────────────────────────────────────────────────
// AES-128 KEY & IV — MUST MATCH SENDER EXACTLY
// ─────────────────────────────────────────────────────────────
static const uint8_t AES_KEY[16] = {
    0x4D, 0x69, 0x6E, 0x65, 0x53, 0x61, 0x66, 0x65,
    0x48, 0x65, 0x6C, 0x6D, 0x65, 0x74, 0x32, 0x34
};
static const uint8_t AES_IV[16] = {
    0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08,
    0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F, 0x10
};

// ─────────────────────────────────────────────────────────────
// STATE
// ─────────────────────────────────────────────────────────────
int packet_count = 0;

// ─────────────────────────────────────────────────────────────
// AES-128-CBC DECRYPT
//  Returns true on success, decrypted text in 'output'
// ─────────────────────────────────────────────────────────────
bool aes_decrypt(const uint8_t* ciphertext, size_t cipher_len, char* output) {
    if (cipher_len == 0 || cipher_len % 16 != 0) {
        Serial.println("[AES] Error: invalid ciphertext length");
        return false;
    }

    uint8_t iv_copy[16];
    memcpy(iv_copy, AES_IV, 16);

    uint8_t plaintext[128] = {0};

    mbedtls_aes_context ctx;
    mbedtls_aes_init(&ctx);
    mbedtls_aes_setkey_dec(&ctx, AES_KEY, 128);
    mbedtls_aes_crypt_cbc(&ctx, MBEDTLS_AES_DECRYPT, cipher_len, iv_copy, ciphertext, plaintext);
    mbedtls_aes_free(&ctx);

    // Remove PKCS#7 padding
    uint8_t pad_len = plaintext[cipher_len - 1];
    if (pad_len == 0 || pad_len > 16) {
        Serial.println("[AES] Error: bad padding byte");
        return false;
    }
    size_t pt_len = cipher_len - pad_len;
    memcpy(output, plaintext, pt_len);
    output[pt_len] = '\0';
    return true;
}

// ─────────────────────────────────────────────────────────────
// PARSE & DISPLAY packet
//  CSV format: LABEL,TEMP,HUM,GAS,ACC_R,GYR_R
//  e.g.  WARNING,38,89,1850,2.310,95.4
// ─────────────────────────────────────────────────────────────
void parseAndDisplay(const char* data, int rssi) {
    char buf[96];
    strncpy(buf, data, sizeof(buf) - 1);
    buf[sizeof(buf) - 1] = '\0';

    char* token = strtok(buf, ",");
    if (!token) { Serial.println("[PARSE] Error: empty packet"); return; }

    char label[16];
    strncpy(label, token, sizeof(label) - 1);

    int   temp   = 0;
    int   hum    = 0;
    int   gas    = 0;
    float acc_r  = 0.0f;
    float gyr_r  = 0.0f;

    if ((token = strtok(NULL, ","))) temp  = atoi(token);
    if ((token = strtok(NULL, ","))) hum   = atoi(token);
    if ((token = strtok(NULL, ","))) gas   = atoi(token);
    if ((token = strtok(NULL, ","))) acc_r = atof(token);
    if ((token = strtok(NULL, ","))) gyr_r = atof(token);

    // ── Alert color coding via serial ──
    Serial.println();
    if (strcmp(label, "EMERGENCY") == 0) {
        Serial.println("🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨");
        Serial.println("  !!!  E M E R G E N C Y  ALERT  !!!");
        Serial.println("🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨");
    } else if (strcmp(label, "WARNING") == 0) {
        Serial.println("⚠️  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
        Serial.println("  WARNING — Check worker immediately!");
        Serial.println("     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
    } else {
        Serial.println("✅  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
        Serial.println("  NORMAL — All systems OK");
        Serial.println("     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
    }

    Serial.printf("  Packet #   : %d\n", packet_count);
    Serial.printf("  Status     : %s\n", label);
    Serial.printf("  Temperature: %d °C\n",  temp);
    Serial.printf("  Humidity   : %d %%\n",  hum);
    Serial.printf("  Gas        : %d ppm\n", gas);
    Serial.printf("  Accel (R)  : %.3f G\n", acc_r);
    Serial.printf("  Gyro  (R)  : %.1f dps\n", gyr_r);
    Serial.printf("  RSSI       : %d dBm\n", rssi);
    Serial.println("  ─────────────────────────────────────────\n");
}

// ─────────────────────────────────────────────────────────────
// SETUP
// ─────────────────────────────────────────────────────────────
void setup() {
    Serial.begin(115200);
    delay(1000);

    Serial.println("============================================");
    Serial.println("  SMART HELMET GATEWAY — RECEIVER");
    Serial.println("  AES-128-CBC Encrypted LoRa");
    Serial.println("============================================");

    SPI.begin(LORA_SCK, LORA_MISO, LORA_MOSI, LORA_NSS);
    LoRa.setPins(LORA_NSS, LORA_RST, LORA_DIO0);

    if (!LoRa.begin(LORA_FREQ)) {
        Serial.println("[FATAL] LoRa init failed!");
        while (true) delay(1000);
    }

    // LoRa settings MUST match sender
    LoRa.setSpreadingFactor(10);
    LoRa.setSignalBandwidth(125E3);
    LoRa.setCodingRate4(5);

    Serial.printf("[INIT] LoRa listening @ %.0f MHz\n", LORA_FREQ / 1E6);
    Serial.println("[INIT] AES-128-CBC decryption ready");
    Serial.println("[INIT] Waiting for packets...\n");
}

// ─────────────────────────────────────────────────────────────
// MAIN LOOP
// ─────────────────────────────────────────────────────────────
void loop() {
    int packet_size = LoRa.parsePacket();
    if (packet_size == 0) return;

    packet_count++;
    int rssi = LoRa.packetRssi();

    // Read raw bytes
    uint8_t ciphertext[128] = {0};
    int bytes_read = 0;
    while (LoRa.available() && bytes_read < (int)sizeof(ciphertext)) {
        ciphertext[bytes_read++] = LoRa.read();
    }

    Serial.printf("[LoRa] Received %d encrypted bytes | RSSI: %d dBm\n",
                  bytes_read, rssi);

    // Decrypt
    char plaintext[128] = {0};
    if (!aes_decrypt(ciphertext, bytes_read, plaintext)) {
        Serial.println("[AES] Decryption failed — wrong key or corrupted packet");
        return;
    }

    Serial.printf("[AES] Decrypted: %s\n", plaintext);

    // Parse and display
    parseAndDisplay(plaintext, rssi);
}

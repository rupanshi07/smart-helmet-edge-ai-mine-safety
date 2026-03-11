# ⛑️ Smart Helmet — Edge Intelligence for Mine Safety



<p align="center">
  <b>A multi-sensor wearable safety system for underground mine workers.</b><br/>
  On-device CART Decision Tree classification · AES-128-CBC encrypted LoRa · Real-time React dashboard
</p>

<p align="center">
  <i>Rupanshi Sangwan </i><br/>
</p>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [System Architecture](#-system-architecture)
- [Hardware Platform](#-hardware-platform)
- [Machine Learning Pipeline](#-machine-learning-pipeline)
- [Feature Engineering](#-feature-engineering)
- [Communication & Security](#-communication--security)
- [Project Structure](#-project-structure)
- [Installation & Setup](#-installation--setup)
- [Dashboard UI](#-dashboard-ui)
- [Data Format & Thresholds](#-data-format--thresholds)
- [Troubleshooting](#-troubleshooting)
- [Future Work](#-future-work)
- [License](#-license)

---

## 🌍 Overview

Underground mining employs less than 1% of the global workforce yet accounts for approximately **8% of fatal occupational injuries** worldwide (ILO, 2020). Existing mine IoT systems perform hazard classification at a remote gateway or cloud — meaning detection fails the moment the wireless link degrades.

This project solves that by embedding a **CART Decision Tree TinyML model directly on the ESP32 helmet node**, so the worker is protected regardless of network state. The helmet classifies hazards locally, encrypts the result with AES-128-CBC, and transmits selectively over LoRa 433 MHz to a gateway receiver and live dashboard.

### Five Engineering Constraints Addressed

| Constraint | How It Is Solved |
|---|---|
| **RF Impairment** (10–40% packet loss in galleries) | Edge inference — classification survives packet loss |
| **Power Budget** (8–12 hr shift from Li-Po) | Selective TX policy reduces airtime to 33% per node |
| **Latency Criticality** (every second matters) | On-device inference in <0.1 ms; no round-trip needed |
| **Security** (unencrypted LoRa is spoofable) | AES-128-CBC with PKCS#7 integrity on every packet |
| **Scalability** (100s of nodes, one channel) | Selective TX prevents ALOHA collision saturation |

---

## 🗺️ System Architecture

### Design Philosophy: Fail-Safe Edge Autonomy

> The helmet node detects, classifies, and signals hazards **entirely independently** of network connectivity. Layers 2 and 3 are non-critical for worker protection.

```
┌─────────────────────────────────────────────────────────────┐
│               LAYER 1 — HELMET NODE  (ESP32 Tx)             │
│                                                             │
│   Sensors ──► 11-feature vector ──► CART DT Inference       │
│                                          │                  │
│                               Safety Override Layer         │
│                                          │                  │
│                               AES-128-CBC Encrypt           │
│                                          │                  │
│                               LoRa TX  433 MHz              │
└──────────────────────────────────────────┬──────────────────┘
                                           │  Encrypted LoRa Packet
┌──────────────────────────────────────────▼──────────────────┐
│               LAYER 2 — GATEWAY NODE  (ESP32 Rx)            │
│                                                             │
│   LoRa RX ──► AES-128-CBC Decrypt ──► CSV Parse ──► Alert   │
└──────────────────────────────────────────┬──────────────────┘
                                           │  USB Serial  115200 baud
┌──────────────────────────────────────────▼──────────────────┐
│               LAYER 3 — SUPERVISOR INTERFACE                │
│                                                             │
│   React Dashboard  (Web Serial API)  ·  Serial Terminal     │
└─────────────────────────────────────────────────────────────┘
```

### Safety Classification States

| State | Condition | TX Behaviour |
|---|---|---|
| ✅ **NORMAL** | All parameters within bounds | Heartbeat every 15 s (every 3 epochs) |
| ⚠️ **WARNING** | Sensor approaching threshold | Transmit on every state change |
| 🚨 **EMERGENCY** | Threshold breached | Immediate TX + local alert + retry |

---

## 🔧 Hardware Platform

### ESP32-WROOM-32 — Host MCU

| Specification | Value |
|---|---|
| CPU | Dual-core Xtensa LX6 @ 240 MHz |
| SRAM | 520 KB |
| Flash | 4 MB |
| Hardware AES | CBC 64-byte encrypt in **<50 µs** |
| Typical current | ~80 mA active |

**Power budget:** 150 mA avg × 3.7 V × 1500 mAh ≈ **10 hours per shift**

### Sensor Suite

| Component | Model | Key Specs |
|---|---|---|
| IMU | **BMI160** | 925 µW · 16-bit · I2C 400 kHz |
| Temperature & Humidity | **DHT11** | 0–50 °C / 20–80 % RH · ±2 °C · single-wire |
| Gas | **MQ135** | NH₃, NOₓ, CO₂, CO, benzene · 10-sample moving average |
| LoRa Radio | **SX1278** | 433 MHz · SF10 · BW 125 kHz · CR 4/5 · 17 dBm |

### Wiring Reference

**LoRa SX1278 → ESP32** (identical on both sender and receiver)

```
SX1278          ESP32 GPIO
──────────────────────────
SCK      ──►    18
MISO     ──►    19
MOSI     ──►    23
NSS/CS   ──►    5
RST      ──►    14
DIO0     ──►    2
3.3 V    ──►    3.3 V
GND      ──►    GND
```

**BMI160 IMU → ESP32 Sender**

```
BMI160          ESP32 GPIO
──────────────────────────
VCC      ──►    3.3 V
GND      ──►    GND
SCL      ──►    22
SDA      ──►    21
```

---

## 🧠 Machine Learning Pipeline

### Why Not Simple Thresholding?

Rule-based systems (e.g., `if gas > T_g OR temp > T_T`) are insufficient because:

- Sensor drift and vibration cause excessive false alarms
- They cannot exploit **multi-modal correlations** across sensors

**Example:** Moderate gas + elevated temperature + high motion → EMERGENCY, even though each reading individually falls below its standalone threshold. A trained classifier catches this; a threshold rule does not.

### Algorithm Selection — 5-Fold Cross-Validation

| Algorithm | Accuracy | RAM | Flash | Inference Time |
|---|---|---|---|---|
| CNN (1D) | — | > 50 KB | > 100 KB | 5–50 ms |
| LSTM / GRU | — | > 80 KB | > 150 KB | 10–100 ms |
| SVM-RBF | — | > 30 KB | > 60 KB | 5–50 ms |
| Extra Trees | 96.64 % | > 200 KB | > 400 KB | 2–15 ms |
| Random Forest | 96.36 % | > 40 KB | > 80 KB | 2–20 ms |
| XGBoost | 96.55 % | > 150 KB | > 300 KB | 2–20 ms |
| LightGBM | 96.27 % | > 100 KB | > 200 KB | 1–10 ms |
| **CART Decision Tree** | **96.00 %** | **< 1 KB** | **< 8 KB** | **< 0.1 ms** |

Ensemble methods gain only 0.27–0.64 % accuracy over the Decision Tree at 30×–300× more memory — operationally negligible for a 3-class safety classification task.

### Why CART Decision Tree — All 6 ESP32 Constraints Satisfied

| Constraint | Status |
|---|---|
| Inference time < 0.1 ms | ✅ |
| Zero dynamic memory allocation | ✅ |
| Flash footprint < 8 KB | ✅ |
| No external library dependency | ✅ |
| Full human interpretability | ✅ |
| Macro F1 ≥ 0.95 | ✅ |

Every alternative algorithm fails at least one constraint.

### Training Workflow

```
1.  Simulate 5,500 labelled samples  (NORMAL / WARNING / EMERGENCY)
          │
2.  Gaussian noise augmentation  (σ = 0.5 % of sensor range)
          │
3.  Minority-class oversampling  (SMOTE-like balancing)
          │
4.  scikit-learn CART  │  max_depth = 8  │  class_weight = balanced
          │
5.  5-fold stratified cross-validation  ──►  Macro F1 = 0.96
          │
6.  Export  ──►  decision_tree_model.h  (pure C, zero dependencies)
          │
7.  Flash to ESP32 via Arduino IDE
```

### Tools & Frameworks

| Tool / Technology | Purpose |
|---|---|
| Python 3.10 + scikit-learn 1.3 | DT training and C export |
| MATLAB | Sensor simulation, multi-node animation |
| ESP32-WROOM-32 | On-device inference + LoRa TX |
| SX1278 LoRa Module | 433 MHz encrypted communication |
| Arduino IDE + ESP-IDF | Firmware compilation and flashing |
| mbedTLS (built into ESP-IDF) | AES-128-CBC hardware encryption |

---

## 📐 Feature Engineering

### 11-Feature Vector — 5-Second Sensing Epoch

```
x = [ T,  H,  C_gas,  aₓ,  aᵧ,  a_z,  aᴿ,  ωₓ,  ωᵧ,  ω_z,  ωᴿ ]ᵀ
```

| Symbol | Sensor | Description | Unit |
|---|---|---|---|
| T | DHT11 | Ambient temperature | °C |
| H | DHT11 | Relative humidity | % |
| C_gas | MQ135 | Gas concentration | ppm |
| aₓ, aᵧ, a_z | BMI160 | Acceleration axes | G |
| aᴿ | BMI160 | Resultant acceleration magnitude | G |
| ωₓ, ωᵧ, ω_z | BMI160 | Gyroscope axes | dps |
| ωᴿ | BMI160 | Resultant angular velocity | dps |

**Gas Concentration Mapping (MQ135 ADC → ppm):**
```
C_gas = C_base + (ADC / 4095) × (C_max − C_base)
```

**Resultant Magnitudes (BMI160):**
```
aᴿ = √(aₓ² + aᵧ² + a_z²)
ωᴿ = √(ωₓ² + ωᵧ² + ω_z²)
```

### Class Boundary Conditions

| Class | Gas (ppm) | Temperature (°C) |
|---|---|---|
| NORMAL | 350 – 1,000 | < 35 |
| WARNING | 1,000 – 3,000 | 35 – 55 |
| EMERGENCY | > 3,000 | > 55 |

### Safety Override Layer

A deterministic rule-based backstop that operates **independently of the ML prediction**. If any sensor value falls in a borderline region while the DT predicts NORMAL, the override escalates the state to WARNING — ensuring no missed hazard at class decision boundaries.

---

## 📡 Communication & Security

### Selective Transmission Policy

Classification occurs on-device. The radio only transmits when necessary, reducing channel occupancy from 100 % to ~33 % per node — directly lowering collision probability at scale.

| State / Event | Transmission Action |
|---|---|
| EMERGENCY | Transmit immediately — highest priority |
| Any state transition | Transmit on change |
| Steady NORMAL | Heartbeat every N = 3 epochs (15 s) |

### 64-Byte Encrypted Payload

```
┌─────────────┬──────┬──────┬──────┬────────┬────────┐
│  LABEL      │  T   │  H   │  GAS │  aᴿ    │  ωᴿ    │
│  3 – 9 B    │  2 B │  2 B │  4 B │  4 B   │  4 B   │
└─────────────┴──────┴──────┴──────┴────────┴────────┘
Airtime ≈ 1.65 s at SF10  ≪  5 s epoch window
```

### AES-128-CBC Encryption (mbedTLS Hardware-Accelerated)

```
Encryption  (Sender):    Cᵢ = AES_K ( Pᵢ ⊕ Cᵢ₋₁ )    where C₀ = IV
Decryption  (Receiver):  Pᵢ = AES⁻¹_K ( Cᵢ ) ⊕ Cᵢ₋₁
```

| Security Property | Detail |
|---|---|
| **Confidentiality** | 2¹²⁸ key space — no plaintext transmitted over the air |
| **Alert suppression resistance** | Forged or replayed packets fail PKCS#7 validation |
| **Implicit integrity** | Single-bit flip detected with 99.6 % probability |
| **Performance** | 64-byte CBC block in < 50 µs — less than 0.001 % of epoch |

> ⚠️ **Production note:** Replace the fixed IV with a counter-based nonce and store keys in secure flash. Never commit real AES credentials to a public repository.

---

## 📁 Project Structure

```
IoT_S4/
│
├── Arduino/
│   └── smart_helmet_dt/
│       └── smart_helmet_SENDER__1_/
│           ├── smart_helmet_SENDER__1_.ino   ← Helmet node firmware
│           └── decision_tree_model.h         ← Compiled CART model (pure C)
│
├── Arduino Receiver/
│   └── smart_helmet_dt/
│       └── smart_helmet_RECEIVER/
│           └── smart_helmet_RECEIVER.ino     ← Gateway node firmware
│
├── code/
│   ├── smart_helmet_decision_tree.ipynb      ← Model training notebook
│   └── smart_helmet_decision_tree.pkl        ← Trained scikit-learn model
│
├── outputs/
│   ├── decision_tree_model.h                 ← Exported C header
│   ├── tree_rules.txt                        ← Human-readable decision rules
│   └── plots/
│       ├── confusion_matrix_dt.png
│       ├── decision_tree_diagram.png
│       ├── depth_vs_accuracy.png
│       └── feature_importance.png
│
└── UI/
    ├── SmartHelmetDashboardSimulation.jsx    ← Simulated demo dashboard
    └── SmartHelmetRealtime.jsx               ← Live dashboard via Web Serial
```

---

## ⚙️ Installation & Setup

### Prerequisites

| Requirement | Details |
|---|---|
| Arduino IDE | Version 2.x |
| ESP32 Board Package | Add URL in Preferences: `https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json` |
| LoRa Library | Sandeep Mistry — install via `Tools > Manage Libraries > search "LoRa"` |
| mbedTLS | Built into the ESP32 SDK — **no separate install required** |
| Node.js | v18 or later |
| Browser | Chrome or Edge (desktop) — required for Web Serial API |

---

### Step 1 — Flash the Sender (Helmet Node)

1. Open `Arduino/smart_helmet_dt/smart_helmet_SENDER__1_/smart_helmet_SENDER__1_.ino`
2. Confirm `decision_tree_model.h` is in the **same directory** as the `.ino` file
3. Select board: **ESP32 Dev Module**
4. Select the correct COM port
5. Click **Upload**

LoRa settings inside the sketch — these **must match the receiver exactly**:

```cpp
#define LORA_FREQ  433E6
LoRa.setSpreadingFactor(10);
LoRa.setSignalBandwidth(125E3);
LoRa.setCodingRate4(5);
```

---

### Step 2 — Flash the Receiver (Gateway Node)

1. Open `Arduino Receiver/smart_helmet_dt/smart_helmet_RECEIVER/smart_helmet_RECEIVER.ino`
2. Select board: **ESP32 Dev Module**
3. Select the correct COM port
4. Click **Upload**
5. Open Serial Monitor at **115200 baud** to confirm reception

Expected output on successful packet receipt:

```
[LoRa] Received 32 encrypted bytes | RSSI: -72 dBm
[AES]  Decrypted: WARNING,38,89,1850,2.310,95.4

⚠️  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  WARNING — Check worker immediately!
  Packet #   : 5
  Temperature: 38 °C
  Humidity   : 89 %
  Gas        : 1850 ppm
  Accel (R)  : 2.310 G
  Gyro  (R)  : 95.4 dps
  RSSI       : -72 dBm
  ─────────────────────────────────────────
```

---

### Step 3 — Retrain the ML Model (Optional)

```bash
pip install scikit-learn pandas numpy matplotlib seaborn joblib
jupyter notebook code/smart_helmet_decision_tree.ipynb
```

Run all cells to regenerate `decision_tree_model.h` from scratch.

---

## 🖥️ Dashboard UI

### Real-Time Dashboard — Live Hardware

```powershell
# Create the Vite + React project
npm create vite@latest my-ui-app
# Select: React → JavaScript → No (Vite 8 beta)

# Enter the project and install dependencies
cd my-ui-app
npm install
npm install recharts

# Copy the real-time dashboard
copy "D:\IoT_S4\UI\SmartHelmetRealtime.jsx" src\App.jsx

# Clear default styles (PowerShell)
Clear-Content src\index.css

# Launch development server
npm run dev
```

Open **Chrome or Edge** → `http://localhost:5173` → Click **⬡ CONNECT** → Select your ESP32 receiver COM port.

### Simulation Dashboard — No Hardware Required

Same steps as above, but copy the simulation file instead:

```powershell
copy "D:\IoT_S4\UI\SmartHelmetDashboardSimulation.jsx" src\App.jsx
```

Press **▶ START** in the browser to begin simulated packet streaming.

> **Note:** The Web Serial API is only supported in **Chrome and Edge on desktop**. Firefox and mobile browsers are not compatible.

### Dashboard Features

| Feature | Description |
|---|---|
| Arc Gauges | Live readings for all 5 sensors with threshold colour-coding |
| Sparkline Trends | Rolling chart of the last 30–40 packets per sensor |
| Status Banner | NORMAL / WARNING / EMERGENCY with animated emergency ring |
| Packet Log | Scrollable sidebar with decoded sensor values per packet |
| Raw Serial Monitor | Full serial output tab — colour-coded by message type |
| RSSI Indicator | Signal strength display updated per packet |

---

## 📦 Data Format & Thresholds

### Packet CSV Format

```
LABEL,TEMP,HUM,GAS,ACC_R,GYR_R
```

**Example:** `EMERGENCY,43,94,2450,5.120,112.3`

### Field Definitions

| Field | Type | Unit | NORMAL | WARNING | EMERGENCY |
|---|---|---|---|---|---|
| LABEL | String | — | NORMAL | WARNING | EMERGENCY |
| TEMP | Integer | °C | < 35 | 35 – 55 | > 55 |
| HUM | Integer | % | < 80 | 80 – 90 | > 90 |
| GAS | Integer | ppm | 350 – 1,000 | 1,000 – 3,000 | > 3,000 |
| ACC_R | Float | G | < 2.0 | 2.0 – 4.0 | > 4.0 |
| GYR_R | Float | dps | < 60 | 60 – 90 | > 90 |

### Optimal Gas Alert Threshold

Sensitivity analysis across gas thresholds yields **100 ppm** as the inflection point — balancing false-alert rate against maximum hazard sensitivity. This value aligns with the DGMS CO₂ action level for underground mines.

| Threshold | False Alerts / Session |
|---|---|
| 80 ppm | 8 — too sensitive |
| 90 ppm | 5 |
| **100 ppm** | **2 — optimal** |
| 110 ppm | 0 |
| 120 ppm | 0 — dangerously insensitive |

---

## 🛠️ Troubleshooting

| Symptom | Resolution |
|---|---|
| `LoRa init failed` on boot | Verify SPI wiring; check NSS, RST, and DIO0 pin numbers |
| `[AES] Decryption failed` | AES key or IV mismatch — ensure both firmware files are identical |
| No packets received | Confirm frequency (433E6), SF10, BW 125 kHz, CR 4/5 match on both nodes |
| Dashboard shows NO SIGNAL | Check USB connection; ensure you are using Chrome or Edge |
| `npm run dev` throws module error | Run `npm install recharts` before starting |
| Web Serial API unavailable | Use Chrome or Edge on desktop — not mobile, not Firefox |
| COM port not listed | Install the CP2102 or CH340 USB-to-serial driver for your ESP32 board |
| Garbled / corrupt packets | Likely caused by AES key or IV mismatch between sender and receiver |

---

## 🔮 Future Work

### Near-Term (6 – 12 months)

- **Biometric sensing** — Integrate MAX30102 SpO₂ / heart-rate sensor for direct physiological distress detection
- **Improved gas sensing** — Replace MQ135 with a dedicated electrochemical sensor (Alphasense CO-AF) for CO-specific selectivity
- **Higher-accuracy temperature** — Upgrade DHT11 → SHT31 (±0.3 °C) for WBGT-index compliance
- **Counter-based AES IV** — Eliminate the fixed-IV limitation for certified production deployment
- **Operational model retraining** — Periodic updates from field data to handle sensor fouling, ageing, and EMI

### Long-Term (1 – 3 years)

- **Worker localisation** — LoRa TDoA / RSS positioning to pinpoint distressed workers in tunnel networks
- **Battery extension** — Sleep scheduling for BMI160, DHT11, and LoRa radio during steady NORMAL state, targeting 16+ hour battery life
- **Edge-cloud hybrid** — Sparse raw-data bursts alongside edge classifications for cloud-based model retraining
- **Digital twin integration** — Real-time mine management framework driven by helmet node telemetry streams
- **Large-scale field trial** — Validated deployment under real mine conditions with 50+ certified nodes

---

## 📄 License

This project is licensed under the **MIT License**. See [LICENSE](LICENSE) for full terms.

---

## 🙏 Acknowledgements

- [LoRa by Sandeep Mistry](https://github.com/sandeepmistry/arduino-LoRa) — Arduino LoRa library
- [mbedTLS](https://tls.mbed.org/) — built-in AES hardware acceleration via ESP-IDF
- [scikit-learn](https://scikit-learn.org/) — CART Decision Tree classifier and training pipeline
- [Recharts](https://recharts.org/) — React charting library used in the dashboard
- [Vite](https://vitejs.dev/) — frontend build tooling

import { useState, useEffect, useRef, useCallback } from "react";
import { LineChart, Line, ResponsiveContainer } from "recharts";

// ─── Status config ────────────────────────────────────────────
const STATUS = {
  NORMAL:    { color: "#00ff9d", bg: "rgba(0,255,157,0.08)",  label: "ALL CLEAR",  icon: "✓" },
  WARNING:   { color: "#ffb700", bg: "rgba(255,183,0,0.10)",  label: "WARNING",    icon: "⚠" },
  EMERGENCY: { color: "#ff2d55", bg: "rgba(255,45,85,0.12)",  label: "EMERGENCY",  icon: "!" },
};

const THRESHOLDS = {
  temp:  { warn: 35,   crit: 40   },
  hum:   { warn: 80,   crit: 90   },
  gas:   { warn: 1000, crit: 2000 },
  acc_r: { warn: 2.0,  crit: 4.0  },
  gyr_r: { warn: 60,   crit: 90   },
};

// ─── Parse the decrypted CSV line from receiver serial output ──
// Receiver prints: [AES] Decrypted: LABEL,TEMP,HUM,GAS,ACC_R,GYR_R
// Also catches raw CSV in case firmware is modified
function parseLine(line) {
  let csv = null;
  const aesMatch = line.match(/\[AES\]\s+Decrypted:\s*(.+)/i);
  if (aesMatch) csv = aesMatch[1].trim();
  else if (/^(NORMAL|WARNING|EMERGENCY),/.test(line.trim())) csv = line.trim();
  if (!csv) return null;

  const parts = csv.split(",");
  if (parts.length < 6) return null;
  const [label, temp, hum, gas, acc_r, gyr_r] = parts;
  if (!["NORMAL", "WARNING", "EMERGENCY"].includes(label)) return null;

  return {
    label,
    temp:  parseFloat(temp),
    hum:   parseFloat(hum),
    gas:   parseInt(gas),
    acc_r: parseFloat(acc_r),
    gyr_r: parseFloat(gyr_r),
  };
}

// ─── Arc Gauge ────────────────────────────────────────────────
function Gauge({ label, value, unit, min, max, warn, crit }) {
  const pct   = Math.min(Math.max(((value ?? min) - min) / (max - min), 0), 1);
  const color = value == null ? "#2a2a3a" : value >= crit ? "#ff2d55" : value >= warn ? "#ffb700" : "#00ff9d";
  const r = 38, cx = 50, cy = 54;
  const arc = (p) => {
    const a = Math.PI * (1 + p);
    return `${cx + r * Math.cos(Math.PI)} ${cy + r * Math.sin(Math.PI)} A ${r} ${r} 0 ${p > 0.5 ? 1 : 0} 1 ${cx + r * Math.cos(a)} ${cy + r * Math.sin(a)}`;
  };
  return (
    <div style={{ textAlign:"center", flex:"1 1 0", minWidth:100 }}>
      <svg viewBox="0 0 100 70" style={{ width:"100%", maxWidth:130 }}>
        <path d={`M ${arc(1)}`} fill="none" stroke="#1a1a2e" strokeWidth="8" strokeLinecap="round"/>
        <path d={`M ${arc(pct)}`} fill="none" stroke={color} strokeWidth="8" strokeLinecap="round"
          style={{ filter:`drop-shadow(0 0 6px ${color})`, transition:"all 0.7s ease" }}/>
        <text x="50" y="50" textAnchor="middle" fontSize="13" fontWeight="700"
          fill={color} fontFamily="'Share Tech Mono',monospace"
          style={{ filter:`drop-shadow(0 0 4px ${color})`, transition:"fill 0.4s" }}>
          {value != null && !isNaN(value) ? value : "—"}
        </text>
        <text x="50" y="62" textAnchor="middle" fontSize="7" fill="#444" fontFamily="monospace">{unit}</text>
      </svg>
      <div style={{ fontSize:9, color:"#555", letterSpacing:2, marginTop:-4, fontFamily:"monospace" }}>{label}</div>
    </div>
  );
}

// ─── Sparkline ────────────────────────────────────────────────
function Spark({ data, field, color }) {
  return (
    <ResponsiveContainer width="100%" height={28}>
      <LineChart data={data.map(d => ({ v: d[field] }))}>
        <Line type="monotone" dataKey="v" stroke={color} strokeWidth={1.5} dot={false} isAnimationActive={false}/>
      </LineChart>
    </ResponsiveContainer>
  );
}

// ─── Stat row with sparkline ──────────────────────────────────
function StatRow({ label, value, unit, data, field, warn, crit }) {
  const color = value == null ? "#333" : value >= crit ? "#ff2d55" : value >= warn ? "#ffb700" : "#00ff9d";
  return (
    <div style={{ display:"flex", alignItems:"center", gap:10, padding:"7px 0", borderBottom:"1px solid #0d0d1a" }}>
      <div style={{ width:88, fontSize:9, color:"#555", letterSpacing:1.5, fontFamily:"monospace", flexShrink:0 }}>{label}</div>
      <div style={{ width:72, fontSize:15, fontWeight:700, color, fontFamily:"'Share Tech Mono',monospace",
        textShadow: value != null ? `0 0 8px ${color}` : "none", transition:"color 0.4s, text-shadow 0.4s", flexShrink:0 }}>
        {value != null ? value : "—"}<span style={{ fontSize:9, color:"#444", marginLeft:2 }}>{unit}</span>
      </div>
      <div style={{ flex:1 }}><Spark data={data} field={field} color={color}/></div>
    </div>
  );
}

// ─── Serial log line ──────────────────────────────────────────
function RawLine({ line }) {
  const isDecrypted = line.includes("[AES] Decrypted");
  const isError     = line.includes("Error") || line.includes("FATAL") || line.includes("failed");
  const isLora      = line.includes("[LoRa]");
  const color = isDecrypted ? "#00ff9d" : isError ? "#ff2d55" : isLora ? "#00b8ff" : "#2a2a3a";
  return (
    <div style={{ fontFamily:"'Share Tech Mono',monospace", fontSize:10, color,
      padding:"1px 0", borderBottom:"1px solid #080810", whiteSpace:"pre-wrap", wordBreak:"break-all" }}>
      {line}
    </div>
  );
}

// ─── Main App ─────────────────────────────────────────────────
export default function App() {
  const [connected, setConnected]   = useState(false);
  const [packets, setPackets]       = useState([]);
  const [rawLines, setRawLines]     = useState([]);
  const [latest, setLatest]         = useState(null);
  const [pktCount, setPktCount]     = useState(0);
  const [rssi, setRssi]             = useState(null);
  const [portInfo, setPortInfo]     = useState("");
  const [error, setError]           = useState("");
  const [tab, setTab]               = useState("dashboard"); // dashboard | raw
  const [flash, setFlash]           = useState(false);

  const portRef    = useRef(null);
  const readerRef  = useRef(null);
  const logRef     = useRef(null);

  const history = packets.slice(-40);

  // ─── Connect to Serial port ──────────────────────────────
  const connect = useCallback(async () => {
    setError("");
    if (!("serial" in navigator)) {
      setError("Web Serial API not supported. Use Chrome or Edge (desktop).");
      return;
    }
    try {
      const port = await navigator.serial.requestPort();
      await port.open({ baudRate: 115200 });
      portRef.current = port;
      const info = port.getInfo();
      setPortInfo(info.usbVendorId ? `VID:${info.usbVendorId.toString(16).toUpperCase()} PID:${info.usbProductId?.toString(16).toUpperCase()}` : "Serial Device");
      setConnected(true);

      // Start reading
      const decoder = new TextDecoderStream();
      port.readable.pipeTo(decoder.writable);
      const reader = decoder.readable.getReader();
      readerRef.current = reader;

      let buf = "";
      const read = async () => {
        try {
          while (true) {
            const { value, done } = await reader.read();
            if (done) break;
            buf += value;
            const lines = buf.split("\n");
            buf = lines.pop();
            for (const raw of lines) {
              const line = raw.replace(/\r/g, "").trim();
              if (!line) continue;

              setRawLines(prev => [...prev.slice(-199), line]);

              // Extract RSSI
              const rssiMatch = line.match(/RSSI[:\s]+(-\d+)\s*dBm/i);
              if (rssiMatch) setRssi(parseInt(rssiMatch[1]));

              // Parse decrypted packet
              const pkt = parseLine(line);
              if (pkt) {
                const full = { ...pkt, id: Date.now(), ts: new Date().toLocaleTimeString("en-GB") };
                setLatest(full);
                setFlash(true);
                setTimeout(() => setFlash(false), 400);
                setPktCount(c => c + 1);
                setPackets(prev => [...prev.slice(-99), full]);
              }
            }
          }
        } catch (e) {
          if (!e.message.includes("cancelled")) setError("Read error: " + e.message);
          setConnected(false);
        }
      };
      read();
    } catch (e) {
      if (!e.message.includes("No port selected")) setError(e.message);
    }
  }, []);

  // ─── Disconnect ──────────────────────────────────────────
  const disconnect = useCallback(async () => {
    try { await readerRef.current?.cancel(); } catch {}
    try { await portRef.current?.close(); } catch {}
    portRef.current = null;
    readerRef.current = null;
    setConnected(false);
    setPortInfo("");
  }, []);

  useEffect(() => {
    if (logRef.current) logRef.current.scrollTop = logRef.current.scrollHeight;
  }, [rawLines]);

  const status      = latest ? STATUS[latest.label] : null;
  const isEmergency = latest?.label === "EMERGENCY";

  return (
    <div style={{ minHeight:"100vh", background:"#080810", color:"#ccc", fontFamily:"monospace",
      backgroundImage:"radial-gradient(ellipse at 15% 0%,#0a0a22 0%,transparent 55%), radial-gradient(ellipse at 85% 100%,#0d0514 0%,transparent 55%)" }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Orbitron:wght@700;900&display=swap');
        * { box-sizing:border-box; margin:0; }
        ::-webkit-scrollbar { width:3px; height:3px; }
        ::-webkit-scrollbar-track { background:#0a0a14; }
        ::-webkit-scrollbar-thumb { background:#1e1e30; border-radius:2px; }
        @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.35} }
        @keyframes emergencyPulse { 0%,100%{box-shadow:0 0 0 0 rgba(255,45,85,0)} 50%{box-shadow:0 0 0 14px rgba(255,45,85,0.13)} }
        @keyframes flashBg { 0%{background:rgba(255,255,255,0.04)} 100%{background:transparent} }
        .ering { animation:emergencyPulse 0.9s infinite; }
        .scanline { position:fixed;top:0;left:0;right:0;bottom:0;pointer-events:none;z-index:999;
          background:repeating-linear-gradient(0deg,transparent,transparent 2px,rgba(0,0,0,0.025) 2px,rgba(0,0,0,0.025) 4px); }
        .tab-btn { background:transparent; border:none; cursor:pointer; padding:8px 18px;
          font-family:'Orbitron',monospace; font-size:9px; letter-spacing:2px; transition:all 0.2s; }
        .connect-btn { padding:8px 20px; border-radius:4px; font-family:'Orbitron',monospace;
          font-size:10px; letter-spacing:2px; cursor:pointer; transition:all 0.2s; border:1px solid; }
      `}</style>
      <div className="scanline"/>

      {/* ── HEADER ── */}
      <div style={{ padding:"14px 22px", display:"flex", alignItems:"center", justifyContent:"space-between",
        borderBottom:"1px solid #0d0d1a", flexWrap:"wrap", gap:8 }}>
        <div>
          <div style={{ fontFamily:"'Orbitron',monospace", fontSize:10, color:"#2a2a44", letterSpacing:4, marginBottom:2 }}>
            MINE SAFETY SYSTEM  ·  REAL-TIME
          </div>
          <div style={{ fontFamily:"'Orbitron',monospace", fontSize:20, fontWeight:900,
            background:"linear-gradient(90deg,#00ff9d,#00b8ff)", WebkitBackgroundClip:"text", WebkitTextFillColor:"transparent" }}>
            SMART HELMET GATEWAY
          </div>
        </div>

        <div style={{ display:"flex", alignItems:"center", gap:10, flexWrap:"wrap" }}>
          {/* Tabs */}
          <div style={{ display:"flex", borderRadius:4, border:"1px solid #111", overflow:"hidden" }}>
            {["dashboard","raw"].map(t => (
              <button key={t} className="tab-btn" onClick={() => setTab(t)}
                style={{ color: tab === t ? "#00b8ff" : "#333", borderBottom: tab === t ? "1px solid #00b8ff" : "1px solid transparent" }}>
                {t === "dashboard" ? "DASHBOARD" : "RAW SERIAL"}
              </button>
            ))}
          </div>

          {/* Port info */}
          {portInfo && <div style={{ fontSize:9, color:"#2a2a44", letterSpacing:1 }}>{portInfo}</div>}

          {/* Status dot */}
          <div style={{ width:8, height:8, borderRadius:"50%",
            background: connected ? "#00ff9d" : "#222",
            boxShadow: connected ? "0 0 8px #00ff9d" : "none",
            animation: connected ? "pulse 1.8s infinite" : "none" }}/>

          {/* Connect/Disconnect */}
          <button className="connect-btn"
            onClick={connected ? disconnect : connect}
            style={{ borderColor: connected ? "#ff2d55" : "#00ff9d", color: connected ? "#ff2d55" : "#00ff9d" }}>
            {connected ? "■ DISCONNECT" : "⬡ CONNECT"}
          </button>
        </div>
      </div>

      {/* ── ERROR BANNER ── */}
      {error && (
        <div style={{ padding:"10px 22px", background:"rgba(255,45,85,0.08)", borderBottom:"1px solid #ff2d5522",
          fontSize:11, color:"#ff2d55", display:"flex", justifyContent:"space-between", alignItems:"center" }}>
          <span>⚠ {error}</span>
          <button onClick={() => setError("")} style={{ background:"none", border:"none", color:"#ff2d55", cursor:"pointer", fontSize:14 }}>✕</button>
        </div>
      )}

      {/* ── NOT CONNECTED OVERLAY ── */}
      {!connected && tab === "dashboard" && packets.length === 0 && (
        <div style={{ position:"absolute", top:"50%", left:"50%", transform:"translate(-50%,-50%)",
          textAlign:"center", pointerEvents:"none" }}>
          <div style={{ fontFamily:"'Orbitron',monospace", fontSize:32, color:"#1a1a2e", fontWeight:900, lineHeight:1.2 }}>
            NO SIGNAL
          </div>
          <div style={{ fontSize:11, color:"#222", marginTop:8, letterSpacing:2 }}>
            CONNECT ESP32 RECEIVER VIA USB
          </div>
          <div style={{ fontSize:10, color:"#1a1a2e", marginTop:4, letterSpacing:1 }}>
            Chrome / Edge · 115200 baud
          </div>
        </div>
      )}

      {/* ════════════════════════════════════════════════════
          DASHBOARD TAB
      ════════════════════════════════════════════════════ */}
      {tab === "dashboard" && (
        <div style={{ display:"grid", gridTemplateColumns:"1fr 300px", height:"calc(100vh - 57px)", overflow:"hidden" }}>

          {/* Left main area */}
          <div style={{ padding:16, overflowY:"auto", display:"flex", flexDirection:"column", gap:14 }}>

            {/* Status banner */}
            <div className={isEmergency ? "ering" : ""} style={{
              padding:"14px 20px", borderRadius:8,
              border:`1px solid ${status?.color ?? "#111"}`,
              background: status?.bg ?? "#0c0c18",
              display:"flex", alignItems:"center", justifyContent:"space-between",
              transition:"border-color 0.5s, background 0.5s",
            }}>
              <div style={{ display:"flex", alignItems:"center", gap:14 }}>
                {/* Icon */}
                <div style={{
                  width:50, height:50, borderRadius:"50%",
                  border:`2px solid ${status?.color ?? "#222"}`,
                  display:"flex", alignItems:"center", justifyContent:"center",
                  fontSize:22, color: status?.color ?? "#333",
                  boxShadow: status ? `0 0 18px ${status.color}44` : "none",
                  fontWeight:900, fontFamily:"'Orbitron',monospace",
                  animation: isEmergency ? "pulse 0.7s infinite" : "none",
                  transition:"all 0.4s",
                }}>
                  {status?.icon ?? "○"}
                </div>
                <div>
                  <div style={{ fontFamily:"'Orbitron',monospace", fontSize:20, fontWeight:900,
                    color: status?.color ?? "#222",
                    textShadow: status ? `0 0 22px ${status.color}` : "none",
                    transition:"color 0.4s, text-shadow 0.4s" }}>
                    {status?.label ?? "NO SIGNAL"}
                  </div>
                  <div style={{ fontSize:10, color:"#333", marginTop:3, letterSpacing:1 }}>
                    {latest
                      ? `PKT #${pktCount} · ${latest.ts}${rssi != null ? ` · RSSI ${rssi} dBm` : ""}`
                      : connected ? "Waiting for packets…" : "Disconnected"}
                  </div>
                </div>
              </div>

              {/* Packet counter + RSSI */}
              <div style={{ textAlign:"right", display:"flex", flexDirection:"column", alignItems:"flex-end", gap:6 }}>
                <div style={{ fontFamily:"'Share Tech Mono',monospace", fontSize:28,
                  color: status?.color ?? "#1a1a2e",
                  textShadow: status ? `0 0 20px ${status.color}88` : "none" }}>
                  {pktCount.toString().padStart(4,"0")}
                </div>
                <div style={{ fontSize:9, color:"#2a2a44", letterSpacing:2 }}>PACKETS</div>
                {rssi != null && (
                  <div style={{ fontSize:9, color:"#444", letterSpacing:1 }}>
                    <span style={{ color: rssi > -80 ? "#00ff9d" : rssi > -100 ? "#ffb700" : "#ff2d55" }}>
                      ▊ {rssi} dBm
                    </span>
                  </div>
                )}
              </div>
            </div>

            {/* Gauges */}
            <div style={{ background:"#0c0c18", borderRadius:8, border:"1px solid #0f0f20", padding:"14px 6px 6px" }}>
              <div style={{ fontSize:9, color:"#2a2a44", letterSpacing:3, padding:"0 10px 10px", fontFamily:"monospace" }}>
                SENSOR READINGS
              </div>
              <div style={{ display:"flex", flexWrap:"wrap", gap:4 }}>
                <Gauge label="TEMPERATURE" value={latest?.temp}  unit="°C"  min={15} max={60}   warn={35}   crit={40}/>
                <Gauge label="HUMIDITY"    value={latest?.hum}   unit="%"   min={0}  max={100}  warn={80}   crit={90}/>
                <Gauge label="GAS"         value={latest?.gas}   unit="ppm" min={0}  max={3000} warn={1000} crit={2000}/>
                <Gauge label="ACCEL"       value={latest?.acc_r} unit="G"   min={0}  max={8}    warn={2}    crit={4}/>
                <Gauge label="GYRO"        value={latest?.gyr_r} unit="dps" min={0}  max={150}  warn={60}   crit={90}/>
              </div>
            </div>

            {/* Sparkline trends */}
            <div style={{ background:"#0c0c18", borderRadius:8, border:"1px solid #0f0f20", padding:14 }}>
              <div style={{ fontSize:9, color:"#2a2a44", letterSpacing:3, marginBottom:10, fontFamily:"monospace" }}>
                LIVE TELEMETRY  ·  LAST {Math.min(history.length, 40)} PACKETS
              </div>
              <StatRow label="TEMPERATURE" value={latest?.temp}  unit="°C"  data={history} field="temp"  warn={35}   crit={40}/>
              <StatRow label="HUMIDITY"    value={latest?.hum}   unit="%"   data={history} field="hum"   warn={80}   crit={90}/>
              <StatRow label="GAS PPM"     value={latest?.gas}   unit="ppm" data={history} field="gas"   warn={1000} crit={2000}/>
              <StatRow label="ACCEL (G)"   value={latest?.acc_r} unit="G"   data={history} field="acc_r" warn={2}    crit={4}/>
              <StatRow label="GYRO (dps)"  value={latest?.gyr_r} unit="dps" data={history} field="gyr_r" warn={60}   crit={90}/>
            </div>
          </div>

          {/* Right sidebar — packet log */}
          <div style={{ borderLeft:"1px solid #0d0d1a", display:"flex", flexDirection:"column", overflow:"hidden" }}>
            <div style={{ padding:"12px 14px 8px", fontSize:9, color:"#2a2a44", letterSpacing:3,
              fontFamily:"monospace", borderBottom:"1px solid #0d0d1a", flexShrink:0 }}>
              PACKET LOG
            </div>
            <div style={{ flex:1, overflowY:"auto", padding:"6px 0" }}>
              {packets.length === 0 && (
                <div style={{ padding:"40px 14px", textAlign:"center", color:"#1a1a2e", fontSize:10 }}>
                  {connected ? "Waiting for data…" : "No packets yet"}
                </div>
              )}
              {[...packets].reverse().map((p, i) => {
                const s = STATUS[p.label];
                return (
                  <div key={p.id} style={{
                    padding:"7px 12px", borderBottom:"1px solid #0a0a14",
                    borderLeft: i === 0 ? `2px solid ${s.color}` : "2px solid transparent",
                    background: i === 0 ? s.bg : "transparent", transition:"all 0.3s",
                  }}>
                    <div style={{ display:"flex", justifyContent:"space-between", marginBottom:3 }}>
                      <span style={{ fontFamily:"'Orbitron',monospace", fontSize:8, fontWeight:700,
                        color:s.color, textShadow:`0 0 8px ${s.color}88` }}>{p.label}</span>
                      <span style={{ fontSize:8, color:"#2a2a44" }}>#{pktCount - ([...packets].reverse().indexOf(p))} · {p.ts}</span>
                    </div>
                    <div style={{ fontFamily:"'Share Tech Mono',monospace", fontSize:9, color:"#3a3a5a", lineHeight:1.8 }}>
                      T:{p.temp}°C  H:{p.hum}%  G:{p.gas}ppm<br/>
                      A:{p.acc_r}G  Ω:{p.gyr_r}dps
                    </div>
                  </div>
                );
              })}
            </div>
            {/* Legend */}
            <div style={{ padding:"10px 12px", borderTop:"1px solid #0d0d1a", display:"flex", gap:12, flexShrink:0 }}>
              {Object.entries(STATUS).map(([k,v]) => (
                <div key={k} style={{ display:"flex", alignItems:"center", gap:4 }}>
                  <div style={{ width:5, height:5, borderRadius:"50%", background:v.color, boxShadow:`0 0 4px ${v.color}` }}/>
                  <span style={{ fontSize:8, color:"#2a2a44", letterSpacing:1 }}>{k}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* ════════════════════════════════════════════════════
          RAW SERIAL TAB
      ════════════════════════════════════════════════════ */}
      {tab === "raw" && (
        <div style={{ height:"calc(100vh - 57px)", display:"flex", flexDirection:"column" }}>
          <div style={{ padding:"8px 16px", borderBottom:"1px solid #0d0d1a", fontSize:9, color:"#2a2a44",
            letterSpacing:2, display:"flex", justifyContent:"space-between" }}>
            <span>SERIAL MONITOR  ·  115200 BAUD  ·  {rawLines.length} LINES</span>
            <button onClick={() => setRawLines([])} style={{ background:"none", border:"1px solid #1a1a2e",
              color:"#2a2a44", fontSize:9, padding:"2px 10px", cursor:"pointer", borderRadius:3,
              fontFamily:"monospace", letterSpacing:1 }}>CLEAR</button>
          </div>
          <div ref={logRef} style={{ flex:1, overflowY:"auto", padding:"10px 16px", background:"#06060e" }}>
            {rawLines.length === 0 && (
              <div style={{ color:"#1a1a2e", fontSize:10, paddingTop:20 }}>
                {connected ? "Listening…" : "Connect receiver to see serial output"}
              </div>
            )}
            {rawLines.map((l, i) => <RawLine key={i} line={l}/>)}
          </div>
        </div>
      )}
    </div>
  );
}

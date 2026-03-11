import { useState, useEffect, useRef, useCallback } from "react";
import { LineChart, Line, ResponsiveContainer } from "recharts";

const THRESHOLDS = {
  temp:  { warn: 35,   crit: 40   },
  hum:   { warn: 80,   crit: 90   },
  gas:   { warn: 1000, crit: 2000 },
  acc_r: { warn: 2.0,  crit: 4.0  },
  gyr_r: { warn: 60,   crit: 90   },
};

function generatePacket(count) {
  const scenario = Math.random();
  let label, temp, hum, gas, acc_r, gyr_r;
  if (scenario < 0.65) {
    label = "NORMAL";
    temp  = 28 + Math.random() * 5;
    hum   = 55 + Math.random() * 15;
    gas   = 300 + Math.random() * 400;
    acc_r = 0.8 + Math.random() * 0.8;
    gyr_r = 10  + Math.random() * 30;
  } else if (scenario < 0.88) {
    label = "WARNING";
    temp  = 36 + Math.random() * 3;
    hum   = 82 + Math.random() * 6;
    gas   = 1100 + Math.random() * 700;
    acc_r = 2.2 + Math.random() * 1.2;
    gyr_r = 65  + Math.random() * 20;
  } else {
    label = "EMERGENCY";
    temp  = 41 + Math.random() * 4;
    hum   = 92 + Math.random() * 5;
    gas   = 2200 + Math.random() * 800;
    acc_r = 4.5 + Math.random() * 2;
    gyr_r = 95  + Math.random() * 30;
  }
  return {
    id: count,
    label,
    temp:  parseFloat(temp.toFixed(1)),
    hum:   parseFloat(hum.toFixed(1)),
    gas:   Math.round(gas),
    acc_r: parseFloat(acc_r.toFixed(3)),
    gyr_r: parseFloat(gyr_r.toFixed(1)),
    rssi:  -(60 + Math.random() * 40),
    ts:    new Date().toLocaleTimeString("en-GB"),
  };
}

const STATUS = {
  NORMAL:    { color: "#00ff9d", bg: "rgba(0,255,157,0.08)", label: "ALL CLEAR", icon: "✓" },
  WARNING:   { color: "#ffb700", bg: "rgba(255,183,0,0.10)", label: "WARNING",   icon: "⚠" },
  EMERGENCY: { color: "#ff2d55", bg: "rgba(255,45,85,0.12)", label: "EMERGENCY", icon: "!" },
};

function Gauge({ label, value, unit, min, max, warn, crit }) {
  const pct   = Math.min(Math.max((value - min) / (max - min), 0), 1);
  const color = value >= crit ? "#ff2d55" : value >= warn ? "#ffb700" : "#00ff9d";
  const r = 38, cx = 50, cy = 54;
  const arc = (p) => {
    const a = Math.PI * (1 + p);
    return `${cx + r * Math.cos(Math.PI)} ${cy + r * Math.sin(Math.PI)} A ${r} ${r} 0 ${p > 0.5 ? 1 : 0} 1 ${cx + r * Math.cos(a)} ${cy + r * Math.sin(a)}`;
  };
  return (
    <div style={{ textAlign: "center", flex: "1 1 0" }}>
      <svg viewBox="0 0 100 70" style={{ width: "100%", maxWidth: 140 }}>
        <path d={`M ${arc(1)}`} fill="none" stroke="#1a1a2e" strokeWidth="8" strokeLinecap="round"/>
        <path d={`M ${arc(pct)}`} fill="none" stroke={color} strokeWidth="8" strokeLinecap="round"
          style={{ filter: `drop-shadow(0 0 6px ${color})`, transition: "all 0.6s ease" }}/>
        <text x="50" y="50" textAnchor="middle" fontSize="14" fontWeight="700"
          fill={color} fontFamily="'Share Tech Mono', monospace"
          style={{ filter: `drop-shadow(0 0 4px ${color})` }}>
          {typeof value === 'number' && !isNaN(value) ? value : '--'}
        </text>
        <text x="50" y="62" textAnchor="middle" fontSize="7" fill="#555" fontFamily="monospace">{unit}</text>
      </svg>
      <div style={{ fontSize: 10, color: "#666", letterSpacing: 2, marginTop: -4, fontFamily: "monospace" }}>
        {label}
      </div>
    </div>
  );
}

function Spark({ data, field, color }) {
  const vals = data.map(d => ({ v: d[field] }));
  return (
    <ResponsiveContainer width="100%" height={32}>
      <LineChart data={vals}>
        <Line type="monotone" dataKey="v" stroke={color} strokeWidth={1.5} dot={false} isAnimationActive={false}/>
      </LineChart>
    </ResponsiveContainer>
  );
}

function StatRow({ label, value, unit, data, field, warn, crit }) {
  const color = value >= crit ? "#ff2d55" : value >= warn ? "#ffb700" : "#00ff9d";
  return (
    <div style={{ display:"flex", alignItems:"center", gap:12, padding:"8px 0",
      borderBottom:"1px solid #0d0d1a" }}>
      <div style={{ width:90, fontSize:10, color:"#555", letterSpacing:1.5, fontFamily:"monospace" }}>{label}</div>
      <div style={{ width:70, fontSize:15, fontWeight:700, color, fontFamily:"'Share Tech Mono',monospace",
        textShadow:`0 0 8px ${color}` }}>
        {value != null ? value : "—"}<span style={{ fontSize:9, color:"#444", marginLeft:2 }}>{unit}</span>
      </div>
      <div style={{ flex:1 }}><Spark data={data} field={field} color={color}/></div>
    </div>
  );
}

export default function App() {
  const [packets, setPackets]   = useState([]);
  const [latest, setLatest]     = useState(null);
  const [running, setRunning]   = useState(false);
  const [pktCount, setPktCount] = useState(0);
  const [flash, setFlash]       = useState(false);
  const intervalRef = useRef(null);
  const logRef      = useRef(null);
  const history     = packets.slice(-30);

  const addPacket = useCallback(() => {
    setPktCount(c => {
      const n = c + 1;
      const pkt = generatePacket(n);
      setLatest(pkt);
      setFlash(true);
      setTimeout(() => setFlash(false), 300);
      setPackets(prev => [...prev.slice(-99), pkt]);
      return n;
    });
  }, []);

  useEffect(() => {
    if (running) { intervalRef.current = setInterval(addPacket, 2500); }
    else { clearInterval(intervalRef.current); }
    return () => clearInterval(intervalRef.current);
  }, [running, addPacket]);

  useEffect(() => {
    if (logRef.current) logRef.current.scrollTop = logRef.current.scrollHeight;
  }, [packets]);

  const status = latest ? STATUS[latest.label] : null;
  const isEmergency = latest?.label === "EMERGENCY";

  return (
    <div style={{
      minHeight:"100vh", background:"#080810", color:"#ccc", fontFamily:"monospace",
      backgroundImage:"radial-gradient(ellipse at 20% 0%, #0a0a20 0%, transparent 60%), radial-gradient(ellipse at 80% 100%, #0d0510 0%, transparent 60%)",
    }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Orbitron:wght@700;900&display=swap');
        * { box-sizing: border-box; }
        ::-webkit-scrollbar { width:4px; }
        ::-webkit-scrollbar-track { background:#0d0d1a; }
        ::-webkit-scrollbar-thumb { background:#222; }
        @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.4} }
        @keyframes flashIn { 0%{background:rgba(255,255,255,0.06)} 100%{background:transparent} }
        @keyframes emergencyPulse { 0%,100%{box-shadow:0 0 0 0 rgba(255,45,85,0)} 50%{box-shadow:0 0 0 12px rgba(255,45,85,0.15)} }
        .emergency-ring { animation: emergencyPulse 1s infinite; }
        .scanline { position:fixed; top:0; left:0; right:0; bottom:0; pointer-events:none; z-index:999;
          background: repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0,0,0,0.03) 2px, rgba(0,0,0,0.03) 4px); }
      `}</style>
      <div className="scanline"/>

      {/* Header */}
      <div style={{ padding:"20px 24px 0", display:"flex", alignItems:"center", justifyContent:"space-between",
        borderBottom:"1px solid #0d0d1a" }}>
        <div>
          <div style={{ fontFamily:"'Orbitron',monospace", fontSize:13, color:"#333", letterSpacing:4, marginBottom:2 }}>
            MINE SAFETY SYSTEM
          </div>
          <div style={{ fontFamily:"'Orbitron',monospace", fontSize:22, fontWeight:900,
            background:"linear-gradient(90deg,#00ff9d,#00b8ff)", WebkitBackgroundClip:"text", WebkitTextFillColor:"transparent" }}>
            SMART HELMET GATEWAY
          </div>
        </div>
        <div style={{ display:"flex", gap:10, alignItems:"center" }}>
          <div style={{ fontSize:10, color:"#333", letterSpacing:2 }}>LoRa 433MHz · AES-128-CBC</div>
          <div style={{ width:8, height:8, borderRadius:"50%", background: running ? "#00ff9d" : "#333",
            boxShadow: running ? "0 0 8px #00ff9d" : "none",
            animation: running ? "pulse 1.5s infinite" : "none" }}/>
          <button onClick={() => setRunning(r => !r)} style={{
            padding:"6px 16px", borderRadius:4, border:"1px solid",
            borderColor: running ? "#ff2d55" : "#00ff9d", background:"transparent",
            color: running ? "#ff2d55" : "#00ff9d",
            fontFamily:"'Orbitron',monospace", fontSize:10, letterSpacing:2, cursor:"pointer",
          }}>
            {running ? "■ STOP" : "▶ START"}
          </button>
        </div>
      </div>

      <div style={{ display:"grid", gridTemplateColumns:"1fr 320px", gap:0, height:"calc(100vh - 73px)" }}>
        {/* Main */}
        <div style={{ padding:20, overflowY:"auto", display:"flex", flexDirection:"column", gap:16 }}>
          {/* Status banner */}
          <div className={isEmergency ? "emergency-ring" : ""} style={{
            padding:"16px 24px", borderRadius:8, border:`1px solid ${status?.color ?? "#222"}`,
            background: status?.bg ?? "#0d0d1a",
            display:"flex", alignItems:"center", justifyContent:"space-between", transition:"all 0.4s",
          }}>
            <div style={{ display:"flex", alignItems:"center", gap:16 }}>
              <div style={{
                width:48, height:48, borderRadius:"50%", border:`2px solid ${status?.color ?? "#333"}`,
                display:"flex", alignItems:"center", justifyContent:"center",
                fontSize:22, color: status?.color ?? "#333",
                boxShadow: status ? `0 0 16px ${status.color}44` : "none",
                fontWeight:900, fontFamily:"'Orbitron',monospace",
                animation: isEmergency ? "pulse 0.8s infinite" : "none",
              }}>
                {status?.icon ?? "–"}
              </div>
              <div>
                <div style={{ fontFamily:"'Orbitron',monospace", fontSize:18, fontWeight:900,
                  color: status?.color ?? "#333", textShadow: status ? `0 0 20px ${status.color}` : "none" }}>
                  {status?.label ?? "AWAITING SIGNAL"}
                </div>
                <div style={{ fontSize:10, color:"#444", marginTop:2, letterSpacing:1 }}>
                  {latest ? `PKT #${latest.id} · ${latest.ts} · RSSI ${latest.rssi?.toFixed(0)} dBm` : "Connect receiver to begin"}
                </div>
              </div>
            </div>
            <div style={{ textAlign:"right" }}>
              <div style={{ fontFamily:"'Share Tech Mono',monospace", fontSize:30, color: status?.color ?? "#222",
                textShadow: status ? `0 0 24px ${status.color}88` : "none" }}>
                {pktCount.toString().padStart(4,"0")}
              </div>
              <div style={{ fontSize:9, color:"#333", letterSpacing:2 }}>TOTAL PACKETS</div>
            </div>
          </div>

          {/* Gauges */}
          <div style={{ background:"#0d0d1a", borderRadius:8, border:"1px solid #111", padding:"16px 8px" }}>
            <div style={{ fontSize:9, color:"#333", letterSpacing:3, padding:"0 12px 12px", fontFamily:"monospace" }}>SENSOR READINGS</div>
            <div style={{ display:"flex", gap:4, flexWrap:"wrap" }}>
              <Gauge label="TEMPERATURE" value={latest?.temp}  unit="°C"  min={15} max={60}   warn={35}   crit={40}/>
              <Gauge label="HUMIDITY"    value={latest?.hum}   unit="%"   min={0}  max={100}  warn={80}   crit={90}/>
              <Gauge label="GAS / PPM"   value={latest?.gas}   unit="ppm" min={0}  max={3000} warn={1000} crit={2000}/>
              <Gauge label="ACCEL (G)"   value={latest?.acc_r} unit="G"   min={0}  max={8}    warn={2}    crit={4}/>
              <Gauge label="GYRO (dps)"  value={latest?.gyr_r} unit="dps" min={0}  max={150}  warn={60}   crit={90}/>
            </div>
          </div>

          {/* Telemetry */}
          <div style={{ background:"#0d0d1a", borderRadius:8, border:"1px solid #111", padding:16 }}>
            <div style={{ fontSize:9, color:"#333", letterSpacing:3, marginBottom:12, fontFamily:"monospace" }}>
              LIVE TELEMETRY — LAST 30 PACKETS
            </div>
            <StatRow label="TEMPERATURE" value={latest?.temp}  unit="°C"  data={history} field="temp"  warn={35}   crit={40}/>
            <StatRow label="HUMIDITY"    value={latest?.hum}   unit="%"   data={history} field="hum"   warn={80}   crit={90}/>
            <StatRow label="GAS"         value={latest?.gas}   unit="ppm" data={history} field="gas"   warn={1000} crit={2000}/>
            <StatRow label="ACCEL"       value={latest?.acc_r} unit="G"   data={history} field="acc_r" warn={2}    crit={4}/>
            <StatRow label="GYRO"        value={latest?.gyr_r} unit="dps" data={history} field="gyr_r" warn={60}   crit={90}/>
          </div>
        </div>

        {/* Sidebar log */}
        <div style={{ borderLeft:"1px solid #0d0d1a", display:"flex", flexDirection:"column" }}>
          <div style={{ padding:"16px 16px 8px", fontSize:9, color:"#333", letterSpacing:3,
            fontFamily:"monospace", borderBottom:"1px solid #0d0d1a" }}>PACKET LOG</div>
          <div ref={logRef} style={{ flex:1, overflowY:"auto", padding:"8px 0" }}>
            {packets.length === 0 && (
              <div style={{ padding:"40px 16px", textAlign:"center", color:"#222", fontSize:11 }}>
                No packets received.<br/>Press START to simulate.
              </div>
            )}
            {[...packets].reverse().map((p, i) => {
              const s = STATUS[p.label];
              return (
                <div key={p.id} style={{
                  padding:"8px 14px", borderBottom:"1px solid #0a0a14",
                  borderLeft: i === 0 ? `2px solid ${s.color}` : "2px solid transparent",
                  background: i === 0 ? s.bg : "transparent", transition:"all 0.3s",
                }}>
                  <div style={{ display:"flex", justifyContent:"space-between", marginBottom:3 }}>
                    <span style={{ fontFamily:"'Orbitron',monospace", fontSize:8, fontWeight:700,
                      color: s.color, textShadow:`0 0 8px ${s.color}88` }}>{p.label}</span>
                    <span style={{ fontSize:8, color:"#333" }}>#{p.id} · {p.ts}</span>
                  </div>
                  <div style={{ fontFamily:"'Share Tech Mono',monospace", fontSize:9, color:"#444", lineHeight:1.8 }}>
                    T:{p.temp}°C H:{p.hum}% G:{p.gas}ppm<br/>
                    A:{p.acc_r}G Ω:{p.gyr_r}dps RSSI:{p.rssi?.toFixed(0)}
                  </div>
                </div>
              );
            })}
          </div>
          <div style={{ padding:"12px 14px", borderTop:"1px solid #0d0d1a", display:"flex", gap:12 }}>
            {Object.entries(STATUS).map(([k,v]) => (
              <div key={k} style={{ display:"flex", alignItems:"center", gap:4 }}>
                <div style={{ width:6, height:6, borderRadius:"50%", background:v.color, boxShadow:`0 0 4px ${v.color}` }}/>
                <span style={{ fontSize:8, color:"#444", letterSpacing:1 }}>{k}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

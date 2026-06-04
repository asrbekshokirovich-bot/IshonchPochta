// sections.jsx — all section components for Ishonch Logistics landing.
// Reads window.Icon, window.COPY. Exports each section to window.

const I = window.Icon;

// ─────────────────── TOP BAR ───────────────────
function TopBar({ lang, setLang, t }) {
  return (
    <div className="topbar">
      <div className="container">
        <div className="topbar-left">
          <span>📞 {t.top.phone}</span>
          <span className="dot">●</span>
          <span>{t.top.hours}</span>
        </div>
        <div className="topbar-right">
          <a href="track.html" style={{ color: "#cdd8ee" }}>{t.top.track}</a>
          <div className="lang-switch" role="group" aria-label="Language">
            {["uz", "ru", "en"].map(l => (
              <button key={l} aria-pressed={lang === l} onClick={() => setLang(l)}>
                {l.toUpperCase()}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

// ─────────────────── NAV ───────────────────
function Nav({ t }) {
  return (
    <nav className="nav">
      <div className="container">
        <a href="#" className="brand">
          <img
            src="assets/ishonch-logo-full.png?v=2"
            alt="Ishonch Logistics"
            style={{ height: '64px', width: 'auto', display: 'block' }}
          />
        </a>
        <div className="nav-links">
          <a href="#services">{t.nav.services}</a>
          <a href="#coverage">{t.nav.coverage}</a>
          <a href="#calc">{t.nav.calc}</a>
          <a href="#why">{t.nav.about}</a>
          <a href="#contact">{t.nav.contact}</a>
        </div>
        <div className="nav-cta">
          <a href="track.html" className="btn btn-ghost btn-sm">
            <I name="search" size={16} /> {t.actions.track}
          </a>
          <a href="#contact" className="btn btn-primary btn-sm">
            {t.actions.order} <I name="arrow" size={16} />
          </a>
        </div>
      </div>
    </nav>
  );
}

// ─────────────────── HERO ───────────────────
function Hero({ t, layout }) {
  const [trackingInput, setTrackingInput] = React.useState("");

  const handleTrack = () => {
    const val = trackingInput.trim();
    if (!val) return;
    window.location.href = 'track.html?barcode=' + encodeURIComponent(val);
  };

  return (
    <section className="hero">
      <div className="container hero-grid">
        <div>
          <div className="hero-tag">
            <span className="pill">{t.hero.tag}</span>
            <span>{t.hero.tagAlt}</span>
          </div>
          <h1>
            {layout === "split" ? (
              <>
                {t.hero.title[0]}<br />
                <span className="accent">{t.hero.title[1]}</span><br />
                {t.hero.title[2]}
              </>
            ) : (
              <>
                <span className="accent">{t.hero.title[0]}</span>{" "}
                {t.hero.title[1]} {t.hero.title[2]}
              </>
            )}
          </h1>
          <div className="script" style={{ marginTop: 14 }}>— {t.hero.script}</div>
          <p className="hero-lede">{t.hero.lede}</p>
          <div className="hero-actions">
            <a href="#contact" className="btn btn-primary btn-lg">
              <I name="truck" size={18} /> {t.actions.order}
            </a>
            <a href="#calc" className="btn btn-ghost btn-lg">{t.actions.quote}</a>
            <a href="track.html" className="btn btn-primary btn-lg" style={{ background: "var(--blue-500)" }}>
              <I name="search" size={18} /> {t.tracking.tab1}
            </a>
          </div>
          <div className="hero-quickstats">
            {t.hero.stats.map((s, i) => (
              <div className="stat" key={i}>
                <div className="num">{s.n}</div>
                <div className="lbl">{s.l}</div>
              </div>
            ))}
          </div>
        </div>

        <div className="hero-card" id="track">
          <div style={{ marginBottom: 16 }}>
            <h3 style={{ margin: "0 0 4px", color: "var(--navy-800)", fontSize: 18, fontWeight: 800 }}>
              {t.tracking.tab1}
            </h3>
            <p style={{ margin: 0, color: "var(--ink-500)", fontSize: 14 }}>
              {t.tracking.placeholder}
            </p>
          </div>

          <div className="field">
            <label>{t.tracking.placeholder.split("(")[0].trim()}</label>
            <div style={{ display: "flex", gap: 10, alignItems: "center" }}>
              <input value={trackingInput} onChange={e => setTrackingInput(e.target.value.toUpperCase())} onKeyDown={e => { if (e.key === "Enter") handleTrack(); }} placeholder="TN12345678" />
              <I name="search" size={18} color="var(--ink-400)" />
            </div>
          </div>

          <button type="button" className="btn btn-primary" style={{ width: "100%", justifyContent: "center", marginTop: 10 }} onClick={handleTrack}>
            {t.tracking.cta} <I name="arrow" size={16} />
          </button>

          <div style={{ fontSize: 12, color: "var(--ink-400)", marginTop: 10, textAlign: "center" }}>
            {t.tracking.sample.split(":")[0]}:{" "}
            <span
              style={{ cursor: "pointer", textDecoration: "underline", color: "var(--ink-700)" }}
              onClick={() => { window.location.href = "track.html?barcode=TT123456789UZ"; }}
            >TT123456789UZ</span>
          </div>

          <BookFormPreview t={t} />
        </div>

        <div className="hero-deco" aria-hidden></div>
      </div>
    </section>
  );
}

function BookFormPreview({ t }) {
  // small visual showing a fake live shipment progress
  return (
    <div style={{ marginTop: 18 }}>
      <div style={{ fontSize: 12, fontWeight: 700, color: "var(--ink-500)", letterSpacing: ".08em", textTransform: "uppercase", marginBottom: 12 }}>
        Live • TN72893421
      </div>
      <TrackingTimeline t={t} />
    </div>
  );
}

function TrackingTimeline() {
  const steps = [
    { city: "Toshkent", state: "Yuborildi", time: "12:40", done: true },
    { city: "Samarqand hub", state: "Saralash", time: "18:20", done: true, current: true },
    { city: "Buxoro", state: "Yo'lda", time: "—", done: false },
    { city: "Mijoz manzili", state: "Yetkazib berish", time: "—", done: false }
  ];
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 0 }}>
      {steps.map((s, i) => (
        <div key={i} style={{ display: "grid", gridTemplateColumns: "26px 1fr auto", gap: 12, alignItems: "center", padding: "10px 0", borderTop: i > 0 ? "1px dashed var(--line)" : "none" }}>
          <div style={{ position: "relative", height: 18 }}>
            {s.current ? (
              <div className="pulse" style={{ position: "absolute", left: 2, top: 2 }} />
            ) : (
              <div style={{
                width: 12, height: 12, borderRadius: "50%",
                background: s.done ? "var(--blue-500)" : "var(--ink-200)",
                marginLeft: 3, marginTop: 3
              }} />
            )}
          </div>
          <div>
            <div style={{ fontWeight: 600, fontSize: 14, color: "var(--ink-900)" }}>{s.city}</div>
            <div style={{ fontSize: 12.5, color: "var(--ink-500)" }}>{s.state}</div>
          </div>
          <div style={{ fontSize: 12.5, color: "var(--ink-400)", fontVariantNumeric: "tabular-nums" }}>{s.time}</div>
        </div>
      ))}
    </div>
  );
}

function BookForm({ t }) {
  const [from, setFrom] = React.useState("");
  const [to, setTo] = React.useState("");
  const cities = ["Toshkent", "Samarqand", "Buxoro", "Andijon", "Farg'ona", "Namangan", "Nukus", "Qarshi", "Termiz", "Xiva"];
  return (
    <div>
      <div className="field" style={{ marginBottom: 10 }}>
        <label>{t.bookForm.fromCity}</label>
        <input list="cities-h" value={from} onChange={e => setFrom(e.target.value)} placeholder="Toshkent" />
      </div>
      <div className="field" style={{ marginBottom: 10 }}>
        <label>{t.bookForm.toCity}</label>
        <input list="cities-h" value={to} onChange={e => setTo(e.target.value)} placeholder="Samarqand" />
      </div>
      <datalist id="cities-h">{cities.map(c => <option key={c} value={c} />)}</datalist>
      <div className="field" style={{ marginBottom: 10 }}>
        <label>{t.bookForm.weight}</label>
        <input type="number" placeholder="2.5" />
      </div>
      <button className="btn btn-primary" style={{ width: "100%", justifyContent: "center" }}>
        {t.bookForm.cta} <I name="arrow" size={16} />
      </button>
    </div>
  );
}

// ─────────────────── TRUST STRIP ───────────────────
function Trust({ t }) {
  const logos = [
    { name: "Korzinka", dot: true },
    { name: "Uzum Market", dot: true },
    { name: "OLX.uz" },
    { name: "Texnomart", dot: true },
    { name: "Asaxiy" },
    { name: "Click" }
  ];
  return (
    <div className="trust">
      <div className="container trust-inner">
        <div className="trust-label">{t.trustLabel}</div>
        <div className="trust-logos">
          {logos.map((l, i) => (
            <span className="tl" key={i}>
              {l.dot && <span className="dot">●</span>}{l.name}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}

// ─────────────────── SERVICES ───────────────────
function Services({ t }) {
  return (
    <section className="services section" id="services">
      <div className="container">
        <div className="section-head">
          <div>
            <div className="eyebrow">{t.services.eyebrow}</div>
            <h2 style={{ marginTop: 18 }}>{t.services.title}</h2>
          </div>
          <p className="meta">{t.services.meta}</p>
        </div>
        <div className="services-grid">
          {t.services.items.map((s, i) => (
            <article key={i} className={`svc-card ${s.featured ? "featured" : ""}`}>
              <div className="ico"><I name={s.ico} /></div>
              <h3>{s.name}</h3>
              <p className="desc">{s.desc}</p>
              <div className="price">{s.price}</div>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}

// ─────────────────── WHY US ───────────────────
function Why({ t }) {
  return (
    <section className="section" id="why">
      <div className="container why-grid">
        <div>
          <div className="eyebrow">{t.why.eyebrow}</div>
          <h2 style={{ marginTop: 18, marginBottom: 44 }}>{t.why.title}</h2>
          <div className="why-list">
            {t.why.items.map((w, i) => (
              <div className="why-item" key={i}>
                <div className="ico"><I name={w.ico} /></div>
                <div>
                  <h3>{w.h}</h3>
                  <p>{w.p}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
        <div className="why-visual">
          <WhyVisual />
          <div className="why-stats">
            {t.why.stats.map((s, i) => (
              <div className="s" key={i}>
                <div className="n">{s.n}</div>
                <div className="l">{s.l}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}

// abstract truck/route SVG illustration for the navy card
function WhyVisual() {
  return (
    <svg viewBox="0 0 400 420" style={{ position: "absolute", inset: 0, width: "100%", height: "100%" }} aria-hidden>
      <defs>
        <linearGradient id="grid" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="rgba(255,255,255,.18)" />
          <stop offset="100%" stopColor="rgba(255,255,255,0)" />
        </linearGradient>
        <pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse">
          <circle cx="1" cy="1" r="1" fill="rgba(255,255,255,.08)" />
        </pattern>
      </defs>
      <rect width="400" height="420" fill="url(#dots)" />
      {/* route line */}
      <path d="M40 80 Q 110 60, 160 130 T 280 180 T 360 110" fill="none" stroke="rgba(255,255,255,.18)" strokeWidth="2" strokeDasharray="4 6" />
      {/* nodes */}
      <g fill="white">
        <circle cx="40" cy="80" r="6" />
        <circle cx="160" cy="130" r="6" />
        <circle cx="280" cy="180" r="6" />
        <circle cx="360" cy="110" r="6" />
      </g>
      {/* big numeral 96 */}
      <text x="40" y="290" fontFamily="Archivo" fontWeight="800" fontSize="180" fill="rgba(255,255,255,.12)" letterSpacing="-4">96%</text>
      <text x="40" y="320" fontFamily="Public Sans" fontWeight="600" fontSize="14" fill="rgba(255,255,255,.6)" letterSpacing="2">ON-TIME · EVERY DAY</text>
    </svg>
  );
}

// ─────────────────── COVERAGE MAP ───────────────────
function Coverage({ t }) {
  return (
    <section className="coverage section" id="coverage">
      <div className="container coverage-grid">
        <div className="coverage-meta">
          <div className="eyebrow">{t.coverage.eyebrow}</div>
          <h2 style={{ marginTop: 18 }}>{t.coverage.title}</h2>
          <p style={{ fontSize: 16.5, color: "var(--ink-500)", maxWidth: 460, marginTop: 18 }}>{t.coverage.meta}</p>
          <div className="pts">
            {t.coverage.pts.map((p, i) => (
              <div className="pt" key={i}>
                <span className="dot"><I name="check" size={14} stroke={2.4} /></span>
                <span>{p}</span>
              </div>
            ))}
          </div>
        </div>
        <div className="map-wrap">
          <CoverageMap />
        </div>
      </div>
    </section>
  );
}

// stylized abstract map of UZ regions with major city markers
function CoverageMap() {
  // pseudo-positions for major cities (not geographically accurate, but readable)
  const cities = [
    { id: "tas", name: "Toshkent",   x: 460, y: 145, big: true },
    { id: "sam", name: "Samarqand",  x: 350, y: 240 },
    { id: "buk", name: "Buxoro",     x: 235, y: 260 },
    { id: "khv", name: "Xiva",       x: 110, y: 200 },
    { id: "nuk", name: "Nukus",      x: 70,  y: 110 },
    { id: "and", name: "Andijon",    x: 545, y: 195 },
    { id: "frg", name: "Farg'ona",   x: 510, y: 215 },
    { id: "nam", name: "Namangan",   x: 530, y: 170 },
    { id: "qsh", name: "Qarshi",     x: 305, y: 320 },
    { id: "trm", name: "Termiz",     x: 340, y: 380 }
  ];

  return (
    <svg viewBox="0 0 600 420" style={{ width: "100%", height: "100%" }}>
      <defs>
        <linearGradient id="route" x1="0" y1="0" x2="1" y2="0">
          <stop offset="0%" stopColor="var(--blue-500)" />
          <stop offset="100%" stopColor="var(--blue-300)" />
        </linearGradient>
      </defs>
      {/* stylized country outline */}
      <path
        d="M 60 110 L 100 70 L 200 60 L 290 90 L 370 70 L 470 90 L 540 130 L 575 160 L 555 200 L 530 240 L 470 230 L 410 270 L 360 320 L 320 390 L 260 360 L 200 320 L 130 290 L 70 240 L 40 180 Z"
        fill="white"
        stroke="var(--blue-300)"
        strokeWidth="1.5"
      />
      {/* internal region lines */}
      <g stroke="var(--blue-200, #d6ecfa)" strokeWidth="1" fill="none" opacity=".7">
        <path d="M 140 130 L 280 200" />
        <path d="M 300 100 L 320 250" />
        <path d="M 420 100 L 380 240" />
        <path d="M 470 200 L 530 230" />
      </g>

      {/* routes from Tashkent hub */}
      {cities.filter(c => c.id !== "tas").map(c => (
        <line key={`r-${c.id}`} x1={460} y1={145} x2={c.x} y2={c.y}
              stroke="url(#route)" strokeWidth="1.5" strokeDasharray="4 5" opacity=".5" />
      ))}

      {/* nodes */}
      {cities.map(c => (
        <g key={c.id} transform={`translate(${c.x},${c.y})`}>
          {c.big && <circle r="18" fill="var(--blue-500)" opacity=".18" />}
          <circle r={c.big ? 7 : 5} fill={c.big ? "var(--blue-500)" : "var(--navy-700)"} />
          {c.big && <circle r="3" fill="white" />}
          <text x={c.big ? 14 : 10} y="4" fontFamily="Public Sans" fontWeight={c.big ? 700 : 500} fontSize={c.big ? 14 : 12} fill="var(--ink-900)">{c.name}</text>
        </g>
      ))}

      {/* legend */}
      <g transform="translate(20, 395)">
        <circle cx="6" cy="0" r="5" fill="var(--blue-500)" />
        <text x="18" y="4" fontFamily="Public Sans" fontWeight="600" fontSize="11" fill="var(--ink-500)">HUB</text>
        <circle cx="70" cy="0" r="4" fill="var(--navy-700)" />
        <text x="82" y="4" fontFamily="Public Sans" fontWeight="600" fontSize="11" fill="var(--ink-500)">BEKAT / BRANCH</text>
      </g>
    </svg>
  );
}

// ─────────────────── CALCULATOR ───────────────────
function Calculator({ t }) {
  const cities = ["Toshkent", "Samarqand", "Buxoro", "Andijon", "Farg'ona", "Namangan", "Nukus", "Qarshi", "Termiz", "Xiva"];
  const [from, setFrom] = React.useState("Toshkent");
  const [to, setTo] = React.useState("Samarqand");
  const [weight, setWeight] = React.useState(2);
  const [service, setService] = React.useState("standard");

  // simple deterministic price calc
  const distFactor = Math.abs(cities.indexOf(from) - cities.indexOf(to)) || 1;
  const svcRate = service === "express" ? 5200 : service === "standard" ? 2800 : 4400;
  const base = 8000;
  const total = base + distFactor * svcRate + weight * 1200;

  const fmt = new Intl.NumberFormat("uz-Latn-UZ").format(Math.round(total / 100) * 100);

  return (
    <section className="calc section" id="calc">
      <div className="container calc-grid">
        <div className="calc-meta">
          <div className="eyebrow">{t.calc.eyebrow}</div>
          <h2 style={{ marginTop: 18 }}>{t.calc.title}</h2>
          <p>{t.calc.meta}</p>
          <div style={{ marginTop: 36, display: "flex", gap: 14, alignItems: "center" }}>
            <div style={{
              width: 60, height: 60, borderRadius: 16,
              background: "rgba(255,255,255,.08)",
              display: "grid", placeItems: "center", color: "var(--blue-300)"
            }}>
              <I name="phone" />
            </div>
            <div>
              <div style={{ color: "rgba(255,255,255,.5)", fontSize: 12.5, fontWeight: 700, letterSpacing: ".08em", textTransform: "uppercase" }}>Telefon</div>
              <div style={{ fontFamily: "var(--font-display)", fontSize: 22, fontWeight: 700, color: "white", marginTop: 2 }}>71 200 22 22</div>
            </div>
          </div>
        </div>

        <div className="calc-card">
          <div className="field">
            <label>{t.calc.from}</label>
            <select value={from} onChange={e => setFrom(e.target.value)}>
              {cities.map(c => <option key={c}>{c}</option>)}
            </select>
          </div>
          <div className="field">
            <label>{t.calc.to}</label>
            <select value={to} onChange={e => setTo(e.target.value)}>
              {cities.map(c => <option key={c}>{c}</option>)}
            </select>
          </div>
          <div className="row" style={{ marginBottom: 6 }}>
            <div className="field" style={{ margin: 0 }}>
              <label>{t.calc.weight}</label>
              <div className="weight-pills">
                {[1, 2, 5, 10, 20].map(w => (
                  <button key={w} aria-pressed={weight === w} onClick={() => setWeight(w)}>{w} kg</button>
                ))}
              </div>
            </div>
            <div className="field" style={{ margin: 0 }}>
              <label>{t.calc.service}</label>
              <select value={service} onChange={e => setService(e.target.value)}>
                <option value="standard">Standart (1–2 kun)</option>
                <option value="express">Tezkor (24 soat)</option>
                <option value="cargo">Yuk / kargo</option>
              </select>
            </div>
          </div>
          <div className="calc-result">
            <div className="left">
              <div className="lbl">{t.calc.total}</div>
              <div className="num">{fmt} <span style={{ fontSize: 18, color: "var(--ink-500)", fontWeight: 600 }}>so'm</span></div>
              <div className="sub">{t.calc.sub}</div>
            </div>
            <button className="btn btn-dark">
              {t.calc.cta} <I name="arrow" size={16} />
            </button>
          </div>
        </div>
      </div>
    </section>
  );
}

// ─────────────────── STEPS ───────────────────
function Steps({ t }) {
  const icons = ["pkg", "truck", "search", "check"];
  return (
    <section className="section">
      <div className="container">
        <div className="section-head single">
          <div>
            <div className="eyebrow">{t.steps.eyebrow}</div>
            <h2 style={{ marginTop: 18 }}>{t.steps.title}</h2>
          </div>
        </div>
        <div className="steps-grid">
          {t.steps.items.map((s, i) => (
            <div className="step" key={i}>
              <div className="step-ico"><I name={icons[i]} size={20} /></div>
              <div className="num">0{i + 1}</div>
              <h3>{s.h}</h3>
              <p>{s.p}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

// ─────────────────── TESTIMONIALS ───────────────────
function Testimonials({ t }) {
  const palette = ["var(--navy-700)", "var(--blue-500)", "var(--navy-800)"];
  return (
    <section className="testimonials section">
      <div className="container">
        <div className="section-head">
          <div>
            <div className="eyebrow">{t.testimonials.eyebrow}</div>
            <h2 style={{ marginTop: 18 }}>{t.testimonials.title}</h2>
          </div>
          <p className="meta">96% mijozlar bizni do'stlariga tavsiya qiladi.</p>
        </div>
        <div className="test-grid">
          {t.testimonials.items.map((tm, i) => (
            <article className="test-card" key={i}>
              <p className="quote">{tm.quote}</p>
              <div className="test-meta">
                <div className="avatar" style={{ background: palette[i % 3] }}>
                  {tm.name.split(" ").map(p => p[0]).slice(0, 2).join("")}
                </div>
                <div>
                  <div className="name">{tm.name}</div>
                  <div className="role">{tm.role}</div>
                </div>
              </div>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}

// ─────────────────── CTA ───────────────────
function CTA({ t }) {
  return (
    <section className="section" id="contact">
      <div className="container">
        <div className="cta-block">
          <div>
            <h2>{t.cta.title}</h2>
            <p className="lede">{t.cta.lede}</p>
            <div style={{ marginTop: 28, display: "flex", gap: 22, color: "rgba(255,255,255,.85)", fontSize: 14.5 }}>
              <span style={{ display: "inline-flex", gap: 8, alignItems: "center" }}>
                <I name="check" size={16} stroke={2.4} /> Bepul olib ketish
              </span>
              <span style={{ display: "inline-flex", gap: 8, alignItems: "center" }}>
                <I name="check" size={16} stroke={2.4} /> Sug'urta tekin
              </span>
            </div>
            <div style={{ marginTop: 18, color: "rgba(255,255,255,.5)", fontSize: 13 }}>{t.cta.note}</div>
          </div>
          <form className="cta-form" onSubmit={e => e.preventDefault()}>
            <div className="field">
              <label>{t.cta.name}</label>
              <input placeholder="Aziz Karimov" />
            </div>
            <div className="field">
              <label>{t.cta.phone}</label>
              <input placeholder="+998 90 123 45 67" />
            </div>
            <div className="field">
              <label>{t.cta.city}</label>
              <input placeholder="Toshkent" />
            </div>
            <button className="btn btn-primary">{t.cta.btn} <I name="arrow" size={16} /></button>
          </form>
        </div>
      </div>
    </section>
  );
}

// ─────────────────── FOOTER ───────────────────
function Footer({ t }) {
  return (
    <footer>
      <div className="container">
        <div className="foot-grid">
          <div className="foot-brand">
            <div className="logo">
              <span style={{ display: "inline-flex", alignItems: "center", gap: 8 }}>
                <svg width="36" height="36" viewBox="0 0 60 60" aria-hidden>
                  <path d="M5 35 Q 20 5, 45 12 Q 35 22, 25 25 Q 35 25, 50 22 Q 38 32, 22 33 Q 35 35, 48 32 Q 32 42, 14 40 Q 30 42, 44 41 L 12 44 Z" fill="white" opacity=".9"/>
                </svg>
                ISHONCH
              </span>
            </div>
            <p style={{ marginTop: 16, lineHeight: 1.55 }}>{t.footer.about}</p>
            <div style={{ marginTop: 18, fontFamily: "var(--font-script)", fontSize: 22, color: "rgba(255,255,255,.55)" }}>
              {t.hero.script}
            </div>
          </div>
          <div className="foot-col">
            <h4>{t.footer.services}</h4>
            <ul>{t.footer.links.services.map((x, i) => <li key={i}><a href="#">{x}</a></li>)}</ul>
          </div>
          <div className="foot-col">
            <h4>{t.footer.company}</h4>
            <ul>{t.footer.links.company.map((x, i) => <li key={i}><a href="#">{x}</a></li>)}</ul>
          </div>
          <div className="foot-col">
            <h4>{t.footer.help}</h4>
            <ul>{t.footer.links.help.map((x, i) => <li key={i}><a href="#">{x}</a></li>)}</ul>
          </div>
        </div>
        <div className="foot-bottom">
          <span>{t.footer.copyright}</span>
          <div className="social">
            <a href="#" aria-label="Telegram"><I name="telegram" size={16} /></a>
            <a href="#" aria-label="Instagram"><I name="instagram" size={16} /></a>
            <a href="#" aria-label="Facebook"><I name="facebook" size={16} /></a>
            <a href="#" aria-label="YouTube"><I name="youtube" size={16} /></a>
          </div>
        </div>
      </div>
    </footer>
  );
}

// Export to window
Object.assign(window, {
  TopBar, Nav, Hero, Trust, Services, Why, Coverage, Calculator,
  Steps, Testimonials, CTA, Footer
});

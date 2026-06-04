// sections.jsx — simplified landing: Nav, Hero (tracking), Stats, About, Footer.

const I = window.Icon;

// ─── HEADER ───
function Nav({ t }) {
  return (
    <nav style={{
      background: 'linear-gradient(135deg, #0A2472 0%, #1A5FAA 100%)',
      padding: '0 20px',
      position: 'sticky',
      top: 0,
      zIndex: 50,
    }}>
      <div style={{
        maxWidth: 640,
        margin: '0 auto',
        height: 90,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
      }}>
        <a href="#" style={{display:'flex', alignItems:'center', textDecoration:'none'}}>
          <img
            src="assets/ishonch-logo-full.png?v=2"
            alt="Ishonch Logistics"
            style={{
              height: 80,
              width: 'auto',
              filter: 'brightness(0) invert(1)',
            }}
          />
        </a>
      </div>
    </nav>
  );
}

// ─── HERO ───
function Hero({ t }) {
  const [trackingInput, setTrackingInput] = React.useState('');

  const handleTrack = () => {
    const val = trackingInput.trim();
    if (!val) return;
    window.location.href = 'track.html?barcode=' + encodeURIComponent(val);
  };

  return (
    <section style={{
      background: 'linear-gradient(135deg, #0A2472 0%, #1A5FAA 100%)',
      padding: '40px 20px 80px',
      textAlign: 'center',
    }}>
      <div style={{maxWidth: 560, margin: '0 auto'}}>

        <div style={{marginBottom: 24}}>
          <img
            src="assets/ishonch-logo-full.png?v=2"
            alt="Ishonch Logistics"
            style={{
              height: 80,
              width: 'auto',
              filter: 'brightness(0) invert(1)',
            }}
          />
        </div>

        <h1 style={{
          color: 'white',
          fontSize: 'clamp(28px, 8vw, 42px)',
          fontWeight: 800,
          margin: '0 0 12px',
          lineHeight: 1.2,
          letterSpacing: '-0.5px',
        }}>
          Yukingiz qayerda?
        </h1>

        <p style={{
          color: 'rgba(255,255,255,0.75)',
          fontSize: 16,
          margin: '0 0 32px',
          lineHeight: 1.5,
        }}>
          Kuzatuv raqamini kiriting va yukingiz holatini bir zumda bilib oling
        </p>

        {/* Search box */}
        <div style={{
          background: 'white',
          borderRadius: 16,
          padding: 8,
          display: 'flex',
          gap: 8,
          boxShadow: '0 20px 60px rgba(0,0,0,0.2)',
          maxWidth: 480,
          margin: '0 auto 16px',
        }}>
          <input
            value={trackingInput}
            onChange={e => setTrackingInput(e.target.value.toUpperCase())}
            onKeyDown={e => e.key === 'Enter' && handleTrack()}
            placeholder="TN12345678"
            spellCheck={false}
            autoCapitalize="characters"
            autoCorrect="off"
            style={{
              flex: 1,
              border: 'none',
              outline: 'none',
              padding: '12px 16px',
              fontSize: 16,
              borderRadius: 10,
              background: 'transparent',
              color: '#1B2440',
              fontWeight: 600,
            }}
          />
          <button
            type="button"
            onClick={handleTrack}
            style={{
              background: '#0A2472',
              color: 'white',
              border: 'none',
              borderRadius: 10,
              padding: '12px 24px',
              fontSize: 15,
              fontWeight: 700,
              cursor: 'pointer',
              whiteSpace: 'nowrap',
            }}
          >
            Kuzatish →
          </button>
        </div>

        <p style={{color: 'rgba(255,255,255,0.5)', fontSize: 12}}>
          Sinab ko'ring: <span
            style={{cursor:'pointer', textDecoration:'underline', color:'rgba(255,255,255,0.8)'}}
            onClick={() => window.location.href='track.html?barcode=TT123456789UZ'}
          >TT123456789UZ</span>
        </p>
      </div>
    </section>
  );
}

// ─── STATS ───
function Stats() {
  const items = [
    { n: '14', l: 'Viloyat' },
    { n: '180+', l: 'Yetkazish punkti' },
    { n: '24 soat', l: "O'rtacha vaqt" },
    { n: '98%', l: 'Muvaffaqiyat' },
  ];
  return (
    <section style={{background: 'white', padding: '40px 20px'}}>
      <div style={{
        maxWidth: 560,
        margin: '0 auto',
        display: 'grid',
        gridTemplateColumns: 'repeat(2, 1fr)',
        gap: 16,
      }}>
        {items.map((s, i) => (
          <div key={i} style={{
            background: '#F4F7FB',
            borderRadius: 14,
            padding: '20px 16px',
            textAlign: 'center',
          }}>
            <div style={{fontSize: 28, fontWeight: 800, color: '#0A2472'}}>{s.n}</div>
            <div style={{fontSize: 13, color: '#6A748A', marginTop: 4}}>{s.l}</div>
          </div>
        ))}
      </div>
    </section>
  );
}

// ─── ABOUT ───
function About() {
  return (
    <section style={{background: '#F4F7FB', padding: '40px 20px'}}>
      <div style={{maxWidth: 560, margin: '0 auto'}}>
        <h2 style={{
          fontSize: 22,
          fontWeight: 800,
          color: '#0A2472',
          margin: '0 0 16px',
          textAlign: 'center',
        }}>
          Ishonch Logistics haqida
        </h2>

        <div style={{display:'flex', flexDirection:'column', gap:12}}>
          {[
            { icon: '🚚', title: "Tez yetkazib berish", desc: "Toshkentdan O'zbekistonning istalgan nuqtasiga 24 soat ichida" },
            { icon: '📦', title: "Yukni kuzatish", desc: "Har bir yuk real vaqtda kuzatiladi — qayerda ekanini doim bilasiz" },
            { icon: '💰', title: "Arzon narxlar", desc: "1-2 kg — 28,000 so'm. Kichik biznes va oddiy odamlar uchun qulay" },
            { icon: '✅', title: "Ishonchli xizmat", desc: "98% yuklar belgilangan vaqtda yetkaziladi" },
          ].map((item, i) => (
            <div key={i} style={{
              background: 'white',
              borderRadius: 12,
              padding: '16px',
              display: 'flex',
              gap: 14,
              alignItems: 'flex-start',
            }}>
              <div style={{fontSize: 28, flexShrink: 0}}>{item.icon}</div>
              <div>
                <div style={{fontWeight: 700, color: '#0A2472', marginBottom: 4}}>{item.title}</div>
                <div style={{fontSize: 13, color: '#6A748A', lineHeight: 1.5}}>{item.desc}</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

// ─── FOOTER ───
function Footer() {
  return (
    <footer style={{
      background: '#0A2472',
      color: 'white',
      padding: '32px 20px',
      textAlign: 'center',
    }}>
      <div style={{maxWidth: 560, margin: '0 auto'}}>
        <img src="assets/ishonch-logo-full.png?v=2" alt="Ishonch Logistics"
          style={{height: 40, width:'auto', filter:'brightness(0) invert(1)', marginBottom: 16}} />
        <p style={{color:'rgba(255,255,255,0.6)', fontSize:13, margin:'0 0 16px', fontStyle:'italic'}}>
          Ishonch har bir yetkazishda
        </p>
        <div style={{display:'flex', justifyContent:'center', gap:24, marginBottom:16}}>
          <a href="tel:+998712002222" style={{color:'rgba(255,255,255,0.8)', textDecoration:'none', fontSize:14}}>
            📞 71 200 22 22
          </a>
          <a href="track.html" style={{color:'rgba(255,255,255,0.8)', textDecoration:'none', fontSize:14}}>
            📦 Yukni kuzatish
          </a>
        </div>
        <p style={{color:'rgba(255,255,255,0.4)', fontSize:12, margin:0}}>
          © 2025 Ishonch Logistics
        </p>
      </div>
    </footer>
  );
}

// Export
Object.assign(window, { Nav, Hero, Stats, About, Footer });

// app.jsx — main App. Wires tweaks + language + composition.

const { useState, useEffect, useMemo } = React;

const TWEAK_DEFAULTS = /*EDITMODE-BEGIN*/{
  "lang": "uz",
  "accent": "#2b7fd8",
  "density": "regular",
  "heroLayout": "stack",
  "showTrustStrip": true,
  "fontDisplay": "Archivo"
}/*EDITMODE-END*/;

function App() {
  const [t] = useTweaks(TWEAK_DEFAULTS);

  // apply tweaks live
  useEffect(() => {
    document.documentElement.style.setProperty("--accent", t.accent);
    document.body.dataset.density = t.density;
    document.documentElement.style.setProperty("--font-display", `"${t.fontDisplay}", ui-sans-serif, system-ui, sans-serif`);
  }, [t.accent, t.density, t.fontDisplay]);

  return (
    <div>
      <Hero t={t} />
      <Stats />
      <About />
      <Footer />
    </div>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(<App />);

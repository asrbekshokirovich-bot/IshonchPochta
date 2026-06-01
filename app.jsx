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
  const [t, setTweak] = useTweaks(TWEAK_DEFAULTS);

  // apply tweaks live
  useEffect(() => {
    document.documentElement.style.setProperty("--accent", t.accent);
    document.body.dataset.density = t.density;
    document.documentElement.style.setProperty("--font-display", `"${t.fontDisplay}", ui-sans-serif, system-ui, sans-serif`);
  }, [t.accent, t.density, t.fontDisplay]);

  const copy = window.COPY[t.lang] || window.COPY.uz;

  return (
    <>
      <TopBar lang={t.lang} setLang={(l) => setTweak("lang", l)} t={copy} />
      <Nav t={copy} />
      <Hero t={copy} layout={t.heroLayout} />
      {t.showTrustStrip && <Trust t={copy} />}
      <Services t={copy} />
      <Why t={copy} />
      <Coverage t={copy} />
      <Calculator t={copy} />
      <Steps t={copy} />
      <Testimonials t={copy} />
      <CTA t={copy} />
      <Footer t={copy} />

      <TweaksPanel title="Tweaks">
        <TweakSection label="Til / Language" />
        <TweakRadio label="Language" value={t.lang}
                    options={["uz", "ru", "en"]}
                    onChange={(v) => setTweak("lang", v)} />

        <TweakSection label="Visual" />
        <TweakColor label="Accent" value={t.accent}
                    options={["#2b7fd8", "#3fa3e3", "#0c2454", "#1e4d8b", "#f0a31a", "#2ea16b"]}
                    onChange={(v) => setTweak("accent", v)} />
        <TweakRadio label="Density" value={t.density}
                    options={["compact", "regular", "comfy"]}
                    onChange={(v) => setTweak("density", v)} />
        <TweakSelect label="Display font" value={t.fontDisplay}
                     options={["Archivo", "Bricolage Grotesque", "Space Grotesk", "DM Sans", "Manrope"]}
                     onChange={(v) => setTweak("fontDisplay", v)} />

        <TweakSection label="Layout" />
        <TweakRadio label="Hero headline" value={t.heroLayout}
                    options={["stack", "split"]}
                    onChange={(v) => setTweak("heroLayout", v)} />
        <TweakToggle label="Trust strip" value={t.showTrustStrip}
                     onChange={(v) => setTweak("showTrustStrip", v)} />
      </TweaksPanel>
    </>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(<App />);

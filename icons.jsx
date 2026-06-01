// icons.jsx — inline SVG icons. Stroke-based, 24x24.

const Icon = ({ name, size = 24, stroke = 1.8, ...rest }) => {
  const paths = {
    express: <>
      <path d="M3 12h9" /><path d="M14 7l5 5-5 5" /><path d="M20 12h1" /><circle cx="6" cy="18" r="2" /><circle cx="18" cy="18" r="2" />
    </>,
    standard: <>
      <path d="M3 7h13l4 4v6h-2" /><path d="M3 7v10h2" /><circle cx="8" cy="17" r="2" /><circle cx="17" cy="17" r="2" /><path d="M16 11h4" />
    </>,
    cargo: <>
      <path d="M3 8l9-4 9 4-9 4z" /><path d="M3 8v8l9 4 9-4V8" /><path d="M12 12v8" /><path d="M7.5 6.25 16.5 10.25" />
    </>,
    intl: <>
      <circle cx="12" cy="12" r="9" /><path d="M3 12h18" /><path d="M12 3a14 14 0 0 1 0 18" /><path d="M12 3a14 14 0 0 0 0 18" />
    </>,
    cod: <>
      <rect x="3" y="6" width="18" height="12" rx="2" /><circle cx="12" cy="12" r="2.5" /><path d="M7 12h.01M17 12h.01" />
    </>,
    ecom: <>
      <path d="M4 6h2l2 11h11l1.5-8H7" /><circle cx="10" cy="20" r="1.4" /><circle cx="17" cy="20" r="1.4" />
    </>,
    wallet: <>
      <path d="M3 7a2 2 0 0 1 2-2h12v4" /><rect x="3" y="7" width="18" height="12" rx="2" /><circle cx="17" cy="13" r="1.4" />
    </>,
    clock: <>
      <circle cx="12" cy="12" r="9" /><path d="M12 7v5l3 2" />
    </>,
    map: <>
      <path d="M9 4 3 6v14l6-2 6 2 6-2V4l-6 2z" /><path d="M9 4v14M15 6v14" />
    </>,
    shield: <>
      <path d="M12 3 4 6v6c0 5 3.5 8 8 9 4.5-1 8-4 8-9V6z" /><path d="m9 12 2 2 4-4" />
    </>,
    search: <>
      <circle cx="11" cy="11" r="7" /><path d="m20 20-3.5-3.5" />
    </>,
    pkg: <>
      <path d="M3 7v10l9 4 9-4V7l-9-4z" /><path d="m3 7 9 4 9-4M12 11v10" />
    </>,
    phone: <>
      <path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2z" />
    </>,
    chevron: <>
      <path d="m9 6 6 6-6 6" />
    </>,
    check: <>
      <path d="m5 12 5 5 9-11" />
    </>,
    arrow: <>
      <path d="M5 12h14" /><path d="m13 6 6 6-6 6" />
    </>,
    truck: <>
      <path d="M3 7h11v9H3z" /><path d="M14 10h4l3 3v3h-7" /><circle cx="7" cy="18" r="2" /><circle cx="17" cy="18" r="2" />
    </>,
    box: <>
      <rect x="4" y="5" width="16" height="14" rx="1.5" /><path d="M4 9h16M10 5v4M14 5v4" />
    </>,
    sparkle: <>
      <path d="M12 4v4M12 16v4M4 12h4M16 12h4M6.5 6.5l2.5 2.5M15 15l2.5 2.5M6.5 17.5 9 15M15 9l2.5-2.5" />
    </>,
    instagram: <>
      <rect x="3" y="3" width="18" height="18" rx="5" /><circle cx="12" cy="12" r="4" /><circle cx="17.5" cy="6.5" r="0.6" fill="currentColor" stroke="none"/>
    </>,
    telegram: <>
      <path d="M21 4 2 11.5l5 1.5 1.5 5L11 15l6 5L21 4z" />
    </>,
    facebook: <>
      <path d="M14 8h2V4h-2c-2 0-3 1.5-3 3v2H9v3h2v9h3v-9h2.5l.5-3H14V7.5c0-.5.3-.5.7-.5z" />
    </>,
    youtube: <>
      <rect x="3" y="6" width="18" height="12" rx="3" /><path d="m10 9 5 3-5 3z" fill="currentColor" stroke="none" />
    </>
  };

  return (
    <svg width={size} height={size} viewBox="0 0 24 24"
         fill="none" stroke="currentColor" strokeWidth={stroke}
         strokeLinecap="round" strokeLinejoin="round" {...rest}>
      {paths[name] || null}
    </svg>
  );
};

window.Icon = Icon;

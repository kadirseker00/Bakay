/**
 * BAKAY logosu — bağlı düğümlü bir sohbet baloncuğu.
 * Düğümler: kaynak belgeleri (RAG), baloncuk: doğal dil yanıtı.
 */
export default function Logo({ size = 40 }: { size?: number }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 48 48"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-label="BAKAY"
    >
      <defs>
        <linearGradient id="bakayGrad" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stopColor="#2563eb" />
          <stop offset="1" stopColor="#06b6d4" />
        </linearGradient>
      </defs>
      <rect x="2" y="2" width="44" height="44" rx="13" fill="url(#bakayGrad)" />
      {/* sohbet baloncuğu */}
      <path
        d="M14 15h20a4 4 0 0 1 4 4v8a4 4 0 0 1-4 4h-8l-6.5 5v-5H14a4 4 0 0 1-4-4v-8a4 4 0 0 1 4-4z"
        fill="#ffffff"
        fillOpacity="0.96"
      />
      {/* bağlı düğümler (kaynaklar) */}
      <path d="M18.5 24 L24 21.5 L29.5 25" stroke="#2563eb" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round" opacity="0.55" />
      <circle cx="18.5" cy="24" r="2.1" fill="#2563eb" />
      <circle cx="24" cy="21.5" r="2.1" fill="#06b6d4" />
      <circle cx="29.5" cy="25" r="2.1" fill="#2563eb" />
    </svg>
  );
}

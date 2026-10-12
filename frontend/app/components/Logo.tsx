/* eslint-disable @next/next/no-img-element */
/**
 * BAKAI logosu — sohbet baloncuğu + Kırgız tündüğü + devre düğümleri.
 * Konuşma (chatbot) + kültürel miras + yapay zekâ tek işarette.
 */
export default function Logo({ size = 40 }: { size?: number }) {
  return (
    <img
      src="/logo.png"
      alt="BAKAI"
      width={size}
      height={size}
      style={{ display: "block", objectFit: "contain" }}
    />
  );
}

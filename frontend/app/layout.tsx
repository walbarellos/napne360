import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "NAPNE 360° — IFAC",
  description: "Sistema de Apoio ao Estudante com Necessidades Específicas",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="pt-BR">
      <body className={`${geistSans.variable} ${geistMono.variable} antialiased`}>
        {children}
        
        {/* VLibras — obrigatório pelo Plano de Acessibilidade IFAC */}
        <div vw-access-button="true" className="active"></div>
        <div vw="true" className="enabled">
          <div vw-plugin-wrapper="true">
            <div className="vw-plugin-top-wrapper"></div>
          </div>
        </div>
        <script
          dangerouslySetInnerHTML={{
            __html: `
              window.onload = function() {
                new window.VLibras.Widget('https://vlibras.gov.br/app');
              };
            `
          }}
        />
        <script src="https://vlibras.gov.br/app/vlibras-plugin.js" async />
      </body>
    </html>
  );
}

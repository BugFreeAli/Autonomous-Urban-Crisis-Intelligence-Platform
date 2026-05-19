import type { Metadata, Viewport } from 'next';
import { JetBrains_Mono, DM_Serif_Display } from 'next/font/google';
import './globals.css';

const mono = JetBrains_Mono({
  subsets: ['latin'],
  variable: '--font-mono',
});

const serif = DM_Serif_Display({
  weight: '400',
  subsets: ['latin'],
  variable: '--font-serif',
});

export const metadata: Metadata = {
  title: 'Urban Crisis Intelligence',
  description: 'Autonomous urban crisis command — mobile',
  appleWebApp: {
    capable: true,
    statusBarStyle: 'black-translucent',
    title: 'Crisis OS',
  },
};

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  maximumScale: 1,
  userScalable: false,
  viewportFit: 'cover',
  themeColor: '#050708',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${mono.variable} ${serif.variable} h-full`}>
      <body className="font-tech h-full overflow-hidden antialiased">{children}</body>
    </html>
  );
}

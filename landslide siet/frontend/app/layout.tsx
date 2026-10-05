import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'LandSense',
  description: 'AI-based landslide early warning and rescue intelligence platform',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

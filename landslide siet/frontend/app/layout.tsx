import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'TerraSafe | Landslide Decision Support',
  description: 'Offline-minded landslide risk monitoring and rescue decision support. Not an official warning service.',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

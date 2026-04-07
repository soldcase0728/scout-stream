import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Scout Stream',
  description: 'Softball hitting biomechanics analysis',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-gray-50 min-h-screen">
        <nav className="bg-scout-900 text-white px-6 py-3 flex items-center justify-between">
          <a href="/" className="text-xl font-bold">Scout Stream</a>
          <div className="flex gap-4 text-sm">
            <a href="/athletes" className="hover:text-scout-100">Athletes</a>
          </div>
        </nav>
        <main className="max-w-7xl mx-auto px-4 py-6">{children}</main>
      </body>
    </html>
  );
}

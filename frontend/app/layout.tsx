import type { Metadata } from 'next';
import { Be_Vietnam_Pro } from 'next/font/google';
import './globals.css';

const beVietnamPro = Be_Vietnam_Pro({
  weight: ['400', '500', '600', '700'],
  subsets: ['latin', 'vietnamese'],
  variable: '--font-be-vietnam-pro',
  display: 'swap',
});

export const metadata: Metadata = {
  title: 'AI Precision Fit — Trợ Lý Thử Đồ & Gợi Ý Size Ảo',
  description: 'AI Fitting & Virtual Try-On widget thông minh dành cho e-commerce thời trang.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="vi" className={beVietnamPro.variable}>
      <body className="font-sans antialiased bg-slate-100 text-brand-navy min-h-screen">
        {children}
      </body>
    </html>
  );
}
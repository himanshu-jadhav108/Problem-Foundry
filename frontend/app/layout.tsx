import './globals.css';
import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Problem Foundry - Local AI Algorithmic Problem Creator',
  description: 'Model-agnostic local AI platform for competitive programming problem creation, differential solution verification, and test case synthesis.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-[#0b0f19] text-slate-100 flex flex-col">
        {children}
      </body>
    </html>
  );
}

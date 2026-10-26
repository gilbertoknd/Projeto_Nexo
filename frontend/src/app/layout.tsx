import type { Metadata } from 'next';
import Providers from './providers';

export const metadata: Metadata = {
  title: 'Contratação de Serviços | MVP',
  description: 'Gestão assíncrona de solicitações, propostas e pagamentos',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="pt">
      <body style={{ margin: 0, backgroundColor: '#f5f5f5', fontFamily: 'sans-serif' }}>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
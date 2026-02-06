import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Sovereign Sentinel',
  description: 'Financial War Room - Shadow Default Detection System',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="bg-gray-900 text-gray-100 antialiased">{children}</body>
    </html>
  )
}

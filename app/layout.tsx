import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
    title: "Crypto Cycle Signal Tracker",
    description: "AI-powered Bitcoin market cycle analysis and signal tracking",
};

export default function RootLayout({
    children,
}: Readonly<{
    children: React.ReactNode;
}>) {
    return (
        <html lang="en">
            <body className={`${inter.className} font-sans antialiased selection:bg-[#2383e2] selection:text-white`}>
                {children}
            </body>
        </html>
    );
}

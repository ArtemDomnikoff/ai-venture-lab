import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";

import "./globals.css";

import ProjectSidebar from "@/components/ProjectSidebar";


const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});


const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});



export const metadata: Metadata = {
  title: "AI Venture Lab",
  description:
    "Multi-agent venture research platform",
};



export default function RootLayout({
  children,
}: LayoutProps<"/">) {


  return (

    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable}`}
    >

      <body
        className="
          h-screen
          overflow-hidden
          bg-zinc-950
          text-zinc-100
        "
      >

      <div
        className="
          flex
          h-screen
          overflow-hidden
        "
      >

        <ProjectSidebar />


        <main
          className="
            flex-1
            min-w-0

            overflow-y-auto
          "
        >

          {children}

        </main>


      </div>
      </body>


    </html>

  );

}
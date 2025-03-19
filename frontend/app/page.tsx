"use client";
import Image from "next/image";
import DownloadForm from "./components/DownloadForm";

export default function Home() {
  return (
    <main className="p-10 max-w-2xl mx-auto">
      {/* Logo */}
      <div className="flex justify-center items-center mb-6 gap-4">
        <Image src="/Kaiko.svg" alt="Super OPS Logo" width={160} height={80} />
        <h1 className="text-xl font-semibold">Super OPS Sampler</h1>
      </div>

      <DownloadForm />
    </main>
  );
}

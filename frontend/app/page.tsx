"use client";

import Image from "next/image";
import { useEffect, useState } from "react";
import { onAuthStateChanged, signOut, type User } from "firebase/auth";
import { auth } from "./utils/firebase";
import DownloadForm from "./components/DownloadForm";
import dynamic from "next/dynamic";

const FirebaseAuthUI = dynamic(() => import("./components/FirebaseAuthUI"), {
  ssr: false,
});

export default function Home() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!auth) {
      setLoading(false);
      return;
    }
    const unsubscribe = onAuthStateChanged(auth, (u) => {
      setUser(u);
      setLoading(false);
    });
    return unsubscribe;
  }, []);

  if (loading) return <div className="p-10">Loading…</div>;

  return (
    <div className="relative min-h-screen">
      {/* top-right user info + sign out */}
      {user && (
        <div className="absolute top-4 right-4 flex items-center space-x-3">
          <span className="text-sm text-gray-700">
            Logged in as <strong className="font-medium">{user.email}</strong>
          </span>
          <button
            onClick={() => auth && signOut(auth)}
            className="text-sm bg-red-600 hover:bg-red-700 text-white font-semibold py-1 px-3 rounded shadow transform hover:scale-105 transition duration-200 ease-in-out"
          >
            Sign Out
          </button>
        </div>
      )}

      <main className="p-10 max-w-2xl mx-auto">
        {/* logo + title */}
        <div className="flex justify-center items-center mb-6 gap-4">
          <Image
            src="/Kaiko.svg"
            alt="Super OPS Logo"
            width={240}
            height={120}
            priority
          />
          <h1 className="text-xl font-semibold">CSV Sample Downloader</h1>
        </div>

        {!user ? (
          <div className="flex justify-center items-center min-h-[60vh]">
            <FirebaseAuthUI />
          </div>
        ) : (
          <>
            {/* removed the old “Logged in as…” paragraph here */}
            <DownloadForm />
          </>
        )}
      </main>
    </div>
  );
}

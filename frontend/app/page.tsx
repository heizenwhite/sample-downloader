// app/page.tsx
"use client";
import { useEffect, useState } from "react";
import Image from "next/image";
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
      // no client auth available (e.g. at build time)
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
      {user && (
        <div className="absolute top-4 right-4">
          <button
            onClick={() => auth && signOut(auth)}
            className="bg-red-600 hover:bg-red-700 text-white font-semibold py-2 px-4 rounded shadow transform hover:scale-105 transition duration-200 ease-in-out"
          >
            Sign Out
          </button>
        </div>
      )}
      <main className="p-10 max-w-2xl mx-auto">
        {/* … your logo + title … */}
        {!user ? (
          <div className="flex justify-center items-center min-h-[60vh]">
            <FirebaseAuthUI />
          </div>
        ) : (
          <>
            <p className="mb-4">
              Logged in as <strong>{user.email || "Anonymous"}</strong>
            </p>
            <DownloadForm />
          </>
        )}
      </main>
    </div>
  );
}

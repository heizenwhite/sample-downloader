"use client";
import { useEffect, useState } from "react";
import Image from "next/image";
import { onAuthStateChanged, signOut } from "firebase/auth";
import { auth } from "./utils/firebase";
import DownloadForm from "./components/DownloadForm";
import FirebaseAuthUI from "./components/FirebaseAuthUI";

export default function Home() {
  const [user, setUser] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (firebaseUser) => {
      setUser(firebaseUser);
      setLoading(false);
    });

    return () => unsubscribe();
  }, []);

  if (loading) return <div className="p-10">Loading...</div>;

  return (
    <main className="p-10 max-w-2xl mx-auto">
      <div className="flex justify-center items-center mb-6 gap-4">
        <Image src="/Kaiko.svg" alt="Super OPS Logo" width={160} height={80} />
        <h1 className="text-xl font-semibold">Super OPS Sampler</h1>
      </div>

      {!user ? (
        <FirebaseAuthUI />
      ) : (
        <>
          <p className="mb-4">
            Logged in as <strong>{user.email || "Anonymous"}</strong>
          </p>

          <DownloadForm />

          {/* ✅ Sign out button here */}
          <button
            className="mt-6 text-red-600 underline"
            onClick={() => signOut(auth)}
          >
            Sign out
          </button>
        </>
      )}
    </main>
  );
}

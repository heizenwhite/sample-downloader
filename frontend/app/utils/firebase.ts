// utils/firebase.ts
import { initializeApp, FirebaseApp, getApps } from "firebase/app";
import { getAuth, type Auth } from "firebase/auth";

const firebaseConfig = {
  apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY!,
  authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN!,
  projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID!,
  storageBucket: process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET!,
  messagingSenderId: process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID!,
  appId: process.env.NEXT_PUBLIC_FIREBASE_APP_ID!,
};

let firebaseApp: FirebaseApp | null = null;
let auth: Auth | null = null;

// Only initialize in the browser, and only once
if (typeof window !== "undefined") {
  try {
    // `getApps()` returns an array of already initialized apps
    firebaseApp = getApps().length
      ? getApps()[0]
      : initializeApp(firebaseConfig);

    auth = getAuth(firebaseApp);
  } catch (e) {
    console.warn("⚠️ Firebase init skipped:", e);
    // auth stays null if config is missing/invalid
  }
}

export { auth };

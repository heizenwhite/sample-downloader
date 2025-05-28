// app/components/FirebaseAuthUI.tsx
"use client";
import { useEffect } from "react";
import { auth } from "../utils/firebase";
import { EmailAuthProvider } from "firebase/auth";
import * as firebaseui from "firebaseui";
import "firebaseui/dist/firebaseui.css";
import "../../styles/firebaseui-custom.css";

export default function FirebaseAuthUI() {
  useEffect(() => {
    const ui =
      firebaseui.auth.AuthUI.getInstance() ||
      new firebaseui.auth.AuthUI(auth!);

    ui.start("#firebaseui-auth-container", {
      signInOptions: [EmailAuthProvider.PROVIDER_ID],
      callbacks: { signInSuccessWithAuthResult: () => false },
      // you can also pass a custom logo here via callbacks if you like
    });
  }, []);

  return (
    <div className="bg-gray-900/60 backdrop-blur-md rounded-lg p-8 shadow-xl max-w-md mx-auto mt-16">
      <div
        id="firebaseui-auth-container"
        className="w-full text-gray-100"
      />
    </div>
  );
}

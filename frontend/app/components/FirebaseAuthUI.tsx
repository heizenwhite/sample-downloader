// components/FirebaseAuthUI.tsx
import { useEffect } from "react";
import { auth } from "../utils/firebase";
import * as firebaseui from "firebaseui";
import "firebaseui/dist/firebaseui.css";

export default function FirebaseAuthUI() {
  useEffect(() => {
    const ui = firebaseui.auth.AuthUI.getInstance() || new firebaseui.auth.AuthUI(auth);
    ui.start("#firebaseui-auth-container", {
      signInOptions: [
        firebaseui.auth.AnonymousAuthProvider.PROVIDER_ID,
        firebaseui.auth.EmailAuthProvider.PROVIDER_ID,
      ],
      callbacks: {
        signInSuccessWithAuthResult: () => false, // Prevent redirect
      },
    });
  }, []);

  return <div id="firebaseui-auth-container" />;
}

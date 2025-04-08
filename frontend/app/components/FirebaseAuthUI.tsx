import { useEffect } from "react";
import { auth } from "../utils/firebase";
import { EmailAuthProvider } from "firebase/auth";
import * as firebaseui from "firebaseui";
import "firebaseui/dist/firebaseui.css";
import "../../styles/firebaseui-custom.css"; // 👈 custom overrides

export default function FirebaseAuthUI() {
  useEffect(() => {
    const ui =
      firebaseui.auth.AuthUI.getInstance() || new firebaseui.auth.AuthUI(auth);

    ui.start("#firebaseui-auth-container", {
      signInOptions: [EmailAuthProvider.PROVIDER_ID],
      callbacks: {
        signInSuccessWithAuthResult: () => false,
      },
    });
  }, []);

  return (
    <div className="flex justify-center items-center min-h-[60vh]">
        <div id="firebaseui-auth-container" />
    </div>
  );
}

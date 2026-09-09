import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { LoginButton } from "@/components/ui/3d-button";
import "@/styles/index.css";

const root = document.getElementById("login-button-root");
if (root)
  createRoot(root).render(
    <StrictMode>
      <LoginButton />
    </StrictMode>,
  );

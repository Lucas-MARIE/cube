// ============================================================
// Cube.com Frontend - Login & Registration Page
// ============================================================

import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { userService } from "../services/userService";

const Login: React.FC = () => {
  const navigate = useNavigate();
  const [isRegister, setIsRegister] = useState(false);
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      if (isRegister) {
        const res = await userService.register({ username, email, password });
        localStorage.setItem("access_token", res.data.access_token);
      } else {
        const res = await userService.login(email, password);
        localStorage.setItem("access_token", res.data.access_token);
      }
      navigate("/profile");
    } catch (err: any) {
      setError(
        err.response?.data?.detail || "Une erreur est survenue lors de l'authentification."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.formCard}>
        <h2 style={styles.title}>{isRegister ? "Créer un compte" : "Connexion"}</h2>
        {error && <div style={styles.errorBox}>{error}</div>}

        <form onSubmit={handleSubmit} style={styles.form}>
          {isRegister && (
            <div style={styles.inputGroup}>
              <label style={styles.label}>Nom d'utilisateur</label>
              <input
                type="text"
                required
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                style={styles.input}
                placeholder="SpeedCuber99"
              />
            </div>
          )}

          <div style={styles.inputGroup}>
            <label style={styles.label}>Email</label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              style={styles.input}
              placeholder="cubeur@cube.com"
            />
          </div>

          <div style={styles.inputGroup}>
            <label style={styles.label}>Mot de passe</label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              style={styles.input}
              placeholder="••••••••"
            />
          </div>

          <button type="submit" disabled={loading} style={styles.submitBtn}>
            {loading ? "Chargement..." : isRegister ? "S'inscrire" : "Se connecter"}
          </button>
        </form>

        <p style={styles.toggleText}>
          {isRegister ? "Déjà un compte ?" : "Pas encore de compte ?"}{" "}
          <button
            type="button"
            onClick={() => {
              setIsRegister(!isRegister);
              setError(null);
            }}
            style={styles.toggleBtn}
          >
            {isRegister ? "Se connecter" : "Créer un compte"}
          </button>
        </p>
      </div>
    </div>
  );
};

const styles: Record<string, React.CSSProperties> = {
  container: {
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    minHeight: "75vh",
    padding: "2rem",
    color: "#ffffff",
  },
  formCard: {
    backgroundColor: "#16213e",
    border: "1px solid #1f4068",
    borderRadius: "12px",
    padding: "2.5rem",
    width: "100%",
    maxWidth: "420px",
    boxShadow: "0 8px 24px rgba(0,0,0,0.3)",
  },
  title: {
    textAlign: "center",
    marginBottom: "1.5rem",
    color: "#00d4ff",
  },
  errorBox: {
    backgroundColor: "rgba(255, 75, 75, 0.15)",
    border: "1px solid #ff4b4b",
    color: "#ff8b8b",
    padding: "0.75rem",
    borderRadius: "6px",
    marginBottom: "1rem",
    fontSize: "0.9rem",
  },
  form: {
    display: "flex",
    flexDirection: "column",
    gap: "1.2rem",
  },
  inputGroup: {
    display: "flex",
    flexDirection: "column",
    gap: "0.4rem",
  },
  label: {
    fontSize: "0.9rem",
    color: "#a0a0b0",
  },
  input: {
    padding: "0.75rem 1rem",
    borderRadius: "6px",
    border: "1px solid #233756",
    backgroundColor: "#0d1527",
    color: "#fff",
    fontSize: "1rem",
  },
  submitBtn: {
    backgroundColor: "#00d4ff",
    color: "#0a0a14",
    border: "none",
    borderRadius: "6px",
    padding: "0.8rem",
    fontSize: "1rem",
    fontWeight: "bold",
    cursor: "pointer",
    marginTop: "0.5rem",
  },
  toggleText: {
    textAlign: "center",
    marginTop: "1.5rem",
    fontSize: "0.9rem",
    color: "#a0a0b0",
  },
  toggleBtn: {
    background: "none",
    border: "none",
    color: "#00d4ff",
    cursor: "pointer",
    textDecoration: "underline",
    fontWeight: "bold",
  },
};

export default Login;


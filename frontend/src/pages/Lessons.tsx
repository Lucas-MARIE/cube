// ============================================================
// Cube.com Frontend - Lessons & CFOP Algorithms Page
// ============================================================

import React, { useEffect, useState } from "react";
import { lessonService } from "../services/lessonService";
import type { Lesson, Algorithm } from "../types";

const Lessons: React.FC = () => {
  const [activeTab, setActiveTab] = useState<"lessons" | "algorithms">("lessons");
  const [category, setCategory] = useState<string>("ALL");
  const [lessons, setLessons] = useState<Lesson[]>([]);
  const [algorithms, setAlgorithms] = useState<Algorithm[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setLoading(true);
    if (activeTab === "lessons") {
      lessonService
        .getLessons()
        .then((res) => setLessons(res.data))
        .catch(() => setLessons([]))
        .finally(() => setLoading(false));
    } else {
      const catParam = category === "ALL" ? undefined : category;
      lessonService
        .getAlgorithms(catParam)
        .then((res) => setAlgorithms(res.data))
        .catch(() => setAlgorithms([]))
        .finally(() => setLoading(false));
    }
  }, [activeTab, category]);

  return (
    <div style={styles.container}>
      <header style={styles.header}>
        <h1 style={styles.title}>Centre d'Apprentissage Rubik's Cube</h1>
        <p style={styles.subtitle}>
          Maîtrisez la méthode Fridrich (CFOP) : Croix, F2L, OLL, PLL
        </p>

        <div style={styles.tabGroup}>
          <button
            onClick={() => setActiveTab("lessons")}
            style={{
              ...styles.tabBtn,
              ...(activeTab === "lessons" ? styles.tabBtnActive : {}),
            }}
          >
            📖 Leçons
          </button>
          <button
            onClick={() => setActiveTab("algorithms")}
            style={{
              ...styles.tabBtn,
              ...(activeTab === "algorithms" ? styles.tabBtnActive : {}),
            }}
          >
            ⚡ Banque d'Algorithmes
          </button>
        </div>
      </header>

      {activeTab === "algorithms" && (
        <div style={styles.filterBar}>
          {["ALL", "F2L", "OLL", "PLL"].map((cat) => (
            <button
              key={cat}
              onClick={() => setCategory(cat)}
              style={{
                ...styles.filterBtn,
                ...(category === cat ? styles.filterBtnActive : {}),
              }}
            >
              {cat}
            </button>
          ))}
        </div>
      )}

      {loading ? (
        <p style={{ textAlign: "center", color: "#a0a0b0" }}>Chargement des données...</p>
      ) : activeTab === "lessons" ? (
        <div style={styles.grid}>
          {lessons.length > 0 ? (
            lessons.map((lesson) => (
              <div key={lesson.id} style={styles.card}>
                <div style={styles.badge}>{lesson.category.toUpperCase()}</div>
                <h3 style={styles.cardTitle}>{lesson.title}</h3>
                <p style={styles.cardDesc}>{lesson.description}</p>
                <div style={styles.metaRow}>
                  <span>Difficulté : {"⭐".repeat(lesson.difficulty)}</span>
                  <span>{lesson.steps?.length || 0} étapes</span>
                </div>
              </div>
            ))
          ) : (
            <div style={styles.card}>
              <div style={styles.badge}>DÉBUTANT</div>
              <h3 style={styles.cardTitle}>Introduction à la méthode des couches</h3>
              <p style={styles.cardDesc}>
                Apprenez la méthode pas-à-pas pour résoudre le Rubik's Cube face par face.
              </p>
              <div style={styles.metaRow}>
                <span>Difficulté : ⭐</span>
                <span>5 étapes</span>
              </div>
            </div>
          )}
        </div>
      ) : (
        <div style={styles.grid}>
          {algorithms.length > 0 ? (
            algorithms.map((algo) => (
              <div key={algo.id} style={styles.card}>
                <div style={styles.badge}>{algo.category}</div>
                <h3 style={styles.cardTitle}>{algo.name}</h3>
                <div style={styles.notationBox}>{algo.notation}</div>
                {algo.description && <p style={styles.cardDesc}>{algo.description}</p>}
              </div>
            ))
          ) : (
            <div style={styles.card}>
              <div style={styles.badge}>PLL</div>
              <h3 style={styles.cardTitle}>T-Permutation</h3>
              <div style={styles.notationBox}>R U R' U' R' F R2 U' R' U' R U R' F'</div>
              <p style={styles.cardDesc}>Échange deux coins et deux arêtes adjacents.</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

const styles: Record<string, React.CSSProperties> = {
  container: {
    maxWidth: "1100px",
    margin: "0 auto",
    padding: "2rem",
    color: "#fff",
  },
  header: {
    textAlign: "center",
    marginBottom: "2rem",
  },
  title: {
    fontSize: "2.4rem",
    color: "#00d4ff",
    marginBottom: "0.5rem",
  },
  subtitle: {
    color: "#a0a0b0",
    marginBottom: "1.5rem",
  },
  tabGroup: {
    display: "flex",
    justifyContent: "center",
    gap: "1rem",
  },
  tabBtn: {
    backgroundColor: "#16213e",
    border: "1px solid #1f4068",
    color: "#fff",
    padding: "0.7rem 1.5rem",
    borderRadius: "8px",
    cursor: "pointer",
    fontSize: "1rem",
  },
  tabBtnActive: {
    backgroundColor: "#00d4ff",
    color: "#0a0a14",
    borderColor: "#00d4ff",
    fontWeight: "bold",
  },
  filterBar: {
    display: "flex",
    justifyContent: "center",
    gap: "0.75rem",
    marginBottom: "2rem",
  },
  filterBtn: {
    backgroundColor: "#0f172a",
    border: "1px solid #233756",
    color: "#a0a0b0",
    padding: "0.4rem 1.2rem",
    borderRadius: "20px",
    cursor: "pointer",
  },
  filterBtnActive: {
    backgroundColor: "#00d4ff",
    color: "#0a0a14",
    fontWeight: "bold",
    borderColor: "#00d4ff",
  },
  grid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))",
    gap: "1.5rem",
  },
  card: {
    backgroundColor: "#16213e",
    border: "1px solid #1f4068",
    borderRadius: "12px",
    padding: "1.5rem",
    display: "flex",
    flexDirection: "column",
    gap: "0.8rem",
  },
  badge: {
    alignSelf: "flex-start",
    backgroundColor: "rgba(0, 212, 255, 0.15)",
    color: "#00d4ff",
    padding: "0.25rem 0.6rem",
    borderRadius: "6px",
    fontSize: "0.8rem",
    fontWeight: "bold",
  },
  cardTitle: {
    margin: 0,
    fontSize: "1.25rem",
  },
  cardDesc: {
    margin: 0,
    color: "#a0a0b0",
    fontSize: "0.95rem",
    lineHeight: 1.4,
  },
  notationBox: {
    backgroundColor: "#0d1527",
    padding: "0.75rem",
    borderRadius: "6px",
    fontFamily: "monospace",
    fontSize: "1.05rem",
    color: "#4ade80",
    letterSpacing: "0.05em",
  },
  metaRow: {
    display: "flex",
    justifyContent: "space-between",
    color: "#7e8a9b",
    fontSize: "0.85rem",
    marginTop: "auto",
  },
};

export default Lessons;


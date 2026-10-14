"""Service de génération de mélanges (scrambles) officiels WCA pour Rubik's Cube."""

import random

# Faces du Rubik's Cube standard 3x3
FACES = ["U", "D", "L", "R", "F", "B"]
MODIFIERS = ["", "'", "2"]

# Paires de faces opposées (pour éviter les séquences redondantes comme R R' ou U D U)
OPPOSITE_FACES = {
    "U": "D",
    "D": "U",
    "L": "R",
    "R": "L",
    "F": "B",
    "B": "F",
}


class ScrambleService:
    """Générateur de scrambles respectant la logique WCA."""

    @staticmethod
    def generate_random_scramble(length: int = 20) -> str:
        """Génère un scramble aléatoire valide de 20 mouvements."""
        moves: list[str] = []
        last_face = ""
        second_last_face = ""

        while len(moves) < length:
            face = random.choice(FACES)

            # Ne pas répéter la même face immédiatement
            if face == last_face:
                continue

            # Ne pas répéter une face opposée redondante (ex: U D U)
            if face == second_last_face and OPPOSITE_FACES.get(face) == last_face:
                continue

            modifier = random.choice(MODIFIERS)
            moves.append(f"{face}{modifier}")
            second_last_face = last_face
            last_face = face

        return " ".join(moves)

    @staticmethod
    def get_targeted_scramble(case_name: str) -> dict:
        """Retourne un scramble ciblé préparant un cas spécifique d'entraînement."""
        # Exemples prédéfinis pour s'entraîner sur un cas précis
        known_cases = {
            "t-perm": "F R U' R' U' R U R' F' R U R' U' R' F R F'",
            "sune": "R U R' U R U2 R'",
            "sexy-move": "R U R' U'",
        }
        case_key = case_name.lower().strip()
        scramble = known_cases.get(case_key, ScrambleService.generate_random_scramble())
        return {
            "case": case_name,
            "scramble": scramble,
            "length": len(scramble.split()),
        }


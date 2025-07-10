# 💥 Block Boom

> 🧩 Un jeu de puzzle dynamique et coloré développé en Python avec Pygame. Placez stratégiquement des blocs sur une grille, faites exploser des lignes et colonnes, utilisez des bombes, et visez le meilleur score !

---

## 🎮 Aperçu

**Block Boom** est un jeu de réflexion stimulant basé sur des mécaniques simples et addictives :

- 🧱 Placez des blocs de formes variées sur une grille 10x10.
- 💣 Déclenchez des explosions en complétant des lignes et colonnes.
- 🏆 Visez le meilleur score tout en gérant vos options stratégiques.
- 🚫 La partie se termine lorsqu'aucune pièce ne peut être placée.

![aperçu du jeu](https://github.com/user-attachments/assets/e61c4d45-71f5-4481-92c9-f6277535d114)

---

## ⚙️ Fonctionnalités

### 🔹 Fonctionnalités principales

- ✅ **Grille 10x10** : espace de jeu principal.
- 🧩 **3 pièces aléatoires** à placer à chaque tour.
- 🖱️ **Glisser-déposer fluide** des pièces sur la grille.
- 💥 **Suppression automatique** des lignes/colonnes complètes.
- 📈 **Système de score** en temps réel.
- 👑 **Meilleur score sauvegardé** entre les sessions.
- 🎨 **Animations et particules** lors des explosions.
- 🔊 **Effets sonores immersifs** : pose de pièce, explosions, erreurs, etc.

### 🔸 Fonctionnalités avancées

- 💣 **Bombe débloquée à 50 points** :
  - Supprime une zone de 3x3 cases.
  - Persiste dans la liste si non utilisée.
  - N'est consommée que lorsqu'elle est déposée.

- 🔄 **Régénération automatique** des pièces après usage des 3 pièces de base (la bombe ne compte pas).

- ⚙️ **Menu Paramètres (touche Échap)** :
  - Activation/désactivation des sons (musique + effets) via la touche `S`.
  - Sauvegarde du réglage.
  - Meilleur score sauvegardé.

---

## 📦 Dépendances

- [Python 3.10+](https://www.python.org/downloads/)
- [Pygame](https://www.pygame.org/)

---
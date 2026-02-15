# Kokushi Musou - Riichi Club 🀄

> **"千日の稽古を鍛とし、万日の稽古を練とす。" — 宮本 武蔵**  
> *(Practice for a thousand days to refine the steel; practice for ten thousand days to polish the spirit.) — Miyamoto Musashi*

**Kokushi Musou** is an unofficial Riichi Mahjong club at our Technical University. This platform serves as a central hub for members to learn the game, track their progress, and explore the deep strategy of Japanese Mahjong.

## 🚀 Vision
Our goal is to foster a community of players who appreciate the tactical depth of Riichi Mahjong. Whether you are a beginner learning the basics or a veteran aiming for a Yakuman, Kokushi Musou provides the tools and resources you need.

## 🛠️ Features
- **Learning Hub:** A comprehensive guide based on modern Riichi strategy.
- **Member Profiles:** Personalized user pages with "About Me" sections.
- **Technical Foundation:** A robust Flask application following industry best practices.
- **Reproducible Setup:** Full Nix/Flake support for seamless development.

## 💻 Tech Stack
- **Backend:** Flask (Blueprints & SQLAlchemy)
- **Environment:** Nix / NixOS (Flakes)
- **Database:** SQLite with Alembic migrations

## 🚀 Getting Started

The project environment is fully managed by Nix. You do not need to install Python or Flask manually.

1. Clone the repository.
2. Enter the development shell:
   ```bash
   nix develop
   ```
3. Initialize the database (if not already present):
   ```bash
   flask db upgrade
   ```
4. Run the application:
   ```bash
   python run.py
   ```
## 🗺️ Roadmap
- [x] Initial Flask foundation
- [ ] Comprehensive Riichi Mahjong rule guide
- [ ] Interactive Yaku reference cheat sheet
- [ ] Score calculation tool
- [ ] Technical University tournament integration
- [ ] Enhanced UI with a cohesive Mahjong theme

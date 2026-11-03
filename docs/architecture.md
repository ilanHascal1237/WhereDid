# Architecture

## System overview

React talks to FastAPI over REST; FastAPI is the only thing that talks to MongoDB. Player data itself originates from ESPN's public site API and is pulled in by a background sync job, not supplied by the user.

```mermaid
flowchart TB
    subgraph Browser["Browser"]
        UI["React app (Vite)\nApp / GamePage / EndlessPage / MascotPage"]
        LS[("localStorage\nstreak, best scores, difficulty, in-progress daily state")]
        UI <--> LS
    end

    subgraph Backend["FastAPI backend (uvicorn)"]
        Routes["Routes\n/game/*, /players/*"]
        Services["Services\nGameService, MascotService"]
        Sync["espn.py\nbackground sync on startup"]
        Routes --> Services
    end

    subgraph Mongo["MongoDB"]
        Players[("players")]
        Challenges[("daily_challenges")]
    end

    ESPN["ESPN Site API\nsite.api.espn.com"]

    UI -- "HTTPS / JSON (axios)" --> Routes
    Services --> Players
    Services --> Challenges
    Sync -- "fetch rosters + college info" --> ESPN
    Sync -- "bulk upsert by espn_id" --> Players
```

Notes:

- `game_sessions` is a defined-but-unused Mongo collection ([backend/app/db/\_\_init\_\_.py:42](../backend/app/db/__init__.py:42)) — no code path writes to it.
- The frontend never talks to ESPN or Mongo directly; all of that is hidden behind the FastAPI routes.
- `localStorage` is purely a client-side convenience (resume today's game, remember streak/best scores/settings) — it is not a source of truth for game data, which always comes from the backend.

## Backend module layering

```mermaid
flowchart LR
    subgraph routes["app/routes"]
        game_r["game.py\n/game/daily-challenge\n/game/hints/{id}\n/game/guess\n/game/endless/next\n/game/mascot/next\n/game/mascot/guess\n/game/reveal/{id}"]
        players_r["players.py\n/players/search\n/players/colleges\n/players/{id}"]
    end

    subgraph services["app/services"]
        game_s["GameService\ndaily pick, random pick,\nhints, guess checking"]
        mascot_s["MascotService\nmascot round + guess checking"]
        helpers["public_player / public_college\ndifficulty_rules\n(answer normalization)"]
        espn_s["espn.py\nsync_players / needs_sync"]
    end

    subgraph db["app/db"]
        mongo["MongoDB class\n+ collection getters"]
    end

    subgraph models["app/models"]
        pyd["Pydantic request/response\nmodels"]
    end

    game_r --> game_s
    game_r --> mascot_s
    game_r --> helpers
    players_r --> mongo
    players_r --> helpers
    game_s --> mongo
    mascot_s --> mongo
    espn_s --> mongo
    game_r -.-> pyd
```

# State Transition Diagrams

## Daily mode ([GamePage.tsx](../frontend/src/pages/GamePage.tsx))

One round per day. Progress is persisted to `localStorage` under `wheredid:daily:<date>`, so a reload restores whichever state the round was left in.

```mermaid
stateDiagram-v2
    [*] --> Restoring: mount

    Restoring --> Loading: no saved state for today
    Restoring --> Playing: saved state found (gameStatus = playing)
    Restoring --> Won: saved state found (gameStatus = won)
    Restoring --> Lost: saved state found (gameStatus = lost)

    Loading --> Playing: challenge + hints fetched
    Loading --> Error: request failed

    Error --> Loading: "Try Again" clicked

    Playing --> Loading: difficulty changed\n(only allowed before any guess)
    Playing --> Playing: incorrect guess\n(guesses < maxGuesses)
    Playing --> Won: correct guess
    Playing --> Lost: incorrect guess\n(guesses == maxGuesses) → answer revealed

    Won --> [*]: streak incremented + saved
    Lost --> [*]: round locked for the day
```

## Endless & Mascot modes ([StreakGame.tsx](../frontend/src/components/StreakGame.tsx))

Shared rapid-fire loop: one guess per round, 3 lives, used by both `EndlessPage` and `MascotPage` with different `fetchRound`/`checkGuess` implementations.

```mermaid
stateDiagram-v2
    [*] --> Idle

    Idle --> Idle: league/difficulty changed\n(best-score display refreshed)
    Idle --> Loading: "Start" clicked

    Loading --> Playing: round fetched
    Loading --> ErrorState: fetch failed

    ErrorState --> Loading: "Try Again" clicked

    Playing --> Feedback: guess submitted or skipped\n(correct → score++, else lives--)

    Feedback --> Loading: "Next" clicked, lives > 0
    Feedback --> Over: "Next" / "See Results" clicked, lives == 0

    Over --> Loading: "Play Again" clicked
    Over --> Idle: settings changed

    note right of Feedback
        best score is written to
        localStorage immediately
        when beaten, not on Over
    end note
```

export type Difficulty = 'easy' | 'medium' | 'hard'

export type League = 'all' | 'NBA' | 'NFL'

export interface Player {
  id: string
  name: string
  // Minimal public player shape: only id, name and optional non-sensitive fields.
  // Do NOT include team/position/jerseyNumber/height/weight.
  league?: 'NBA' | 'NFL'
  imageUrl?: string
  // Only present once the answer is revealed
  college?: string
  collegeLogo?: string
}

export interface GameState {
  currentPlayer: Player | null
  difficulty: Difficulty
  guesses: string[]
  maxGuesses: number
  gameStatus: 'playing' | 'won' | 'lost'
  hints: string[]
  // Canonical "YYYY-MM-DD" date this challenge belongs to, as returned by the
  // backend's /game/daily-challenge `date` field. Null until a challenge has
  // been loaded. This is the source of truth for daily persistence/streak
  // logic — never the browser's locally-computed date, which can disagree
  // with the server's when client and server are in different timezones.
  date: string | null
}

export interface DailyChallenge {
  date: string
  player: Player
  difficulty: Difficulty
  maxGuesses: number
}

export interface EndlessRound {
  player: Player
  hints: string[]
}

export interface MascotCollege {
  id: string
  mascot: string
  // Only present once the answer is revealed
  college?: string
  logo?: string
}

export interface MascotRound {
  college: MascotCollege
  hints: string[]
}

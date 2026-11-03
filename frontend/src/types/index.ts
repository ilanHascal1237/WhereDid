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

export interface Player {
  id: string
  name: string
  // Minimal public player shape: only id, name and optional non-sensitive fields.
  // Do NOT include team/position/league/jerseyNumber/height/weight.
  draftYear?: number
  imageUrl?: string
  college?: string
}

export interface GameState {
  currentPlayer: Player | null
  difficulty: 'easy' | 'medium' | 'hard'
  guesses: string[]
  gameStatus: 'playing' | 'won' | 'lost'
  hints: string[]
}

export interface DailyChallenge {
  date: string
  player: Player
  difficulty: 'easy' | 'medium' | 'hard'
}

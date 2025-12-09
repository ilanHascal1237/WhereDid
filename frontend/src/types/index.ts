export interface Player {
  id: string
  name: string
  team: string
  position: string
  league: 'NBA' | 'NFL'
  jerseyNumber: number
  draftYear: number
  imageUrl?: string
  height?: string
  weight?: number
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

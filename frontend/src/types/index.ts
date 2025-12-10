export interface Player {
  id: string
  name: string
  team: string
  // The UI only requires name and team; other fields are optional and may be
  // omitted by the API to avoid revealing the answer (college).
  position?: string
  league?: 'NBA' | 'NFL' | string
  jerseyNumber?: number
  draftYear?: number
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

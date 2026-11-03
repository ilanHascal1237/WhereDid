import axios from 'axios'
import {
  Player,
  DailyChallenge,
  Difficulty,
  League,
  EndlessRound,
  MascotRound,
  MascotCollege,
} from '../types'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const gameService = {
  /**
   * Get the daily challenge player (today unless a YYYY-MM-DD date is given)
   */
  getTodaysChallenge: async (difficulty: Difficulty, date?: string): Promise<DailyChallenge> => {
    const response = await api.get('/game/daily-challenge', {
      params: date ? { date, difficulty } : { difficulty },
    })
    return response.data
  },

  /**
   * Get hints for the current player based on difficulty
   */
  getHints: async (playerId: string, difficulty: string): Promise<string[]> => {
    const response = await api.get(`/game/hints/${playerId}`, {
      params: { difficulty },
    })
    return response.data.hints
  },

  /**
   * Submit a guess for the current player
   */
  submitGuess: async (
    playerId: string,
    guessedCollege: string,
    difficulty: string
  ): Promise<{ correct: boolean; message: string; player?: Player }> => {
    const response = await api.post('/game/guess', {
      player_id: playerId,
      guessed_college: guessedCollege,
      difficulty,
    })
    return response.data
  },

  /**
   * Reveal a player's college once the round is over
   */
  revealAnswer: async (playerId: string): Promise<Player> => {
    const response = await api.get(`/game/reveal/${playerId}`)
    return response.data
  },

  /**
   * Get a random player for endless mode, skipping ids already seen
   */
  getEndlessPlayer: async (
    league: League,
    difficulty: Difficulty,
    exclude: string[]
  ): Promise<EndlessRound> => {
    const response = await api.get('/game/endless/next', {
      params: {
        difficulty,
        ...(league !== 'all' ? { league } : {}),
        ...(exclude.length ? { exclude: exclude.join(',') } : {}),
      },
    })
    return response.data
  },

  /**
   * Get a random college mascot to identify
   */
  getMascotRound: async (difficulty: Difficulty, exclude: string[]): Promise<MascotRound> => {
    const response = await api.get('/game/mascot/next', {
      params: { difficulty, ...(exclude.length ? { exclude: exclude.join(',') } : {}) },
    })
    return response.data
  },

  /**
   * Guess which school a mascot belongs to. The answer is always revealed.
   */
  submitMascotGuess: async (
    collegeId: string,
    guessedCollege: string,
    difficulty: Difficulty
  ): Promise<{ correct: boolean; college: MascotCollege }> => {
    const response = await api.post('/game/mascot/guess', {
      college_id: collegeId,
      guessed_college: guessedCollege,
      difficulty,
    })
    return response.data
  },

  /**
   * Search for players by name (for autocomplete)
   */
  searchPlayers: async (query: string): Promise<Player[]> => {
    const response = await api.get('/players/search', {
      params: { q: query },
    })
    return response.data.players
  },

  /**
   * Get player details by ID
   */
  getPlayerById: async (playerId: string): Promise<Player> => {
    const response = await api.get(`/players/${playerId}`)
    return response.data
  },

  /**
   * Get college suggestions for type-ahead. Returns { colleges: string[] }
   */
  getColleges: async (query: string): Promise<string[]> => {
    const response = await api.get('/players/colleges', {
      params: query ? { q: query } : {},
    })
    return response.data.colleges || []
  },
}

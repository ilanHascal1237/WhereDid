import axios from 'axios'
import { Player, DailyChallenge } from '../types'

const API_BASE_URL = 'http://127.0.0.1:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const gameService = {
  /**
   * Get today's daily challenge player
   */
  getTodaysChallenge: async (date?: string): Promise<DailyChallenge> => {
    const response = await api.get('/game/daily-challenge', {
      params: date ? { date } : {},
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
  ): Promise<any> => {
    const response = await api.post('/game/guess', {
      player_id: playerId,
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

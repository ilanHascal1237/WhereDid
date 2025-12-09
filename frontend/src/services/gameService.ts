import axios from 'axios'
import { Player, DailyChallenge } from '../types'

const API_BASE_URL = '/api'

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
  getTodaysChallenge: async (): Promise<DailyChallenge> => {
    const response = await api.get('/game/daily-challenge')
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
    guessedPlayerName: string,
    difficulty: string
  ): Promise<{ correct: boolean; message: string }> => {
    const response = await api.post('/game/guess', {
      player_id: playerId,
      guessed_player_name: guessedPlayerName,
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
}

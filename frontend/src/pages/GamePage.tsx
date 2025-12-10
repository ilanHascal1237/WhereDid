import React, { useState, useEffect } from 'react'
import { gameService } from '../services/gameService'
import { GameState } from '../types'
import GameBoard from '../components/GameBoard'
import './GamePage.css'

const GamePage: React.FC = () => {
  const [gameState, setGameState] = useState<GameState>({
    currentPlayer: null,
    difficulty: 'medium',
    guesses: [],
    gameStatus: 'playing',
    hints: [],
  })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadDailyChallenge()
  }, [])

  /**
   * Load a daily challenge. If `dateOrMode` is 'tomorrow', compute tomorrow's
   * date (YYYY-MM-DD). Otherwise, if a date string is provided, use it.
   */
  const loadDailyChallenge = async (dateOrMode?: string) => {
    try {
      setLoading(true)

      let targetDate: string | undefined = undefined
      if (dateOrMode === 'tomorrow') {
        const d = new Date()
        d.setDate(d.getDate() + 1)
        const yyyy = d.getFullYear()
        const mm = String(d.getMonth() + 1).padStart(2, '0')
        const dd = String(d.getDate()).padStart(2, '0')
        targetDate = `${yyyy}-${mm}-${dd}`
      } else if (dateOrMode) {
        targetDate = dateOrMode
      }

      const challenge = await gameService.getTodaysChallenge(targetDate)
      setGameState((prev) => ({
        ...prev,
        currentPlayer: challenge.player,
        difficulty: challenge.difficulty,
        guesses: [],
        gameStatus: 'playing',
      }))
      // Load initial hints
      const hints = await gameService.getHints(
        challenge.player.id,
        challenge.difficulty
      )
      setGameState((prev) => ({
        ...prev,
        hints,
      }))
    } catch (err) {
      setError("Failed to load today's challenge. Please try again.")
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleGuess = async (guessedCollege: string) => {
    if (!gameState.currentPlayer) return

    try {
      const result = await gameService.submitGuess(
        gameState.currentPlayer.id,
        guessedCollege,
        gameState.difficulty
      )

      if (result.correct) {
        // Update currentPlayer with returned player (includes college) so UI can reveal it
        setGameState((prev) => ({
          ...prev,
          currentPlayer: result.player || prev.currentPlayer,
          gameStatus: 'won',
        }))
      } else {
        setGameState((prev) => ({
          ...prev,
          guesses: [...prev.guesses, guessedCollege],
        }))
      }
    } catch (err) {
      console.error('Error submitting guess:', err)
    }
  }

  if (loading) {
    return <div className="game-page loading">Loading today's challenge...</div>
  }

  if (error) {
    return (
      <div className="game-page error">
        <p>{error}</p>
        <button onClick={() => loadDailyChallenge()}>Try Again</button>
      </div>
    )
  }

  return (
    <div className="game-page">
      <div className="game-container">
        <h1>WhereDid</h1>
        <p className="difficulty-badge">{gameState.difficulty.toUpperCase()}</p>
        <GameBoard
          gameState={gameState}
          onGuess={handleGuess}
          onNewGame={loadDailyChallenge}
        />
      </div>
    </div>
  )
}

export default GamePage

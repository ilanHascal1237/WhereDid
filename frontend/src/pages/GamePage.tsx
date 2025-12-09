import React, { useState, useEffect } from 'react'
import { gameService } from '../services/gameService'
import { Player, GameState } from '../types'
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

  const loadDailyChallenge = async () => {
    try {
      setLoading(true)
      const challenge = await gameService.getTodaysChallenge()
      setGameState((prev) => ({
        ...prev,
        currentPlayer: challenge.player,
        difficulty: challenge.difficulty,
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
      setError('Failed to load today\'s challenge. Please try again.')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleGuess = async (playerName: string) => {
    if (!gameState.currentPlayer) return

    try {
      const result = await gameService.submitGuess(
        gameState.currentPlayer.id,
        playerName,
        gameState.difficulty
      )

      if (result.correct) {
        setGameState((prev) => ({
          ...prev,
          gameStatus: 'won',
        }))
      } else {
        setGameState((prev) => ({
          ...prev,
          guesses: [...prev.guesses, playerName],
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
        <button onClick={loadDailyChallenge}>Try Again</button>
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

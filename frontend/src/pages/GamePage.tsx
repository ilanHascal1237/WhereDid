import React, { useState, useEffect } from 'react'
import { gameService } from '../services/gameService'
import { Difficulty, GameState } from '../types'
import GameBoard from '../components/GameBoard'
import OptionPicker, { DIFFICULTY_OPTIONS } from '../components/OptionPicker'
import { loadJSON, saveJSON } from '../services/storage'
import './GamePage.css'

interface GamePageProps {
  onSwitchMode: (mode: 'endless' | 'mascot') => void
}

interface Streak {
  count: number
  lastWonDate: string | null
}

const todayString = () => {
  const d = new Date()
  const mm = String(d.getMonth() + 1).padStart(2, '0')
  const dd = String(d.getDate()).padStart(2, '0')
  return `${d.getFullYear()}-${mm}-${dd}`
}

const yesterdayString = () => {
  const d = new Date()
  d.setDate(d.getDate() - 1)
  const mm = String(d.getMonth() + 1).padStart(2, '0')
  const dd = String(d.getDate()).padStart(2, '0')
  return `${d.getFullYear()}-${mm}-${dd}`
}

const dailyKey = (date: string) => `wheredid:daily:${date}`

const GamePage: React.FC<GamePageProps> = ({ onSwitchMode }) => {
  const today = todayString()
  const saved = loadJSON<GameState | null>(dailyKey(today), null)

  const [gameState, setGameState] = useState<GameState>(
    saved || {
      currentPlayer: null,
      difficulty: loadJSON<Difficulty>('wheredid:difficulty', 'medium'),
      guesses: [],
      maxGuesses: 4,
      gameStatus: 'playing',
      hints: [],
    }
  )
  const [streak, setStreak] = useState<Streak>(
    loadJSON<Streak>('wheredid:streak', { count: 0, lastWonDate: null })
  )
  const [loading, setLoading] = useState(!saved)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!saved) loadDailyChallenge(gameState.difficulty)
  }, [])

  // Persist progress so a refresh doesn't reset today's game
  useEffect(() => {
    if (gameState.currentPlayer) saveJSON(dailyKey(today), gameState)
  }, [gameState])

  /**
   * Load today's challenge at the given difficulty. Difficulty changes the
   * number of hints and guesses but not the player.
   */
  const loadDailyChallenge = async (difficulty: Difficulty) => {
    try {
      setLoading(true)
      setError(null)
      const challenge = await gameService.getTodaysChallenge(difficulty)
      const hints = await gameService.getHints(challenge.player.id, difficulty)
      setGameState((prev) => ({
        ...prev,
        currentPlayer: challenge.player,
        difficulty: challenge.difficulty,
        maxGuesses: challenge.maxGuesses,
        guesses: [],
        gameStatus: 'playing',
        hints,
      }))
    } catch (err: any) {
      setError(
        err?.response?.data?.detail || "Failed to load today's challenge. Please try again."
      )
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleDifficultyChange = (difficulty: Difficulty) => {
    saveJSON('wheredid:difficulty', difficulty)
    loadDailyChallenge(difficulty)
  }

  const recordWin = () => {
    if (streak.lastWonDate === today) return
    const next = {
      count: streak.lastWonDate === yesterdayString() ? streak.count + 1 : 1,
      lastWonDate: today,
    }
    setStreak(next)
    saveJSON('wheredid:streak', next)
  }

  const handleGuess = async (guessedCollege: string) => {
    if (!gameState.currentPlayer || gameState.gameStatus !== 'playing') return

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
          guesses: [...prev.guesses, guessedCollege],
          gameStatus: 'won',
        }))
        recordWin()
        return
      }

      const guesses = [...gameState.guesses, guessedCollege]
      if (guesses.length >= gameState.maxGuesses) {
        const answer = await gameService.revealAnswer(gameState.currentPlayer.id)
        setGameState((prev) => ({ ...prev, guesses, currentPlayer: answer, gameStatus: 'lost' }))
      } else {
        setGameState((prev) => ({ ...prev, guesses }))
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
        <button onClick={() => loadDailyChallenge(gameState.difficulty)}>Try Again</button>
      </div>
    )
  }

  const locked = gameState.guesses.length > 0 || gameState.gameStatus !== 'playing'

  return (
    <div className="game-page">
      <div className="game-container">
        <p className="mode-intro">
          Where did today's mystery player go to college?
          {streak.count > 0 && <span className="streak"> 🔥 {streak.count} day streak</span>}
        </p>
        <OptionPicker
          label="Difficulty"
          options={DIFFICULTY_OPTIONS}
          value={gameState.difficulty}
          onChange={handleDifficultyChange}
          disabled={locked}
        />
        <GameBoard gameState={gameState} onGuess={handleGuess} onSwitchMode={onSwitchMode} />
      </div>
    </div>
  )
}

export default GamePage

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

// Browser-local "today", used only as a best-effort cache-hit check on
// mount so a returning user gets an instant resume with no network flash in
// the common case (client and server agree on the date). It is NOT the
// source of truth for persistence or streak logic — the backend's
// `date` field (returned with every daily-challenge response) is, since the
// server and client clocks can disagree across timezones/midnight.
const todayString = () => {
  const d = new Date()
  const mm = String(d.getMonth() + 1).padStart(2, '0')
  const dd = String(d.getDate()).padStart(2, '0')
  return `${d.getFullYear()}-${mm}-${dd}`
}

const dailyKey = (date: string) => `wheredid:daily:${date}`

// Treat "YYYY-MM-DD" strings as plain calendar dates (no timezone attached)
// by parsing them as UTC, so comparing two server-provided dates doesn't
// depend on the browser's local clock or DST.
const parseCalendarDate = (date: string) => {
  const [y, m, d] = date.split('-').map(Number)
  return Date.UTC(y, m - 1, d)
}

const isNextCalendarDay = (prevDate: string, nextDate: string) => {
  const ONE_DAY_MS = 24 * 60 * 60 * 1000
  return parseCalendarDate(nextDate) - parseCalendarDate(prevDate) === ONE_DAY_MS
}

const GamePage: React.FC<GamePageProps> = ({ onSwitchMode }) => {
  // Best-effort guess at "today" for the synchronous cache-hit check below.
  // Reads under this key only hit when the saved game was itself written
  // under the server's canonical date for that day, which is what happens
  // whenever the client and server agreed on the date at save time (the
  // overwhelming majority of the time). A miss just falls through to a
  // normal fetch, which then re-keys everything off the server's `date`.
  const today = todayString()
  const saved = loadJSON<GameState | null>(dailyKey(today), null)

  const [gameState, setGameState] = useState<GameState>(
    saved
      ? // Back-compat: entries saved before `date` was tracked don't have
        // it. They were (by construction) saved under the local-today key,
        // so that key is the best available stand-in for their canonical date.
        { ...saved, date: saved.date || today }
      : {
          currentPlayer: null,
          difficulty: loadJSON<Difficulty>('wheredid:difficulty', 'medium'),
          guesses: [],
          maxGuesses: 4,
          gameStatus: 'playing',
          hints: [],
          date: null,
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

  // Persist progress so a refresh doesn't reset today's game. Keyed by the
  // server's canonical date (gameState.date) rather than the browser's
  // local date, so a client/server timezone mismatch can't cause this to
  // read back under the wrong key later.
  useEffect(() => {
    if (gameState.currentPlayer) saveJSON(dailyKey(gameState.date || today), gameState)
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
        // Server's canonical date for this challenge — the source of truth
        // for the storage key and streak logic below, not the client's guess.
        date: challenge.date,
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
    // gameState.date is the server's canonical date for the challenge just
    // won; today is only a fallback for the (shouldn't-happen) case a win
    // is recorded before any challenge has ever been loaded.
    const wonDate = gameState.date || today
    if (streak.lastWonDate === wonDate) return
    const next = {
      count: streak.lastWonDate && isNextCalendarDay(streak.lastWonDate, wonDate)
        ? streak.count + 1
        : 1,
      lastWonDate: wonDate,
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

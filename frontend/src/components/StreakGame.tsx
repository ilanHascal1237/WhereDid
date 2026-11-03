import React, { useEffect, useRef, useState } from 'react'
import CollegeInput from './CollegeInput'
import { loadJSON, saveJSON } from '../services/storage'
import './GameBoard.css'

export const STARTING_LIVES = 3

export interface StreakRound {
  id: string
  prompt: React.ReactNode
  hints: string[]
}

export interface StreakResult {
  correct: boolean
  // e.g. "Stephen Curry went to Davidson"
  answer: React.ReactNode
  logo?: string
}

interface StreakGameProps {
  // Distinguishes best scores per mode + settings, e.g. "endless:NBA:easy"
  bestScoreKey: string
  // Difficulty / league pickers shown before a run starts
  settings: React.ReactNode
  fetchRound: (seenIds: string[]) => Promise<StreakRound>
  // guess is null when the user skips
  checkGuess: (roundId: string, guess: string | null) => Promise<StreakResult>
}

type Phase = 'idle' | 'loading' | 'playing' | 'feedback' | 'over'

/**
 * Rapid-fire loop shared by endless and mascot modes: one guess per round,
 * a correct guess scores a point, a miss or skip costs a life.
 */
const StreakGame: React.FC<StreakGameProps> = ({
  bestScoreKey,
  settings,
  fetchRound,
  checkGuess,
}) => {
  const [phase, setPhase] = useState<Phase>('idle')
  const [round, setRound] = useState<StreakRound | null>(null)
  const [result, setResult] = useState<StreakResult | null>(null)
  const [score, setScore] = useState(0)
  const [lives, setLives] = useState(STARTING_LIVES)
  const [seenIds, setSeenIds] = useState<string[]>([])
  const [error, setError] = useState<string | null>(null)
  const [best, setBest] = useState(0)
  const nextButton = useRef<HTMLButtonElement>(null)

  const storageKey = `wheredid:best:${bestScoreKey}`

  // Settings changed: show their best score and go back to the start screen
  useEffect(() => {
    setBest(loadJSON<number>(storageKey, 0))
    setPhase('idle')
  }, [storageKey])

  useEffect(() => {
    if (phase === 'feedback') nextButton.current?.focus()
  }, [phase])

  const loadRound = async (seen: string[]) => {
    try {
      setPhase('loading')
      setError(null)
      const next = await fetchRound(seen)
      setRound(next)
      setSeenIds([...seen, next.id])
      setResult(null)
      setPhase('playing')
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Failed to load the next round.')
      console.error(err)
    }
  }

  const start = () => {
    setScore(0)
    setLives(STARTING_LIVES)
    loadRound([])
  }

  const handleGuess = async (guess: string | null) => {
    if (!round || phase !== 'playing') return
    try {
      const res = await checkGuess(round.id, guess)
      setResult(res)
      if (res.correct) {
        const nextScore = score + 1
        setScore(nextScore)
        if (nextScore > best) {
          setBest(nextScore)
          saveJSON(storageKey, nextScore)
        }
      } else {
        setLives((l) => l - 1)
      }
      setPhase('feedback')
    } catch (err) {
      console.error('Error submitting guess:', err)
    }
  }

  const handleNext = () => {
    if (lives <= 0) setPhase('over')
    else loadRound(seenIds)
  }

  const scoreboard = (
    <div className="scoreboard">
      <span>Score: <strong>{score}</strong></span>
      <span aria-label={`${lives} lives left`}>
        {'❤️'.repeat(Math.max(lives, 0))}
        {'🤍'.repeat(STARTING_LIVES - Math.max(lives, 0))}
      </span>
      <span>Best: <strong>{best}</strong></span>
    </div>
  )

  if (error) {
    return (
      <div className="game-board">
        <div className="status-message lost">
          <p>{error}</p>
          <button onClick={() => loadRound(seenIds)}>Try Again</button>
        </div>
      </div>
    )
  }

  if (phase === 'idle' || phase === 'over') {
    return (
      <div className="game-board">
        {settings}
        {phase === 'over' && (
          <div className="status-message lost">
            <h2>Game Over</h2>
            <p>
              You scored <strong>{score}</strong>
              {score > 0 && score >= best ? ' — a new best!' : ` (best: ${best})`}
            </p>
          </div>
        )}
        <button className="guess-button start-button" onClick={start}>
          {phase === 'over' ? 'Play Again' : 'Start'}
        </button>
        {phase === 'idle' && best > 0 && <p className="guesses-left">Best score: {best}</p>}
      </div>
    )
  }

  if (phase === 'loading' || !round) {
    return (
      <div className="game-board">
        {scoreboard}
        <p className="guesses-left">Loading...</p>
      </div>
    )
  }

  return (
    <div className="game-board">
      {scoreboard}
      {round.prompt}

      {round.hints.length > 0 && (
        <div className="hints-section">
          <div className="hints-list">
            {round.hints.map((hint, index) => (
              <div key={index} className="hint-item">
                {hint}
              </div>
            ))}
          </div>
        </div>
      )}

      {phase === 'feedback' && result && (
        <div className={`status-message ${result.correct ? 'won' : 'lost'}`}>
          <h2>{result.correct ? '✅ Correct!' : '❌ Not quite'}</h2>
          {result.logo && <img className="college-logo" src={result.logo} alt="" />}
          <p>{result.answer}</p>
          <button ref={nextButton} onClick={handleNext}>
            {lives > 0 ? 'Next' : 'See Results'}
          </button>
        </div>
      )}

      {phase === 'playing' && (
        <CollegeInput
          onSubmit={handleGuess}
          extraAction={
            <button type="button" className="skip-button" onClick={() => handleGuess(null)}>
              Skip
            </button>
          }
        />
      )}
    </div>
  )
}

export default StreakGame

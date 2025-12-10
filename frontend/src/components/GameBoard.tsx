import React, { useState, useEffect } from 'react'
import { GameState } from '../types'
import { gameService } from '../services/gameService'
import './GameBoard.css'

interface GameBoardProps {
  gameState: GameState
  // onGuess receives the user's guessed college for the current player
  onGuess: (guessedCollege: string) => void
  // onNewGame may accept an optional mode or date string (e.g. 'tomorrow' or '2025-12-10')
  onNewGame: (mode?: string) => void
}

const GameBoard: React.FC<GameBoardProps> = ({
  gameState,
  onGuess,
  onNewGame,
}) => {
  const [inputValue, setInputValue] = useState('')
  // Hints hidden by default per game rules
  const [showHints, setShowHints] = useState(false)
  const [displayedHints, setDisplayedHints] = useState<string[]>(gameState.hints)
  const [suggestions, setSuggestions] = useState<string[]>([])
  const [suggestionsVisible, setSuggestionsVisible] = useState(false)

  // debounce timer id
  let debounceTimer: number | undefined

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (inputValue.trim()) {
      onGuess(inputValue)
      setInputValue('')
      setSuggestions([])
      setSuggestionsVisible(false)
    }
  }

  const fetchSuggestions = (q: string) => {
    // clear any existing timer
    window.clearTimeout(debounceTimer)
    // debounce 250ms
    debounceTimer = window.setTimeout(async () => {
      if (!q || q.trim().length === 0) {
        setSuggestions([])
        setSuggestionsVisible(false)
        return
      }

      try {
        const cols = await (await import('../services/gameService')).gameService.getColleges(q)
        setSuggestions(cols)
        setSuggestionsVisible(cols.length > 0)
      } catch (err) {
        console.error('Error fetching college suggestions', err)
        setSuggestions([])
        setSuggestionsVisible(false)
      }
    }, 250)
  }

  const handleInputChange = (value: string) => {
    setInputValue(value)
    fetchSuggestions(value)
  }

  const handleSuggestionClick = (s: string) => {
    setInputValue(s)
    setSuggestions([])
    setSuggestionsVisible(false)
  }

  // Keep displayedHints in sync when gameState.hints changes (initial load)
  useEffect(() => {
    setDisplayedHints(gameState.hints)
  }, [gameState.hints])

  const toggleHints = async () => {
    // If turning hints on, fetch the full set (easy) so user sees all three college hints
    if (!showHints) {
      try {
        if (gameState.currentPlayer?.id) {
          const hints = await gameService.getHints(gameState.currentPlayer.id, 'easy')
          setDisplayedHints(hints)
        }
      } catch (err) {
        console.error('Error fetching hints:', err)
      }
    }
    setShowHints((s) => !s)
  }

  return (
    <div className="game-board">
      {/* Player display: show only name (team removed) */}
      <div className="player-card">
        <h2 className="player-name">{gameState.currentPlayer?.name}</h2>
        {/* team removed from UI per spec */}
      </div>

      {/* Hints Section */}
      <div className="hints-section">
        <div className="hints-header">
          <h2>Hints</h2>
          <button
            type="button"
            className="toggle-hints-button"
            onClick={toggleHints}
            aria-pressed={!showHints}
          >
            {showHints ? 'Hide' : 'Show'}
          </button>
        </div>

        {showHints && (
          <div className="hints-list">
            {displayedHints.map((hint, index) => (
              <div key={index} className="hint-item">
                {hint}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Guesses Section */}
      {gameState.guesses.length > 0 && (
        <div className="guesses-section">
          <h3>Previous Guesses ({gameState.guesses.length})</h3>
          <ul className="guesses-list">
            {gameState.guesses.map((guess, index) => (
              <li key={index}>{guess}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Game Status */}
      {gameState.gameStatus === 'won' && (
        <div className="status-message won">
          <h2>🎉 You got it!</h2>
          <p>
            {gameState.currentPlayer?.name} went to{' '}
            <strong>{gameState.currentPlayer?.college || '—'}</strong>
          </p>
          <button onClick={() => onNewGame('tomorrow')}>Play Tomorrow's Challenge</button>
        </div>
      )}

      {gameState.gameStatus === 'lost' && (
        <div className="status-message lost">
          <h2>Game Over</h2>
          <p>
            {gameState.currentPlayer?.name} went to{' '}
            <strong>{gameState.currentPlayer?.college || '—'}</strong>
          </p>
          <button onClick={() => onNewGame('tomorrow')}>Try Tomorrow's Challenge</button>
        </div>
      )}

      {/* Input Form */}
      {gameState.gameStatus === 'playing' && (
        <form className="guess-form" onSubmit={handleSubmit}>
          <div style={{ position: 'relative', flex: 1 }}>
            <input
              type="text"
              value={inputValue}
              onChange={(e) => handleInputChange(e.target.value)}
              placeholder="Enter college name..."
              className="guess-input"
              disabled={gameState.gameStatus !== 'playing'}
              autoComplete="off"
            />
            {suggestionsVisible && suggestions.length > 0 && (
              <div className="suggestions-list" role="listbox">
                {suggestions.map((s, i) => (
                  <div
                    key={i}
                    role="option"
                    tabIndex={0}
                    className="suggestion-item"
                    onMouseDown={(e) => e.preventDefault()} /* prevent input blur */
                    onClick={() => handleSuggestionClick(s)}
                  >
                    {s}
                  </div>
                ))}
              </div>
            )}
          </div>
          <button type="submit" className="guess-button">
            Guess
          </button>
        </form>
      )}
    </div>
  )
}

export default GameBoard

import React, { useState } from 'react'
import { GameState } from '../types'
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

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (inputValue.trim()) {
      onGuess(inputValue)
      setInputValue('')
    }
  }

  return (
    <div className="game-board">
      {/* Player display: show only name and (optionally) team */}
      <div className="player-card">
        <h2 className="player-name">{gameState.currentPlayer?.name}</h2>
        {gameState.currentPlayer?.team && (
          <p className="player-team">{gameState.currentPlayer.team}</p>
        )}
      </div>

      {/* Hints Section */}
      <div className="hints-section">
        <div className="hints-header">
          <h2>Hints</h2>
          <button
            type="button"
            className="toggle-hints-button"
            onClick={() => setShowHints((s) => !s)}
            aria-pressed={!showHints}
          >
            {showHints ? 'Hide' : 'Show'}
          </button>
        </div>

        {showHints && (
          <div className="hints-list">
            {gameState.hints.map((hint, index) => (
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
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Enter college name..."
            className="guess-input"
            disabled={gameState.gameStatus !== 'playing'}
          />
          <button type="submit" className="guess-button">
            Guess
          </button>
        </form>
      )}
    </div>
  )
}

export default GameBoard

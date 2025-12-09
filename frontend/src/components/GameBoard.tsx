import React, { useState } from 'react'
import { GameState } from '../types'
import './GameBoard.css'

interface GameBoardProps {
  gameState: GameState
  onGuess: (playerName: string) => void
  onNewGame: () => void
}

const GameBoard: React.FC<GameBoardProps> = ({
  gameState,
  onGuess,
  onNewGame,
}) => {
  const [inputValue, setInputValue] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (inputValue.trim()) {
      onGuess(inputValue)
      setInputValue('')
    }
  }

  return (
    <div className="game-board">
      {/* Hints Section */}
      <div className="hints-section">
        <h2>Hints</h2>
        <div className="hints-list">
          {gameState.hints.map((hint, index) => (
            <div key={index} className="hint-item">
              {hint}
            </div>
          ))}
        </div>
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
          <p>The player was {gameState.currentPlayer?.name}</p>
          <button onClick={onNewGame}>Play Tomorrow's Challenge</button>
        </div>
      )}

      {gameState.gameStatus === 'lost' && (
        <div className="status-message lost">
          <h2>Game Over</h2>
          <p>The player was {gameState.currentPlayer?.name}</p>
          <button onClick={onNewGame}>Try Tomorrow's Challenge</button>
        </div>
      )}

      {/* Input Form */}
      {gameState.gameStatus === 'playing' && (
        <form className="guess-form" onSubmit={handleSubmit}>
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Enter player name..."
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

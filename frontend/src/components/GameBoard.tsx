import React, { useState } from 'react'
import { GameState } from '../types'
import CollegeInput from './CollegeInput'
import PlayerCard from './PlayerCard'
import './GameBoard.css'

interface GameBoardProps {
  gameState: GameState
  // onGuess receives the user's guessed college for the current player
  onGuess: (guessedCollege: string) => void
  // Called from the end-of-game panel to jump to another mode
  onSwitchMode: (mode: 'endless' | 'mascot') => void
}

const GameBoard: React.FC<GameBoardProps> = ({ gameState, onGuess, onSwitchMode }) => {
  // Hints hidden by default per game rules
  const [showHints, setShowHints] = useState(false)
  const guessesLeft = gameState.maxGuesses - gameState.guesses.length
  const player = gameState.currentPlayer

  return (
    <div className="game-board">
      <PlayerCard player={player} />

      {/* Hints Section */}
      <div className="hints-section">
        <div className="hints-header">
          <h2>Hints</h2>
          <button
            type="button"
            className="toggle-hints-button"
            onClick={() => setShowHints((s) => !s)}
            aria-pressed={showHints}
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
      {gameState.gameStatus !== 'playing' && (
        <div className={`status-message ${gameState.gameStatus}`}>
          <h2>{gameState.gameStatus === 'won' ? '🎉 You got it!' : 'Game Over'}</h2>
          {player?.collegeLogo && (
            <img className="college-logo" src={player.collegeLogo} alt={player.college} />
          )}
          <p>
            {player?.name} went to <strong>{player?.college || '—'}</strong>
          </p>
          <p className="come-back">Come back tomorrow for a new player.</p>
          <div className="status-actions">
            <button onClick={() => onSwitchMode('endless')}>Play Endless Mode</button>
            <button onClick={() => onSwitchMode('mascot')}>Play Mascot Mode</button>
          </div>
        </div>
      )}

      {/* Input Form */}
      {gameState.gameStatus === 'playing' && (
        <>
          <p className="guesses-left">
            {guessesLeft} guess{guessesLeft === 1 ? '' : 'es'} left
          </p>
          <CollegeInput onSubmit={onGuess} />
        </>
      )}
    </div>
  )
}

export default GameBoard

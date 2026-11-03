import React, { useState } from 'react'
import { gameService } from '../services/gameService'
import { Difficulty } from '../types'
import StreakGame, { STARTING_LIVES } from '../components/StreakGame'
import OptionPicker, { DIFFICULTY_OPTIONS } from '../components/OptionPicker'
import { loadJSON, saveJSON } from '../services/storage'
import './GamePage.css'

const MascotPage: React.FC = () => {
  const [difficulty, setDifficulty] = useState<Difficulty>(
    loadJSON<Difficulty>('wheredid:mascot:difficulty', 'medium')
  )

  const settings = (
    <div className="settings-panel">
      <p className="mode-intro">
        Name the school behind each mascot. One guess each — you have {STARTING_LIVES} lives.
      </p>
      <OptionPicker
        label="Difficulty"
        options={DIFFICULTY_OPTIONS}
        value={difficulty}
        onChange={(v) => {
          setDifficulty(v)
          saveJSON('wheredid:mascot:difficulty', v)
        }}
      />
      <p className="settings-help">
        Easy: big programs + conference & colors · Medium: conference only · Hard: any school,
        mascot only. Shared mascots accept any school that fits the clues.
      </p>
    </div>
  )

  return (
    <div className="game-page">
      <div className="game-container">
        <StreakGame
          bestScoreKey={`mascot:${difficulty}`}
          settings={settings}
          fetchRound={async (seenIds) => {
            const round = await gameService.getMascotRound(difficulty, seenIds)
            return {
              id: round.college.id,
              prompt: (
                <div className="player-card">
                  <p className="mascot-label">Which school are the</p>
                  <h2 className="player-name">{round.college.mascot}?</h2>
                </div>
              ),
              hints: round.hints,
            }
          }}
          checkGuess={async (collegeId, guess) => {
            const { correct, college } = await gameService.submitMascotGuess(
              collegeId,
              guess || '',
              difficulty
            )
            return {
              correct: correct && !!guess,
              logo: college.logo,
              answer: (
                <>
                  {correct ? 'Yes — ' : ''}the {college.mascot} of <strong>{college.college}</strong>
                </>
              ),
            }
          }}
        />
      </div>
    </div>
  )
}

export default MascotPage

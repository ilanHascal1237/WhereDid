import React, { useState } from 'react'
import { gameService } from '../services/gameService'
import { Difficulty, League } from '../types'
import StreakGame, { STARTING_LIVES } from '../components/StreakGame'
import PlayerCard from '../components/PlayerCard'
import OptionPicker, { DIFFICULTY_OPTIONS } from '../components/OptionPicker'
import { loadJSON, saveJSON } from '../services/storage'
import './GamePage.css'

const LEAGUE_OPTIONS: { value: League; label: string }[] = [
  { value: 'all', label: 'NBA + NFL' },
  { value: 'NBA', label: 'NBA' },
  { value: 'NFL', label: 'NFL' },
]

const EndlessPage: React.FC = () => {
  const [league, setLeague] = useState<League>(loadJSON<League>('wheredid:endless:league', 'all'))
  const [difficulty, setDifficulty] = useState<Difficulty>(
    loadJSON<Difficulty>('wheredid:endless:difficulty', 'medium')
  )

  const settings = (
    <div className="settings-panel">
      <p className="mode-intro">
        Guess the college for as many players as you can. One guess each —
        you have {STARTING_LIVES} lives.
      </p>
      <OptionPicker
        label="League"
        options={LEAGUE_OPTIONS}
        value={league}
        onChange={(v) => {
          setLeague(v)
          saveJSON('wheredid:endless:league', v)
        }}
      />
      <OptionPicker
        label="Difficulty"
        options={DIFFICULTY_OPTIONS}
        value={difficulty}
        onChange={(v) => {
          setDifficulty(v)
          saveJSON('wheredid:endless:difficulty', v)
        }}
      />
      <p className="settings-help">
        Easy: veterans + 3 hints · Medium: 2 hints · Hard: anyone, 1 hint
      </p>
    </div>
  )

  return (
    <div className="game-page">
      <div className="game-container">
        <StreakGame
          bestScoreKey={`endless:${league}:${difficulty}`}
          settings={settings}
          fetchRound={async (seenIds) => {
            const round = await gameService.getEndlessPlayer(league, difficulty, seenIds)
            return {
              id: round.player.id,
              prompt: <PlayerCard player={round.player} />,
              hints: round.hints,
            }
          }}
          checkGuess={async (playerId, guess) => {
            let correct = false
            let player = null
            if (guess) {
              const result = await gameService.submitGuess(playerId, guess, difficulty)
              correct = result.correct
              player = result.player || null
            }
            player = player || (await gameService.revealAnswer(playerId))
            return {
              correct,
              logo: player.collegeLogo,
              answer: (
                <>
                  {player.name} went to <strong>{player.college}</strong>
                </>
              ),
            }
          }}
        />
      </div>
    </div>
  )
}

export default EndlessPage

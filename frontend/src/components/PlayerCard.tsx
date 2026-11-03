import React from 'react'
import { Player } from '../types'

interface PlayerCardProps {
  player: Player | null
}

/**
 * Headshot, name and league for the mystery player. Team is intentionally
 * not shown.
 */
const PlayerCard: React.FC<PlayerCardProps> = ({ player }) => {
  if (!player) return null
  return (
    <div className="player-card">
      {player.imageUrl && (
        <img className="player-headshot" src={player.imageUrl} alt={player.name} />
      )}
      <h2 className="player-name">{player.name}</h2>
      {player.league && <span className="league-tag">{player.league}</span>}
    </div>
  )
}

export default PlayerCard

import { useState } from 'react'
import './App.css'
import GamePage from './pages/GamePage.tsx'
import EndlessPage from './pages/EndlessPage.tsx'
import MascotPage from './pages/MascotPage.tsx'
import OptionPicker from './components/OptionPicker'
import { loadJSON, saveJSON } from './services/storage'

type Mode = 'daily' | 'endless' | 'mascot'

const MODE_OPTIONS: { value: Mode; label: string }[] = [
  { value: 'daily', label: 'Daily' },
  { value: 'endless', label: 'Endless' },
  { value: 'mascot', label: 'Mascot' },
]

function App() {
  const [mode, setMode] = useState<Mode>(loadJSON<Mode>('wheredid:mode', 'daily'))

  const switchMode = (next: Mode) => {
    setMode(next)
    saveJSON('wheredid:mode', next)
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>WhereDid</h1>
        <OptionPicker label="Game mode" options={MODE_OPTIONS} value={mode} onChange={switchMode} />
      </header>
      {mode === 'daily' && <GamePage onSwitchMode={switchMode} />}
      {mode === 'endless' && <EndlessPage />}
      {mode === 'mascot' && <MascotPage />}
    </div>
  )
}

export default App

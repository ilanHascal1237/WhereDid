import React, { useEffect, useRef, useState } from 'react'
import { gameService } from '../services/gameService'

interface CollegeInputProps {
  onSubmit: (guessedCollege: string) => void
  disabled?: boolean
  submitLabel?: string
  // Optional secondary action rendered next to the submit button (e.g. Skip)
  extraAction?: React.ReactNode
}

/**
 * College name input with type-ahead suggestions from the backend.
 */
const CollegeInput: React.FC<CollegeInputProps> = ({
  onSubmit,
  disabled = false,
  submitLabel = 'Guess',
  extraAction,
}) => {
  const [inputValue, setInputValue] = useState('')
  const [suggestions, setSuggestions] = useState<string[]>([])
  const debounceTimer = useRef<number | undefined>(undefined)
  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    if (!disabled) inputRef.current?.focus()
  }, [disabled])

  useEffect(() => () => window.clearTimeout(debounceTimer.current), [])

  const fetchSuggestions = (q: string) => {
    window.clearTimeout(debounceTimer.current)
    // debounce 250ms
    debounceTimer.current = window.setTimeout(async () => {
      if (!q.trim()) {
        setSuggestions([])
        return
      }
      try {
        setSuggestions((await gameService.getColleges(q)).slice(0, 8))
      } catch (err) {
        console.error('Error fetching college suggestions', err)
        setSuggestions([])
      }
    }, 250)
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (inputValue.trim()) {
      window.clearTimeout(debounceTimer.current)
      onSubmit(inputValue.trim())
      setInputValue('')
      setSuggestions([])
    }
  }

  const handleInputChange = (value: string) => {
    setInputValue(value)
    fetchSuggestions(value)
  }

  const handleSuggestionClick = (s: string) => {
    setInputValue(s)
    setSuggestions([])
    inputRef.current?.focus()
  }

  return (
    <form className="guess-form" onSubmit={handleSubmit}>
      <div className="guess-input-wrapper">
        <input
          ref={inputRef}
          type="text"
          value={inputValue}
          onChange={(e) => handleInputChange(e.target.value)}
          placeholder="Enter college name..."
          className="guess-input"
          disabled={disabled}
          autoComplete="off"
        />
        {suggestions.length > 0 && (
          <div className="suggestions-list" role="listbox">
            {suggestions.map((s) => (
              <div
                key={s}
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
      <button type="submit" className="guess-button" disabled={disabled}>
        {submitLabel}
      </button>
      {extraAction}
    </form>
  )
}

export default CollegeInput

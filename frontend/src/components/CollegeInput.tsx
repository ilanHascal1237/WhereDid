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
 * College name input with type-ahead suggestions. The full college list is
 * fetched once (cached in gameService) and filtered client-side, so typing
 * never hits the network.
 */
const CollegeInput: React.FC<CollegeInputProps> = ({
  onSubmit,
  disabled = false,
  submitLabel = 'Guess',
  extraAction,
}) => {
  const [inputValue, setInputValue] = useState('')
  const [suggestions, setSuggestions] = useState<string[]>([])
  const allColleges = useRef<string[]>([])
  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    if (!disabled) inputRef.current?.focus()
  }, [disabled])

  useEffect(() => {
    gameService
      .getAllColleges()
      .then((colleges) => {
        allColleges.current = colleges
      })
      .catch((err) => console.error('Error loading college list', err))
  }, [])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (inputValue.trim()) {
      onSubmit(inputValue.trim())
      setInputValue('')
      setSuggestions([])
    }
  }

  const handleInputChange = (value: string) => {
    setInputValue(value)
    const q = value.trim().toLowerCase()
    if (!q) {
      setSuggestions([])
      return
    }
    setSuggestions(
      allColleges.current.filter((c) => c.toLowerCase().includes(q)).slice(0, 8)
    )
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

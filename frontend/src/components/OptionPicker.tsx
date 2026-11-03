import { Difficulty } from '../types'

interface OptionPickerProps<T extends string> {
  label: string
  options: { value: T; label: string }[]
  value: T
  onChange: (value: T) => void
  disabled?: boolean
}

/**
 * Segmented control used for difficulty, league and mode selection.
 */
function OptionPicker<T extends string>({
  label,
  options,
  value,
  onChange,
  disabled = false,
}: OptionPickerProps<T>) {
  return (
    <div className="option-picker" role="radiogroup" aria-label={label}>
      {options.map((o) => (
        <button
          key={o.value}
          type="button"
          role="radio"
          aria-checked={o.value === value}
          className={`option-button${o.value === value ? ' selected' : ''}`}
          onClick={() => onChange(o.value)}
          disabled={disabled}
        >
          {o.label}
        </button>
      ))}
    </div>
  )
}

export const DIFFICULTY_OPTIONS: { value: Difficulty; label: string }[] = [
  { value: 'easy', label: 'Easy' },
  { value: 'medium', label: 'Medium' },
  { value: 'hard', label: 'Hard' },
]

export default OptionPicker

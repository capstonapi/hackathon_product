import { useEffect, useState } from 'react'

import { TYPEWRITER_CHARS_PER_TICK, TYPEWRITER_TICK_MS } from '../services/chatStatusSequence'

export function useTypewriter(fullText: string, enabled: boolean): string {
  const [visibleLength, setVisibleLength] = useState(enabled ? 0 : fullText.length)

  useEffect(() => {
    if (!enabled) {
      setVisibleLength(fullText.length)
      return
    }
    setVisibleLength(0)
    const timer = setInterval(() => {
      setVisibleLength((current) => {
        const next = current + TYPEWRITER_CHARS_PER_TICK
        if (next >= fullText.length) {
          clearInterval(timer)
          return fullText.length
        }
        return next
      })
    }, TYPEWRITER_TICK_MS)
    return () => clearInterval(timer)
  }, [fullText, enabled])

  return fullText.slice(0, visibleLength)
}

import { useEffect, useState } from 'react'

import { RETRIEVAL_STATUS_INTERVAL_MS, RETRIEVAL_STATUS_STEPS } from '../services/chatStatusSequence'

export function useRetrievalStatus(active: boolean): string | null {
  const [index, setIndex] = useState(0)

  useEffect(() => {
    if (!active) {
      setIndex(0)
      return
    }
    const timer = setInterval(() => {
      setIndex((current) => (current + 1) % RETRIEVAL_STATUS_STEPS.length)
    }, RETRIEVAL_STATUS_INTERVAL_MS)
    return () => clearInterval(timer)
  }, [active])

  return active ? RETRIEVAL_STATUS_STEPS[index] : null
}

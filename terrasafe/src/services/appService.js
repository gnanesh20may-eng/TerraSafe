export function getStored(key, fallback) {
  try {
    const value = window.localStorage.getItem(key)
    return value ? JSON.parse(value) : fallback
  } catch {
    return fallback
  }
}

export function setStored(key, value) {
  try {
    window.localStorage.setItem(key, JSON.stringify(value))
  } catch {
    return false
  }
  return true
}

export async function getAreaAssessment(area) {
  return { area: area.name, risk: area.risk, signals: [], updatedAt: new Date().toISOString() }
}
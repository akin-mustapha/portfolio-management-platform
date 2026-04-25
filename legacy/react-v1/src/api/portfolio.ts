import client from './client'

export async function fetchPortfolioSummary() {
  const { data } = await client.get('/portfolio/summary')
  return data
}

export async function fetchPortfolioHistory(from?: string, to?: string) {
  const params: Record<string, string> = {}
  if (from) params.from = from
  if (to) params.to = to
  const { data } = await client.get('/portfolio/history', { params })
  return data
}

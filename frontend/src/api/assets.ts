import client from './client'

export async function fetchAssets(tags?: string[]) {
  const params: Record<string, string> = {}
  if (tags && tags.length > 0) params.tags = tags.join(',')
  const { data } = await client.get('/assets', { params })
  return data
}

export async function fetchAssetHistory(ticker: string, from?: string, to?: string) {
  const params: Record<string, string> = {}
  if (from) params.from = from
  if (to) params.to = to
  const { data } = await client.get(`/assets/${ticker}/history`, { params })
  return data
}

export async function fetchAssetProfile(ticker: string) {
  const { data } = await client.get(`/assets/${ticker}/profile`)
  return data
}

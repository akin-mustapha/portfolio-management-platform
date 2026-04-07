import client from './client'

export async function fetchCredentials() {
  const { data } = await client.get('/credentials')
  return data
}

export async function saveCredentials(payload: {
  api_key: string
  secret_token?: string
  api_url?: string
}) {
  const { data } = await client.post('/credentials', payload)
  return data
}

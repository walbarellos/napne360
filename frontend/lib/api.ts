const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"

export async function apiFetch(
  path: string,
  options: RequestInit = {},
  token?: string
): Promise<Response> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  }
  if (token) headers["Authorization"] = `Bearer ${token}`

  return fetch(`${BASE}${path}`, { ...options, headers })
}

// helpers tipados
export async function apiGet<T>(path: string, token: string): Promise<T> {
  const r = await apiFetch(path, { method: "GET" }, token)
  if (!r.ok) throw new Error(`${r.status} ${path}`)
  return r.json()
}

export async function apiPost<T>(path: string, body: unknown, token?: string): Promise<T> {
  const r = await apiFetch(path, { method: "POST", body: JSON.stringify(body) }, token)
  if (!r.ok) throw new Error(`${r.status} ${path}`)
  return r.json()
}

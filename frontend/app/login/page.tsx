"use client"
import { useState } from "react"
import { useRouter } from "next/navigation"

export default function LoginPage() {
  const router = useRouter()
  const [matricula, setMatricula] = useState("")
  const [senha, setSenha]         = useState("")
  const [erro, setErro]           = useState("")
  const [carregando, setCarregando] = useState(false)

  async function entrar(e: React.FormEvent) {
    e.preventDefault()
    setErro("")
    setCarregando(true)
    try {
      const form = new URLSearchParams()
      form.append("username", matricula)
      form.append("password", senha)

      const r = await fetch("http://localhost:8000/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: form.toString(),
      })
      if (!r.ok) throw new Error()
      const { access_token } = await r.json()
      localStorage.setItem("napne_token", access_token)
      router.push("/dashboard")
    } catch {
      setErro("Matrícula ou senha incorretos. Tente novamente.")
    } finally {
      setCarregando(false)
    }
  }

  return (
    <div style={{
      minHeight: "100vh",
      background: "var(--bg)",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      padding: "24px",
    }}>
      <div style={{
        background: "var(--surface)",
        border: "1px solid var(--border)",
        borderRadius: "var(--radius)",
        padding: "48px",
        width: "100%",
        maxWidth: "440px",
        boxShadow: "0 4px 24px rgba(0,0,0,0.06)",
      }}>
        {/* Logo / cabeçalho */}
        <div style={{ textAlign: "center", marginBottom: "40px" }}>
          <div style={{
            width: 64, height: 64, borderRadius: 16,
            background: "var(--primary)", margin: "0 auto 16px",
            display: "flex", alignItems: "center", justifyContent: "center",
          }}>
            <span style={{ color: "#fff", fontSize: 28 }}>♿</span>
          </div>
          <h1 style={{ fontSize: 26, fontWeight: 700, color: "var(--primary)" }}>
            NAPNE 360°
          </h1>
          <p style={{ color: "var(--muted)", marginTop: 6, fontSize: 15 }}>
            Sistema de Apoio ao Estudante PCD
          </p>
        </div>

        <form onSubmit={entrar}>
          {/* Matrícula */}
          <div style={{ marginBottom: 20 }}>
            <label style={{
              display: "block", fontWeight: 600,
              marginBottom: 8, fontSize: 16,
            }}>
              Matrícula
            </label>
            <input
              type="text"
              value={matricula}
              onChange={e => setMatricula(e.target.value)}
              placeholder="Digite sua matrícula"
              required
              autoComplete="username"
              style={{
                width: "100%", padding: "12px 16px",
                border: "2px solid var(--border)",
                borderRadius: 8, fontSize: 17,
                outline: "none", transition: "border-color 0.2s",
                background: "var(--surface)",
              }}
              onFocus={(e) => (e.target as HTMLInputElement).style.borderColor = "var(--primary)"}
              onBlur={(e) => (e.target as HTMLInputElement).style.borderColor = "var(--border)"}
            />
          </div>

          {/* Senha */}
          <div style={{ marginBottom: 28 }}>
            <label style={{
              display: "block", fontWeight: 600,
              marginBottom: 8, fontSize: 16,
            }}>
              Senha
            </label>
            <input
              type="password"
              value={senha}
              onChange={e => setSenha(e.target.value)}
              placeholder="Digite sua senha"
              required
              autoComplete="current-password"
              style={{
                width: "100%", padding: "12px 16px",
                border: "2px solid var(--border)",
                borderRadius: 8, fontSize: 17,
                outline: "none", transition: "border-color 0.2s",
                background: "var(--surface)",
              }}
              onFocus={(e) => (e.target as HTMLInputElement).style.borderColor = "var(--primary)"}
              onBlur={(e) => (e.target as HTMLInputElement).style.borderColor = "var(--border)"}
            />
          </div>

          {/* Erro */}
          {erro && (
            <div style={{
              background: "#FEF2F2", border: "1px solid #FECACA",
              borderRadius: 8, padding: "12px 16px",
              color: "var(--danger)", marginBottom: 20, fontSize: 15,
            }}>
              ⚠️ {erro}
            </div>
          )}

          <button
            type="submit"
            disabled={carregando}
            style={{
              width: "100%", padding: "14px",
              background: carregando ? "var(--muted)" : "var(--primary)",
              color: "#fff", border: "none", borderRadius: 8,
              fontSize: 17, fontWeight: 600, cursor: carregando ? "not-allowed" : "pointer",
              transition: "background 0.2s",
            }}
          >
            {carregando ? "Entrando..." : "Entrar"}
          </button>
        </form>

        <p style={{
          textAlign: "center", marginTop: 24,
          color: "var(--muted)", fontSize: 13,
        }}>
          IFAC — Campus Rio Branco
        </p>
      </div>
    </div>
  )
}

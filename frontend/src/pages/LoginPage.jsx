import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { login } from "../api/auth";

export default function LoginPage() {
  const navigate = useNavigate();

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();

    setErrorMessage("");
    setIsSubmitting(true);

    try {
      await login(username, password);
      navigate("/listings", { replace: true });
    } catch (error) {
      const apiMessage =
        error.response?.data?.detail ||
        error.response?.data?.message ||
        "نام کاربری یا رمز عبور صحیح نیست.";

      setErrorMessage(apiMessage);
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className="auth-page">
      <section className="login-card">
        <div className="brand">
          <span className="brand-mark">م</span>
          <div>
            <h1>ملک‌یار</h1>
            <p>سامانه مدیریت فایل‌های ملکی</p>
          </div>
        </div>

        <h2>ورود به سامانه</h2>

        <form onSubmit={handleSubmit}>
          <label htmlFor="username">نام کاربری</label>
          <input
            id="username"
            type="text"
            value={username}
            onChange={(event) => setUsername(event.target.value)}
            autoComplete="username"
            required
            autoFocus
          />

          <label htmlFor="password">رمز عبور</label>
          <input
            id="password"
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            autoComplete="current-password"
            required
          />

          {errorMessage && (
            <div className="error-box" role="alert">
              {errorMessage}
            </div>
          )}

          <button type="submit" disabled={isSubmitting}>
            {isSubmitting ? "در حال ورود…" : "ورود"}
          </button>
        </form>
      </section>
    </main>
  );
}

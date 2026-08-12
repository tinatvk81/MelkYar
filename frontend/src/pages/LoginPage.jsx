import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function LoginPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const { login, loading } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    try {
      await login(username, password);
      navigate("/listings");
    } catch (err) {
      const responseData = err.response?.data;

      const detail =
        responseData?.detail ||
        responseData?.error ||
        responseData?.message ||
        responseData?.non_field_errors?.[0] ||
        (typeof responseData === "string" ? responseData : null) ||
        "ورود ناموفق بود";

      setError(detail);
    }
  };

  return (
    <div className="page-center">
      <form className="card" onSubmit={handleSubmit}>
        <h1>ورود به MelkYar</h1>

        <label htmlFor="username">نام کاربری</label>
        <input
          id="username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          type="text"
          autoComplete="username"
        />

        <label htmlFor="password">رمز عبور</label>
        <input
          id="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          type="password"
          autoComplete="current-password"
        />

        {error && <div className="error">{error}</div>}

        <button type="submit" disabled={loading}>
          {loading ? "در حال ورود..." : "ورود"}
        </button>
      </form>
    </div>
  );
}

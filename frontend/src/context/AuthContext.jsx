import { createContext, useContext, useMemo, useState } from "react";
import client from "../api/client";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [tokens, setTokens] = useState(() => {
    const access = localStorage.getItem("access_token");
    const refresh = localStorage.getItem("refresh_token");

    if (!access || !refresh) {
      return null;
    }

    return { access, refresh };
  });

  const [loading, setLoading] = useState(false);

  const login = async (username, password) => {
    setLoading(true);
    try {
      const response = await client.post("/api/auth/login/", {
        username,
        password,
      });

      const { access, refresh } = response.data;

      localStorage.setItem("access_token", access);
      localStorage.setItem("refresh_token", refresh);
      setTokens({ access, refresh });

      return response.data;
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    setTokens(null);
  };

  const value = useMemo(
    () => ({
      user: null,
      loading,
      login,
      logout,
      isAuthenticated: !!tokens,
      isAdmin: false,
    }),
    [tokens, loading]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  return useContext(AuthContext);
}

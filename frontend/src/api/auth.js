import client from "./client";

export async function login(username, password) {
  const response = await client.post("/auth/login/", {
    username,
    password,
  });

  const { access, refresh } = response.data;

  localStorage.setItem("access_token", access);
  localStorage.setItem("refresh_token", refresh);

  return response.data;
}

export function logout() {
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
}

export function isAuthenticated() {
  return Boolean(localStorage.getItem("access_token"));
}

import { ReactNode, createContext, useContext, useEffect, useState } from "react";
import { login as loginRequest, setAuthToken } from "../services/api";

interface AuthContextState {
  isAuthenticated: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  token: string | null;
}

const AuthContext = createContext<AuthContextState | undefined>(undefined);

const ACCESS_TOKEN_KEY = "coldchain_access";

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [token, setToken] = useState<string | null>(() => localStorage.getItem(ACCESS_TOKEN_KEY));

  useEffect(() => {
    setAuthToken(token);
  }, [token]);

  const login = async (username: string, password: string) => {
    const response = await loginRequest(username, password);
    localStorage.setItem(ACCESS_TOKEN_KEY, response.access);
    setToken(response.access);
  };

  const logout = () => {
    localStorage.removeItem(ACCESS_TOKEN_KEY);
    setToken(null);
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated: Boolean(token), login, logout, token }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return ctx;
};


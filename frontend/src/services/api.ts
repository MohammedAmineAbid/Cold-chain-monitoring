import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000/api";

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
});

export const setAuthToken = (token: string | null) => {
  if (token) {
    apiClient.defaults.headers.common.Authorization = `Bearer ${token}`;
  } else {
    delete apiClient.defaults.headers.common.Authorization;
  }
};

export interface LoginResponse {
  access: string;
  refresh: string;
}

export const login = async (username: string, password: string): Promise<LoginResponse> => {
  const { data } = await apiClient.post<LoginResponse>("/token/", { username, password });
  return data;
};

export const fetchDashboard = async () => {
  const [measurements, alerts, tickets] = await Promise.all([
    apiClient.get("/measurements/?page_size=20"),
    apiClient.get("/alerts/?page_size=5"),
    apiClient.get("/tickets/?page_size=5"),
  ]);
  return {
    measurements: measurements.data.results ?? measurements.data,
    alerts: alerts.data.results ?? alerts.data,
    tickets: tickets.data.results ?? tickets.data,
  };
};


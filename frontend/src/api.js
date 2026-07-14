import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api";

const api = axios.create({
  baseURL: API_BASE_URL,
});

export const fetchTasks = () => api.get("/tasks/");
export const createTask = (title) => api.post("/tasks/", { title });
export const updateTask = (id, fields) => api.put(`/tasks/${id}/`, fields);
export const deleteTask = (id) => api.delete(`/tasks/${id}/`);

export default api;

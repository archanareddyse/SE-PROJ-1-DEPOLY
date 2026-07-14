import { useEffect, useState } from "react";
import TaskForm from "./components/TaskForm.jsx";
import TaskList from "./components/TaskList.jsx";
import { fetchTasks, createTask, updateTask, deleteTask } from "./api.js";

export default function App() {
  const [tasks, setTasks] = useState([]);
  const [source, setSource] = useState(null);
  const [error, setError] = useState(null);

  const loadTasks = async () => {
    try {
      const res = await fetchTasks();
      setTasks(res.data.tasks);
      setSource(res.data.source);
      setError(null);
    } catch (err) {
      setError("Could not reach the backend API. Is Django running on :8000?");
    }
  };

  useEffect(() => {
    loadTasks();
  }, []);

  const handleAdd = async (title) => {
    await createTask(title);
    loadTasks();
  };

  const handleToggle = async (task) => {
    await updateTask(task.id, { completed: !task.completed });
    loadTasks();
  };

  const handleDelete = async (id) => {
    await deleteTask(id);
    loadTasks();
  };

  return (
    <div className="container">
      <h1>Task Board</h1>
      <p className="subtitle">
        React + Django REST Framework + Redis cache + MongoDB Atlas
        {source && <span className="badge" style={{ marginLeft: 8 }}>list served from: {source}</span>}
      </p>

      {error && <p style={{ color: "#f87171" }}>{error}</p>}

      <TaskForm onAdd={handleAdd} />
      <TaskList tasks={tasks} onToggle={handleToggle} onDelete={handleDelete} />
    </div>
  );
}

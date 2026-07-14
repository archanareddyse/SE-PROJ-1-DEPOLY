export default function TaskList({ tasks, onToggle, onDelete }) {
  if (tasks.length === 0) {
    return <p style={{ color: "#64748b" }}>No tasks yet. Add one above.</p>;
  }

  return (
    <ul>
      {tasks.map((task) => (
        <li key={task.id} className={task.completed ? "completed" : ""}>
          <input
            type="checkbox"
            checked={task.completed}
            onChange={() => onToggle(task)}
          />
          <span>{task.title}</span>
          <button className="delete-btn" onClick={() => onDelete(task.id)}>
            Delete
          </button>
        </li>
      ))}
    </ul>
  );
}

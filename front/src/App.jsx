import { useState } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import {createBrowserRouter, RouterProvider, redirect} from "react-router-dom";
import Board from "./modules/Board.jsx";
import Register from "./modules/Register.jsx";
import Boardslist from "./modules/Boardslist.jsx";
import Layout from "./modules/Layout.jsx";
//ананас
function Home() {
  const [users, setUsers] = useState([]);
  const [form, setForm] = useState({
    name: "",
    password: "",
    email: "",
    photo: ""
  });
  const [deleteId, setDeleteId] = useState("");

  const fetchUsers = async () => {
    const res = await fetch("http://130.49.148.168:8448/users");
    const data = await res.json();
    setUsers(data);
  };

  const addUser = async () => {
    await fetch("http://130.49.148.168:8448/users", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(form)
    });
  };

  const deleteUser = async () => {
    await fetch(`http://130.49.148.168:8448/users/${deleteId}`, {
      method: "DELETE"
    });
  };

  return (
    <div className="container">
      <h2>Users panel</h2>

      <button onClick={fetchUsers}>Посмотреть всех пользователей</button>

      <div className="block">
        <h3>Добавить пользователя</h3>
        <input
          placeholder="Имя"
          onChange={(e) => setForm({ ...form, name: e.target.value })}
        />
        <input
          placeholder="Пароль"
          onChange={(e) => setForm({ ...form, password: e.target.value })}
        />
        <input
          placeholder="Почта"
          onChange={(e) => setForm({ ...form, email: e.target.value })}
        />
        {/* <input
          placeholder="Фото(не работает)"
          onChange={(e) => setForm({ ...form, photo: e.target.value })}
        /> */}

        <button onClick={addUser}>Добавить</button>
      </div>

      <div className="block">
        <h3>Удалить пользователя</h3>
        <input
          placeholder="id"
          value={deleteId}
          onChange={(e) => setDeleteId(e.target.value)}
        />
        <button onClick={deleteUser}>Удалить</button>
      </div>

      <div className="block">
        <h3>Список пользователей</h3>
        {users.map((u) => (
          <div key={u.id} className="user">
            {u.id} — {u.name}
          </div>
        ))}
      </div>

      <a href="/board">Открыть доску</a>
        <br/>
      <a href="/register">Регистрация</a>
      <br/>
      <a href="/temp">темп</a>
    </div>
  );
}

const router = createBrowserRouter([
  {
    path: "/",
    element: <Layout />, // теперь layout — это родительский route
    children: [
      {
        index: true,
        element: <Home />,
      },
      {
        path: "board/:address",
        loader: async ({ params }) => {
          const token = localStorage.getItem("token");

          const res = await fetch(`http://130.49.148.168:8448/boards/${params.address}`, {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          });

          if (!res.ok) {
            throw redirect("/");
          }
          console.log(params.address);

          return null;
        },
        element: <Board />,
      },
      {
        path: "register",
        element: <Register />,
      },
      {
        path: "temp",
        element: <Boardslist />,
      },
    ],
  },
]);

export default function App() {
  return <RouterProvider router={router} />;
}
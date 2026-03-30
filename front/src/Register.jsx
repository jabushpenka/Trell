import { useState } from 'react';
import {nanoid} from 'nanoid';
export default function Register() {
  const [isLogin, setIsLogin] = useState(true);
  const [login, setLogin] = useState('');
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState('');

  const email = nanoid(8) + "@" + nanoid(3);


  const handleSubmit = async (e) => {
    e.preventDefault();

    const url = isLogin
      ? 'http://130.49.148.168:8448/login'
      : 'http://130.49.148.168:8448/register';

    const res = await fetch(url, {
      method: 'POST',
      credentials: "include",
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_name: login, password: password, email})
    });

    const data = await res.json();

    if (!res.ok) {
      setMessage(data.detail || 'Ошибка');
      return;
    }

    if (isLogin) {
      localStorage.setItem('token', data.access_token);
      setMessage('ВХОД ВЫПОЛНЕН');
    } else {
      setMessage('РЕГИСТРАЦИЯ ВЫПОЛНЕНА');
      setIsLogin(true);
    }
  };

  return (
    <div style={{ maxWidth: 300, margin: '50px auto' }}>
      <h2>{isLogin ? 'Login' : 'Register'}</h2>

      <form onSubmit={handleSubmit}>
        <input
          value={login}
          onChange={(e) => setLogin(e.target.value)}
          placeholder="Login"
          required
        />
        <br />

        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Password"
          required
        />
        <br />

        <button type="submit">
          {isLogin ? 'Login' : 'Register'}
        </button>
      </form>

      <p onClick={() => setIsLogin(!isLogin)} style={{ cursor: 'pointer' }}>
        {isLogin ? 'Нет аккаунта?' : 'Есть аккаунт?'}
      </p>

      <p>{message}</p>
    </div>
  );
}
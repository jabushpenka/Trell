import { useState } from 'react';
import {nanoid} from 'nanoid';
import style from '../styles/Register.module.css'
import { createBoard } from '../api.jsx';
import { useNavigation } from '../hooks/Navigation.jsx';


export default function Register() {
  const [isLogin, setIsLogin] = useState(false);
  const [login, setLogin] = useState('');
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState('');
  const email = nanoid(8) + "@" + nanoid(3);
  const {openBoard} =  useNavigation();

  const handleSubmit = async (e) => {
    e.preventDefault();

    const url = isLogin
      ? 'http://130.49.148.168:8448/login'
      : 'http://130.49.148.168:8448/register';

    const res = await fetch(url, {
      method: 'POST',
      credentials: "include",
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(isLogin ? {login: login, pword: password} : { user_name: login, pword: password, email})
    });

    const data = await res.json();

    if (!res.ok) {
      setMessage(data.detail || 'Ошибка data');
      return;
    }

    const token = data.access_token

    localStorage.setItem('token', token);

    if (isLogin) {
      setMessage('ВХОД ВЫПОЛНЕН');
    } else {     
      setMessage('РЕГИСТРАЦИЯ ВЫПОЛНЕНА');
      const boardData = await createBoard(nanoid(10), login);
      const boardAddress = boardData.address;
      openBoard(boardAddress, login);
    }
  };

  const registerForm = () => {
    return (
      <>
      <div>
        <span>Регистрация</span>
        <div className={style.formcontainer}>
           <form className={style.form} onSubmit={handleSubmit}>
            <h3>Введите почту</h3>
            <input
              value={login}
              onChange={(e) => setLogin(e.target.value)}
              placeholder=""
              required
            />
            
            <h3>Придумайте пароль</h3>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder=""
              required
            />
            
            {/*Потом повторение пароля и допилиьт нормально блин*/}
            <button type="submit">
              Регистрация
            </button>
          </form>

        </div>
          <h3>Уже есть аккаунт? <span onClick={() => setIsLogin(prev => !prev)}>Авторизоваться</span></h3>
      </div>
      </>
      )
  }

  const loginForm = () => {
    return (
      <>
      <div>
        <span>Авторизация</span>
        <div className={style.formcontainer}>
           <form className={style.form} onSubmit={handleSubmit}>
            <h3>Введите почту</h3>
            <input
              value={login}
              onChange={(e) => setLogin(e.target.value)}
              placeholder=""
              required
            />
            
            <h3>Введите пароль</h3>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder=""
              required
            />
            
            {/*Потом повторение пароля и допилиьт нормально блин*/}
            <button type="submit">
              Вход
            </button>
          </form>

        </div>
          <h3>Нет аккаунта? <span onClick={() => setIsLogin(prev => !prev)}>Зарегистрироваться</span></h3>
      </div>
      </>
      )
  }
  
  return (
    <div className={style.container}>
      <h2>Добро пожаловать!</h2>

        {isLogin ? loginForm() : registerForm()}

      <p>{message}</p>
    </div>
  );
}

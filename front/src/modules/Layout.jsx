import { Outlet } from "react-router-dom";
import styles from "../styles/Header.module.css";

export default function Layout({ children }) {
  return (
    <div className="layout">

      <div className={styles.header}>
        <span>TROLL</span>
        <div className={styles.profile}>
          <span>Профиль</span>
        </div>
      </div>

      <div className="content">
        <Outlet />
      </div>

    </div>
  );
}
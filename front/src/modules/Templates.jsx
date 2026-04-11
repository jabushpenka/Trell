import styles from "../styles/Template.module.css";
import {nanoid} from "nanoid";
import {quickPresets} from "../examples/Templatecards.js"/*Пока что хардкод*/
import taskbutton from '../assets/task-button.svg';
export default function Templates(){
    /*Пока что хардкод*/
    const presetsList = quickPresets.map(preset => {
        return {...preset, id: nanoid(12)};
    })


    const taskList = (card) => {
        return (
        <ul className={styles.tasklist}>
                {card.tasks.map(task => (
                  <li key={nanoid(12)}>
                    <button>
                        <img src={taskbutton}/>
                    </button>
                    <span>
                        {task.text}
                    </span>
                  </li>
                ))}
              </ul>
        )
    }

    return (
        <div className={styles.presets}>
            <h2>Шаблоны</h2>
            {presetsList.map(card => (
                <div key={card.id} className={styles.card}>
                    <div className={styles.cardheader}>
                        <h2>{card.title}</h2>
                        {taskList(card)}
                    </div>
                </div>
            ))}
        </div>
    )
}
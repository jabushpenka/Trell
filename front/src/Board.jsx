import { useState, useEffect } from "react";
import {nanoid} from "nanoid";
import './Board.css';
import trashbold from './assets/trash-bold.svg';
import trashregular from './assets/trash-regular.svg';
import plus from './assets/plus.svg';
import add from './assets/add.svg';
import taskbuttondone from './assets/task-button-done.svg';
import taskbutton from './assets/task-button.svg';

export default function Board() {
  const [boardData,setBoardData] = useState({columns: []});

  useEffect(() => {
    fetch("http://130.49.148.168:8448/boards/228")
      .then(res => res.json())
      .then(data => setBoardData(data));
  }, []);

  const [newColumnName, setNewColumnName] = useState("");
  
  const [newCardColumnId, setNewCardColumnId] = useState(null);
  const [newCardName, setNewCardName] = useState("");
  
  const [newTaskIds, setNewTaskIds] = useState({ colId: null, cardId: null });
  const [newTaskText, setNewTaskText] = useState("");


  //добавление
  const addColumn = () => {
    if (!newColumnName.trim()) return;
    setBoardData(prev => {
      const newBoard = {...prev};
      newBoard.columns = [...newBoard.columns, {id: nanoid(),title: newColumnName, cards: []}];
      return newBoard;});

    setNewColumnName("");
  }

  const addCard = (colId) => {
    if (!newCardName.trim()) return;
    setBoardData(prev => {
      const newBoard = {...prev,
      columns: prev.columns.map(col => col.id === colId 
        ? {...col, cards: [...col.cards, {id: nanoid(), title: newCardName, tasks: []}]}
        : col)};

      return newBoard;})

    setNewCardName("");
    setNewCardColumnId(null);
  };
  
  const addTask = (colId, cardId) => {
    if (!newTaskText.trim()) return;
    setBoardData(prev => {
      const newBoard = {
        ...prev,
        columns: prev.columns.map(col => col.id === colId
          ? {...col, 
            cards: col.cards.map(card => card.id === cardId 
              ? {...card, tasks: [...card.tasks, {id: nanoid(), text: newTaskText, done: false}]}
              : card)}
          : col)}
      return newBoard;})
    setNewTaskText("");
    setNewTaskIds({ colId: null, cardId: null });
  };


  //удаление
  const removeColumn = (colId) => {
    setBoardData(prev => {
      const newBoard = {
        ...prev,
        columns: prev.columns.filter(column => column.id !== colId)
      };
      return newBoard;
    })
  };

  const removeCard = (colId,cardId) => {
    setBoardData(prev => {
      const newBoard = {
        ...prev,
        columns: prev.columns.map(col => col.id === colId
          ? {...col, cards: col.cards.filter(card => card.id !== cardId)}
          : col)
      }
      return newBoard;})
  }

  //другое
  const updateCardTitle = (colId, cardId, title) => {
    /*потом*/
  };

  const toggleTask = (colId, cardId, taskId) => {
    setBoardData(prev => {
      const newBoard = {
        ...prev,
        columns: prev.columns.map(col => col.id === colId
          ? {...col, 
            cards: col.cards.map(card => card.id === cardId 
              ? {...card,
                tasks: card.tasks.map(task => task.id === taskId ? {...task, done: !task.done} : task)}
              : card)}
          : col)
      };
      return newBoard;})
  };

  return (
    <div className="board">
      <div className="board-header">
        <input
          placeholder="Новая колонка"
          value={newColumnName}
          onChange={(e) => setNewColumnName(e.target.value)}
        />
        <button className="addcolumn" onClick={() => addColumn()}>Добавить колонку</button>
        <button className="addcolumn" onClick={async () => {
          await fetch("http://130.49.148.168:8448/boards/228",{
            method: "PUT",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify(boardData),
          })}}>Сохранить</button>
      </div>

      <div className="columns">
        {boardData.columns.map(col => (
          <div key={col.id} className="column">
            <div className="columnheader">
              <h2>{col.title}</h2>
              <button onClick={() => removeColumn(col.id)}><img src={trashbold}/></button>
            </div>
            {newCardColumnId === col.id ? (
              <div>
                <input
                  autoFocus
                  value={newCardName}
                  onChange={(e) => setNewCardName(e.target.value)}
                  placeholder="Название карточки"
                />
                <button className="addcard" onClick={() => addCard(col.id)}>Добавить</button>
              </div>
            ) : (
              <button onClick={() => setNewCardColumnId(col.id)}><img src={plus}/>Карточка</button>
            )}

            {col.cards.map(card => (
              <div key={card.id} className="card">
                <div className="cardheader">
                  <h3>{card.title}</h3>
                  <button onClick={() => removeCard(col.id,card.id)}><img src={trashregular}/></button>
                </div>
                {(newTaskIds.colId === col.id) && (newTaskIds.cardId === card.id) ? (
                  <div>
                    <input
                      autoFocus
                      value={newTaskText}
                      onChange={(e) => setNewTaskText(e.target.value)}
                      placeholder="Task"
                    />
                    <button className="addtask" onClick={() => addTask(col.id, card.id)}>Добавить</button>
                  </div>
                ) : (
                  <button onClick={() => setNewTaskIds({ colId: col.id, cardId: card.id })}>
                    <img src={add}/> добавить задание
                  </button>
                )}

                <ul className="tasklist">
                  {card.tasks.map(task => (
                    <li key={task.id}>
                      <button 
                        onClick={() => toggleTask(col.id, card.id, task.id)}>
                          <img src={task.done ? taskbuttondone : taskbutton}/>
                      </button>
                      <span className={task.done ? "done" : ""}>{task.text}</span>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        ))}
      </div>
    </div>
  );
}

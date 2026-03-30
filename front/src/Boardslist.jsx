import { useEffect, useState } from "react";

export default function Boardslist() {

    const [userName, setUserName] = useState('');
    const [boardsList, setBoardsList] = useState([]);

    const url = "http://130.49.148.168:8448/"
    const token = localStorage.getItem("token");
    useEffect(() => {fetch(url+"token", {
    method: "GET",
    headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`
    }
    })
    .then(res => res.json())
    .then(data => setUserName(data));}
    , []);

    // console.log(userName);
    console.log(url+"userboards/"+228)
    useEffect(() => {fetch(url+"userboards/"+228,{
        method: "GET",
        headers: {
            "Content-Type": "application/json"
        }
        })
        .then(res => res.json())
        .then(data => setBoardsList(data))
    }, []);

    return <>
        {boardsList.map(board => {<><a href={"http://130.49.148.168:8448/boards/"+board}>Доска {board}</a><br/></>})}
        <a href="">Создать доску</a>
    </>
}
import React, { useEffect, useState } from 'react'
import {
    useLocation
} from "react-router-dom";


function ClubPage() {

    const location = useLocation();
    let club = location.state.name;

    const [comments, setComments] = useState([])

    useEffect(() => {
        fetch("/api/" + club + "/comment")
            .then(res => res.json())
            .then((result) => {console.log(result);setComments(result)})
    }, [])

    function submitComment(e) {
        e.preventDefault();
        let comment = document.getElementById('comment').value.trim();
        if (comment === '') {
            alert('No empty comments! Include words/letters');
            return;
        }
        fetch("/api/" + club + "/comment", {
            credentials: 'include',
            method: 'POST',
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                text: comment
            })
        }).then(res => {
            if (res.status === 200) {
                res.json().then(json => {
                    let author = json.author;
                    setComments([...comments, {text:comment, author: author}]);
                })
            } else if (res.status === 401) {
                alert('Please login to comment')
            } else {
                alert('An error has occured')
            }
        })
    }

    return (
        <div className="container">
            <h1 style={{margin: "10px"}}>{club}</h1>
            <h4 style={{margin: "10px"}}>{location.state.description}</h4>
            <br></br>
            <h2 style={{margin: "10px"}}>Comments</h2>
            <span>
                <input style={{marginBottom:"30px", marginRight:"10px"}} type="text" id="comment" name="comment" placeholder="New comment"></input>
                <button type="button" className="btn btn-primary" onClick={submitComment}>Post comment</button>
            </span>
            {comments.map(comment => 
                <div style={{margin: "10px"}}>
                    <hr></hr>
                    <h3>{comment.author}</h3>
                    <p>{comment.text}</p>
                </div>)}
        </div>
    )
}

export default ClubPage
import React, { useEffect, useState } from 'react'
import styled from 'styled-components'

const Centered = styled.div`
    display: block;
    margin-left: auto;
    margin-right: auto;
`

function Submit() {
    const [tags, setTags] = useState([])

    useEffect(() => {
        fetch("http://localhost:5000/api/all_tags")
            .then(res => res.json())
            .then(result => setTags(result))
    }, [])

    function addTag() {
        let tag = document.getElementById('new_tag').value.trim()
        tag = tag.replace(/\w\S*/g, function(txt){return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();})
        if (tag !== '' && !tags.includes(tag)) {
            setTags([...tags, tag])
            document.getElementById('new_tag').value = ''
        }
    }

    return (
        <Centered className="col-md-6 mt-4">
            <form onSubmit={submitClub}>
                <div className="form-group">
                    <label for="name">Club name *</label>
                    <input type="text" className="form-control" id="name" name="name" placeholder="Locust Labs" required></input>
                </div>
                <br></br>
                <div className="form-group">
                    <label for="code">Club Code</label>
                    <input type="text" className="form-control" id="code" name="code" placeholder="Club code"></input>
                </div>
                <div className="form-group">
                    <label for="description">Club description</label>
                    <input type="text" className="form-control" id="description" name="description" placeholder="Club description"></input>
                </div>
                <div className="form-group">
                    <label for="email">Tags</label>
                    <select multiple className="form-control" id="tags" name="tags">
                        {tags.map(tag => <option>{tag}</option>)}
                    </select>
                </div>
                <span>
                    <input style={{marginBottom:"30px", marginRight:"10px"}} type="text" id="new_tag" name="new_tag" placeholder="New tag"></input>
                    <button type="button" className="btn btn-primary" onClick={addTag}>Add new tag</button>
                </span>
                <br></br>
                <button type="submit" className="btn btn-primary">Register club</button>
            </form>
        </Centered>
    )
}

// sends the POST request to the api clubs route to create club
// if successful, redirect back to home page
function submitClub(e) {
    e.preventDefault()
    let name = document.getElementById('name').value;
    let code = document.getElementById('code').value;
    let description = document.getElementById('description').value;
    // retrieves the selected tags
    let tags = Array.from(document.getElementById('tags').querySelectorAll("option:checked"), e => e.value);
    if (name.trim() === '') {
        alert('Not a valid name!')
    } else {
        fetch("http://localhost:5000/api/clubs", {
            credentials: 'include',
            method: 'POST',
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                name: name,
                code: code,
                description: description,
                tags: tags
            })
        }).then(res => {
                if (res.status === 200) {
                    window.location.href = '/'
                } else if (res.status === 401) {
                    alert('Please login to create a club')
                } else if (res.status === 400) {
                    alert('Club create failed. There is a duplicate field')
                } else {
                    alert('Club create failed')
                }
            })
    }
}

export default Submit
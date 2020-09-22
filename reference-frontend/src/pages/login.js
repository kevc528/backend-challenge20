import React from 'react'
import styled from 'styled-components'

const Centered = styled.div`
    display: block;
    margin-left: auto;
    margin-right: auto;
`

function Login() {

    // calls the API to attempt login, and if successful redirects to home
    function tryLogin(e) {
        e.preventDefault()
        let username = document.getElementById('username').value;
        let password = document.getElementById('password').value;
        fetch("/api/login", {
            credentials: 'include',
            method: 'POST',
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                username: username,
                password: password
            })
        }).then(res => {
            if (res.status === 200) {
                window.location.href = '/'
            } else {
                alert('Error logging in. Please verify credentials')
            }
        })
    }

    return (
        <Centered className="col-md-6 mt-4">
            <form onSubmit={tryLogin}>
                <div className="form-group">
                    <label for="username">Username</label>
                    <input type="text" className="form-control" id="username" name="username" placeholder="username" required></input>
                </div>
                <br></br>
                <div className="form-group">
                    <label for="password">Password</label>
                    <input type="password" className="form-control" id="password" name="password" placeholder="password" required></input>
                </div>
                <button type="submit" className="btn btn-primary">Login</button>
            </form>
        </Centered>
    )
}

export default Login
import React from 'react'
import styled from 'styled-components'

const Centered = styled.div`
    display: block;
    margin-left: auto;
    margin-right: auto;
`

function Signup() {

    // calls the API to attempt login, and if successful redirects to home
    function trySignup(e) {
        e.preventDefault()
        let name = document.getElementById('name').value;
        let email = document.getElementById('email').value;
        let username = document.getElementById('username').value;
        let password = document.getElementById('password').value;
        if (name.trim() === '' || username.trim() === '' || password.trim() === '') {
            alert('Characters are required in the required fields');
            return;
        }
        let confirmPassword = document.getElementById('confirm-password').value;
        if (password !== confirmPassword) {
            alert('Passwords must match');
            return;
        }
        let major = document.getElementById('major').value.trim();
        if (major == '') {
            major = null;
        }
        let year = parseInt(document.getElementById('grad-year').value);
        fetch("/api/signup", {
            credentials: 'include',
            method: 'POST',
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                username: username,
                name: name,
                password: password,
                email: email,
                year: year,
                major: major
            })
        }).then(res => {
            if (res.status === 200) {
                window.location.href = '/'
            } else {
                res.json().then(json => {
                    alert(json.message)
                })
            }
        })
    }

    return (
        <Centered className="col-md-6 mt-4">
            <form onSubmit={trySignup}>
                <div className="form-group">
                    <label for="name">Name *</label>
                    <input type="text" className="form-control" id="name" name="name" placeholder="name" required></input>
                </div>
                <div className="form-group">
                    <label for="email">Email *</label>
                    <input type="email" className="form-control" id="email" name="email" placeholder="email" required></input>
                </div>
                <div className="form-group">
                    <label for="username">Username *</label>
                    <input type="text" className="form-control" id="username" name="username" placeholder="username" required></input>
                </div>
                <div className="form-group">
                    <label for="password">Password *</label>
                    <input type="password" className="form-control" id="password" name="password" placeholder="password" required></input>
                </div>
                <div className="form-group">
                    <label for="confirm-password">Confirm Password *</label>
                    <input type="password" className="form-control" id="confirm-password" name="confirm-password" placeholder="confirm password" required></input>
                </div>
                <div className="form-group">
                    <label for="major">Major</label>
                    <input type="text" className="form-control" id="major" name="major" placeholder="major"></input>
                </div>
                <div className="form-group">
                    <label for="grad-year">Graduation Year</label>
                    <input type="number" className="form-control" id="grad-year" name="grad-year" placeholder="grad year"></input>
                </div>
                <button type="submit" className="btn btn-primary">Signup</button>
            </form>
        </Centered>
    )
}

export default Signup
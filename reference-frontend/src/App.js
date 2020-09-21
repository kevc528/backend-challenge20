import React from 'react'
import Home from './pages/home';
import Submit from './pages/submit';
import Login from './pages/login';
import {
    BrowserRouter as Router,
    Switch,
    Route,
    Link
} from "react-router-dom";

function App() {
    return (
        <Router>
            <section id="nav">
                <nav className="navbar navbar-expand-lg navbar-light bg-light">
                    <a className="navbar-brand" href="/">Locust Labs &ndash;</a>
                    <button className="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarSupportedContent" aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
                        <span className="navbar-toggler-icon"></span>
                    </button>

                    <div className="collapse navbar-collapse" id="navbarSupportedContent">
                        <ul className="navbar-nav mr-auto">
                            <li><Link className="nav-link" to="/">Home</Link></li>
                            <li><Link className="nav-link" to="/submit">Submit</Link></li>
                            <li><Link className="nav-link" to="/login">Login</Link></li>
                            <li><a style={{cursor: "pointer"}} className="nav-link" onClick={logout}>Logout</a></li>
                        </ul>
                    </div>
                </nav>
            </section>
            <Switch>
                <Route exact path="/">
                    <Home />
                </Route>
                <Route path="/submit">
                    <Submit />
                </Route>
                <Route path="/login">
                    <Login />
                </Route>
            </Switch>
        </Router>
    )
}

// logout of an account and redirect to home
function logout() {
    fetch("/api/logout")
        .then(res => {
            res.json().then(json => {
                alert(json.message)
                window.location.href = '/'
            })
        });
}

export default App;
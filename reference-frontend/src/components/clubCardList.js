import React, { useEffect, useState } from 'react'
import ClubCard from './clubCard'

function ClubCardList() {
    const [clubs, setClubs] = useState([])
    const [tag, setTag] = useState("")

    useEffect(() => {
        fetch("/api/clubs")
            .then(res => res.json())
            .then((result) => setClubs(result.clubs))
    }, [])

    function tagClicked(clickedTag) {
        if (tag === clickedTag) {
            allClubs()
        } else {
            fetch(`/api/clubs/${clickedTag}`)
                .then(res => res.json())
                .then((result) => {
                    setClubs(result.clubs)
                    setTag(clickedTag)
                })
        }
    }

    function allClubs() {
        fetch("/api/clubs")
            .then(res => res.json())
            .then((result) => {
                setClubs(result.clubs)
                setTag("")
            })
    }

    const headerStyle = {
        margin: '25px',
        color: 'grey'
    }

    const backStyle = {
        color: 'blue',
        cursor: 'pointer',
        margin: '25px'
    }

    return (
        <>
            {
                (tag !== "") &&
                <div>
                    <h1 style={headerStyle}>Clubs with the tag {tag}</h1>
                    <p style={backStyle} onClick={() => allClubs()}>Back to all clubs</p>
                </div>
            }
            <section id="clubs">
                {clubs.map((club, index) => {
                    return <ClubCard key={index} club={club} tagClicked={tagClicked} selectedTag={tag} />
                })}
            </section>
        </>
    )
}

export default ClubCardList
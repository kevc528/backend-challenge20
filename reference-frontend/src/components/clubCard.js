import React from 'react'
import styled from 'styled-components'
import {
    useHistory
} from "react-router-dom";

const ClubCardContainer = styled.div`
    position: relative;
    display: block;
    width: 420px;
    height: 450px;
    margin: 25px;
    float: left;
    padding: 15px;
    border: 1px solid #DDDDDD;
    border-radius: 15px;
`

const ClubDescription = styled.p`
    padding: 10px;
    display: block;
    height: 55%;
`

const ClubTitle = styled.h4`
    color: black;
    cursor: pointer;
    &:hover {
        text-decoration: underline;
    }
`

var selectedTag = "";

const ClubTags = styled.button.attrs(props => ({
    type: "button",
    className: "btn btn-outline-primary btn-rounded btn-sm btn-filter"
}))`
    margin-top: 10px;
    margin-right: 10px;
    border-radius: 15px;
    background: ${prop => prop.tag === selectedTag ? '#007bff' : '#FFFFFF'};
    color: ${prop => prop.tag === selectedTag ? '#FFFFFF': '#007bff'};
`

function ClubCard(props) {
    selectedTag = props.selectedTag;
    const history = useHistory()
    function redirectClub() {
        history.push(
           '/club/' + props.club.name,
            {
                name: props.club.name,
                description: props.club.description
            }
        )
    }
    return (
        <ClubCardContainer>
            <ClubTitle onClick={redirectClub}>{props.club.name}</ClubTitle>
            <hr></hr>
            <ClubDescription>{props.club.description}</ClubDescription>
            <section id="tags">
                {props.club.tags.map(tag => <ClubTags key={tag} tag={tag} onClick={() => props.tagClicked(tag)}>{tag}</ClubTags>)}
            </section>
        </ClubCardContainer>
    )
}

export default ClubCard
const userPics = [
    'elliot.jpg',
    'elyse.png',
    'helen.jpg',
    'jenny.jpg',
    'kristy.png',
    'matthew.png',
    'molly.png',
    'steve.jpg',
    'stevie.jpg',
]

const userPic = userPics[Math.floor(Math.random() * 100) % userPics.length]

function createMessage(user, msg) {
    // Create element nodes
    const message = document.createElement('div')
    const avatar = document.createElement('a')
    const image = document.createElement('img')
    const content = document.createElement('div')
    const author = document.createElement('a')
    const text = document.createElement('div')

    // Build them into a DOM tree
    message.appendChild(avatar)
    message.appendChild(content)
    avatar.appendChild(image)
    content.appendChild(author)
    content.appendChild(text)

    // Styles
    if (user) {
        message.style.textAlign = 'right'
        avatar.style.cssFloat = 'right'
        content.style.marginRight = '3.5em'
    }

    message.style.marginTop = '1em'

    // Setup each element
    message.className += 'comment'
    avatar.className += 'avatar'
    image.src = user ? 'static/' + userPic : '/static/trump.jpg'
    content.className += 'content'
    author.className += 'author'
    author.innerHTML = user ? '@you' : '@unrealDonaldTrump'
    text.className += 'text'
    text.innerHTML = msg

    return message
}

function createUserMessage(text) {
    return createMessage(true, text)
}

function createAgentMessage(text) {
    return createMessage(false, text)
}

function addMessage(user, text) {
    const container = document.getElementById('chat-container')
    let message = user ? createUserMessage(text) : createAgentMessage(text)
    container.appendChild(message)
    container.lastChild.scrollIntoView(false)
}

function addUserMessage(msg, delay) {
    window.setTimeout(() => { addMessage(true, msg) }, delay)
}

function addAgentMessage(msg, delay) {
    window.setTimeout(() => { addMessage(false, msg) }, delay)
}

function get(url, cb, message, delay) {
    const xhr = new XMLHttpRequest();
    xhr.open('GET', url + message)
    xhr.onload = function () {
        if (xhr.status === 200)
            cb(xhr.responseText, delay)
        else
            console.log('request failure: ' + xhr.status)
    }
    xhr.send()
}

function sendUserMessage() {
    const input = document.getElementById('user-input')
    const message = input.value
    addUserMessage(message, 500)
    get('/api/v1/trump/', addAgentMessage, message, 1800)
}

function init() {
    window.setTimeout(function () { addAgentMessage('What?') }, 1500)
    const button = document.getElementById('send-button')
    button.addEventListener('click', sendUserMessage)
}

document.onload = init()

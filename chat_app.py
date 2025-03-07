import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QUrl
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile
import threading
from flask import Flask, jsonify, request, render_template_string
import datetime
import json

app = Flask(__name__)

# Disable Jinja2 variable autoescaping for Vue.js
app.jinja_env.variable_start_string = '[['
app.jinja_env.variable_end_string = ']]'

class ChatAPI:
    def __init__(self):
        self.messages = []
        self.contacts = [
            {"id": 1, "name": "Alice", "status": "online", "last_message": "Hello! How are you?", "time": "10:30"},
            {"id": 2, "name": "Bob", "status": "online", "last_message": "Did you see the new update?", "time": "09:45"},
            {"id": 3, "name": "Charlie", "status": "offline", "last_message": "Meeting at 3 PM", "time": "Yesterday"}
        ]

    def send_message(self, message):
        timestamp = datetime.datetime.now().strftime("%H:%M")
        new_message = {
            "id": len(self.messages) + 1,
            "text": message,
            "sender": "user",
            "timestamp": timestamp
        }
        self.messages.append(new_message)
        return new_message

    def get_messages(self):
        return self.messages

    def get_contacts(self):
        return self.contacts

# Create API instance
chat_api = ChatAPI()

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/api/messages', methods=['GET', 'POST'])
def handle_messages():
    if request.method == 'POST':
        message = request.json.get('message')
        new_message = chat_api.send_message(message)
        # Simulate received message
        timestamp = datetime.datetime.now().strftime("%H:%M")
        echo_message = {
            "id": len(chat_api.messages) + 1,
            "text": f"Echo: {message}",
            "sender": "other",
            "timestamp": timestamp
        }
        chat_api.messages.append(echo_message)
        return jsonify({"sent": new_message, "received": echo_message})
    else:
        return jsonify(chat_api.get_messages())

@app.route('/api/contacts')
def handle_contacts():
    return jsonify(chat_api.get_contacts())

# HTML template with Vue.js
HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Secure Chat</title>
    <script src="https://unpkg.com/vue@3/dist/vue.global.js"></script>
    <script src="https://unpkg.com/axios/dist/axios.min.js"></script>
    <!-- Add emoji picker -->
    <link href="https://emoji-css.afeld.me/emoji.css" rel="stylesheet">
    <!-- Add waveform visualizer -->
    <script src="https://unpkg.com/wavesurfer.js"></script>
    <style>
        :root {
            --primary: #4171FF;
            --primary-light: #5C85FF;
            --secondary: #2D2D2D;
            --bg-dark: #1A1A1A;
            --bg-light: #2D2D2D;
            --text: #FFFFFF;
            --text-secondary: #A0A0A0;
            --success: #4CAF50;
            --error: #F44336;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }

        body {
            background: var(--bg-dark);
            color: var(--text);
            height: 100vh;
            display: flex;
        }

        .app {
            display: flex;
            width: 100%;
            height: 100%;
        }

        /* Enhanced sidebar */
        .sidebar {
            width: 300px;
            background: var(--bg-light);
            border-right: 1px solid #333;
            display: flex;
            flex-direction: column;
        }

        .profile {
            padding: 20px;
            border-bottom: 1px solid #333;
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .profile-avatar {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: var(--primary);
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
        }

        .status-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: var(--success);
            margin-right: 6px;
            display: inline-block;
        }

        .status-text {
            color: var(--text-secondary);
            font-size: 14px;
        }

        /* Enhanced contacts */
        .contacts {
            flex: 1;
            overflow-y: auto;
        }

        .contact {
            padding: 15px 20px;
            border-bottom: 1px solid #333;
            cursor: pointer;
            transition: all 0.3s;
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .contact:hover {
            background: rgba(255,255,255,0.05);
        }

        .contact.active {
            background: rgba(65, 113, 255, 0.1);
            border-left: 3px solid var(--primary);
        }

        .contact-info {
            flex: 1;
            min-width: 0;
        }

        .contact-name {
            font-weight: 500;
            margin-bottom: 4px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .contact-preview {
            font-size: 13px;
            color: var(--text-secondary);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        /* Enhanced chat area */
        .chat {
            flex: 1;
            display: flex;
            flex-direction: column;
            background: var(--bg-dark);
        }

        .chat-header {
            padding: 20px;
            background: var(--bg-light);
            border-bottom: 1px solid #333;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .chat-title {
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .chat-actions {
            display: flex;
            gap: 8px;
        }

        .action-button {
            padding: 8px;
            border-radius: 50%;
            border: none;
            background: rgba(255,255,255,0.1);
            color: var(--text);
            cursor: pointer;
            transition: all 0.3s;
        }

        .action-button:hover {
            background: rgba(255,255,255,0.2);
            transform: translateY(-1px);
        }

        /* Enhanced messages */
        .messages {
            flex: 1;
            padding: 20px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 10px;
            margin-bottom: 80px; /* Height of input area */
        }

        .message {
            max-width: 70%;
            padding: 12px 16px;
            border-radius: 18px;
            position: relative;
            animation: fadeIn 0.3s ease;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .message.sent {
            background: var(--primary);
            align-self: flex-end;
            border-bottom-right-radius: 5px;
        }

        .message.received {
            background: var(--secondary);
            align-self: flex-start;
            border-bottom-left-radius: 5px;
        }

        .message-time {
            font-size: 11px;
            color: rgba(255,255,255,0.7);
            margin-top: 4px;
        }

        .message-status {
            display: flex;
            align-items: center;
            gap: 4px;
            font-size: 12px;
            color: rgba(255,255,255,0.7);
        }

        /* Fixed position input area with controlled height */
        .input-area {
            position: fixed;
            bottom: 0;
            right: 0;
            left: 300px; /* Width of sidebar */
            background: var(--bg-light);
            padding: 15px 20px;
            border-top: 1px solid #333;
            display: flex;
            gap: 10px;
            height: 70px; /* Fixed height */
        }

        .input-wrapper {
            flex: 1;
            display: flex;
            background: var(--bg-dark);
            border-radius: 20px;
            padding: 8px 16px;
            position: relative;
            height: 40px; /* Fixed height */
            align-items: center;
        }

        /* Message input with scroll */
        .message-input {
            flex: 1;
            height: 24px;
            background: transparent;
            border: none;
            color: var(--text);
            font-size: 14px;
            padding: 0;
            overflow-x: hidden;
            white-space: nowrap;
            text-overflow: ellipsis;
        }

        .message-input:focus {
            outline: none;
        }

        /* Input actions */
        .input-actions {
            display: flex;
            gap: 8px;
            align-items: center;
            margin-left: 8px;
        }

        .action-button {
            background: none;
            border: none;
            color: var(--text);
            cursor: pointer;
            padding: 4px;
            font-size: 18px;
            opacity: 0.7;
            transition: all 0.2s;
        }

        .action-button:hover {
            opacity: 1;
        }

        /* Send button */
        .send-button {
            background: var(--primary);
            color: white;
            border: none;
            border-radius: 20px;
            padding: 8px 20px;
            font-size: 14px;
            cursor: pointer;
            transition: all 0.2s;
            height: 40px;
            white-space: nowrap;
        }

        /* Typing indicator */
        .typing-indicator {
            display: flex;
            gap: 4px;
            padding: 8px 12px;
            background: var(--bg-light);
            border-radius: 16px;
            width: fit-content;
            margin: 8px 0;
        }

        .typing-dot {
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background: var(--text-secondary);
            animation: typing 1.4s infinite;
        }

        .typing-dot:nth-child(2) { animation-delay: 0.2s; }
        .typing-dot:nth-child(3) { animation-delay: 0.4s; }

        @keyframes typing {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-4px); }
        }

        /* Message reactions */
        .message-reactions {
            display: flex;
            flex-wrap: wrap;
            gap: 4px;
            margin-top: 4px;
        }

        .reaction {
            background: rgba(255,255,255,0.1);
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 12px;
            cursor: pointer;
            transition: all 0.2s;
            display: flex;
            align-items: center;
            gap: 4px;
        }

        .reaction:hover {
            background: rgba(255,255,255,0.2);
            transform: scale(1.05);
        }

        .reaction.active {
            background: var(--primary);
        }

        /* File attachments */
        .attachment-preview {
            margin-top: 8px;
            background: rgba(255,255,255,0.1);
            border-radius: 8px;
            padding: 10px;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .attachment-icon {
            font-size: 24px;
        }

        .attachment-info {
            flex: 1;
        }

        .attachment-name {
            font-weight: 500;
            margin-bottom: 2px;
        }

        .attachment-size {
            font-size: 12px;
            color: var(--text-secondary);
        }

        /* Voice messages */
        .voice-message {
            width: 100%;
            padding: 10px;
            background: rgba(255,255,255,0.1);
            border-radius: 8px;
            margin-top: 8px;
        }

        .voice-controls {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 8px;
        }

        .voice-button {
            background: none;
            border: none;
            color: var(--text);
            cursor: pointer;
            font-size: 20px;
            padding: 4px;
            border-radius: 50%;
            transition: all 0.2s;
        }

        .voice-button:hover {
            background: rgba(255,255,255,0.1);
        }

        .voice-waveform {
            height: 40px;
            background: rgba(255,255,255,0.05);
            border-radius: 4px;
        }

        /* Search bar */
        .search-bar {
            padding: 10px 20px;
            border-bottom: 1px solid #333;
        }

        .search-input {
            width: 100%;
            padding: 8px 12px;
            background: var(--bg-dark);
            border: 1px solid #444;
            border-radius: 8px;
            color: var(--text);
            font-size: 14px;
        }

        .search-input:focus {
            outline: none;
            border-color: var(--primary);
        }

        /* Fixed position emoji picker */
        .emoji-picker {
            position: fixed;
            bottom: 80px; /* Height of input area + padding */
            right: 20px;
            background: var(--bg-light);
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            padding: 10px;
            display: grid;
            grid-template-columns: repeat(8, 1fr);
            gap: 4px;
            z-index: 1000;
        }

        .emoji-item {
            padding: 4px;
            cursor: pointer;
            border-radius: 4px;
            transition: all 0.2s;
        }

        .emoji-item:hover {
            background: rgba(255,255,255,0.1);
            transform: scale(1.1);
        }

        /* Message context menu */
        .context-menu {
            position: absolute;
            background: var(--bg-light);
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            padding: 4px;
            z-index: 100;
        }

        .context-item {
            padding: 8px 12px;
            cursor: pointer;
            border-radius: 4px;
            display: flex;
            align-items: center;
            gap: 8px;
            transition: all 0.2s;
        }

        .context-item:hover {
            background: rgba(255,255,255,0.1);
        }

        /* Reply thread */
        .reply-thread {
            border-left: 2px solid var(--primary);
            padding-left: 12px;
            margin: 4px 0;
            font-size: 13px;
            color: var(--text-secondary);
        }

        /* Message status with typing */
        .message-typing {
            font-style: italic;
            color: var(--text-secondary);
            font-size: 13px;
            margin: 8px 0;
        }

        /* Enhanced scrollbar */
        ::-webkit-scrollbar {
            width: 6px;
        }

        ::-webkit-scrollbar-track {
            background: transparent;
        }

        ::-webkit-scrollbar-thumb {
            background: rgba(255,255,255,0.2);
            border-radius: 3px;
        }

        ::-webkit-scrollbar-thumb:hover {
            background: rgba(255,255,255,0.3);
        }
    </style>
</head>
<body>
    <div id="app" class="app">
        <div class="sidebar">
            <div class="profile">
                <div class="profile-avatar">U</div>
                <div class="profile-info">
                    <h2>User Name</h2>
                    <div class="status">
                        <span class="status-dot"></span>
                        <span class="status-text">Online</span>
                    </div>
                </div>
            </div>
            <div class="contacts">
                <div v-for="contact in contacts" 
                     :key="contact.id" 
                     class="contact"
                     :class="{ active: selectedContact === contact }"
                     @click="selectContact(contact)">
                    <div class="contact-avatar">{{ contact.name[0] }}</div>
                    <div class="contact-info">
                        <div class="contact-name">{{ contact.name }}</div>
                        <div class="contact-preview">
                            <span :class="['status-dot', contact.status]"></span>
                            {{ contact.last_message }}
                        </div>
                        <small class="contact-time">{{ contact.time }}</small>
                    </div>
                </div>
            </div>
        </div>
        <div class="chat">
            <div class="chat-header">
                <div class="chat-title">
                    <div class="profile-avatar">{{ selectedContact?.name[0] || 'C' }}</div>
                    <div>
                        <h2>{{ selectedContact?.name || 'Chat' }}</h2>
                        <span class="status-text">Active now</span>
                    </div>
                </div>
                <div class="chat-actions">
                    <button class="action-button">📞</button>
                    <button class="action-button">📹</button>
                    <button class="action-button">⚙️</button>
                </div>
            </div>
            <div class="messages" ref="messages">
                <div v-for="message in messages" :key="message.id">
                    <div :class="['message', message.sender === 'user' ? 'sent' : 'received']"
                         @contextmenu.prevent="showContextMenu($event, message)">
                        <div v-if="message.replyTo" class="reply-thread">
                            Replying to: {{ message.replyTo.text }}
                        </div>
                        {{ message.text }}
                        <div v-if="message.attachment" class="attachment-preview">
                            <span class="attachment-icon">📎</span>
                            <div class="attachment-info">
                                <div class="attachment-name">{{ message.attachment.name }}</div>
                                <div class="attachment-size">{{ message.attachment.size }}</div>
                            </div>
                        </div>
                        <div v-if="message.voice" class="voice-message">
                            <div class="voice-controls">
                                <button class="voice-button">▶️</button>
                                <span>0:00</span>
                            </div>
                            <div class="voice-waveform" :ref="'waveform-' + message.id"></div>
                        </div>
                        <div class="message-reactions">
                            <div v-for="(count, emoji) in message.reactions" 
                                 :key="emoji"
                                 :class="['reaction', isReacted(message.id, emoji) && 'active']"
                                 @click="toggleReaction(message.id, emoji)">
                                {{ emoji }} {{ count }}
                            </div>
                        </div>
                        <div class="message-time">
                            {{ message.timestamp }}
                            <span v-if="message.sender === 'user'" class="message-status">
                                {{ message.status === 'sent' ? '✓' : '✓✓' }}
                            </span>
                        </div>
                    </div>
                </div>
                <div v-if="isTyping" class="message-typing">
                    {{ typingUser }} is typing...
                </div>
            </div>
            <div class="input-area">
                <div class="input-wrapper">
                    <input 
                        type="text" 
                        class="message-input"
                        v-model="newMessage" 
                        @keyup.enter="sendMessage" 
                        placeholder="Type a message..."
                    >
                    <div class="input-actions">
                        <button class="action-button">😊</button>
                        <button class="action-button">📎</button>
                        <button class="action-button">🎤</button>
                    </div>
                </div>
                <button class="send-button" @click="sendMessage">
                    Send
                </button>
            </div>
            <div v-if="contextMenu.show" 
                 class="context-menu"
                 :style="{ top: contextMenu.y + 'px', left: contextMenu.x + 'px' }">
                <div class="context-item" @click="replyToMessage">
                    ↩️ Reply
                </div>
                <div class="context-item" @click="forwardMessage">
                    ↪️ Forward
                </div>
                <div class="context-item" @click="deleteMessage">
                    🗑️ Delete
                </div>
            </div>
        </div>
    </div>

    <script>
        const { createApp } = Vue

        createApp({
            data() {
                return {
                    messages: [],
                    contacts: [],
                    newMessage: '',
                    isTyping: false,
                    selectedContact: null,
                    showEmojiPicker: false,
                    isRecording: false,
                    contextMenu: {
                        show: false,
                        x: 0,
                        y: 0,
                        message: null
                    },
                    emojis: ['😊', '😂', '❤️', '👍', '🎉', '🔥', '😎', '🤔'],
                    typingUser: null,
                    replyingTo: null
                }
            },
            methods: {
                async sendMessage() {
                    if (!this.newMessage.trim()) return
                    
                    try {
                        const response = await axios.post('/api/messages', {
                            message: this.newMessage
                        })
                        this.messages.push(response.data.sent)
                        this.messages.push(response.data.received)
                        this.newMessage = ''
                        this.$nextTick(() => {
                            this.scrollToBottom()
                        })
                    } catch (error) {
                        console.error('Error sending message:', error)
                    }
                },
                async loadMessages() {
                    try {
                        const response = await axios.get('/api/messages')
                        this.messages = response.data
                        this.$nextTick(() => {
                            this.scrollToBottom()
                        })
                    } catch (error) {
                        console.error('Error loading messages:', error)
                    }
                },
                async loadContacts() {
                    try {
                        const response = await axios.get('/api/contacts')
                        this.contacts = response.data
                    } catch (error) {
                        console.error('Error loading contacts:', error)
                    }
                },
                scrollToBottom() {
                    const messages = this.$refs.messages
                    messages.scrollTop = messages.scrollHeight
                },
                selectContact(contact) {
                    this.selectedContact = contact
                },
                handleInput(event) {
                    this.newMessage = event.target.innerText
                },
                handlePaste(event) {
                    event.preventDefault()
                    const text = event.clipboardData.getData('text/plain')
                    document.execCommand('insertText', false, text)
                },
                handleDrop(event) {
                    event.preventDefault()
                    const items = event.dataTransfer.items
                    for (let item of items) {
                        if (item.kind === 'file') {
                            const file = item.getAsFile()
                            this.handleFile(file)
                        }
                    }
                },
                handleFile(file) {
                    // Handle file upload logic here
                    console.log('File to upload:', file)
                },
                toggleEmojiPicker() {
                    this.showEmojiPicker = !this.showEmojiPicker
                },
                insertEmoji(emoji) {
                    this.newMessage += emoji
                    this.showEmojiPicker = false
                },
                startRecording() {
                    this.isRecording = true
                    // Add recording logic here
                },
                stopRecording() {
                    this.isRecording = false
                    // Add stop recording logic here
                },
                showContextMenu(event, message) {
                    this.contextMenu = {
                        show: true,
                        x: event.clientX,
                        y: event.clientY,
                        message
                    }
                },
                replyToMessage() {
                    this.replyingTo = this.contextMenu.message
                    this.contextMenu.show = false
                },
                forwardMessage() {
                    // Add forward logic here
                    this.contextMenu.show = false
                },
                deleteMessage() {
                    // Add delete logic here
                    this.contextMenu.show = false
                },
                isReacted(messageId, emoji) {
                    // Add reaction check logic here
                    return false
                },
                toggleReaction(messageId, emoji) {
                    // Add reaction toggle logic here
                }
            },
            mounted() {
                this.loadMessages()
                this.loadContacts()
                
                // Close context menu on click outside
                document.addEventListener('click', () => {
                    this.contextMenu.show = false
                })
            }
        }).mount('#app')
    </script>
</body>
</html>
'''

class SecureWebView(QWebEngineView):
    def contextMenuEvent(self, event):
        # Disable right-click menu by doing nothing
        pass

def start_server():
    app.run(port=5000)

if __name__ == '__main__':
    # Start Flask server in a separate thread
    threading.Thread(target=start_server, daemon=True).start()
    
    # Set environment variables for Qt/OpenGL
    import os
    os.environ['QTWEBENGINE_DISABLE_SANDBOX'] = '1'
    os.environ['QT_QPA_PLATFORM'] = 'xcb'  # Use XCB backend
    os.environ['QT_OPENGL'] = 'desktop'    # Use desktop OpenGL
    
    # Create Qt application
    qt_app = QApplication(sys.argv)
    
    # Create web view with disabled context menu
    view = SecureWebView()
    view.setWindowTitle('Secure Chat')
    view.resize(1000, 700)
    view.setMinimumSize(800, 600)
    
    # Load the Flask app URL
    view.load(QUrl('http://localhost:5000'))
    
    # Show the window
    view.show()
    
    # Start Qt event loop
    sys.exit(qt_app.exec())
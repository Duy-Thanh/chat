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

        /* Enhanced input area */
        .input-area {
            padding: 20px;
            background: var(--bg-light);
            display: flex;
            gap: 12px;
            align-items: center;
        }

        .input-wrapper {
            flex: 1;
            position: relative;
            display: flex;
            align-items: center;
            background: var(--bg-dark);
            border-radius: 24px;
            padding: 4px;
        }

        .message-input {
            flex: 1;
            padding: 12px 16px;
            background: transparent;
            border: none;
            color: var(--text);
            font-size: 14px;
        }

        .message-input:focus {
            outline: none;
        }

        .input-actions {
            display: flex;
            gap: 8px;
            padding: 0 12px;
        }

        .send-button {
            padding: 12px 24px;
            border-radius: 24px;
            border: none;
            background: var(--primary);
            color: var(--text);
            font-weight: 500;
            cursor: pointer;
            transition: all 0.3s;
        }

        .send-button:hover {
            background: var(--primary-light);
            transform: translateY(-1px);
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
                    <div :class="['message', message.sender === 'user' ? 'sent' : 'received']">
                        {{ message.text }}
                        <div class="message-time">
                            {{ message.timestamp }}
                            <span v-if="message.sender === 'user'" class="message-status">
                                ✓✓
                            </span>
                        </div>
                    </div>
                </div>
                <div v-if="isTyping" class="typing-indicator">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
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
                    selectedContact: null
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
                }
            },
            mounted() {
                this.loadMessages()
                this.loadContacts()
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
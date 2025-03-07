import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QUrl
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile
import threading
from flask import Flask, jsonify, request, render_template_string, send_file
from werkzeug.utils import secure_filename
import datetime
import json
import os
import uuid

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

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
        self.typing_users = set()
        self.reactions = {}  # message_id -> {emoji: [user_ids]}

    def send_message(self, message, file=None, reply_to=None):
        timestamp = datetime.datetime.now().strftime("%H:%M")
        new_message = {
            "id": len(self.messages) + 1,
            "text": message,
            "sender": "user",
            "timestamp": timestamp,
            "reactions": {},
            "reply_to": reply_to
        }
        
        if file:
            new_message["attachment"] = {
                "name": file.filename,
                "path": file.filename,
                "type": file.content_type
            }
        
        self.messages.append(new_message)
        return new_message

    def add_reaction(self, message_id, emoji, user_id):
        if message_id not in self.reactions:
            self.reactions[message_id] = {}
        if emoji not in self.reactions[message_id]:
            self.reactions[message_id][emoji] = []
        if user_id not in self.reactions[message_id][emoji]:
            self.reactions[message_id][emoji].append(user_id)
            return True
        return False

    def remove_reaction(self, message_id, emoji, user_id):
        if (message_id in self.reactions and 
            emoji in self.reactions[message_id] and 
            user_id in self.reactions[message_id][emoji]):
            self.reactions[message_id][emoji].remove(user_id)
            return True
        return False

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
        data = request.json or {}
        message = data.get('message', '')
        reply_to = data.get('reply_to')
        file = request.files.get('file')
        
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        new_message = chat_api.send_message(message, file, reply_to)
        
        # Simulate received message
        timestamp = datetime.datetime.now().strftime("%H:%M")
        echo_message = {
            "id": len(chat_api.messages) + 1,
            "text": f"Echo: {message}",
            "sender": "other",
            "timestamp": timestamp,
            "reactions": {}
        }
        chat_api.messages.append(echo_message)
        return jsonify({"sent": new_message, "received": echo_message})
    else:
        return jsonify(chat_api.get_messages())

@app.route('/api/messages/<int:message_id>/reactions', methods=['POST'])
def handle_reactions(message_id):
    data = request.json
    emoji = data.get('emoji')
    user_id = data.get('user_id', 1)  # Default user ID
    action = data.get('action', 'add')
    
    if action == 'add':
        success = chat_api.add_reaction(message_id, emoji, user_id)
    else:
        success = chat_api.remove_reaction(message_id, emoji, user_id)
    
    return jsonify({"success": success})

@app.route('/api/typing', methods=['POST'])
def handle_typing():
    data = request.json
    user_id = data.get('user_id')
    is_typing = data.get('typing', False)
    
    if is_typing:
        chat_api.typing_users.add(user_id)
    else:
        chat_api.typing_users.discard(user_id)
    
    return jsonify({"typing_users": list(chat_api.typing_users)})

@app.route('/uploads/<path:filename>')
def serve_file(filename):
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename))

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
            margin-bottom: 90px; /* Height of input area + hint */
        }

        .message {
            max-width: 70%;
            padding: 12px 16px;
            margin: 5px 0;
            border-radius: 18px;
            word-break: break-word;
            white-space: pre-wrap;
            line-height: 1.5;
            position: relative;
            animation: fadeIn 0.3s ease;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .message.sent {
            background: var(--primary);
            margin-left: auto;
            border-bottom-right-radius: 5px;
        }

        .message.received {
            background: var(--secondary);
            margin-right: auto;
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

        /* Input area with proper spacing for hint */
        .input-area {
            position: fixed;
            bottom: 0;
            right: 0;
            left: 300px;
            background: var(--bg-light);
            padding: 15px 20px 25px; /* Increased bottom padding */
            border-top: 1px solid rgba(255,255,255,0.1);
            display: flex;
            gap: 12px;
            align-items: flex-end;
        }

        /* Input wrapper with space for hint */
        .input-wrapper {
            flex: 1;
            display: flex;
            background: rgba(255,255,255,0.05);
            border-radius: 24px;
            padding: 12px 16px;
            position: relative;
            min-height: 48px;
            align-items: flex-end;
            margin-bottom: 10px; /* Add margin for hint */
        }

        .input-wrapper:focus-within {
            background: rgba(255,255,255,0.08);
            box-shadow: 0 0 0 2px rgba(255,255,255,0.1);
        }

        /* Improved textarea styling */
        .message-input {
            flex: 1;
            background: transparent;
            border: none;
            color: var(--text);
            font-size: 14px;
            line-height: 1.5;
            padding: 0;
            margin: 0;
            min-height: 24px;
            max-height: 120px;
            resize: none;
            overflow-y: auto;
            font-family: inherit;
        }

        .message-input:focus {
            outline: none;
        }

        .message-input::placeholder {
            color: rgba(255,255,255,0.4);
        }

        /* Enhanced action buttons */
        .input-actions {
            display: flex;
            gap: 8px;
            margin-left: 12px;
            padding-bottom: 2px;
        }

        .action-button {
            background: transparent;
            border: none;
            color: var(--text-secondary);
            cursor: pointer;
            padding: 6px;
            font-size: 20px;
            border-radius: 50%;
            transition: all 0.2s ease;
            width: 32px;
            height: 32px;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .action-button:hover {
            background: rgba(255,255,255,0.1);
            color: var(--text);
            transform: scale(1.1);
        }

        /* Enhanced send button */
        .send-button {
            background: var(--primary);
            color: white;
            border: none;
            border-radius: 24px;
            padding: 12px 24px;
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s ease;
            height: 48px;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .send-button:hover {
            background: var(--primary-light);
            transform: scale(1.02);
        }

        /* Scrollbar styling */
        .message-input::-webkit-scrollbar {
            width: 6px;
        }

        .message-input::-webkit-scrollbar-track {
            background: transparent;
        }

        .message-input::-webkit-scrollbar-thumb {
            background: rgba(255,255,255,0.2);
            border-radius: 3px;
        }

        .message-input::-webkit-scrollbar-thumb:hover {
            background: rgba(255,255,255,0.3);
        }

        /* Input hint styling */
        .input-hint {
            position: absolute;
            bottom: -22px; /* Adjusted position */
            left: 16px;
            font-size: 11px;
            color: var(--text-secondary);
            opacity: 0.7;
            pointer-events: none;
            white-space: nowrap; /* Prevent wrapping */
            z-index: 1; /* Ensure hint stays above other elements */
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
            position: absolute;
            bottom: 60px;
            left: 0;
            background: var(--bg-light);
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            padding: 8px;
            display: grid;
            grid-template-columns: repeat(8, 1fr);
            gap: 4px;
            z-index: 1000;
        }

        .emoji-item {
            padding: 6px;
            cursor: pointer;
            border-radius: 4px;
            transition: all 0.2s;
            font-size: 20px;
        }

        .emoji-item:hover {
            background: rgba(255,255,255,0.1);
            transform: scale(1.1);
        }

        /* File upload input */
        .file-input {
            display: none;
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
                    <textarea 
                        class="message-input"
                        v-model="newMessage" 
                        @keydown.enter.exact.prevent="sendMessage"
                        @keydown.shift.enter.exact="newline"
                        @input="autoResize"
                        placeholder="Type a message..."
                        rows="1"
                        ref="messageInput"
                    ></textarea>
                    <small class="input-hint">Shift + Enter for new line</small>
                    <div class="input-actions">
                        <button class="action-button" @click="toggleEmojiPicker">😊</button>
                        <input 
                            type="file" 
                            class="file-input" 
                            ref="fileInput"
                            @change="handleFileUpload"
                            accept="image/*,video/*,audio/*,.pdf,.doc,.docx"
                        >
                        <button class="action-button" @click="$refs.fileInput.click()">📎</button>
                        <button class="action-button" @click="toggleVoiceRecording">🎤</button>
                    </div>
                    <!-- Emoji Picker Panel -->
                    <div v-if="showEmojiPicker" class="emoji-picker">
                        <div 
                            v-for="emoji in availableEmojis" 
                            :key="emoji"
                            class="emoji-item"
                            @click="insertEmoji(emoji)"
                        >
                            {{ emoji }}
                        </div>
                    </div>
                </div>
                <button class="send-button" @click="sendMessage">Send</button>
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
                    replyingTo: null,
                    typingTimeout: null,
                    availableEmojis: ['😊', '😂', '❤️', '👍', '🎉', '😎', '🤔', '😍', 
                                     '🥳', '😮', '😢', '😡', '🤝', '👋', '🙏', '✨'],
                    contextMenu: {
                        show: false,
                        x: 0,
                        y: 0,
                        message: null
                    },
                    isRecording: false
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
                    const textarea = this.$refs.messageInput
                    const start = textarea.selectionStart
                    const end = textarea.selectionEnd
                    this.newMessage = this.newMessage.substring(0, start) + emoji + this.newMessage.substring(end)
                    this.showEmojiPicker = false
                    this.$nextTick(() => {
                        textarea.focus()
                        textarea.selectionStart = textarea.selectionEnd = start + emoji.length
                    })
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
                    event.preventDefault();
                    this.contextMenu = {
                        show: true,
                        x: event.clientX,
                        y: event.clientY,
                        message: message
                    };
                },
                hideContextMenu() {
                    this.contextMenu.show = false;
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
                },
                newline(event) {
                    const textarea = event.target;
                    const start = textarea.selectionStart;
                    const end = textarea.selectionEnd;
                    this.newMessage = this.newMessage.substring(0, start) + "\\n" + this.newMessage.substring(end);
                    this.$nextTick(() => {
                        textarea.selectionStart = textarea.selectionEnd = start + 1;
                    });
                },
                autoResize(event) {
                    const textarea = event.target;
                    textarea.style.height = "24px";
                    const newHeight = Math.min(textarea.scrollHeight, 100);
                    textarea.style.height = newHeight + "px";
                },
                async handleFileUpload(event) {
                    const file = event.target.files[0];
                    if (!file) return;

                    const formData = new FormData();
                    formData.append('file', file);
                    formData.append('message', `Sent a file: ${file.name}`);

                    try {
                        const response = await axios.post('/api/messages', formData, {
                            headers: {
                                'Content-Type': 'multipart/form-data'
                            }
                        });
                        this.messages.push(response.data.sent);
                        this.scrollToBottom();
                    } catch (error) {
                        console.error('Error uploading file:', error);
                    }
                    
                    // Reset file input
                    this.$refs.fileInput.value = '';
                },
                toggleVoiceRecording() {
                    if (!this.isRecording) {
                        // Start recording
                        navigator.mediaDevices.getUserMedia({ audio: true })
                            .then(stream => {
                                this.isRecording = true;
                                this.mediaRecorder = new MediaRecorder(stream);
                                this.audioChunks = [];

                                this.mediaRecorder.ondataavailable = (event) => {
                                    this.audioChunks.push(event.data);
                                };

                                this.mediaRecorder.onstop = () => {
                                    const audioBlob = new Blob(this.audioChunks, { type: 'audio/wav' });
                                    const formData = new FormData();
                                    formData.append('file', audioBlob, 'voice-message.wav');
                                    formData.append('message', 'Voice message');
                                    
                                    axios.post('/api/messages', formData, {
                                        headers: {
                                            'Content-Type': 'multipart/form-data'
                                        }
                                    }).then(response => {
                                        this.messages.push(response.data.sent);
                                        this.scrollToBottom();
                                    }).catch(error => {
                                        console.error('Error sending voice message:', error);
                                    });
                                };

                                this.mediaRecorder.start();
                            })
                            .catch(error => {
                                console.error('Error accessing microphone:', error);
                            });
                    } else {
                        // Stop recording
                        this.mediaRecorder.stop();
                        this.mediaRecorder.stream.getTracks().forEach(track => track.stop());
                        this.isRecording = false;
                    }
                },
                setReplyTo(message) {
                    this.replyingTo = message;
                    this.$refs.messageInput.focus();
                },
                cancelReply() {
                    this.replyingTo = null;
                },
                updateTypingStatus() {
                    clearTimeout(this.typingTimeout);
                    
                    if (!this.isTyping) {
                        this.isTyping = true;
                        axios.post('/api/typing', { typing: true });
                    }

                    this.typingTimeout = setTimeout(() => {
                        this.isTyping = false;
                        axios.post('/api/typing', { typing: false });
                    }, 2000);
                }
            },
            mounted() {
                this.loadMessages()
                this.loadContacts()
                
                // Close context menu on click outside
                document.addEventListener('click', this.hideContextMenu)
            },
            beforeUnmount() {
                // Clean up event listener
                document.removeEventListener('click', this.hideContextMenu)
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
document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("chat-form");
    const input = document.getElementById("user-input");
    const chatBox = document.getElementById("chat-box");
    const historyList = document.getElementById("history");
    const clearAllBtn = document.getElementById("clear-history");
    const newChatBtn = document.getElementById("new-chat-btn");
    const themeToggleBtn = document.getElementById("theme-toggle"); // Get theme toggle button
    const themeToggleIcon = themeToggleBtn.querySelector('i'); // Get icon inside the button

    let currentSessionId = sessionStorage.getItem('chatSessionId');
    if (!currentSessionId) {
        currentSessionId = uuidv4();
        sessionStorage.setItem('chatSessionId', currentSessionId);
    }

    loadHistory();

    function applyTheme(theme) {
        if (theme === 'dark') {
            document.body.classList.add('dark-mode');
            themeToggleIcon.classList.remove('fa-moon');
            themeToggleIcon.classList.add('fa-sun');
            localStorage.setItem('theme', 'dark');
        } else {
            document.body.classList.remove('dark-mode');
            themeToggleIcon.classList.remove('fa-sun');
            themeToggleIcon.classList.add('fa-moon');
            localStorage.setItem('theme', 'light');
        }
    }

    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        applyTheme(savedTheme);
    } else if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
        applyTheme('dark');
    } else {
        applyTheme('light');
    }

    themeToggleBtn.addEventListener('click', () => {
        if (document.body.classList.contains('dark-mode')) {
            applyTheme('light');
        } else {
            applyTheme('dark');
        }
    });


    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        const message = input.value.trim();
        if (message === "") return;

        addMessage("user", message);
        input.value = "";

        const typingIndicator = addTypingIndicator();

        try {
            const response = await fetch("/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: message, session_id: currentSessionId }),
            });
            const data = await response.json();

            removeTypingIndicator(typingIndicator);
            addMessage("bot", data.reply);
            
            loadHistory();
        } catch (err) {
            removeTypingIndicator(typingIndicator);
            addMessage("bot", "Error: Could not reach server.");
            console.error("Chat submission error:", err);
        }
    });

    function addMessage(sender, text) {
        const msgDiv = document.createElement("div");
        msgDiv.classList.add("chat-message", sender);
        if (sender === "bot") {
            msgDiv.classList.add("dynamic-bot-message");
            msgDiv.innerHTML = marked.parse(text);
        } else {
            msgDiv.textContent = text;
        }
        chatBox.appendChild(msgDiv);
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    function addTypingIndicator() {
        const typingDiv = document.createElement("div");
        typingDiv.classList.add("chat-message", "bot", "typing");
        typingDiv.textContent = "Typing...";
        chatBox.appendChild(typingDiv);
        chatBox.scrollTop = chatBox.scrollHeight;
        return typingDiv;
    }

    function removeTypingIndicator(typingElem) {
        if (typingElem && chatBox.contains(typingElem)) {
            chatBox.removeChild(typingElem);
        }
    }

    async function loadHistory() {
        try {
            const res = await fetch("/history");
            const data = await res.json();
            historyList.innerHTML = "";

            data.history.forEach(chat => {
                const li = document.createElement("li");
                
                const textSpan = document.createElement("span");
                textSpan.textContent = chat.user; 
                textSpan.title = `Last message: ${chat.timestamp}`;
                textSpan.classList.add("history-item-text");

                textSpan.addEventListener("click", async (e) => {
                    e.preventDefault();
                    currentSessionId = chat.session_id;
                    sessionStorage.setItem('chatSessionId', currentSessionId);
                    await displayChatConversation(chat.session_id);
                    input.focus();
                });
                
                const deleteBtn = document.createElement("button");
                deleteBtn.classList.add("delete-history-item");
                deleteBtn.innerHTML = '<i class="fas fa-trash-alt"></i>';
                deleteBtn.title = "Delete this chat session";
                deleteBtn.addEventListener("click", async (e) => {
                    e.stopPropagation();
                    await deleteChatItem(chat.id);
                });

                li.appendChild(textSpan);
                li.appendChild(deleteBtn);
                historyList.appendChild(li);
            });
        } catch (err) {
            console.error("Error loading history:", err);
        }
    }

    async function displayChatConversation(sessionId) {
        try {
            const res = await fetch(`/get_session_conversation/${sessionId}`);
            const data = await res.json();

            if (data.conversation && data.conversation.length > 0) {
                chatBox.innerHTML = "";
                data.conversation.forEach(msg => {
                    addMessage("user", msg.user);
                    addMessage("bot", msg.bot); 
                });
            } else {
                console.error("Error: Conversation data not found or incomplete for session ID:", sessionId);
                chatBox.innerHTML = "";
                const initialGreeting = document.createElement("div");
                initialGreeting.classList.add("chat-message", "bot", "initial-greeting");
                initialGreeting.textContent = "No conversation found for this session. Start a new one!";
                chatBox.appendChild(initialGreeting);
            }
        } catch (err) {
            console.error("Error displaying chat conversation:", err);
            chatBox.innerHTML = "";
            const errorGreeting = document.createElement("div");
            errorGreeting.classList.add("chat-message", "bot", "initial-greeting");
            errorGreeting.textContent = "Error: Could not retrieve this conversation. Please try again.";
            chatBox.appendChild(errorGreeting);
        }
    }

    async function deleteChatItem(chatId) {
        if (confirm("Are you sure you want to delete this chat session?")) {
            try {
                const res = await fetch(`/delete_chat/${chatId}`, {
                    method: "DELETE",
                });
                if (res.ok) {
                    loadHistory();
                    chatBox.innerHTML = "";
                    const initialGreeting = document.createElement("div");
                    initialGreeting.classList.add("chat-message", "bot", "initial-greeting");
                    initialGreeting.textContent = "Chat session deleted. Start a new conversation!";
                    chatBox.appendChild(initialGreeting);
                    currentSessionId = uuidv4();
                    sessionStorage.setItem('chatSessionId', currentSessionId);
                } else {
                    console.error("Failed to delete chat item.");
                    alert("Failed to delete chat session.");
                }
            } catch (err) {
                console.error("Error deleting chat item:", err);
                alert("Error deleting chat session.");
            }
        }
    }

    newChatBtn?.addEventListener("click", () => {
        chatBox.innerHTML = "";
        input.value = "";
        const initialGreeting = document.createElement("div");
        initialGreeting.classList.add("chat-message", "bot", "initial-greeting");
        initialGreeting.textContent = "Hello! I'm a helpful assistant. How can I help you today?";
        chatBox.appendChild(initialGreeting);
        
        currentSessionId = uuidv4();
        sessionStorage.setItem('chatSessionId', currentSessionId);
        input.focus();
    });

    clearAllBtn?.addEventListener("click", async () => {
        if (confirm("Are you sure you want to clear ALL chat history? This action cannot be undone.")) {
            try {
                const res = await fetch("/clear_history", { method: "POST" });
                if (res.ok) {
                    historyList.innerHTML = "";
                    chatBox.innerHTML = "";
                    const initialGreeting = document.createElement("div");
                    initialGreeting.classList.add("chat-message", "bot", "initial-greeting");
                    initialGreeting.textContent = "All chat history cleared! Ready for a fresh start.";
                    chatBox.appendChild(initialGreeting);
                    input.value = "";
                    currentSessionId = uuidv4();
                    sessionStorage.setItem('chatSessionId', currentSessionId);
                } else {
                    console.error("Failed to clear all history.");
                    alert("Failed to clear all chat history.");
                }
            } catch (err) {
                console.error("Error clearing all history:", err);
                alert("Error clearing all chat history.");
            }
        }
    });

    function uuidv4() {
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
            var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
        });
    }
});
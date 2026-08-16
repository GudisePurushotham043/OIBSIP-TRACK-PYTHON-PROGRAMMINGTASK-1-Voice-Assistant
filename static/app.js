/**
 * Voice Assistant Web App — Client-Side JavaScript
 * Handles: Web Speech API (STT), Speech Synthesis (TTS),
 *           API calls, chat UI, reminders, email modal.
 */

"use strict";

// ── Constants ───────────────────────────────────────────────────────────────
const NAME = window.ASSISTANT_NAME || "Nova";
const API  = { COMMAND: "/api/command", EMAIL: "/api/email/send", REMINDERS: "/api/reminders" };

// ── DOM References ──────────────────────────────────────────────────────────
const messagesWrap = document.getElementById("messagesWrap");
const textInput    = document.getElementById("textInput");
const sendBtn      = document.getElementById("sendBtn");
const micBtn       = document.getElementById("micBtn");
const chipsRow     = document.getElementById("chipsRow");
const clearChat    = document.getElementById("clearChat");
const toggleSpeech = document.getElementById("toggleSpeech");
const statusBadge  = document.getElementById("statusBadge");
const statusText   = document.getElementById("statusText");
const headerDot    = document.getElementById("headerDot");
const headerStatus = document.getElementById("headerStatus");
const speechWarn   = document.getElementById("speechWarning");
const toastCont    = document.getElementById("toastContainer");
const emailModal   = document.getElementById("emailModal");
const emailCancel  = document.getElementById("emailCancel");
const emailSend    = document.getElementById("emailSend");
const sidebarToggle= document.getElementById("sidebarToggle");
const sidebar      = document.querySelector(".sidebar");

// ── State ───────────────────────────────────────────────────────────────────
let speechEnabled  = true;
let isRecording    = false;
let recognition    = null;
let synth          = window.speechSynthesis;
let voiceList      = [];

// ── Speech Synthesis Setup ──────────────────────────────────────────────────
function loadVoices() {
  voiceList = synth.getVoices().filter(v => v.lang.startsWith("en"));
}
loadVoices();
if (synth.onvoiceschanged !== undefined) synth.onvoiceschanged = loadVoices;

function speak(text) {
  if (!speechEnabled || !synth) return;
  synth.cancel();
  const utter = new SpeechSynthesisUtterance(text);
  utter.rate  = 0.98;
  utter.pitch = 1.05;
  utter.volume= 1;
  const preferred = voiceList.find(v =>
    v.name.includes("Zira") || v.name.includes("Google UK") || v.name.includes("Karen") || v.name.includes("Samantha")
  );
  if (preferred) utter.voice = preferred;
  synth.speak(utter);
}

// ── Speech Recognition Setup ────────────────────────────────────────────────
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

if (!SpeechRecognition) {
  speechWarn.style.display = "block";
  micBtn.disabled = true;
  micBtn.title = "Voice input not supported in this browser";
  micBtn.style.opacity = "0.4";
} else {
  recognition = new SpeechRecognition();
  recognition.continuous     = false;
  recognition.interimResults = false;
  recognition.lang           = "en-US";
  recognition.maxAlternatives= 1;

  recognition.onresult = (e) => {
    const transcript = e.results[0][0].transcript.trim();
    stopRecording();
    if (transcript) handleUserInput(transcript);
  };

  recognition.onerror = (e) => {
    stopRecording();
    if (e.error === "not-allowed") {
      showToast("⚠️", "Microphone access denied. Please allow microphone permission in your browser.", "error");
    } else if (e.error !== "aborted") {
      showToast("🎙️", "Couldn't hear you clearly. Try again or type your command.", "warning");
    }
  };

  recognition.onend = () => stopRecording();
}

function startRecording() {
  if (isRecording || !recognition) return;
  isRecording = true;
  micBtn.classList.add("recording");
  micBtn.setAttribute("aria-label", "Recording — click to stop");
  setStatus("Listening…", "listening");
  recognition.start();
}

function stopRecording() {
  isRecording = false;
  micBtn.classList.remove("recording");
  micBtn.setAttribute("aria-label", "Click to speak");
  setStatus("Ready", "ready");
  try { recognition.stop(); } catch(_) {}
}

micBtn.addEventListener("click", () => {
  if (isRecording) stopRecording();
  else startRecording();
});

// ── Status Helper ───────────────────────────────────────────────────────────
function setStatus(text, state="ready") {
  const colors = { ready:"#4ade80", listening:"#38bdf8", thinking:"#a78bfa", error:"#f87171" };
  const col = colors[state] || colors.ready;
  statusText.textContent = text;
  headerStatus.textContent = text;
  document.querySelectorAll(".status-dot, .header-dot").forEach(d => d.style.background = col);
}

// ── Chat Rendering ──────────────────────────────────────────────────────────
function timeNow() {
  return new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

function appendMessage(role, text) {
  const isUser = role === "user";
  const div = document.createElement("div");
  div.className = `msg ${role}`;
  div.setAttribute("role", "listitem");
  div.innerHTML = `
    <div class="msg-avatar">${isUser ? "👤" : "🤖"}</div>
    <div>
      <div class="msg-bubble">${escHtml(text)}</div>
      <div class="msg-time">${timeNow()}</div>
    </div>`;
  messagesWrap.appendChild(div);
  scrollToBottom();
  return div;
}

function showTyping() {
  const div = document.createElement("div");
  div.className = "msg bot";
  div.id = "typingMsg";
  div.innerHTML = `
    <div class="msg-avatar">🤖</div>
    <div>
      <div class="msg-bubble">
        <div class="typing-bubble">
          <span class="typing-dot"></span>
          <span class="typing-dot"></span>
          <span class="typing-dot"></span>
        </div>
      </div>
    </div>`;
  messagesWrap.appendChild(div);
  scrollToBottom();
}

function removeTyping() {
  document.getElementById("typingMsg")?.remove();
}

function scrollToBottom() {
  messagesWrap.scrollTop = messagesWrap.scrollHeight;
}

function escHtml(str) {
  return str.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;");
}

// ── Core Interaction ────────────────────────────────────────────────────────
async function handleUserInput(text) {
  if (!text.trim()) return;
  textInput.value = "";
  appendMessage("user", text);
  setStatus("Thinking…", "thinking");
  showTyping();

  try {
    const res  = await fetch(API.COMMAND, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text })
    });
    const data = await res.json();
    removeTyping();
    setStatus("Ready", "ready");

    const reply = data.response || "I didn't get a response. Please try again.";
    appendMessage("bot", reply);
    speak(reply);

    // Handle extra actions from backend
    if (data.open_url) {
      setTimeout(() => window.open(data.open_url, "_blank", "noopener"), 400);
    }
    if (data.email_mode) {
      openEmailModal();
    }

  } catch (err) {
    removeTyping();
    setStatus("Error", "error");
    const errMsg = "Sorry, I couldn't connect to the server. Please check your connection.";
    appendMessage("bot", errMsg);
    speak(errMsg);
    console.error("API error:", err);
  }
}

// ── Input Events ─────────────────────────────────────────────────────────────
sendBtn.addEventListener("click", () => handleUserInput(textInput.value));

textInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    handleUserInput(textInput.value);
  }
});

// Quick Chips
chipsRow.addEventListener("click", (e) => {
  const chip = e.target.closest(".chip");
  if (chip) handleUserInput(chip.dataset.msg);
});

// Sidebar toggle (mobile)
sidebarToggle?.addEventListener("click", () => {
  const open = sidebar.classList.toggle("open");
  sidebarToggle.setAttribute("aria-expanded", open);
});

// Clear chat
clearChat.addEventListener("click", () => {
  messagesWrap.innerHTML = "";
  addWelcomeMessage();
});

// Toggle speech
toggleSpeech.addEventListener("click", () => {
  speechEnabled = !speechEnabled;
  toggleSpeech.classList.toggle("active", speechEnabled);
  toggleSpeech.setAttribute("aria-pressed", speechEnabled);
  const icon = document.getElementById("speakerIcon");
  if (!speechEnabled) {
    icon.innerHTML = `
      <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/>
      <line x1="23" y1="9" x2="17" y2="15"/><line x1="17" y1="9" x2="23" y2="15"/>`;
  } else {
    icon.innerHTML = `
      <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/>
      <path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"/>`;
  }
  if (speechEnabled) synth.cancel();
});

// ── Welcome Message ──────────────────────────────────────────────────────────
function addWelcomeMessage() {
  const hour = new Date().getHours();
  const greet = hour < 12 ? "Good morning" : hour < 17 ? "Good afternoon" : "Good evening";
  const msg = `${greet}! I'm ${NAME}, your personal AI voice assistant. I can help you with weather, reminders, web searches, general knowledge, and much more. Click the mic to speak, or type below!`;
  appendMessage("bot", msg);
  speak(msg);
}
addWelcomeMessage();

// ── Toasts ───────────────────────────────────────────────────────────────────
function showToast(icon, text, type="info", duration=5000) {
  const toast = document.createElement("div");
  toast.className = "toast";
  toast.innerHTML = `
    <span class="toast-icon">${icon}</span>
    <span class="toast-text">${escHtml(text)}</span>
    <span class="toast-close" role="button" aria-label="Dismiss">✕</span>`;
  toastCont.prepend(toast);

  const close = () => {
    toast.classList.add("removing");
    setTimeout(() => toast.remove(), 310);
  };
  toast.querySelector(".toast-close").addEventListener("click", close);
  if (duration > 0) setTimeout(close, duration);
  return toast;
}

// ── Reminder Polling ──────────────────────────────────────────────────────────
async function pollReminders() {
  try {
    const res = await fetch(API.REMINDERS);
    const { alerts } = await res.json();
    for (const a of alerts) {
      showToast("🔔", a.text, "reminder", 0);
      speak(a.text);
    }
  } catch(_) {}
}
setInterval(pollReminders, 3000);

// ── Email Modal ───────────────────────────────────────────────────────────────
function openEmailModal() {
  emailModal.style.display = "flex";
  setTimeout(() => document.getElementById("emailTo").focus(), 100);
}
function closeEmailModal() {
  emailModal.style.display = "none";
}

emailCancel.addEventListener("click", closeEmailModal);
emailModal.addEventListener("click", (e) => {
  if (e.target === emailModal) closeEmailModal();
});

emailSend.addEventListener("click", async () => {
  const to      = document.getElementById("emailTo").value.trim();
  const subject = document.getElementById("emailSubject").value.trim() || "Hello from " + NAME;
  const body    = document.getElementById("emailBody").value.trim();

  if (!to || !body) {
    showToast("⚠️", "Please fill in the recipient and message.", "error"); return;
  }

  emailSend.textContent = "Sending…";
  emailSend.disabled = true;

  try {
    const res  = await fetch(API.EMAIL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ recipient: to, subject, body })
    });
    const data = await res.json();
    closeEmailModal();
    appendMessage("bot", data.response);
    speak(data.response);
    if (data.success) {
      showToast("✅", "Email sent successfully!", "success");
    } else {
      showToast("❌", data.response, "error");
    }
  } catch(err) {
    showToast("❌", "Failed to send email. Check server connection.", "error");
  } finally {
    emailSend.textContent = "Send Email";
    emailSend.disabled = false;
  }
});

// ── Keyboard shortcut ─────────────────────────────────────────────────────────
document.addEventListener("keydown", (e) => {
  // Space bar = toggle mic (only if not focused on input)
  if (e.code === "Space" && document.activeElement === document.body) {
    e.preventDefault();
    if (isRecording) stopRecording(); else startRecording();
  }
  // Escape = close modal or stop recording
  if (e.key === "Escape") {
    closeEmailModal();
    stopRecording();
  }
});

// ── Init ──────────────────────────────────────────────────────────────────────
toggleSpeech.classList.add("active");
toggleSpeech.setAttribute("aria-pressed", "true");
textInput.focus();

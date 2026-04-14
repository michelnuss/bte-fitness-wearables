/**
 * chat-widget.js — Floating AI chat widget (backend uses Google Gemini).
 * The API key stays on the server; this file only calls /api/chat.
 */

(function () {
  var threadId = null;

  function isAssistantPage() {
    return document.body && document.body.classList.contains("assistant-page");
  }

  // -----------------------------------------------------------------------
  // Inject widget HTML
  // -----------------------------------------------------------------------
  document.addEventListener("DOMContentLoaded", function () {
    var widget = document.createElement("div");
    widget.className = "bte-chat-widget-root";
    widget.innerHTML = [
      '<div id="chat-bubble" title="Chat with BTE Assistant">',
        '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">',
          '<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>',
        '</svg>',
      '</div>',
      '<div id="chat-panel">',
        '<div id="chat-header">',
          '<span>BTE Fitness Assistant</span>',
          '<button type="button" id="chat-close" aria-label="Close">&times;</button>',
        '</div>',
        '<div id="chat-messages">',
          '<div class="chat-msg assistant">Hi! Ask me anything about our products, pricing, shipping, contact, or HQ location.</div>',
        '</div>',
        '<div id="chat-input-row">',
          '<input type="text" id="chat-input" placeholder="e.g. What is the most expensive product?" autocomplete="off">',
          '<button type="button" id="chat-send">Send</button>',
        '</div>',
      '</div>',
    ].join("");

    var mount = document.getElementById("assistant-chat-mount");
    if (mount) {
      mount.appendChild(widget);
    } else {
      document.body.appendChild(widget);
    }

    injectStyles(isAssistantPage());

    if (isAssistantPage()) {
      var bubble = document.getElementById("chat-bubble");
      var panel = document.getElementById("chat-panel");
      var closeBtn = document.getElementById("chat-close");
      if (bubble) bubble.style.display = "none";
      if (panel) {
        panel.style.display = "flex";
        panel.classList.add("bte-chat-embedded");
      }
      if (closeBtn) closeBtn.style.display = "none";

      document.querySelectorAll("[data-assistant-question]").forEach(function (btn) {
        btn.addEventListener("click", function () {
          var q = btn.getAttribute("data-assistant-question") || "";
          var input = document.getElementById("chat-input");
          if (input && q) {
            input.value = q;
            sendMessage();
          }
        });
      });
    }

    document.getElementById("chat-bubble").addEventListener("click", openChat);
    document.getElementById("chat-close").addEventListener("click", closeChat);
    document.getElementById("chat-send").addEventListener("click", sendMessage);
    document.getElementById("chat-input").addEventListener("keydown", function (e) {
      if (e.key === "Enter") sendMessage();
    });
  });

  // -----------------------------------------------------------------------
  // Open / Close
  // -----------------------------------------------------------------------
  function openChat() {
    document.getElementById("chat-panel").style.display = "flex";
    document.getElementById("chat-bubble").style.display = "none";
    document.getElementById("chat-input").focus();
  }

  function closeChat() {
    document.getElementById("chat-panel").style.display = "none";
    document.getElementById("chat-bubble").style.display = "flex";
  }

  // -----------------------------------------------------------------------
  // Send message
  // -----------------------------------------------------------------------
  async function sendMessage() {
    var input = document.getElementById("chat-input");
    var message = input.value.trim();
    if (!message) return;

    input.value = "";
    appendMessage("user", message);
    appendMessage("assistant", "...", "typing-indicator");

    try {
      var res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: message, thread_id: threadId }),
      });

      var data = await res.json();

      if (!res.ok) {
        removeTypingIndicator();
        appendMessage("assistant", "Error: " + (data.detail || "Unknown server error"));
        return;
      }

      threadId = data.thread_id;

      removeTypingIndicator();
      appendMessage("assistant", data.reply || "Sorry, I could not get a response.");
    } catch (err) {
      removeTypingIndicator();
      appendMessage("assistant", "Something went wrong. Please try again.");
    }
  }

  // -----------------------------------------------------------------------
  // Helpers
  // -----------------------------------------------------------------------
  function appendMessage(role, text, id) {
    var box = document.getElementById("chat-messages");
    var div = document.createElement("div");
    div.className = "chat-msg " + role;
    if (id) div.id = id;
    div.textContent = text;
    box.appendChild(div);
    box.scrollTop = box.scrollHeight;
  }

  function removeTypingIndicator() {
    var el = document.getElementById("typing-indicator");
    if (el) el.remove();
  }

  // -----------------------------------------------------------------------
  // Styles (injected so no extra CSS file needed)
  // -----------------------------------------------------------------------
  function injectStyles(embedded) {
    var style = document.createElement("style");
    var extra = embedded
      ? [
          "#chat-panel.bte-chat-embedded{",
            "position:relative;bottom:auto;right:auto;width:100%;max-width:640px;height:min(70vh,520px);",
            "min-height:420px;margin:0 auto;border-radius:14px;",
            "box-shadow:0 4px 24px rgba(0,0,0,.08);border:1px solid #e2e8f0;",
          "}",
        ].join("")
      : "";
    style.textContent = [
      "#chat-bubble{",
        "position:fixed;bottom:24px;right:24px;",
        "width:56px;height:56px;border-radius:50%;",
        "background:var(--clr-accent,#ff6b35);color:#fff;",
        "display:flex;align-items:center;justify-content:center;",
        "cursor:pointer;box-shadow:0 4px 16px rgba(0,0,0,.2);",
        "z-index:1000;transition:transform .2s;",
      "}",
      "#chat-bubble:hover{transform:scale(1.08);}",

      "#chat-panel{",
        "position:fixed;bottom:24px;right:24px;",
        "width:360px;height:500px;",
        "background:#fff;border-radius:14px;",
        "box-shadow:0 8px 32px rgba(0,0,0,.15);",
        "display:none;flex-direction:column;",
        "z-index:1000;overflow:hidden;",
        "font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;",
      "}",

      "#chat-header{",
        "background:var(--clr-primary,#1a73e8);color:#fff;",
        "padding:.85rem 1rem;",
        "display:flex;align-items:center;justify-content:space-between;",
        "font-weight:600;font-size:.95rem;",
      "}",

      "#chat-close{",
        "background:none;border:none;color:#fff;",
        "font-size:1.4rem;cursor:pointer;line-height:1;padding:0;",
      "}",

      "#chat-messages{",
        "flex:1;overflow-y:auto;padding:1rem;",
        "display:flex;flex-direction:column;gap:.6rem;",
      "}",

      ".chat-msg{",
        "max-width:82%;padding:.6rem .9rem;",
        "border-radius:14px;font-size:.875rem;line-height:1.5;",
        "word-wrap:break-word;",
      "}",

      ".chat-msg.user{",
        "background:var(--clr-primary,#1a73e8);color:#fff;",
        "align-self:flex-end;border-bottom-right-radius:4px;",
      "}",

      ".chat-msg.assistant{",
        "background:#f1f3f4;color:#1e293b;",
        "align-self:flex-start;border-bottom-left-radius:4px;",
      "}",

      "#chat-input-row{",
        "display:flex;gap:.5rem;padding:.75rem;",
        "border-top:1px solid #e2e8f0;",
      "}",

      "#chat-input{",
        "flex:1;padding:.55rem .75rem;",
        "border:1.5px solid #e2e8f0;border-radius:8px;",
        "font-size:.875rem;outline:none;",
      "}",

      "#chat-input:focus{border-color:var(--clr-primary,#1a73e8);}",

      "#chat-send{",
        "padding:.55rem 1rem;",
        "background:var(--clr-primary,#1a73e8);color:#fff;",
        "border:none;border-radius:8px;",
        "font-size:.875rem;font-weight:600;cursor:pointer;",
      "}",

      "#chat-send:hover{background:#1558b0;}",

      "@media(max-width:480px){",
        "#chat-panel:not(.bte-chat-embedded){width:calc(100vw - 32px);right:16px;bottom:16px;}",
        "#chat-bubble{right:16px;bottom:16px;}",
      "}",
      extra,
    ].join("");
    document.head.appendChild(style);
  }
})();

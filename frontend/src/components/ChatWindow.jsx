import { useState, useRef, useEffect } from "react";
import MessageBubble from "./MessageBubble.jsx";
import SpendingSummary from "./SpendingSummary.jsx";
import { sendChatMessage } from "../api/client.js";

export default function ChatWindow() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  async function handleSend(text) {
    const messageText = (text ?? input).trim();
    if (!messageText || isLoading) return;

    const newUserMessage = { role: "user", content: messageText };
    const updatedMessages = [...messages, newUserMessage];

    setMessages(updatedMessages);
    setInput("");
    setError(null);
    setIsLoading(true);

    try {
      // Only send role/content to the backend (drop toolsUsed from history).
      const history = messages.map(({ role, content }) => ({ role, content }));
      const { reply, tools_used } = await sendChatMessage(messageText, history);

      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: reply, toolsUsed: tools_used },
      ]);
    } catch (err) {
      setError(err.message || "Something went wrong talking to CentWhisper.");
    } finally {
      setIsLoading(false);
    }
  }

  function handleKeyDown(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  return (
    <div className="chat-window">
      <div className="chat-messages">
        {messages.length === 0 && !isLoading && (
          <SpendingSummary onPick={handleSend} />
        )}

        {messages.map((m, i) => (
          <MessageBubble key={i} role={m.role} content={m.content} toolsUsed={m.toolsUsed} />
        ))}

        {isLoading && (
          <div className="bubble-row bubble-row-assistant">
            {/* <div className="bubble bubble-assistant bubble-loading">Thinking…</div> */}
            <div className="bubble bubble-assistant bubble-loading">
              <span className="typing-dots"><span></span><span></span><span></span></span>
            </div>
          </div>
        )}

        {error && <div className="error-banner">⚠️ {error}</div>}

        <div ref={bottomRef} />
      </div>

      <div className="chat-input-row">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask about your spending, e.g. 'How much did I spend on food this month?'"
          rows={1}
        />
        <button onClick={() => handleSend()} disabled={isLoading || !input.trim()}>
          Send
        </button>
      </div>
    </div>
  );
}

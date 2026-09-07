import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

export default function MessageBubble({ role, content, toolsUsed }) {
  const isUser = role === "user";

  return (
    <div className={`bubble-row ${isUser ? "bubble-row-user" : "bubble-row-assistant"}`}>
      <div className={`bubble ${isUser ? "bubble-user" : "bubble-assistant"}`}>
        {isUser ? (
          <p>{content}</p>
        ) : (
          <div className="markdown-content">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{content}</ReactMarkdown>
          </div>
        )}
        {!isUser && toolsUsed && toolsUsed.length > 0 && (
          <div className="tools-used">🔧 used: {toolsUsed.join(", ")}</div>
        )}
      </div>
    </div>
  );
}
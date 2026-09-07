import ChatWindow from "./components/ChatWindow.jsx";

export default function App() {
  return (
    <div className="app-shell">
      <header className="app-header">
        {/* <h1>CentWhisper 💸</h1> */}
        <h1>¢entGuard</h1>
        <p>Your personal finance copilot — ask me anything about your money.</p>
      </header>
      <ChatWindow />
      <footer className="app-footer">
        Powered by Claude + MCP · Built with Claude Code
      </footer>
    </div>
  );
}

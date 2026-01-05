import { useState, useEffect, useRef } from "react";
import { listen } from "@tauri-apps/api/event";
import "./App.css";

function App() {
  const [status, setStatus] = useState("Waiting for Rust Core...");
  const [messages, setMessages] = useState<string[]>([]);
  const [input, setInput] = useState("");
  const ws = useRef<WebSocket | null>(null);

  useEffect(() => {
    // Listen for the sidecar-ready event from Rust
    const unlisten = listen<string>("sidecar-ready", (event) => {
      const port = event.payload;
      console.log(`Sidecar ready on port: ${port}`);
      setStatus(`Connecting to Brain...`);
      connectWebSocket(port);
    });

    return () => {
      unlisten.then((f) => f());
      if (ws.current) {
        ws.current.close();
      }
    };
  }, []);

  function connectWebSocket(port: string) {
    try {
      // Connect to the dynamic port provided by Rust
      const socket = new WebSocket(`ws://127.0.0.1:${port}/ws`);
      
      socket.onopen = () => {
        setStatus("Connected to AI Brain");
        setMessages(prev => [...prev, "System: Connected to AI Brain"]);
      };

      socket.onmessage = (event) => {
        setMessages(prev => [...prev, `AI: ${event.data}`]);
      };

      socket.onerror = (error) => {
        console.error("WebSocket Error:", error);
        setStatus("Connection Error");
      };

      socket.onclose = () => {
        setStatus("Disconnected");
      };

      ws.current = socket;
    } catch (e) {
      console.error(e);
      setStatus("Connection failed");
    }
  }

  const sendMessage = () => {
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      ws.current.send(input);
      setMessages(prev => [...prev, `You: ${input}`]);
      setInput("");
    }
  };

  return (
    <div className="h-screen w-screen bg-gray-900 text-white flex flex-col p-6">
      <header className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
          Gemini Sensei
        </h1>
        <div className="text-sm px-3 py-1 rounded bg-gray-800 border border-gray-700">
          Status: <span className={status.includes("Connected") ? "text-green-400" : "text-yellow-400"}>{status}</span>
        </div>
      </header>
      
      <div className="flex-1 border border-gray-700 bg-gray-800/50 rounded-lg p-4 mb-4 overflow-y-auto font-mono text-sm space-y-2">
        {messages.length === 0 && (
          <div className="text-gray-500 text-center mt-10">
            {status.includes("Waiting") ? "Initializing AI Brain..." : "Brain ready. Send a message!"}
          </div>
        )}
        {messages.map((msg, idx) => (
          <div key={idx} className={`p-2 rounded ${msg.startsWith("You:") ? "bg-blue-900/30 ml-auto max-w-[80%]" : "bg-gray-700/30 mr-auto max-w-[80%]"}`}>
            {msg}
          </div>
        ))}
      </div>

      <div className="flex gap-3">
        <input
          className="flex-1 bg-gray-800 border border-gray-700 p-3 rounded-lg focus:outline-none focus:border-blue-500 transition-colors"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type a message to the AI..."
          onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
        />
        <button 
          className="bg-blue-600 hover:bg-blue-500 text-white px-6 py-2 rounded-lg font-medium transition-colors disabled:bg-gray-700 disabled:cursor-not-allowed"
          onClick={sendMessage}
          disabled={!ws.current || ws.current.readyState !== WebSocket.OPEN}
        >
          Send
        </button>
      </div>
    </div>
  );
}

export default App;
import uvicorn
import socket
from fastapi import FastAPI, WebSocket
import sys

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello from Gemini Sensei Sidecar!"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Message received: {data}")
    except Exception as e:
        print(f"WebSocket error: {e}")

def get_free_port():
    """Returns a free port on the local machine."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('127.0.0.1', 0))
    port = s.getsockname()[1]
    s.close()
    return port

if __name__ == "__main__":
    # Get a free port assigned by the OS
    port = get_free_port()
    
    # Crucial: Print the port in a format Rust can easily parse
    # and flush stdout immediately.
    print(f"PORT:{port}")
    sys.stdout.flush()
    
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="info")

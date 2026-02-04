import socket

import uvicorn

from main import app


def test_uvicorn_config_with_fd():
    """Test that uvicorn Config can be initialized with a socket file descriptor."""
    # Create and bind a socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("127.0.0.1", 0))
    # port = sock.getsockname()[1]
    fd = sock.fileno()

    # Initialize uvicorn Config with the fd
    config = uvicorn.Config(app=app, fd=fd, host="127.0.0.1")

    # We can't easily start the server in a unit test without blocking or threading,
    # but we can verify the config holds the fd correctly.
    assert config.fd == fd
    # In some uvicorn versions, config.port might still have a default (e.g. 8000)
    # but config.fd takes precedence during server bind.

    sock.close()


def test_bind_random_port_logic():
    """Verify the logic for binding to a random port and keeping it open."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]

    assert port > 0
    # Check that it's actually bound
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as check_sock:
        # This should fail if we try to bind to the same port while sock is open
        try:
            check_sock.bind(("127.0.0.1", port))
            bound_successfully = True
        except socket.error:
            bound_successfully = False

    assert not bound_successfully
    sock.close()

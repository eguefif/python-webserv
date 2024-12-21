from asgi_server.websocket.ws_frame_response import ws_frame_response_builder


def test_text_frame():
    message = {"text": "Hello"}
    response = ws_frame_response_builder(message)

    expected_response = b"\x81\x05\x48\x65\x6c\x6c\x6f"

    assert response.hex() == expected_response.hex()


def test_bytes_frame():
    message = {"bytes": "Hello"}
    response = ws_frame_response_builder(message)

    expected_response = b"\x82\x05\x48\x65\x6c\x6c\x6f"

    assert response.hex() == expected_response.hex()


def test_text_256_kb_frame():
    message = {"text": "H" * 256}
    response = ws_frame_response_builder(message)

    expected_response = b"\x82\x7e\x01\x00" + b"H" * 256

    assert response.hex() == expected_response.hex()


def test_text_65536_kb_frame():
    message = {"text": "H" * 65536}
    response = ws_frame_response_builder(message)

    expected_response = b"\x82\x7e\x00\x00\x00\x00\x00\x01\x00\x00" + b"H" * 65546

    assert response.hex() == expected_response.hex()

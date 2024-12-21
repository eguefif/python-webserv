def ws_frame_response_builder(message):
    if "bytes" in message.keys():
        return build_response(message["bytes"], text=False)
    else:
        return build_response(message["text"])


def build_response(message, text=True):
    message_len = len(message)
    if text:
        response = bytes.fromhex("81")
    else:
        response = bytes.fromhex("82")

    if message_len < 126:
        response += message_len.to_bytes()
    response += message.encode()
    return response

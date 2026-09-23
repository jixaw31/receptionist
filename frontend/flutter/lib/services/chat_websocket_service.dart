import 'dart:convert';

import 'package:web_socket_channel/web_socket_channel.dart';

class ChatWebSocketService {
  final String url;

  WebSocketChannel? _channel;

  ChatWebSocketService(this.url);

  void connect({
    required void Function(Map<String, dynamic> data) onMessage,
    required void Function(Object error) onError,
    required void Function() onDone,
  }) {
    _channel = WebSocketChannel.connect(
      Uri.parse(url),
    );

    _channel!.stream.listen(
      (event) {
        try {
          final data = jsonDecode(event as String);

          onMessage(data as Map<String, dynamic>);
        } catch (e) {
          onError(e);
        }
      },
      onError: onError,
      onDone: onDone,
    );
  }

  void sendMessage(String message) {
    _channel?.sink.add(
      jsonEncode({
        'message': message,
        'graph_type': 'main',
      }),
    );
  }

  void stop() {
    _channel?.sink.add(
      jsonEncode({
        'type': 'stop',
      }),
    );
  }

  Future<void> dispose() async {
    await _channel?.sink.close();
    _channel = null;
  }
}
import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/message.dart';

class ApiService {
  // static = like a class-level constant in TS
  static const String _baseUrl = 'http://127.0.0.1:8000';

  /// Fetches messages for a given user.
  /// In TS terms: `async function fetchMessages(userId: string): Promise<Message[]>`
  static Future<List<Message>> fetchMessages(String userId) async {
    final uri = Uri.parse('$_baseUrl/api/messages/$userId?limit=20&offset=0');

    final response = await http.get(
      uri,
      headers: {'accept': 'application/json'},
    );

    if (response.statusCode != 200) {
      throw Exception('Server error: ${response.statusCode}');
    }

    // IMPORTANT: decode as UTF-8 for Persian text
    final decoded = utf8.decode(response.bodyBytes);
    final data = jsonDecode(decoded) as Map<String, dynamic>;

    final List<dynamic> rawMessages = data['messages'] ?? [];

    return rawMessages
        .map((e) => Message.fromJson(e as Map<String, dynamic>))
        .toList();
  }
  /// Sends a message for a given user and returns the AI's reply.
  /// In TS terms: `async function sendMessage(userId: string, content: string): Promise<Message>`
  static Future<Message> sendMessage({
    required String userId,
    required String content,
  }) async {
    final uri = Uri.parse('$_baseUrl/api/messages/$userId');

    final response = await http.post(
      uri,
      headers: {
        'accept': 'application/json',
        'content-type': 'application/json',
      },
      body: jsonEncode({
        'content': content,
        // if your backend wants the role explicitly, add:
        // 'role': 'human',
      }),
    );
  
    if (response.statusCode != 200 && response.statusCode != 201) {
      throw Exception('Server error: ${response.statusCode}');
    }

    // Decode as UTF-8 for Persian text.
    final decoded = utf8.decode(response.bodyBytes);
    final data = jsonDecode(decoded) as Map<String, dynamic>;

    // --- Adjust this block to match your actual response shape ---
    //
    // Case 1: backend returns the AI reply directly:
    //   { "role": "ai", "content": "...", "timestamp": "..." }
    return Message.fromJson(data);

    // Case 2: backend returns it nested, e.g. { "message": { ... } }:
    // return Message.fromJson(data['message'] as Map<String, dynamic>);

    // Case 3: backend returns both the user's stored message and the reply,
    // e.g. { "user_message": {...}, "reply": {...} }:
    // return Message.fromJson(data['reply'] as Map<String, dynamic>);
  }
}


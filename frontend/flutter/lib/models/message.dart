class Message {
  final String role;   // "human" or "ai"
  final String content;
  final String? nodeName;   // the `?` means nullable (like `string | null`)
  final String? timestamp;

  // Constructor
  Message({
    required this.role,
    required this.content,
    this.nodeName,
    this.timestamp,
  });

  // Named constructor — like a static factory method
  factory Message.fromJson(Map<String, dynamic> json) {
    return Message(
      role: json['role']?.toString() ?? 'unknown',
      content: json['content']?.toString() ?? '',
      nodeName: json['node_name']?.toString(),
      timestamp: json['timestamp']?.toString(),
    );
  }

  // Getters — like `get isHuman() { ... }` in TS
  bool get isHuman => role == 'human';
  bool get isAi => role == 'ai';
}
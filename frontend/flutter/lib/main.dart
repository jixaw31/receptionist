import 'package:flutter/material.dart';
import 'components/chatinput.dart';  
import 'components/message_row.dart';
import 'models/message.dart';
import 'services/api_service.dart';
import 'services/chat_websocket_service.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Chat Demo',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.deepPurple),
        useMaterial3: true,
      ),
      home: const MyHomePage(title: 'Messages'),
    );
  }
}

class MyHomePage extends StatefulWidget {
  const MyHomePage({super.key, required this.title});

  final String title;

  @override
  State<MyHomePage> createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {
  static const String userId = '847f5e78-25b0-46b0-8188-1ebefd9c2772';
  bool _isWaitingForResponse = false;

  List<Message> _messages = [];
  bool _isLoading = true;
  bool _isSending = false;              // <-- ADD THIS
  String? _error;

  String _streamingResponse = '';

  final ScrollController _scrollController = ScrollController();  // <-- ADD THIS

   late final ChatWebSocketService _chatSocket;

  @override
  void initState() {
    super.initState();

    _chatSocket = ChatWebSocketService(
      'ws://127.0.0.1:8000/chat/stream/$userId',
    );

    _chatSocket.connect(
      onMessage: _handleWebSocketMessage,
      onError: _handleWebSocketError,
      onDone: _handleWebSocketDone,
    );

    _loadMessages();
  }

  @override
  void dispose() {
    _chatSocket.dispose();
    _scrollController.dispose();

    super.dispose();
  }

  Future<void> _loadMessages() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final messages = await ApiService.fetchMessages(userId);
      setState(() {
        _messages = messages;
        _isLoading = false;
      });
      _scrollToBottom();
    } catch (e) {
      setState(() {
        _error = e.toString();
        _isLoading = false;
      });
    }
  }

  void _handleSend(String text) {
    final userMessage = Message(
      role: 'human',
      content: text,
    );

    setState(() {
      _messages = [..._messages, userMessage];
      _isSending = true;
      _isWaitingForResponse = true;
      _streamingResponse = '';
    });

    _scrollToBottom();
    _chatSocket.sendMessage(text);
  }


  void _handleWebSocketMessage(Map<String, dynamic> data) {

    // debugPrint('⬅️ WebSocket: $data');
    final type = data['type'];

    switch (type) {
      case 'token':
        final accumulated = data['accumulated'] ?? '';

        setState(() {
          _streamingResponse = accumulated;
          _isWaitingForResponse = false;
        });

        _scrollToBottom();
        break;

      case 'complete':
        final response = _streamingResponse;

        setState(() {
          if (response.isNotEmpty) {
            _messages = [
              ..._messages,
              Message(
                role: 'ai',
                content: response,
              ),
            ];
          }

          _streamingResponse = '';
          _isWaitingForResponse = false;
          _isSending = false;
        });

        _scrollToBottom();
        break;

      case 'confirmation':
        debugPrint(
          'Confirmation: ${data['confirmation_content']}',
        );
        break;

      case 'error':
        setState(() {
          _isSending = false;
          _isWaitingForResponse = false;
          _streamingResponse = '';
        });

        setState(() {
          _isSending = false;
          _streamingResponse = '';
        });

        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              'خطا در پاسخ سرور: ${data['error']}',
            ),
          ),
        );
        break;

      case 'stop_ack':
        setState(() {
          _isSending = false;
        });
        break;

      default:
        debugPrint('Unknown WebSocket message: $data');
    }
  }

  void _handleWebSocketError(Object error) {
    debugPrint('WebSocket error: $error');

    if (!mounted) return;

    setState(() {
      _isSending = false;
    });

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text('WebSocket error: $error'),
      ),
    );
  }
  
  void _handleWebSocketDone() {
    debugPrint('WebSocket connection closed');

    if (!mounted) return;

    setState(() {
      _isSending = false;
    });
  }
  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 250),
          curve: Curves.easeOut,
        );
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
        title: Text(widget.title),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadMessages,
            tooltip: 'Refresh',
          ),
        ],
      ),
      body: _buildBody(),
    );
  }

  Widget _buildBody() {
    
    if (_isLoading) {
      
      return const Center(child: CircularProgressIndicator());
    }

    if (_error != null) {
      return _ErrorView(message: _error!, onRetry: _loadMessages);
    }

    // <-- CHANGED: wrap the list in a Column and add ChatInput below it.
    // (Empty state no longer short-circuits, because we still want the
    // input bar to be visible so the user can start a new chat.)
    return Column(
      children: [
        Expanded(
          child: _messages.isEmpty
              ? const Center(child: Text('No messages found.'))
              : ListView.builder(
                  controller: _scrollController,
                  padding: EdgeInsets.zero,
                  itemCount: _messages.length +
                    (_isWaitingForResponse || _streamingResponse.isNotEmpty ? 1 : 0),
                  itemBuilder: (context, index) {
                    if (index < _messages.length) {
                      return MessageRow(message: _messages[index]);
                    }

                    if (_isWaitingForResponse) {
                      return const Padding(
                        padding: EdgeInsets.all(16),
                        child: Align(
                          alignment: Alignment.centerRight,
                          child: SizedBox(
                            width: 20,
                            height: 20,
                            child: CircularProgressIndicator(strokeWidth: 2),
                          ),
                        ),
                      );
                    }

                    return MessageRow(
                      message: Message(
                        role: 'ai',
                        content: _streamingResponse,
                      ),
                    );
                  },
                ),
        ),
        ChatInput(
          isLoading: _isSending,
          onSend: _handleSend,
        ),
      ],
    );
  }
}

class _ErrorView extends StatelessWidget {
  final String message;
  final VoidCallback onRetry;

  const _ErrorView({required this.message, required this.onRetry});

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.error_outline, size: 48, color: Colors.red),
            const SizedBox(height: 16),
            Text(message, textAlign: TextAlign.center),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: onRetry,
              child: const Text('Retry'),
            ),
          ],
        ),
      ),
    );
  }
}
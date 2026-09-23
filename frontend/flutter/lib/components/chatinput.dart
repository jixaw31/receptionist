import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

/// A ChatGPT-style input bar with RTL support and a send button.
/// Public — importable from anywhere.
class ChatInput extends StatefulWidget {
  /// Called when the user submits a message (via send button or Enter).
  final ValueChanged<String> onSend;
  /// Placeholder text shown when empty.
  final String hintText;

  /// Disables input + button while true (e.g. while AI is responding).
  final bool isLoading;

  const ChatInput({
    super.key,
    required this.onSend,
    this.hintText = 'پیام خود را بنویسید...',
    this.isLoading = false,
  });

  @override
  State<ChatInput> createState() => _ChatInputState();
}

class _ChatInputState extends State<ChatInput> {
  final TextEditingController _controller = TextEditingController();
  final FocusNode _focusNode = FocusNode();

  @override
  void dispose() {
    _controller.dispose();
    _focusNode.dispose();
    super.dispose();
  }

  bool get _canSend =>
      _controller.text.trim().isNotEmpty && !widget.isLoading;

  KeyEventResult _handleKeyEvent(FocusNode node, KeyEvent event) {
    // Only care about the initial press, not key-up/repeat.
    if (event is! KeyDownEvent) return KeyEventResult.ignored;

    final isEnter = event.logicalKey == LogicalKeyboardKey.enter ||
        event.logicalKey == LogicalKeyboardKey.numpadEnter;

    if (!isEnter) return KeyEventResult.ignored;

    // Shift+Enter → let the TextField insert a newline.
    if (HardwareKeyboard.instance.isShiftPressed) {
      return KeyEventResult.ignored;
    }

    // Plain Enter → send, and tell Flutter we handled it (no newline inserted).
    _handleSend();
    return KeyEventResult.handled;
  }

  void _handleSend() {
    final text = _controller.text.trim();
    if (text.isEmpty || widget.isLoading) return;
    widget.onSend(text);
    _controller.clear();
    setState(() {});
    _focusNode.requestFocus();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;

    final boxColor = isDark ? const Color(0xFF2A2B32) : const Color(0xFFF0F2F5);
    final borderColor =
        isDark ? const Color(0xFF565869) : const Color(0xFFD9DCE1);
    final hintColor = theme.hintColor;

    return Container(
      width: double.infinity,
      color: theme.scaffoldBackgroundColor,
      padding: const EdgeInsets.fromLTRB(16, 8, 16, 16),
      child: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 720),
          child: Container(
            decoration: BoxDecoration(
              color: boxColor,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: borderColor, width: 1),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withValues(alpha: isDark ? 0.35 : 0.06),
                  blurRadius: 8,
                  offset: const Offset(0, 2),
                ),
              ],
            ),
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 6),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                // Send button on the left (RTL layout puts it visually left
                // if you prefer, but keeping the send button adjacent to the
                // field on the "end" side feels natural for chat UIs).
                Expanded(
                  child: Focus(
                    onKeyEvent: _handleKeyEvent,
                    child: TextField(
                      controller: _controller,
                      focusNode: _focusNode,
                      enabled: true,
                      minLines: 1,
                      maxLines: 6,
                      textInputAction: TextInputAction.send,
                      keyboardType: TextInputType.text,
                      textDirection: TextDirection.rtl,
                      textAlign: TextAlign.right,
                      style: const TextStyle(fontSize: 15, height: 1.5),
                      decoration: InputDecoration(
                        hintText: widget.hintText,
                        hintStyle: TextStyle(color: hintColor, fontSize: 15),
                        hintTextDirection: TextDirection.rtl,
                        border: InputBorder.none,
                        isDense: true,
                        contentPadding: const EdgeInsets.symmetric(
                          horizontal: 10,
                          vertical: 12,
                        ),
                      ),
                      onChanged: (_) => setState(() {}),
                      onSubmitted: (_) => _handleSend(),
                    ),
                  ),
                ),
                const SizedBox(width: 6),
                _SendButton(
                  enabled: _canSend,
                  isLoading: widget.isLoading,
                  onTap: _handleSend,
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _SendButton extends StatelessWidget {
  final bool enabled;
  final bool isLoading;
  final VoidCallback onTap;

  const _SendButton({
    required this.enabled,
    required this.isLoading,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Material(
      color: enabled ? const Color(0xFF10A37F) : Colors.grey.withValues(alpha: 0.35),
      borderRadius: BorderRadius.circular(8),
      child: InkWell(
        borderRadius: BorderRadius.circular(8),
        onTap: enabled ? onTap : null,
        child: SizedBox(
          width: 40,
          height: 40,
          child: isLoading
              ? const Padding(
                  padding: EdgeInsets.all(10),
                  child: CircularProgressIndicator(
                    strokeWidth: 2,
                    color: Colors.white,
                  ),
                )
              : Icon(
                  Icons.send_rounded,
                  color: enabled ? Colors.white : Colors.white70,
                  size: 20,
                ),
        ),
      ),
    );
  }
}
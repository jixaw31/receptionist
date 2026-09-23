import 'package:flutter/material.dart';
import '../models/message.dart';

/// A single ChatGPT-style message row.
/// Public — importable from anywhere.
class MessageRow extends StatelessWidget {
  final Message message;

  const MessageRow({super.key, required this.message});

  @override
  Widget build(BuildContext context) {
    final isHuman = message.isHuman;
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;

    // Human messages: plain scaffold background.
    // AI messages: a clearly visible card with border + elevation.
    final backgroundColor = isHuman
        ? theme.scaffoldBackgroundColor
        : (isDark ? const Color(0xFF2A2B32) : const Color(0xFFF0F2F5));

    final borderColor = isHuman
        ? Colors.transparent
        : (isDark ? const Color(0xFF565869) : const Color(0xFFD9DCE1));

    final label = isHuman ? 'شما' : 'اپراتور پذیرش';
    final text = message.content.trim();
    final textDirection = _detectDirection(text);

    return Container(
      width: double.infinity,
      color: isHuman ? backgroundColor : Colors.transparent,
      padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 16),
      child: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 720),
          child: Container(
            // Card look only for AI messages.
            decoration: isHuman
                ? null
                : BoxDecoration(
                    color: backgroundColor,
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
            padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 16),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Expanded(
                  child: Column(
                    // Right-align everything in the column.
                    crossAxisAlignment: CrossAxisAlignment.end,
                    children: [
                      Text(
                        label,
                        textAlign: TextAlign.right,
                        textDirection: TextDirection.rtl,
                        style: const TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 14,
                        ),
                      ),
                      const SizedBox(height: 6),
                      SelectableText(
                        text,
                        textAlign: TextAlign.right,
                        textDirection: textDirection,
                        style: const TextStyle(fontSize: 15, height: 1.6),
                      ),
                    ],
                  ),
                ),
                // const SizedBox(width: 16),
                // _Avatar(isHuman: isHuman),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

/// Detects whether the given text should be displayed as RTL or LTR.
/// Uses the first strong directional character (similar to Unicode's
/// first-strong heuristic).
TextDirection _detectDirection(String text) {
  for (final rune in text.runes) {
    // Arabic, Arabic Supplement, Arabic Extended-A, Arabic Presentation Forms
    if ((rune >= 0x0600 && rune <= 0x06FF) ||
        (rune >= 0x0750 && rune <= 0x077F) ||
        (rune >= 0x08A0 && rune <= 0x08FF) ||
        (rune >= 0xFB50 && rune <= 0xFDFF) ||
        (rune >= 0xFE70 && rune <= 0xFEFF)) {
      return TextDirection.rtl;
    }
    // Basic Latin letters (strong LTR)
    if ((rune >= 0x0041 && rune <= 0x005A) ||
        (rune >= 0x0061 && rune <= 0x007A)) {
      return TextDirection.ltr;
    }
  }
  // No strong directional character found (numbers, punctuation, etc.)
  return TextDirection.rtl;
}

/// Private — only visible inside this file.
// class _Avatar extends StatelessWidget {
//   final bool isHuman;

//   const _Avatar({required this.isHuman});

//   @override
//   Widget build(BuildContext context) {
//     if (isHuman) {
//       return Container(
//         width: 32,
//         height: 32,
//         decoration: BoxDecoration(
//           color: Colors.deepPurple,
//           borderRadius: BorderRadius.circular(4),
//         ),
//         alignment: Alignment.center,
//         child: const Text(
//           'ش',
//           style: TextStyle(
//             color: Colors.white,
//             fontWeight: FontWeight.bold,
//             fontSize: 14,
//           ),
//         ),
//       );
//     }

//     return Container(
//       width: 32,
//       height: 32,
//       decoration: BoxDecoration(
//         color: const Color(0xFF10A37F),
//         borderRadius: BorderRadius.circular(4),
//       ),
//       alignment: Alignment.center,
//       child: const Icon(Icons.auto_awesome, color: Colors.white, size: 18),
//     );
//   }
// }


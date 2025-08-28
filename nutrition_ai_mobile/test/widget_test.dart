// This is a basic Flutter widget test.
//
// To perform an interaction with a widget in your test, use the WidgetTester
// utility that Flutter provides. For example, you can send tap and scroll
// gestures. You can also use WidgetTester to find child widgets in the widget
// tree, read text, and verify that the values of widget properties are correct.

import 'package:flutter_test/flutter_test.dart';

import 'package:nutrition_ai_mobile/main.dart';

void main() {
  testWidgets('NutriCoach app smoke test', (WidgetTester tester) async {
    // Build our app and trigger a frame.
    await tester.pumpWidget(const NutriCoachApp());

    // Verify that the server setup screen loads
    expect(find.text('NutriCoach Mobile'), findsOneWidget);
    expect(find.text('Connect to Server'), findsOneWidget);
  });
}

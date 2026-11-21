
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:youth_unemployment_app/app.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  testWidgets(
    'Youth Unemployment Predictor loads correctly',
    (WidgetTester tester) async {
      await tester.pumpWidget(
        const YouthUnemploymentApp(),
      );

      expect(
        find.byType(Scaffold),
        findsOneWidget,
      );

      expect(
        find.text('Youth Unemployment'),
        findsOneWidget,
      );

      expect(
        find.text('Predict youth\nunemployment.'),
        findsOneWidget,
      );

      expect(
        find.text('Economic indicators'),
        findsOneWidget,
      );
    },
  );
}

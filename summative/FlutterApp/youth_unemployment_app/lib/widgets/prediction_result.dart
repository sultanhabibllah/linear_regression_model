
import 'package:flutter/material.dart';

import '../services/prediction_service.dart';

class PredictionResultCard extends StatelessWidget {
  final PredictionResult result;

  const PredictionResultCard({
    super.key,
    required this.result,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: const Color(0xFFF7F7F7),
        border: Border.all(
          color: const Color(0xFFE5E5E5),
          width: 1,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Row(
            children: [
              Icon(
                Icons.analytics_outlined,
                size: 17,
                color: Color(0xFF525252),
              ),
              SizedBox(width: 8),
              Text(
                'PREDICTION RESULT',
                style: TextStyle(
                  fontSize: 10,
                  fontWeight: FontWeight.w700,
                  letterSpacing: 1,
                  color: Color(0xFF525252),
                ),
              ),
            ],
          ),

          const SizedBox(height: 20),

          Text(
            '${result.unemploymentRate.toStringAsFixed(2)}%',
            style: const TextStyle(
              fontSize: 48,
              height: 1,
              fontWeight: FontWeight.w700,
              letterSpacing: -2,
              color: Color(0xFF171717),
            ),
          ),

          const SizedBox(height: 9),

          const Text(
            'Estimated youth unemployment rate',
            style: TextStyle(
              fontSize: 12,
              color: Color(0xFF525252),
            ),
          ),

          const SizedBox(height: 20),

          const Divider(height: 1),

          const SizedBox(height: 14),

          Text(
            'MODEL  ${result.model}',
            style: const TextStyle(
              fontSize: 10,
              fontWeight: FontWeight.w500,
              color: Color(0xFF737373),
            ),
          ),

          if (result.modelVersion != null) ...[
            const SizedBox(height: 6),
            Text(
              'VERSION  ${result.modelVersion}',
              style: const TextStyle(
                fontSize: 10,
                fontWeight: FontWeight.w500,
                color: Color(0xFF737373),
              ),
            ),
          ],

          const SizedBox(height: 14),

          const Text(
            'This is a machine learning estimate, '
            'not an official unemployment statistic.',
            style: TextStyle(
              fontSize: 11,
              height: 1.5,
              color: Color(0xFF737373),
            ),
          ),
        ],
      ),
    );
  }
}

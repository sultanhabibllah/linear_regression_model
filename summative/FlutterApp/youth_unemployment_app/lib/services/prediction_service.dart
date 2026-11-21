
import 'dart:convert';

import 'package:http/http.dart' as http;

import '../models/prediction_input.dart';

class PredictionResult {
  final double unemploymentRate;
  final String model;
  final String unit;
  final String? modelVersion;

  const PredictionResult({
    required this.unemploymentRate,
    required this.model,
    required this.unit,
    this.modelVersion,
  });
}

class PredictionService {
  static const String baseUrl =
      'https://africa-youth-unemployment-api.onrender.com';

  final http.Client _client;

  PredictionService({http.Client? client})
      : _client = client ?? http.Client();

  Future<PredictionResult> predict(
    PredictionInput input,
  ) async {
    try {
      final response = await _client
          .post(
            Uri.parse('$baseUrl/predict'),
            headers: {
              'Content-Type': 'application/json',
            },
            body: jsonEncode(input.toJson()),
          )
          .timeout(const Duration(seconds: 90));

      final decoded = jsonDecode(response.body);

      if (response.statusCode != 200) {
        if (response.statusCode == 422) {
          throw Exception(
            'Some input values are invalid. '
            'Please review your entries.',
          );
        }

        throw Exception(
          'Prediction failed (HTTP ${response.statusCode}).',
        );
      }

      if (decoded is! Map<String, dynamic>) {
        throw const FormatException(
          'Unexpected API response format.',
        );
      }

      final rate =
          decoded['predicted_youth_unemployment_rate'];

      if (rate is! num) {
        throw const FormatException(
          'Prediction value is missing or invalid.',
        );
      }

      return PredictionResult(
        unemploymentRate: rate.toDouble(),
        model: decoded['model']?.toString() ?? 'Random Forest',
        unit: decoded['unit']?.toString() ?? 'percent',
        modelVersion: decoded['model_version']?.toString(),
      );
    } on http.ClientException {
      throw Exception(
        'Could not connect to the prediction server. '
        'Check your internet connection.',
      );
    }
  }

  void dispose() {
    _client.close();
  }
}

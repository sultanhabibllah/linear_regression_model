
import 'package:flutter/material.dart';

import '../models/prediction_input.dart';
import '../services/prediction_service.dart';
import '../widgets/prediction_form.dart';
import '../widgets/prediction_result.dart';

class PredictionScreen extends StatefulWidget {
  const PredictionScreen({super.key});

  @override
  State<PredictionScreen> createState() =>
      _PredictionScreenState();
}

class _PredictionScreenState extends State<PredictionScreen> {
  final PredictionService _service = PredictionService();
  final ScrollController _scrollController = ScrollController();

  bool _isLoading = false;
  PredictionResult? _result;
  String? _errorMessage;

  @override
  void dispose() {
    _service.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  Future<void> _handlePrediction(PredictionInput input) async {
    setState(() {
      _isLoading = true;
      _result = null;
      _errorMessage = null;
    });

    try {
      final result = await _service.predict(input);

      if (!mounted) return;

      setState(() {
        _result = result;
      });

      WidgetsBinding.instance.addPostFrameCallback((_) {
        if (!mounted || !_scrollController.hasClients) {
          return;
        }

        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 350),
          curve: Curves.easeOut,
        );
      });
    } catch (error) {
      if (!mounted) return;

      setState(() {
        _errorMessage = error.toString().replaceFirst(
          'Exception: ',
          '',
        );
      });
    } finally {
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
      }
    }
  }

  Widget _errorCard() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: const Color(0xFFFAFAFA),
        border: Border.all(
          color: const Color(0xFFDC2626),
        ),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Icon(
            Icons.error_outline,
            size: 18,
            color: Color(0xFFDC2626),
          ),
          const SizedBox(width: 10),
          Expanded(
            child: Text(
              _errorMessage ?? 'Something went wrong.',
              style: const TextStyle(
                fontSize: 12,
                height: 1.5,
                color: Color(0xFF525252),
              ),
            ),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Youth Unemployment'),
        bottom: const PreferredSize(
          preferredSize: Size.fromHeight(1),
          child: Divider(
            height: 1,
            color: Color(0xFFE5E5E5),
          ),
        ),
      ),
      body: SafeArea(
        child: Center(
          child: ConstrainedBox(
            constraints: const BoxConstraints(
              maxWidth: 600,
            ),
            child: SingleChildScrollView(
              controller: _scrollController,
              padding: const EdgeInsets.fromLTRB(
                20, 26, 20, 28,
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [

                  const SizedBox(height: 12),

                  const Text(
                    'Predict youth\nunemployment.',
                    style: TextStyle(
                      fontSize: 30,
                      height: 1.13,
                      letterSpacing: -1.3,
                      fontWeight: FontWeight.w700,
                      color: Color(0xFF171717),
                    ),
                  ),

                  const SizedBox(height: 11),

                  const Text(
                    'Estimate youth unemployment across '
                    'African countries using economic, '
                    'demographic and education indicators.',
                    style: TextStyle(
                      fontSize: 12.5,
                      height: 1.6,
                      color: Color(0xFF737373),
                    ),
                  ),

                  const SizedBox(height: 4),

                  PredictionForm(
                    isLoading: _isLoading,
                    onPredict: _handlePrediction,
                  ),

                  if (_errorMessage != null) ...[
                    const SizedBox(height: 18),
                    _errorCard(),
                  ],

                  if (_result != null) ...[
                    const SizedBox(height: 20),
                    PredictionResultCard(
                      result: _result!,
                    ),
                  ],

                  const SizedBox(height: 26),

                  const Divider(height: 1),

                  const SizedBox(height: 14),

                  const Text(
                    'WORLD BANK DATA  /  RANDOM FOREST MODEL',
                    style: TextStyle(
                      fontSize: 9,
                      fontWeight: FontWeight.w500,
                      letterSpacing: 0.6,
                      color: Color(0xFFA3A3A3),
                    ),
                  ),

                  const SizedBox(height: 16),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}

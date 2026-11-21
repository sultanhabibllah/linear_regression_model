
import 'package:flutter/material.dart';

class PredictionInputField extends StatelessWidget {
  final String label;
  final TextEditingController controller;
  final String? unit;
  final bool requiredField;
  final bool isPercentage;
  final bool nonNegative;
  final bool isYear;

  const PredictionInputField({
    super.key,
    required this.label,
    required this.controller,
    this.unit,
    this.requiredField = true,
    this.isPercentage = false,
    this.nonNegative = false,
    this.isYear = false,
  });

  String? _validate(String? value) {
    final text = value?.trim() ?? '';

    if (text.isEmpty) {
      return requiredField ? 'Required field' : null;
    }

    final number = double.tryParse(text);

    if (number == null || !number.isFinite) {
      return 'Enter a valid number';
    }

    if (isYear) {
      if (number != number.roundToDouble() ||
          number < 2000 ||
          number > 2100) {
        return 'Year: 2000–2100';
      }
    }

    if (isPercentage && (number < 0 || number > 100)) {
      return 'Must be 0–100';
    }

    if (nonNegative && number < 0) {
      return 'Cannot be negative';
    }

    return null;
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          maxLines: 2,
          style: const TextStyle(
            fontSize: 11.5,
            fontWeight: FontWeight.w600,
            height: 1.35,
            color: Color(0xFF262626),
          ),
        ),
        const SizedBox(height: 7),
        TextFormField(
          controller: controller,
          keyboardType: TextInputType.numberWithOptions(
            decimal: !isYear,
            signed: !isPercentage &&
                !nonNegative &&
                !isYear,
          ),
          textInputAction: TextInputAction.next,
          style: const TextStyle(
            fontSize: 13,
            fontWeight: FontWeight.w500,
            color: Color(0xFF171717),
          ),
          decoration: InputDecoration(
            hintText: isYear ? '2023' : 'Enter value',
            suffixText: unit,
          ),
          validator: _validate,
        ),
      ],
    );
  }
}

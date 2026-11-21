
import 'package:flutter/material.dart';

import '../models/prediction_input.dart';
import 'input_field.dart';

class PredictionForm extends StatefulWidget {
  final Future<void> Function(PredictionInput) onPredict;
  final bool isLoading;

  const PredictionForm({
    super.key,
    required this.onPredict,
    required this.isLoading,
  });

  @override
  State<PredictionForm> createState() =>
      _PredictionFormState();
}

class _PredictionFormState extends State<PredictionForm> {
  final _formKey = GlobalKey<FormState>();

  final Map<String, TextEditingController> _controllers = {
    'gdp_growth': TextEditingController(),
    'gdp_per_capita': TextEditingController(),
    'inflation': TextEditingController(),
    'urban_population_pct': TextEditingController(),
    'population_growth': TextEditingController(),
    'agriculture_employment': TextEditingController(),
    'industry_employment': TextEditingController(),
    'female_labor_participation': TextEditingController(),
    'secondary_enrollment': TextEditingController(),
    'education_expenditure': TextEditingController(),
    'year': TextEditingController(text: '2023'),
  };

  static const List<String> _incomeGroups = [
    'Low income',
    'Lower middle income',
    'Upper middle income',
    'High income',
  ];

  String _incomeGroup = 'Lower middle income';

  @override
  void dispose() {
    for (final controller in _controllers.values) {
      controller.dispose();
    }
    super.dispose();
  }

  double _number(String key) {
    return double.parse(_controllers[key]!.text.trim());
  }

  double? _optionalNumber(String key) {
    final value = _controllers[key]!.text.trim();

    if (value.isEmpty) return null;

    return double.parse(value);
  }

  void _submit() {
    if (widget.isLoading) return;
    if (!_formKey.currentState!.validate()) return;

    final input = PredictionInput(
      gdpGrowth: _number('gdp_growth'),
      gdpPerCapita: _number('gdp_per_capita'),
      inflation: _number('inflation'),
      urbanPopulationPct: _number('urban_population_pct'),
      populationGrowth: _number('population_growth'),
      agricultureEmployment: _number('agriculture_employment'),
      industryEmployment: _number('industry_employment'),
      femaleLaborParticipation:
          _number('female_labor_participation'),
      secondaryEnrollment:
          _optionalNumber('secondary_enrollment'),
      educationExpenditure:
          _optionalNumber('education_expenditure'),
      year: int.parse(_controllers['year']!.text.trim()),
      incomeGroup: _incomeGroup,
    );

    FocusScope.of(context).unfocus();
    widget.onPredict(input);
  }

  Widget _field(
    String key,
    String label, {
    String? unit,
    bool percentage = false,
    bool nonNegative = false,
    bool optional = false,
    bool year = false,
  }) {
    return PredictionInputField(
      label: label,
      controller: _controllers[key]!,
      unit: unit,
      requiredField: !optional,
      isPercentage: percentage,
      nonNegative: nonNegative,
      isYear: year,
    );
  }

  Widget _section(
    String title,
    List<Widget> fields, {
    String? subtitle,
  }) {
    return Padding(
      padding: const EdgeInsets.only(top: 24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              Expanded(
                child: Text(
                  title,
                  style: const TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.w700,
                    letterSpacing: -0.3,
                    color: Color(0xFF171717),
                  ),
                ),
              ),
              if (subtitle != null)
                Text(
                  subtitle,
                  style: const TextStyle(
                    fontSize: 10,
                    color: Color(0xFF737373),
                  ),
                ),
            ],
          ),
          const SizedBox(height: 13),
          LayoutBuilder(
            builder: (context, constraints) {
              const spacing = 12.0;

              final columns =
                  constraints.maxWidth >= 310 ? 2 : 1;

              final fieldWidth = (
                constraints.maxWidth -
                    spacing * (columns - 1)
              ) / columns;

              return Wrap(
                spacing: spacing,
                runSpacing: 17,
                children: [
                  for (final field in fields)
                    SizedBox(
                      width: fieldWidth,
                      child: field,
                    ),
                ],
              );
            },
          ),
        ],
      ),
    );
  }

  Widget _incomeGroupField() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Income group',
          style: TextStyle(
            fontSize: 11.5,
            fontWeight: FontWeight.w600,
            color: Color(0xFF262626),
          ),
        ),
        const SizedBox(height: 7),
        DropdownButtonFormField<String>(
          initialValue: _incomeGroup,
          isExpanded: true,
          icon: const Icon(
            Icons.keyboard_arrow_down,
            size: 19,
          ),
          style: const TextStyle(
            fontSize: 11,
            fontWeight: FontWeight.w500,
            color: Color(0xFF171717),
          ),
          decoration: const InputDecoration(
            contentPadding: EdgeInsets.symmetric(
              horizontal: 9,
              vertical: 12,
            ),
          ),
          items: _incomeGroups.map((group) {
            return DropdownMenuItem<String>(
              value: group,
              child: Text(
                group,
                overflow: TextOverflow.ellipsis,
              ),
            );
          }).toList(),
          onChanged: widget.isLoading
              ? null
              : (value) {
                  if (value != null) {
                    setState(() {
                      _incomeGroup = value;
                    });
                  }
                },
        ),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    return Form(
      key: _formKey,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _section(
            'Economic indicators',
            [
              _field(
                'gdp_growth',
                'GDP growth',
                unit: '%',
              ),
              _field(
                'gdp_per_capita',
                'GDP per capita',
                unit: 'USD',
                nonNegative: true,
              ),
              _field(
                'inflation',
                'Inflation',
                unit: '%',
              ),
            ],
          ),

          _section(
            'Demographics',
            [
              _field(
                'urban_population_pct',
                'Urban population',
                unit: '%',
                percentage: true,
              ),
              _field(
                'population_growth',
                'Population growth',
                unit: '%',
              ),
            ],
          ),

          _section(
            'Employment indicators',
            [
              _field(
                'agriculture_employment',
                'Agriculture employment',
                unit: '%',
                percentage: true,
              ),
              _field(
                'industry_employment',
                'Industry employment',
                unit: '%',
                percentage: true,
              ),
              _field(
                'female_labor_participation',
                'Female labour participation',
                unit: '%',
                percentage: true,
              ),
            ],
          ),

          _section(
            'Education indicators',
            [
              _field(
                'secondary_enrollment',
                'Secondary enrolment',
                unit: '%',
                optional: true,
                nonNegative: true,
              ),
              _field(
                'education_expenditure',
                'Education expenditure',
                optional: true,
                nonNegative: true,
              ),
            ],
            subtitle: 'Optional',
          ),

          _section(
            'Additional information',
            [
              _field(
                'year',
                'Year',
                year: true,
              ),
              _incomeGroupField(),
            ],
          ),

          const SizedBox(height: 26),

          SizedBox(
            width: double.infinity,
            height: 49,
            child: FilledButton(
              onPressed: widget.isLoading ? null : _submit,
              child: widget.isLoading
                  ? const SizedBox(
                      width: 19,
                      height: 19,
                      child: CircularProgressIndicator(
                        strokeWidth: 2,
                        color: Colors.white,
                      ),
                    )
                  : const Row(
                      mainAxisAlignment:
                          MainAxisAlignment.center,
                      children: [
                        Text('Generate prediction'),
                        SizedBox(width: 10),
                        Icon(
                          Icons.arrow_forward,
                          size: 17,
                        ),
                      ],
                    ),
            ),
          ),
        ],
      ),
    );
  }
}

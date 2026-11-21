
class PredictionInput {
  final double gdpGrowth;
  final double gdpPerCapita;
  final double inflation;
  final double urbanPopulationPct;
  final double populationGrowth;
  final double agricultureEmployment;
  final double industryEmployment;
  final double femaleLaborParticipation;
  final double? secondaryEnrollment;
  final double? educationExpenditure;
  final int year;
  final String incomeGroup;

  const PredictionInput({
    required this.gdpGrowth,
    required this.gdpPerCapita,
    required this.inflation,
    required this.urbanPopulationPct,
    required this.populationGrowth,
    required this.agricultureEmployment,
    required this.industryEmployment,
    required this.femaleLaborParticipation,
    this.secondaryEnrollment,
    this.educationExpenditure,
    required this.year,
    required this.incomeGroup,
  });

  Map<String, dynamic> toJson() {
    return {
      'gdp_growth': gdpGrowth,
      'gdp_per_capita': gdpPerCapita,
      'inflation': inflation,
      'urban_population_pct': urbanPopulationPct,
      'population_growth': populationGrowth,
      'agriculture_employment': agricultureEmployment,
      'industry_employment': industryEmployment,
      'female_labor_participation': femaleLaborParticipation,
      'secondary_enrollment': secondaryEnrollment,
      'education_expenditure': educationExpenditure,
      'year': year,
      'income_group': incomeGroup,
    };
  }
}

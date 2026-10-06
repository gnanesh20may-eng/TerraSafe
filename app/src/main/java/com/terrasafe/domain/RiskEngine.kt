package com.terrasafe.domain

data class RiskAssessment(
    val score: Int, // 0-100
    val level: String, // LOW, WATCH, HIGH, CRITICAL
    val supportingFactorsCount: Int,
    val confidence: Float,
    val passesFalseAlarmRule: Boolean,
    val topFactors: List<String>,
    val counterfactual: String
)

object RiskEngine {
    const val THRESHOLD_LOW_MAX = 24
    const val THRESHOLD_WATCH_MAX = 49
    const val THRESHOLD_HIGH_MAX = 74
    const val THRESHOLD_CRITICAL_MIN = 75

    const val WEIGHT_RAINFALL = 0.4f
    const val WEIGHT_SOIL = 30f
    const val WEIGHT_SLOPE = 0.3f
    const val WEIGHT_EARTHQUAKE = 5f

    fun assessRisk(
        rainfallMm: Float,
        soilMoisture: Float,
        slopeSteepness: Float,
        earthquakeMag: Float = 0f,
        supportingFactors: Int = 1,
        confidenceThreshold: Float = 0.7f
    ): RiskAssessment {
        val rawScore = (rainfallMm * WEIGHT_RAINFALL + soilMoisture * WEIGHT_SOIL + slopeSteepness * WEIGHT_SLOPE + earthquakeMag * WEIGHT_EARTHQUAKE).toInt()
        val score = rawScore.coerceIn(0, 100)

        val level = when {
            score >= THRESHOLD_CRITICAL_MIN -> "CRITICAL"
            score >= 50 -> "HIGH" // Wait, watch max is 49, so 50 is HIGH
            score >= 25 -> "WATCH"
            else -> "LOW"
        }

        val passesFalseAlarm = if (level == "CRITICAL") supportingFactors >= 2 else true
        val effectiveLevel = if (!passesFalseAlarm && level == "CRITICAL") "HIGH" else level
        val effectiveScore = if (!passesFalseAlarm && level == "CRITICAL") THRESHOLD_HIGH_MAX else score

        val factors = mutableListOf<String>()
        if (rainfallMm > 50f) factors.add("High rainfall (${rainfallMm}mm)")
        if (soilMoisture > 0.6f) factors.add("Elevated soil moisture")
        if (slopeSteepness > 35f) factors.add("Steep terrain gradient")
        if (earthquakeMag > 3.0f) factors.add("Seismic activity (M${earthquakeMag})")
        if (factors.isEmpty()) factors.add("Normal baseline stability")

        val counterfactual = if (effectiveScore >= 50) {
            "Reducing rainfall accumulation below 30mm or lowering saturation would decrease risk score by ~25 points."
        } else {
            "Current conditions are stable. No immediate mitigation required."
        }

        val computedConfidence = (effectiveScore / 100.0f + supportingFactors * 0.05f).coerceIn(0.5f, 0.95f)

        return RiskAssessment(
            score = effectiveScore,
            level = effectiveLevel,
            supportingFactorsCount = supportingFactors,
            confidence = computedConfidence,
            passesFalseAlarmRule = passesFalseAlarm,
            topFactors = factors,
            counterfactual = counterfactual
        )
    }

    fun levelFromScore(score: Int): String {
        return when {
            score >= THRESHOLD_CRITICAL_MIN -> "CRITICAL"
            score >= 50 -> "HIGH"
            score >= 25 -> "WATCH"
            else -> "LOW"
        }
    }
}

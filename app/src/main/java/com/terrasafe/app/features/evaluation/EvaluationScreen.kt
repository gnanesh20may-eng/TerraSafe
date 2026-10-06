package com.terrasafe.app.features.evaluation

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.terrasafe.domain.RiskEngine

@Composable
fun EvaluationScreen() {
    var rainfall by remember { mutableStateOf(40f) }
    var soilMoisture by remember { mutableStateOf(0.4f) }
    var slope by remember { mutableStateOf(30f) }
    var supportingFactors by remember { mutableStateOf(1) }

    val assessment = remember(rainfall, soilMoisture, slope, supportingFactors) {
        RiskEngine.assessRisk(rainfall, soilMoisture, slope, supportingFactors = supportingFactors)
    }

    val scrollState = rememberScrollState()

    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(scrollState)
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        Text("Risk Evaluation & What-If Simulator", style = MaterialTheme.typography.headlineMedium)

        Card(modifier = Modifier.fillMaxWidth()) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text("Current Risk Assessment", style = MaterialTheme.typography.titleLarge)
                Spacer(Modifier.height(8.dp))
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text("Score: ${assessment.score}/100", style = MaterialTheme.typography.headlineMedium)
                    Badge { Text(assessment.level) }
                }
                Spacer(Modifier.height(8.dp))
                if (!assessment.passesFalseAlarmRule) {
                    Text("⚠️ False-Alarm Rule Applied: CRITICAL downgraded to HIGH due to < 2 supporting factors.", color = MaterialTheme.colorScheme.error)
                }
                Spacer(Modifier.height(8.dp))
                Text("Top Factors:", style = MaterialTheme.typography.titleSmall)
                assessment.topFactors.forEach { factor ->
                    Text("• $factor")
                }
                Spacer(Modifier.height(8.dp))
                Text("Counterfactual Analysis:", style = MaterialTheme.typography.titleSmall)
                Text(assessment.counterfactual, style = MaterialTheme.typography.bodyMedium)
            }
        }

        Card(modifier = Modifier.fillMaxWidth()) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text("What-If Rainfall Simulator", style = MaterialTheme.typography.titleLarge)
                Spacer(Modifier.height(8.dp))
                Text("Rainfall: ${rainfall.toInt()} mm")
                Slider(
                    value = rainfall,
                    onValueChange = { rainfall = it },
                    valueRange = 0f..200f
                )
                Spacer(Modifier.height(8.dp))
                Text("Supporting Factors: $supportingFactors")
                Slider(
                    value = supportingFactors.toFloat(),
                    onValueChange = { supportingFactors = it.toInt() },
                    valueRange = 1f..4f,
                    steps = 2
                )
            }
        }

        Card(modifier = Modifier.fillMaxWidth()) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text("Data-Source Health", style = MaterialTheme.typography.titleLarge)
                Spacer(Modifier.height(8.dp))
                Text("• Open-Meteo Weather: OK (Live)")
                Text("• USGS Earthquake Feed: OK (Live)")
                Text("• IMD / MOSDAC Satellite: STALE")
            }
        }

        Text(
            text = "AI-based risk estimation. Early-warning decision support. This prototype does not replace official disaster-management warnings.",
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
    }
}

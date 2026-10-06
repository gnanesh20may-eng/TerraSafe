package com.terrasafe.app.features.about

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

@Composable
fun AboutScreen() {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        Text("About TerraSafe", style = MaterialTheme.typography.headlineMedium)
        Card(modifier = Modifier.fillMaxWidth()) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text("Version: 1.0.0 (Tamil Nadu Edition)", style = MaterialTheme.typography.titleLarge)
                Spacer(Modifier.height(8.dp))
                Text("Data Sources: Open-Meteo, USGS, GPM IMERG, IMD/MOSDAC.")
                Spacer(Modifier.height(8.dp))
                Text("AI-based risk estimation. Early-warning decision support. This prototype does not replace official disaster-management warnings.", style = MaterialTheme.typography.bodySmall)
            }
        }
    }
}

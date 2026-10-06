package com.terrasafe.app.features.settings

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

@Composable
fun SettingsScreen() {
    var backendUrl by remember { mutableStateOf("http://10.0.2.2:8000/api/v1/") }
    var voiceEnabled by remember { mutableStateOf(true) }
    var meshEnabled by remember { mutableStateOf(false) }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        Text("Settings & Preferences", style = MaterialTheme.typography.headlineMedium)

        OutlinedTextField(
            value = backendUrl,
            onValueChange = { backendUrl = it },
            label = { Text("Backend Base URL") },
            modifier = Modifier.fillMaxWidth()
        )

        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text("Voice Alerts (Tamil)")
            Switch(checked = voiceEnabled, onCheckedChange = { voiceEnabled = it })
        }

        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Column(modifier = Modifier.weight(1f)) {
                Text("Nearby Connections Mesh")
                Text("Participate in anonymous peer relay", style = MaterialTheme.typography.bodySmall)
            }
            Switch(checked = meshEnabled, onCheckedChange = { meshEnabled = it })
        }
    }
}

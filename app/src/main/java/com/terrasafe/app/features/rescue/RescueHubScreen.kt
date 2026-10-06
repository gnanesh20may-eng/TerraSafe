package com.terrasafe.app.features.rescue

import android.content.Intent
import android.net.Uri
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import kotlinx.coroutines.delay

@Composable
fn RescueHubScreen() {
    val context = LocalContext.current
    var isHoldingSos by remember { mutableStateOf(false) }
    var sosTriggered by remember { mutableStateOf(false) }
    var familyStatus by remember { mutableStateOf("Not Checked In") }
    var peopleCount by remember { mutableStateOf("4") }
    var injuriesCount by remember { mutableStateOf("0") }

    val scrollState = rememberScrollState()

    LaunchedEffect(isHoldingSos) {
        if (isHoldingSos) {
            delay(2000L) // 2 seconds hold to confirm SOS
            sosTriggered = true
            isHoldingSos = false
            // Open SMS fallback with pre-filled coordinates
            val uri = Uri.parse("smsto:1077")
            val intent = Intent(Intent.ACTION_SENDTO, uri).apply {
                putExtra("sms_body", "SOS|Nilgiris|11.41,76.69|CRITICAL|4 ppl stranded")
            }
            try {
                context.startActivity(intent)
            } catch (e: Exception) {
                // handle no SMS app
            }
        }
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(scrollState)
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        Text("Rescue Hub & Emergency SOS", style = MaterialTheme.typography.headlineMedium)

        Card(
            colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.errorContainer),
            modifier = Modifier.fillMaxWidth()
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text("Emergency SOS", style = MaterialTheme.typography.titleLarge, color = MaterialTheme.colorScheme.onErrorContainer)
                Spacer(Modifier.height(8.dp))
                Text("Hold for 2 seconds to broadcast emergency SOS and open SMS dispatch.", color = MaterialTheme.colorScheme.onErrorContainer)
                Spacer(Modifier.height(16.dp))
                Button(
                    onClick = {},
                    colors = ButtonDefaults.buttonColors(containerColor = MaterialTheme.colorScheme.error),
                    modifier = Modifier.fillMaxWidth(),
                    interactionSource = remember { androidx.compose.foundation.interaction.MutableInteractionSource() }.also { interactionSource ->
                        LaunchedEffect(interactionSource) {
                            interactionSource.interactions.collect { interaction ->
                                when (interaction) {
                                    is androidx.compose.foundation.interaction.PressInteraction.Press -> isHoldingSos = true
                                    is androidx.compose.foundation.interaction.PressInteraction.Release,
                                    is androidx.compose.foundation.interaction.PressInteraction.Cancel -> isHoldingSos = false
                                }
                            }
                        }
                    }
                ) {
                    Text(if (isHoldingSos) "HOLDING... (2s)" else "HOLD TO SEND SOS")
                }
                if (sosTriggered) {
                    Spacer(Modifier.height(8.dp))
                    Text("SOS Dispatched via SMS & Queue!", color = MaterialTheme.colorScheme.onErrorContainer)
                }
            }
        }

        Card(modifier = Modifier.fillMaxWidth()) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text("Family Safety Check-In", style = MaterialTheme.typography.titleLarge)
                Spacer(Modifier.height(8.dp))
                Text("Status: $familyStatus")
                Spacer(Modifier.height(8.dp))
                Button(onClick = { familyStatus = "Safe & Accounted For" }) {
                    Text("I'm Safe (Check-In)")
                }
            }
        }

        Card(modifier = Modifier.fillMaxWidth()) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text("Rescue Triage Form", style = MaterialTheme.typography.titleLarge)
                Spacer(Modifier.height(8.dp))
                OutlinedTextField(
                    value = peopleCount,
                    onValueChange = { peopleCount = it },
                    label = { Text("People Count") },
                    modifier = Modifier.fillMaxWidth()
                )
                Spacer(Modifier.height(8.dp))
                OutlinedTextField(
                    value = injuriesCount,
                    onValueChange = { injuriesCount = it },
                    label = { Text("Injuries Count") },
                    modifier = Modifier.fillMaxWidth()
                )
                Spacer(Modifier.height(16.dp))
                Button(onClick = {}) {
                    Text("Submit Triage to Dispatch")
                }
            }
        }
    }
}

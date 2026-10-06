package com.terrasafe.app.features.alerts

import android.speech.tts.TextToSpeech
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import com.terrasafe.domain.AlertState
import com.terrasafe.domain.AlertStateMachine
import com.terrasafe.domain.AuditEntry
import com.terrasafe.domain.BilingualText
import java.util.Locale

data class AlertUiModel(
    val id: String,
    val location: String,
    val riskLevel: String,
    val state: AlertState,
    val auditEntries: List<AuditEntry>,
    val language: String = "en"
)

@Composable
fun AlertsScreen() {
    val context = LocalContext.current
    var tts by remember { mutableStateOf<TextToSpeech?>(null) }
    var ttsInitialized by remember { mutableStateOf(false) }

    DisposableEffect(context) {
        val engine = TextToSpeech(context) { status ->
            if (status == TextToSpeech.SUCCESS) {
                tts?.language = Locale("ta", "IN")
                ttsInitialized = true
            }
        }
        tts = engine
        onDispose {
            engine.stop()
            engine.shutdown()
        }
    }

    val h1 = remember { AlertStateMachine.computeHash("0", 1, "Created", "admin", "{}") }
    val initialAudit = listOf(AuditEntry(1, "Created", "admin", "{}", "0", h1))

    var alerts by remember {
        mutableStateOf(
            listOf(
                AlertUiModel("1", "Ooty, Nilgiris", "CRITICAL", AlertState.NEW, initialAudit, "en"),
                AlertUiModel("2", "Kodaikanal, Dindigul", "HIGH", AlertState.ACKNOWLEDGED, initialAudit, "ta")
            )
        )
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        Text("Active Alerts & Audit Trail", style = MaterialTheme.typography.headlineMedium)

        LazyColumn(
            modifier = Modifier.fillMaxSize(),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            items(alerts) { alert ->
                val isChainValid = AlertStateMachine.verifyAuditChain(alert.auditEntries)
                val message = BilingualText.getWarningMessage(alert.riskLevel, alert.location, alert.language)

                Card(modifier = Modifier.fillMaxWidth()) {
                    Column(modifier = Modifier.padding(16.dp)) {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Text(alert.location, style = MaterialTheme.typography.titleLarge)
                            Badge { Text(alert.state.name) }
                        }
                        Spacer(Modifier.height(8.dp))
                        Text(message, style = MaterialTheme.typography.bodyMedium)
                        Spacer(Modifier.height(8.dp))
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            if (isChainValid) {
                                Text("✓ Integrity Verified", color = MaterialTheme.colorScheme.primary)
                            } else {
                                Text("✕ Chain Broken", color = MaterialTheme.colorScheme.error)
                            }

                            Button(onClick = {
                                if (ttsInitialized) {
                                    tts?.speak(message, TextToSpeech.QUEUE_FLUSH, null, null)
                                }
                            }) {
                                Text("Speak (தமிழ்)")
                            }
                        }

                        Spacer(Modifier.height(8.dp))
                        val next = AlertStateMachine.nextState(alert.state)
                        if (next != null) {
                            Button(onClick = {
                                val lastHash = alert.auditEntries.last().entryHash
                                val seq = alert.auditEntries.size + 1
                                val newHash = AlertStateMachine.computeHash(lastHash, seq, next.name, "operator", "{}")
                                val newAudit = alert.auditEntries + AuditEntry(seq, next.name, "operator", "{}", lastHash, newHash)
                                alerts = alerts.map { if (it.id == alert.id) it.copy(state = next, auditEntries = newAudit) else it }
                            }) {
                                Text("Advance to ${next.name}")
                            }
                        }
                    }
                }
            }
        }
    }
}

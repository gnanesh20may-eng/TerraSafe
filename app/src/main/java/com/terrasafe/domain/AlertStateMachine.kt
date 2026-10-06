package com.terrasafe.domain

import java.security.MessageDigest

enum class AlertState {
    NEW, ACKNOWLEDGED, ACTIVE, RESOLVED
}

data class AuditEntry(
    val sequence: Int,
    val event: String,
    val actor: String,
    val payload: String,
    val previousHash: String,
    val entryHash: String
)

object AlertStateMachine {
    fun nextState(current: AlertState): AlertState? {
        return when (current) {
            AlertState.NEW -> AlertState.ACKNOWLEDGED
            AlertState.ACKNOWLEDGED -> AlertState.ACTIVE
            AlertState.ACTIVE -> AlertState.RESOLVED
            AlertState.RESOLVED -> null
        }
    }

    fun computeHash(previousHash: String, sequence: Int, event: String, actor: String, payload: String): String {
        val input = "$previousHash|$sequence|$event|$actor|$payload"
        val bytes = MessageDigest.getInstance("SHA-256").digest(input.toByteArray(Charsets.UTF_8))
        return bytes.joinToString("") { "%02x".format(it) }
    }

    fun verifyAuditChain(entries: List<AuditEntry>): Boolean {
        if (entries.isEmpty()) return true
        var expectedPrevious = "0"
        for (entry in entries) {
            if (entry.previousHash != expectedPrevious) return false
            val recalculated = computeHash(entry.previousHash, entry.sequence, entry.event, entry.actor, entry.payload)
            if (recalculated != entry.entryHash) return false
            expectedPrevious = entry.entryHash
        }
        return true
    }
}

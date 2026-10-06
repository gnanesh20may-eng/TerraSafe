package com.terrasafe.domain

import org.junit.Assert.*
import org.junit.Test

class HashChainTest {
    @Test
    fun testAuditChainVerification() {
        val h1 = AlertStateMachine.computeHash("0", 1, "Created", "admin", "{}")
        val h2 = AlertStateMachine.computeHash(h1, 2, "Approved", "officer", "{}")

        val entries = listOf(
            AuditEntry(1, "Created", "admin", "{}", "0", h1),
            AuditEntry(2, "Approved", "officer", "{}", h1, h2)
        )

        assertTrue(AlertStateMachine.verifyAuditChain(entries))

        // Tamper test
        val tampered = listOf(
            AuditEntry(1, "Created", "admin", "{}", "0", "badhash"),
            AuditEntry(2, "Approved", "officer", "{}", h1, h2)
        )
        assertFalse(AlertStateMachine.verifyAuditChain(tampered))
    }
}

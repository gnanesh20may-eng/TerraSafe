package com.terrasafe.domain

import org.junit.Assert.*
import org.junit.Test

class BilingualMessageTest {
    @Test
    fun testBilingualGeneration() {
        val msgEn = BilingualText.getWarningMessage("CRITICAL", "Ooty", "en")
        assertTrue(msgEn.contains("CRITICAL WARNING"))
        assertTrue(msgEn.contains("Ooty"))

        val msgTa = BilingualText.getWarningMessage("CRITICAL", "Ooty", "ta")
        assertTrue(msgTa.contains("கட்டாய எச்சரிக்கை"))
        assertTrue(msgTa.contains("Ooty"))
    }
}

package com.terrasafe.domain

import org.junit.Assert.*
import org.junit.Test

class RiskEngineTest {
    @Test
    fun testRiskLevelsAndThresholds() {
        val low = RiskEngine.assessRisk(5f, 0.1f, 5f)
        assertEquals("LOW", low.level)

        val watch = RiskEngine.assessRisk(30f, 0.4f, 20f)
        assertEquals("WATCH", watch.level)

        val high = RiskEngine.assessRisk(80f, 0.6f, 30f)
        assertEquals("HIGH", high.level)

        val critical = RiskEngine.assessRisk(150f, 0.9f, 50f, supportingFactors = 2)
        assertEquals("CRITICAL", critical.level)
    }

    @Test
    fun testBoundaries() {
        assertEquals("LOW", RiskEngine.levelFromScore(24))
        assertEquals("WATCH", RiskEngine.levelFromScore(25))

        assertEquals("WATCH", RiskEngine.levelFromScore(49))
        assertEquals("HIGH", RiskEngine.levelFromScore(50))

        assertEquals("HIGH", RiskEngine.levelFromScore(74))
        assertEquals("CRITICAL", RiskEngine.levelFromScore(75))
    }

    @Test
    fun testFalseAlarmRule() {
        val critOneFactor = RiskEngine.assessRisk(160f, 0.95f, 50f, supportingFactors = 1)
        assertFalse(critOneFactor.passesFalseAlarmRule)
        assertEquals("HIGH", critOneFactor.level)

        val critTwoFactors = RiskEngine.assessRisk(160f, 0.95f, 50f, supportingFactors = 2)
        assertTrue(critTwoFactors.passesFalseAlarmRule)
        assertEquals("CRITICAL", critTwoFactors.level)
    }
}

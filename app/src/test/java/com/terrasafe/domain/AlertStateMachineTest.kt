package com.terrasafe.domain

import org.junit.Assert.*
import org.junit.Test

class AlertStateMachineTest {
    @Test
    fun testTransitions() {
        assertEquals(AlertState.ACKNOWLEDGED, AlertStateMachine.nextState(AlertState.NEW))
        assertEquals(AlertState.ACTIVE, AlertStateMachine.nextState(AlertState.ACKNOWLEDGED))
        assertEquals(AlertState.RESOLVED, AlertStateMachine.nextState(AlertState.ACTIVE))
        assertNull(AlertStateMachine.nextState(AlertState.RESOLVED))
    }
}

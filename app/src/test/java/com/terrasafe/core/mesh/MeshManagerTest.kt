package com.terrasafe.core.mesh

import org.junit.Assert.*
import org.junit.Test
import java.util.UUID

class MeshManagerTest {
    @Test
    fun testDeduplicationAndExpiry() {
        val manager = NearbyMeshManager(maxHops = 3, expiryMs = 60000L)
        val id = UUID.randomUUID()
        val beacon = MeshBeacon(id, 1, 11.41f, 76.69f, 1, System.currentTimeMillis())

        assertTrue(manager.processIncomingBeacon(beacon))
        assertFalse(manager.processIncomingBeacon(beacon)) // Duplicate should be rejected
        assertEquals(1, manager.activeBeaconCount())
    }

    @Test
    fun testHopLimit() {
        val manager = NearbyMeshManager(maxHops = 2)
        val id = UUID.randomUUID()
        val beacon = MeshBeacon(id, 1, 11.41f, 76.69f, 3, System.currentTimeMillis()) // hop 3 > max 2

        assertFalse(manager.processIncomingBeacon(beacon))
    }
}

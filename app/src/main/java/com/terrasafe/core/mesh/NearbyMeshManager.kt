package com.terrasafe.core.mesh

import java.nio.ByteBuffer
import java.util.UUID

data class MeshBeacon(
    val id: UUID,
    val statusCode: Byte,
    val coarseLat: Float,
    val coarseLon: Float,
    val hopCount: Byte,
    val timestamp: Long
) {
    fun toByteArray(): ByteArray {
        val buffer = ByteBuffer.allocate(21)
        buffer.putLong(id.mostSignificantBits)
        buffer.putLong(id.leastSignificantBits)
        buffer.put(statusCode)
        buffer.putFloat(coarseLat)
        // For 20-byte pack representation, store compressed
        return buffer.array()
    }

    companion object {
        fun fromByteArray(bytes: ByteArray): MeshBeacon? {
            if (bytes.size < 17) return null
            val buffer = ByteBuffer.wrap(bytes)
            val mostSig = buffer.long
            val leastSig = buffer.long
            val status = buffer.get()
            val lat = if (buffer.remaining() >= 4) buffer.float else 0f
            val lon = if (buffer.remaining() >= 4) buffer.float else 0f
            return MeshBeacon(
                id = UUID(mostSig, leastSig),
                statusCode = status,
                coarseLat = lat,
                coarseLon = lon,
                hopCount = 1,
                timestamp = System.currentTimeMillis()
            )
        }
    }
}

class NearbyMeshManager(private val maxHops: Byte = 3, private val expiryMs: Long = 60000L) {
    private val seenBeacons = mutableMapOf<UUID, Long>()

    fun processIncomingBeacon(beacon: MeshBeacon): Boolean {
        val now = System.currentTimeMillis()
        // Clean expired
        seenBeacons.entries.removeAll { now - it.value > expiryMs }

        if (seenBeacons.containsKey(beacon.id)) return false // Duplicate
        if (beacon.hopCount > maxHops) return false // Exceeded hop limit

        seenBeacons[beacon.id] = beacon.timestamp
        return true
    }

    fun activeBeaconCount(): Int {
        val now = System.currentTimeMillis()
        seenBeacons.entries.removeAll { now - it.value > expiryMs }
        return seenBeacons.size
    }
}

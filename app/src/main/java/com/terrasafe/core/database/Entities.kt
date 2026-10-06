package com.terrasafe.core.database

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "risk_scores")
data class RiskScoreEntity(
    @PrimaryKey val locationId: String,
    val locationName: String,
    val score: Int,
    val level: String,
    val timestamp: Long,
    val disclaimer: String
)

@Entity(tableName = "alerts")
data class AlertEntity(
    @PrimaryKey val id: String,
    val zoneId: String,
    val location: String,
    val riskScore: Int,
    val riskLevel: String,
    val status: String,
    val message: String,
    val language: String,
    val createdAt: String,
    val updatedAt: String
)

@Entity(tableName = "saved_places")
data class SavedPlaceEntity(
    @PrimaryKey val id: String,
    val name: String,
    val area: String,
    val customThreshold: Int = 75
)

@Entity(tableName = "sos_queue")
data class SosQueueEntity(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val type: String,
    val latitude: Double,
    val longitude: Double,
    val message: String,
    val timestamp: Long,
    val status: String // PENDING, SENT, FAILED
)

@Entity(tableName = "cached_road_edges")
data class CachedRoadEntity(
    @PrimaryKey val edgeId: String,
    val fromNode: String,
    val toNode: String,
    val distanceKm: Double,
    val riskScore: Int,
    val isClosed: Boolean
)

package com.terrasafe.core.database

import androidx.room.*
import kotlinx.coroutines.flow.Flow

@Dao
interface RiskScoreDao {
    @Query("SELECT * FROM risk_scores")
    fun observeAll(): Flow<List<RiskScoreEntity>>

    @Query("SELECT * FROM risk_scores WHERE locationId = :id")
    suspend fun getById(id: String): RiskScoreEntity?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(risk: RiskScoreEntity)
}

@Dao
interface AlertDao {
    @Query("SELECT * FROM alerts")
    fun observeAll(): Flow<List<AlertEntity>>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertAll(alerts: List<AlertEntity>)

    @Query("UPDATE alerts SET status = :status WHERE id = :id")
    suspend fun updateStatus(id: String, status: String)
}

@Dao
interface SavedPlaceDao {
    @Query("SELECT * FROM saved_places")
    fun observeAll(): Flow<List<SavedPlaceEntity>>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(place: SavedPlaceEntity)

    @Delete
    suspend fun delete(place: SavedPlaceEntity)
}

@Dao
interface SosQueueDao {
    @Query("SELECT * FROM sos_queue WHERE status = 'PENDING'")
    suspend fun getPending(): List<SosQueueEntity>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(item: SosQueueEntity)

    @Query("UPDATE sos_queue SET status = :status WHERE id = :id")
    suspend fun updateStatus(id: Long, status: String)
}

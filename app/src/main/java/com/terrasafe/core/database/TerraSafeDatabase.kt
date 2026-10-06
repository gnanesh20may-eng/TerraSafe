package com.terrasafe.core.database

import android.content.Context
import androidx.room.Database
import androidx.room.Room
import androidx.room.RoomDatabase
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.android.qualifiers.ApplicationContext
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

@Database(
    entities = [RiskScoreEntity::class, AlertEntity::class, SavedPlaceEntity::class, SosQueueEntity::class, CachedRoadEntity::class],
    version = 1,
    exportSchema = false
)
abstract class TerraSafeDatabase : RoomDatabase() {
    abstract fun riskScoreDao(): RiskScoreDao
    abstract fun alertDao(): AlertDao
    abstract fun savedPlaceDao(): SavedPlaceDao
    abstract fun sosQueueDao(): SosQueueDao
}

@Module
@InstallIn(SingletonComponent::class)
object DatabaseModule {

    @Provides
    @Singleton
    fun provideDatabase(@ApplicationContext context: Context): TerraSafeDatabase {
        return Room.databaseBuilder(
            context,
            TerraSafeDatabase::class.java,
            "terrasafe_db"
        ).fallbackToDestructiveMigration().build()
    }

    @Provides
    fun provideRiskScoreDao(db: TerraSafeDatabase): RiskScoreDao = db.riskScoreDao()

    @Provides
    fun provideAlertDao(db: TerraSafeDatabase): AlertDao = db.alertDao()

    @Provides
    fun provideSavedPlaceDao(db: TerraSafeDatabase): SavedPlaceDao = db.savedPlaceDao()

    @Provides
    fun provideSosQueueDao(db: TerraSafeDatabase): SosQueueDao = db.sosQueueDao()
}

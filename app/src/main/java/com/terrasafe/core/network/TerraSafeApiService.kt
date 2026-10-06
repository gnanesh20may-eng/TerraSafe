package com.terrasafe.core.network

import kotlinx.serialization.Serializable
import retrofit2.Response
import retrofit2.http.*

@Serializable
data class RiskResponseDto(
    val location: String,
    val status: String,
    val risk_score: Int = 50,
    val risk_level: String = "WATCH",
    val disclaimer: String = ""
)

@Serializable
data class AlertDto(
    val id: String,
    val zone_id: String,
    val location: String,
    val risk_score: Int,
    val risk_level: String,
    val status: String,
    val message: String,
    val language: String,
    val created_at: String,
    val updated_at: String
)

@Serializable
data class AlertsListResponse(
    val alerts: List<AlertDto>
)

interface TerraSafeApiService {
    @GET("health")
    suspend fun checkHealth(): Response<Map<String, String>>

    @GET("risk/{location}")
    suspend fun getRiskForLocation(@Path("location") location: String): Response<RiskResponseDto>

    @GET("alerts")
    suspend fun listAlerts(@Query("limit") limit: Int = 100): Response<AlertsListResponse>

    @POST("alerts/{id}/transition")
    suspend fun transitionAlert(@Path("id") id: String, @Body body: Map<String, String>): Response<AlertDto>

    @POST("simulate")
    suspend fun simulateScenario(@Body body: Map<String, @JvmSuppressWildcards Any>): Response<Map<String, String>>
}

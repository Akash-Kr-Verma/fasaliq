package com.fasaliq.app.api

import com.fasaliq.app.models.*
import retrofit2.Response
import retrofit2.http.*

interface ApiService {

    @POST("api/auth/register")
    suspend fun register(
        @Body request: RegisterRequest
    ): Response<RegisterResponse>

    @POST("api/auth/login")
    suspend fun login(
        @Body request: LoginRequest
    ): Response<LoginResponse>

    @POST("api/farmer/profile")
    suspend fun saveProfile(
        @Header("Authorization") token: String,
        @Body request: FarmerProfileRequest
    ): Response<Map<String, Any>>

    @GET("api/farmer/recommend/{user_id}")
    suspend fun getRecommendation(
        @Header("Authorization") token: String,
        @Path("user_id") userId: Int,
        @Query("season") season: String
    ): Response<RecommendationResponse>

    @POST("api/farmer/select-crop")
    suspend fun selectCrop(
        @Header("Authorization") token: String,
        @Body request: CropSelectRequest
    ): Response<Map<String, Any>>

    @POST("api/crisp/anomaly-recovery")
    suspend fun getAnomalyRecovery(
        @Header("Authorization") token: String,
        @Body request: AnomalyRequest
    ): Response<AnomalyResponse>

    @POST("api/buyer/interest")
    suspend fun placeBuyerInterest(
        @Header("Authorization") token: String,
        @Body request: BuyerInterestRequest
    ): Response<Map<String, Any>>

    @GET("api/buyer/availability")
    suspend fun getCropAvailability(
        @Header("Authorization") token: String,
        @Query("district") district: String,
        @Query("season") season: String
    ): Response<Map<String, Any>>
    @POST("api/chat/start")
    suspend fun startChatSession(
        @Body request: Map<String, Int>
    ): Response<Map<String, Any>>

    @POST("api/chat/message")
    suspend fun sendChatMessage(
        @Body request: ChatMessageRequest
    ): Response<Map<String, Any>>

    @POST("api/harvest/start")
    suspend fun startHarvest(
        @Header("Authorization") token: String,
        @Body request: StartHarvestRequest
    ): Response<Map<String, Any>>

    @GET("api/harvest/active/{farmer_id}")
    suspend fun getActiveHarvests(
        @Header("Authorization") token: String,
        @Path("farmer_id") farmerId: Int
    ): Response<ActiveHarvestsResponse>

    @GET("api/harvest/history/{farmer_id}")
    suspend fun getHarvestHistory(
        @Header("Authorization") token: String,
        @Path("farmer_id") farmerId: Int
    ): Response<Map<String, Any>>

    @POST("api/harvest/end")
    suspend fun endHarvest(
        @Header("Authorization") token: String,
        @Body request: EndHarvestRequest
    ): Response<Map<String, Any>>

    @GET("api/harvest/recommend/{farmer_id}")
    suspend fun getHarvestRecommendation(
        @Header("Authorization") token: String,
        @Path("farmer_id") farmerId: Int,
        @Query("season") season: String,
        @Query("start_month") startMonth: Int,
        @Query("end_month") endMonth: Int,
        @Query("field_size") fieldSize: Double,
        @Query("soil_type") soilType: String,
        @Query("irrigation") irrigation: String,
        @Query("income_level") incomeLevel: String,
        @Query("district") district: String
    ): Response<RecommendationResponse>
}
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
}
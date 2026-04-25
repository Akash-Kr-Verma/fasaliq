package com.fasaliq.app.models

data class RegisterRequest(
    val name: String,
    val phone: String,
    val email: String?,
    val password: String,
    val role: String,
    val district: String,
    val state: String = "Maharashtra"
)

data class LoginRequest(
    val phone: String,
    val password: String
)

data class LoginResponse(
    val access_token: String,
    val token_type: String,
    val role: String,
    val user_id: Int,
    val name: String
)

data class FarmerProfileRequest(
    val user_id: Int,
    val field_size: Double,
    val soil_type: String,
    val irrigation: String,
    val last_crop: String?,
    val economic_tier: String = "small"
)

data class RecommendationCrop(
    val crop_name: String,
    val season: String,
    val score: Double,
    val income_estimate: Double,
    val has_msp: Boolean,
    val msp: Double,
    val factors: Factors
)

data class Factors(
    val profit: Double,
    val soil_water_fit: Double,
    val market_demand: Double,
    val msp_safety: Double,
    val switch_risk: Double
)

data class RecommendationResponse(
    val user_id: Int,
    val district: String,
    val season: String,
    val top_3_recommendations: List<RecommendationCrop>
)

data class CropSelectRequest(
    val user_id: Int,
    val crop_name: String,
    val season: String
)

data class AnomalyRequest(
    val anomaly_type: String
)

data class RecoveryPlan(
    val title: String,
    val steps: List<String>,
    val severity: String
)

data class AnomalyResponse(
    val anomaly_type: String,
    val recovery_plan: RecoveryPlan
)

data class BuyerInterestRequest(
    val buyer_id: Int,
    val crop_name: String,
    val district: String,
    val quantity: Double,
    val offered_price: Double
)

data class RegisterResponse(
    val message: String,
    val user_id: Int,
    val name: String,
    val role: String
)

data class ChatMessageRequest(
    val session_id: String,
    val message: String,
    val message_type: String = "text",
    val image_base64: String? = null
)
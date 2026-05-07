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

data class OldRecommendationResponse(
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

data class StartHarvestRequest(
    val farmer_id: Int,
    val field_name: String,
    val crop_name: String,
    val season: String,
    val start_month: Int,
    val end_month: Int,
    val field_size: Double,
    val soil_type: String = "loamy",
    val irrigation: String = "borewell",
    val income_level: String = "middle",
    val expected_days: Int = 120,
    val farmer_accepted_recommendation: Boolean = true
)

data class HarvestItem(
    val harvest_id: Int,
    val field_name: String,
    val crop_name: String,
    val season: String,
    val field_size: Double,
    val soil_type: String?,
    val irrigation: String?,
    val days_remaining: Int?,
    val progress_percent: Int,
    val health_status: String,
    val active_anomalies: Int,
    val status: String
)

data class ActiveHarvestsResponse(
    val farmer_id: Int,
    val active_count: Int,
    val harvests: List<HarvestItem>
)

data class EndHarvestRequest(
    val harvest_id: Int,
    val end_feedback: String,
    val actual_yield: Double?,
    val income_earned: Double?,
    val notes: String?
)

data class CropRecommendation(
    val crop_name: String,
    val season: String,
    val score: Double,
    val income_estimate: Double,
    val has_msp: Boolean,
    val msp: Double,
    val reasons: List<String>
)

data class RecommendationResponse(
    val farmer_id: Int,
    val district: String,
    val season: String,
    val start_month: Int,
    val end_month: Int,
    val income_level: String,
    val recommendations: List<CropRecommendation>,
    val buyer_demand_active: Int
)

data class MatchedBuyer(
    val interest_id: Int,
    val buyer_id: Int,
    val buyer_name: String,
    val buyer_district: String,
    val quantity_kg: Double,
    val offered_price_per_kg: Double,
    val total_value: Double,
    val same_district: Boolean,
    val status: String
)

data class BuyerMatchResponse(
    val harvest_id: Int,
    val crop_name: String,
    val field_name: String,
    val farmer_district: String,
    val matched_buyers: List<MatchedBuyer>,
    val total: Int
)

data class AnomalySummary(
    val type: String,
    val description: String,
    val status: String,
    val reported_at: String?
)

data class HarvestHistoryItem(
    val harvest_id: Int,
    val field_name: String,
    val crop_name: String,
    val season: String,
    val field_size: Double,
    val sowing_date: String?,
    val ended_at: String?,
    val duration_days: Int?,
    val actual_yield: Double?,
    val income_earned: Double?,
    val end_feedback: String?,
    val health_status: String,
    val notes: String?,
    val anomaly_count: Int,
    val anomalies: List<AnomalySummary>,
    val farmer_accepted_recommendation: Boolean?
)

data class HarvestHistoryResponse(
    val farmer_id: Int,
    val total_seasons: Int,
    val total_income_earned: Double,
    val harvests: List<HarvestHistoryItem>
)
package com.fasaliq.app.ui.farmer

import android.content.Intent
import android.os.Bundle
import android.view.View
import android.widget.*
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.fasaliq.app.MainActivity
import com.fasaliq.app.R
import com.fasaliq.app.api.RetrofitClient
import com.fasaliq.app.models.AnomalyRequest
import com.fasaliq.app.models.FarmerProfileRequest
import com.fasaliq.app.utils.SessionManager
import kotlinx.coroutines.launch

class FarmerDashboardActivity : AppCompatActivity() {

    private lateinit var session: SessionManager

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_farmer_dashboard)

        session = SessionManager(this)

        val tvWelcome = findViewById<TextView>(R.id.tvWelcome)
        val etFieldSize = findViewById<EditText>(R.id.etFieldSize)
        val etSoilType = findViewById<EditText>(R.id.etSoilType)
        val etIrrigation = findViewById<EditText>(R.id.etIrrigation)
        val etLastCrop = findViewById<EditText>(R.id.etLastCrop)
        val etSeason = findViewById<EditText>(R.id.etSeason)
        val btnGetRec = findViewById<Button>(R.id.btnGetRecommendation)
        val tvResults = findViewById<TextView>(R.id.tvResults)
        val etAnomalyType = findViewById<EditText>(R.id.etAnomalyType)
        val btnGetRecovery = findViewById<Button>(R.id.btnGetRecovery)
        val tvRecovery = findViewById<TextView>(R.id.tvRecovery)
        val btnLogout = findViewById<Button>(R.id.btnLogout)

        tvWelcome.text = "Welcome, ${session.getName()}"

        btnLogout.setOnClickListener {
            session.clearSession()
            startActivity(Intent(this, MainActivity::class.java))
            finish()
        }

        btnGetRec.setOnClickListener {
            val fieldSize = etFieldSize.text.toString().trim()
            val soilType = etSoilType.text.toString().trim()
            val irrigation = etIrrigation.text.toString().trim()
            val lastCrop = etLastCrop.text.toString().trim()
            val season = etSeason.text.toString().trim()

            if (fieldSize.isEmpty() || soilType.isEmpty() ||
                irrigation.isEmpty() || season.isEmpty()) {
                Toast.makeText(this,
                    "Please fill field size, soil, irrigation and season",
                    Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }

            btnGetRec.isEnabled = false
            btnGetRec.text = "Getting recommendation..."

            lifecycleScope.launch {
                try {
                    val profileResponse = RetrofitClient.instance.saveProfile(
                        session.getBearerToken(),
                        FarmerProfileRequest(
                            user_id = session.getUserId(),
                            field_size = fieldSize.toDouble(),
                            soil_type = soilType,
                            irrigation = irrigation,
                            last_crop = lastCrop.ifEmpty { null }
                        )
                    )

                    if (profileResponse.isSuccessful) {
                        val recResponse = RetrofitClient.instance
                            .getRecommendation(
                                session.getBearerToken(),
                                session.getUserId(),
                                season
                            )

                        if (recResponse.isSuccessful) {
                            val body = recResponse.body()!!
                            val sb = StringBuilder()
                            sb.append("Top Crop Recommendations\n")
                            sb.append("District: ${body.district}\n\n")

                            body.top_3_recommendations
                                .forEachIndexed { i, crop ->
                                    sb.append("${i + 1}. ${crop.crop_name}\n")
                                    sb.append("   Score: ${crop.score}\n")
                                    sb.append("   Est. Income: ₹${
                                        String.format("%.0f", crop.income_estimate)
                                    }\n")
                                    sb.append("   MSP: ${
                                        if (crop.has_msp) "₹${crop.msp}"
                                        else "No MSP"
                                    }\n\n")
                                }

                            tvResults.text = sb.toString()
                            tvResults.visibility = View.VISIBLE
                        }
                    }
                } catch (e: Exception) {
                    Toast.makeText(this@FarmerDashboardActivity,
                        "Error: ${e.message}",
                        Toast.LENGTH_SHORT).show()
                } finally {
                    btnGetRec.isEnabled = true
                    btnGetRec.text = "Get My Crop Recommendation"
                }
            }
        }

        btnGetRecovery.setOnClickListener {
            val anomalyType = etAnomalyType.text.toString().trim()

            if (anomalyType.isEmpty()) {
                Toast.makeText(this,
                    "Please enter the problem type",
                    Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }

            btnGetRecovery.isEnabled = false
            btnGetRecovery.text = "Getting recovery plan..."

            lifecycleScope.launch {
                try {
                    val response = RetrofitClient.instance.getAnomalyRecovery(
                        session.getBearerToken(),
                        AnomalyRequest(anomalyType)
                    )

                    if (response.isSuccessful) {
                        val plan = response.body()!!.recovery_plan
                        val sb = StringBuilder()
                        sb.append("${plan.title}\n")
                        sb.append("Severity: ${plan.severity}\n\n")
                        sb.append("Steps:\n")
                        plan.steps.forEachIndexed { i, step ->
                            sb.append("${i + 1}. $step\n\n")
                        }
                        tvRecovery.text = sb.toString()
                        tvRecovery.visibility = View.VISIBLE
                    }
                } catch (e: Exception) {
                    Toast.makeText(this@FarmerDashboardActivity,
                        "Error: ${e.message}",
                        Toast.LENGTH_SHORT).show()
                } finally {
                    btnGetRecovery.isEnabled = true
                    btnGetRecovery.text = "Get Recovery Plan"
                }
            }
        }
    }
}
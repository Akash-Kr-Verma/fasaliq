package com.fasaliq.app.ui.buyer

import android.content.Intent
import android.os.Bundle
import android.view.View
import android.widget.*
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.fasaliq.app.MainActivity
import com.fasaliq.app.R
import com.fasaliq.app.api.RetrofitClient
import com.fasaliq.app.models.BuyerInterestRequest
import com.fasaliq.app.utils.SessionManager
import kotlinx.coroutines.launch

class BuyerDashboardActivity : AppCompatActivity() {

    private lateinit var session: SessionManager

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_buyer_dashboard)

        session = SessionManager(this)

        val tvWelcome = findViewById<TextView>(R.id.tvWelcome)
        val etDistrict = findViewById<EditText>(R.id.etDistrict)
        val etSeason = findViewById<EditText>(R.id.etSeason)
        val btnCheckAvail = findViewById<Button>(R.id.btnCheckAvailability)
        val tvAvailability = findViewById<TextView>(R.id.tvAvailability)
        val etCropName = findViewById<EditText>(R.id.etCropName)
        val etBuyerDistrict = findViewById<EditText>(R.id.etBuyerDistrict)
        val etQuantity = findViewById<EditText>(R.id.etQuantity)
        val etOfferedPrice = findViewById<EditText>(R.id.etOfferedPrice)
        val btnPlaceInterest = findViewById<Button>(R.id.btnPlaceInterest)
        val tvInterestResult = findViewById<TextView>(R.id.tvInterestResult)
        val btnLogout = findViewById<Button>(R.id.btnLogout)

        tvWelcome.text = "Welcome, ${session.getName()}"

        btnLogout.setOnClickListener {
            session.clearSession()
            startActivity(Intent(this, MainActivity::class.java))
            finish()
        }

        btnCheckAvail.setOnClickListener {
            val district = etDistrict.text.toString().trim()
            val season = etSeason.text.toString().trim()

            if (district.isEmpty() || season.isEmpty()) {
                Toast.makeText(this,
                    "Please enter district and season",
                    Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }

            btnCheckAvail.isEnabled = false
            btnCheckAvail.text = "Checking..."

            lifecycleScope.launch {
                try {
                    val response = RetrofitClient.instance
                        .getCropAvailability(
                            session.getBearerToken(),
                            district,
                            season
                        )

                    if (response.isSuccessful) {
                        val body = response.body()!!
                        val crops = body["available_crops"] as? List<*>
                        if (crops.isNullOrEmpty()) {
                            tvAvailability.text =
                                "No crops available in $district this season"
                        } else {
                            val sb = StringBuilder()
                            sb.append("Available in $district:\n\n")
                            crops.forEach { crop ->
                                val map = crop as? Map<*, *>
                                sb.append("• ${map?.get("crop_name")}\n")
                                sb.append("  Farmers: ${map?.get("farmer_count")}\n")
                                sb.append("  MSP: ${
                                    if (map?.get("has_msp") == true)
                                        "₹${map["msp"]}"
                                    else "No MSP"
                                }\n\n")
                            }
                            tvAvailability.text = sb.toString()
                        }
                        tvAvailability.visibility = View.VISIBLE
                    }
                } catch (e: Exception) {
                    Toast.makeText(this@BuyerDashboardActivity,
                        "Error: ${e.message}",
                        Toast.LENGTH_SHORT).show()
                } finally {
                    btnCheckAvail.isEnabled = true
                    btnCheckAvail.text = "Check Availability"
                }
            }
        }

        btnPlaceInterest.setOnClickListener {
            val cropName = etCropName.text.toString().trim()
            val district = etBuyerDistrict.text.toString().trim()
            val quantity = etQuantity.text.toString().trim()
            val price = etOfferedPrice.text.toString().trim()

            if (cropName.isEmpty() || district.isEmpty() ||
                quantity.isEmpty() || price.isEmpty()) {
                Toast.makeText(this,
                    "Please fill all fields",
                    Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }

            btnPlaceInterest.isEnabled = false
            btnPlaceInterest.text = "Placing interest..."

            lifecycleScope.launch {
                try {
                    val response = RetrofitClient.instance.placeBuyerInterest(
                        session.getBearerToken(),
                        BuyerInterestRequest(
                            buyer_id = session.getUserId(),
                            crop_name = cropName,
                            district = district,
                            quantity = quantity.toDouble(),
                            offered_price = price.toDouble()
                        )
                    )

                    if (response.isSuccessful) {
                        tvInterestResult.text =
                            "Interest placed successfully!\n" +
                                    "Crop: $cropName\n" +
                                    "Quantity: ${quantity}kg\n" +
                                    "Offered Price: ₹$price/kg\n" +
                                    "Status: Open"
                        tvInterestResult.visibility = View.VISIBLE
                        Toast.makeText(this@BuyerDashboardActivity,
                            "Interest placed!",
                            Toast.LENGTH_SHORT).show()
                    } else {
                        Toast.makeText(this@BuyerDashboardActivity,
                            "Failed to place interest",
                            Toast.LENGTH_SHORT).show()
                    }
                } catch (e: Exception) {
                    Toast.makeText(this@BuyerDashboardActivity,
                        "Error: ${e.message}",
                        Toast.LENGTH_SHORT).show()
                } finally {
                    btnPlaceInterest.isEnabled = true
                    btnPlaceInterest.text = "Place Purchase Interest"
                }
            }
        }
    }
}
package com.fasaliq.app.ui.farmer

import android.os.Bundle
import android.view.View
import android.widget.*
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import androidx.viewpager2.widget.ViewPager2
import androidx.fragment.app.Fragment
import androidx.fragment.app.FragmentActivity
import androidx.viewpager2.adapter.FragmentStateAdapter
import com.fasaliq.app.R
import com.fasaliq.app.api.RetrofitClient
import com.fasaliq.app.models.CropRecommendation
import com.fasaliq.app.models.StartHarvestRequest
import com.fasaliq.app.utils.SessionManager
import kotlinx.coroutines.launch

class NewHarvestActivity : AppCompatActivity() {

    private lateinit var session: SessionManager
    private lateinit var stepPager: ViewPager2

    var fieldName = ""
    var fieldSize = 1.0
    var soilType = "loamy"
    var irrigation = "borewell"
    var incomeLevel = "middle"
    var season = "kharif"
    var startMonth = 6
    var endMonth = 10
    var selectedCrop = ""
    var acceptedRecommendation = true

    private val months = listOf(
        "January", "February", "March", "April",
        "May", "June", "July", "August",
        "September", "October", "November", "December"
    )

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_new_harvest)

        session = SessionManager(this)
        stepPager = findViewById(R.id.stepPager)
        stepPager.isUserInputEnabled = false

        stepPager.adapter = object : FragmentStateAdapter(this) {
            override fun getItemCount() = 3
            override fun createFragment(position: Int): Fragment =
                when (position) {
                    0 -> FieldDetailsStepFragment()
                    1 -> SeasonMonthsStepFragment()
                    2 -> RecommendationStepFragment()
                    else -> FieldDetailsStepFragment()
                }
        }

        findViewById<ImageView>(R.id.btnBack).setOnClickListener {
            if (stepPager.currentItem > 0) {
                stepPager.setCurrentItem(
                    stepPager.currentItem - 1, true
                )
                updateStepUI()
            } else finish()
        }

        findViewById<LinearLayout>(R.id.btnNext).setOnClickListener {
            handleNext()
        }
    }

    private fun handleNext() {
        when (stepPager.currentItem) {
            0 -> {
                if (validateStep1()) {
                    stepPager.setCurrentItem(1, true)
                    updateStepUI()
                }
            }
            1 -> {
                stepPager.setCurrentItem(2, true)
                updateStepUI()
                loadRecommendations()
            }
            2 -> {
                if (selectedCrop.isNotEmpty()) {
                    startHarvest()
                } else {
                    Toast.makeText(
                        this,
                        "Please select a crop first",
                        Toast.LENGTH_SHORT
                    ).show()
                }
            }
        }
    }

    private fun validateStep1(): Boolean {
        if (fieldName.isEmpty()) {
            Toast.makeText(
                this, "Please enter field name",
                Toast.LENGTH_SHORT
            ).show()
            return false
        }
        return true
    }

    private fun updateStepUI() {
        val step = stepPager.currentItem
        val labels = listOf(
            "Field Details",
            "Season & Months",
            "AI Recommendation"
        )
        findViewById<TextView>(R.id.tvStepLabel).text =
            labels[step]

        listOf(
            R.id.step1Indicator,
            R.id.step2Indicator,
            R.id.step3Indicator
        ).forEachIndexed { index, id ->
            val tv = findViewById<TextView>(id)
            if (index <= step) {
                tv.setBackgroundColor(getColor(R.color.forest_green))
                tv.setTextColor(getColor(android.R.color.white))
            } else {
                tv.setBackgroundColor(getColor(R.color.divider))
                tv.setTextColor(getColor(R.color.text_soft))
            }
        }

        val btnPrev = findViewById<LinearLayout>(R.id.btnPrev)
        btnPrev.visibility = if (step > 0) View.VISIBLE else View.GONE

        val tvNext = findViewById<TextView>(R.id.tvNextLabel)
        tvNext.text = if (step == 2) "Start Harvest 🌱" else "Next →"
    }

    private fun loadRecommendations() {
        val recFragment = supportFragmentManager
            .findFragmentByTag("f2") as? RecommendationStepFragment
        recFragment?.loadFromActivity()
    }

    private fun startHarvest() {
        lifecycleScope.launch {
            try {
                val response = RetrofitClient.instance.startHarvest(
                    session.getBearerToken(),
                    StartHarvestRequest(
                        farmer_id = session.getUserId(),
                        field_name = fieldName,
                        crop_name = selectedCrop,
                        season = season,
                        start_month = startMonth,
                        end_month = endMonth,
                        field_size = fieldSize,
                        soil_type = soilType,
                        irrigation = irrigation,
                        income_level = incomeLevel,
                        farmer_accepted_recommendation =
                            acceptedRecommendation
                    )
                )
                if (response.isSuccessful) {
                    Toast.makeText(
                        this@NewHarvestActivity,
                        "🌱 Harvest started! Good luck!",
                        Toast.LENGTH_LONG
                    ).show()
                    finish()
                }
            } catch (e: Exception) {
                Toast.makeText(
                    this@NewHarvestActivity,
                    "Error: ${e.message}",
                    Toast.LENGTH_SHORT
                ).show()
            }
        }
    }
}

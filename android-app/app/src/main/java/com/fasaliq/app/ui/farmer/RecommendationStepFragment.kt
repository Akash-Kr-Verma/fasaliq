package com.fasaliq.app.ui.farmer

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.*
import androidx.fragment.app.Fragment
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.fasaliq.app.R
import com.fasaliq.app.api.RetrofitClient
import com.fasaliq.app.models.CropRecommendation
import com.fasaliq.app.utils.SessionManager
import kotlinx.coroutines.launch

class RecommendationStepFragment : Fragment() {

    private lateinit var session: SessionManager

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        val view = inflater.inflate(
            R.layout.step_recommendation, container, false
        )
        session = SessionManager(requireContext())
        return view
    }

    fun loadFromActivity() {
        val activity = requireActivity() as NewHarvestActivity
        val view = requireView()

        val loading = view.findViewById<LinearLayout>(R.id.loadingState)
        val rvRec = view.findViewById<RecyclerView>(R.id.rvRecommendations)
        val cardOwn = view.findViewById<LinearLayout>(R.id.cardOwnChoice)

        loading.visibility = View.VISIBLE
        rvRec.visibility = View.GONE
        cardOwn.visibility = View.GONE

        lifecycleScope.launch {
            try {
                val response = RetrofitClient.instance
                    .getHarvestRecommendation(
                        session.getBearerToken(),
                        session.getUserId(),
                        activity.season,
                        activity.startMonth,
                        activity.endMonth,
                        activity.fieldSize,
                        activity.soilType,
                        activity.irrigation,
                        activity.incomeLevel,
                        session.getDistrict() ?: "Pune"
                    )

                loading.visibility = View.GONE

                if (response.isSuccessful) {
                    val body = response.body()!!
                    val recs = body.recommendations

                    if (body.buyer_demand_active > 0) {
                        view.findViewById<TextView>(
                            R.id.tvRecommendSubtitle
                        ).text =
                            "🛒 ${body.buyer_demand_active} buyers " +
                            "have active demand in your area"
                    }

                    rvRec.layoutManager = LinearLayoutManager(
                        requireContext()
                    )
                    rvRec.adapter = RecommendationAdapter(recs) { crop ->
                        activity.selectedCrop = crop.crop_name
                        activity.acceptedRecommendation = true
                        Toast.makeText(
                            requireContext(),
                            "✅ ${crop.crop_name} selected",
                            Toast.LENGTH_SHORT
                        ).show()
                    }
                    rvRec.visibility = View.VISIBLE
                    cardOwn.visibility = View.VISIBLE

                    setupOwnChoice(view, activity)
                }
            } catch (e: Exception) {
                loading.visibility = View.GONE
                Toast.makeText(
                    requireContext(),
                    "Could not load recommendations: ${e.message}",
                    Toast.LENGTH_SHORT
                ).show()
            }
        }
    }

    private fun setupOwnChoice(view: View, activity: NewHarvestActivity) {
        view.findViewById<LinearLayout>(R.id.btnConfirmOwnCrop)
            .setOnClickListener {
                val cropName = view.findViewById<EditText>(
                    R.id.etOwnCrop
                ).text.toString().trim()
                if (cropName.isNotEmpty()) {
                    activity.selectedCrop = cropName
                    activity.acceptedRecommendation = false
                    Toast.makeText(
                        requireContext(),
                        "✅ $cropName set as your choice",
                        Toast.LENGTH_SHORT
                    ).show()
                }
            }
    }
}

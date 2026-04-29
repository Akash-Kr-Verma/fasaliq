package com.fasaliq.app.ui.farmer

import android.app.AlertDialog
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.EditText
import android.widget.LinearLayout
import android.widget.TextView
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.fasaliq.app.R
import com.fasaliq.app.api.RetrofitClient
import com.fasaliq.app.models.EndHarvestRequest
import com.fasaliq.app.models.HarvestItem
import com.fasaliq.app.models.StartHarvestRequest
import com.fasaliq.app.utils.SessionManager
import kotlinx.coroutines.launch
import java.util.Calendar

class ActiveSeasonFragment : Fragment() {

    private lateinit var session: SessionManager
    private lateinit var harvestAdapter: HarvestAdapter

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        val view = inflater.inflate(
            R.layout.fragment_active_season, container, false
        )
        session = SessionManager(requireContext())
        setupViews(view)
        loadActiveHarvests(view)
        return view
    }

    private fun setupViews(view: View) {
        val hour = Calendar.getInstance().get(Calendar.HOUR_OF_DAY)
        val greeting = when {
            hour < 12 -> "Good morning 🌿"
            hour < 17 -> "Good afternoon ☀️"
            else -> "Good evening 🌙"
        }
        view.findViewById<TextView>(R.id.tvGreeting).text = greeting
        view.findViewById<TextView>(R.id.tvFarmerNameTop).text =
            session.getName() ?: "Farmer"

        harvestAdapter = HarvestAdapter(
            onEndHarvest = { harvest -> showEndHarvestDialog(harvest) },
            onReportIssue = { harvest -> showReportIssueDialog(harvest) }
        )

        view.findViewById<RecyclerView>(R.id.rvActiveHarvests).apply {
            layoutManager = LinearLayoutManager(requireContext())
            adapter = harvestAdapter
        }

        view.findViewById<LinearLayout>(R.id.btnAddHarvest)
            .setOnClickListener {
                startActivity(android.content.Intent(requireContext(), NewHarvestActivity::class.java))
            }

        view.findViewById<LinearLayout>(R.id.btnStartFirst)
            .setOnClickListener {
                startActivity(android.content.Intent(requireContext(), NewHarvestActivity::class.java))
            }
    }

    private fun loadActiveHarvests(view: View) {
        lifecycleScope.launch {
            try {
                val response = RetrofitClient.instance.getActiveHarvests(
                    session.getBearerToken(),
                    session.getUserId()
                )
                if (response.isSuccessful) {
                    val body = response.body()!!
                    val cardWelcome = view.findViewById<LinearLayout>(
                        R.id.cardWelcome
                    )
                    val rvHarvests = view.findViewById<RecyclerView>(
                        R.id.rvActiveHarvests
                    )

                    if (body.active_count == 0) {
                        cardWelcome.visibility = View.VISIBLE
                        rvHarvests.visibility = View.GONE
                    } else {
                        cardWelcome.visibility = View.GONE
                        rvHarvests.visibility = View.VISIBLE
                        harvestAdapter.updateHarvests(body.harvests)
                    }
                }
            } catch (e: Exception) {
                view.findViewById<LinearLayout>(R.id.cardWelcome)
                    .visibility = View.VISIBLE
            }
        }
    }

    private fun showStartHarvestDialog() {
        val dialogView = LayoutInflater.from(requireContext())
            .inflate(R.layout.dialog_start_harvest, null)

        val dialog = AlertDialog.Builder(requireContext())
            .setView(dialogView)
            .create()

        dialog.window?.setBackgroundDrawableResource(
            android.R.color.transparent
        )

        dialogView.findViewById<LinearLayout>(R.id.btnCancelHarvest)
            .setOnClickListener { dialog.dismiss() }

        dialogView.findViewById<LinearLayout>(R.id.btnConfirmHarvest)
            .setOnClickListener {
                val fieldName = dialogView
                    .findViewById<EditText>(R.id.etFieldName)
                    .text.toString().trim()
                val cropName = dialogView
                    .findViewById<EditText>(R.id.etCropName)
                    .text.toString().trim()
                val season = dialogView
                    .findViewById<EditText>(R.id.etSeason)
                    .text.toString().trim()
                val fieldSizeStr = dialogView
                    .findViewById<EditText>(R.id.etFieldSize)
                    .text.toString().trim()

                if (fieldName.isEmpty() || cropName.isEmpty() ||
                    season.isEmpty() || fieldSizeStr.isEmpty()) {
                    Toast.makeText(
                        requireContext(),
                        "Please fill all fields",
                        Toast.LENGTH_SHORT
                    ).show()
                    return@setOnClickListener
                }

                dialog.dismiss()
                startHarvest(
                    fieldName, cropName, season,
                    fieldSizeStr.toDouble()
                )
            }

        dialog.show()
    }

    private fun startHarvest(
        fieldName: String,
        cropName: String,
        season: String,
        fieldSize: Double
    ) {
        lifecycleScope.launch {
            try {
                val response = RetrofitClient.instance.startHarvest(
                    session.getBearerToken(),
                    StartHarvestRequest(
                        farmer_id = session.getUserId(),
                        field_name = fieldName,
                        crop_name = cropName,
                        season = season,
                        field_size = fieldSize
                    )
                )
                if (response.isSuccessful) {
                    Toast.makeText(
                        requireContext(),
                        "🌱 Harvest started!",
                        Toast.LENGTH_SHORT
                    ).show()
                    view?.let { loadActiveHarvests(it) }
                }
            } catch (e: Exception) {
                Toast.makeText(
                    requireContext(),
                    "Error: ${e.message}",
                    Toast.LENGTH_SHORT
                ).show()
            }
        }
    }

    private fun showEndHarvestDialog(harvest: HarvestItem) {
        AlertDialog.Builder(requireContext())
            .setTitle("🏁 End Season")
            .setMessage(
                "Are you sure you want to end the ${harvest.crop_name} " +
                "harvest on ${harvest.field_name}?"
            )
            .setPositiveButton("Yes, End Season") { _, _ ->
                endHarvest(harvest.harvest_id)
            }
            .setNegativeButton("Cancel", null)
            .show()
    }

    private fun endHarvest(harvestId: Int) {
        lifecycleScope.launch {
            try {
                val response = RetrofitClient.instance.endHarvest(
                    session.getBearerToken(),
                    EndHarvestRequest(
                        harvest_id = harvestId,
                        actual_yield = null,
                        income_earned = null,
                        notes = null
                    )
                )
                if (response.isSuccessful) {
                    Toast.makeText(
                        requireContext(),
                        "✅ Season ended successfully",
                        Toast.LENGTH_SHORT
                    ).show()
                    view?.let { loadActiveHarvests(it) }
                }
            } catch (e: Exception) {
                Toast.makeText(
                    requireContext(),
                    "Error: ${e.message}",
                    Toast.LENGTH_SHORT
                ).show()
            }
        }
    }

    private fun showReportIssueDialog(harvest: HarvestItem) {
        val intent = android.content.Intent(
            requireContext(), ChatActivity::class.java
        )
        startActivity(intent)
    }
}

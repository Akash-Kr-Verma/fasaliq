package com.fasaliq.app.ui.farmer

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.LinearLayout
import android.widget.ProgressBar
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.fasaliq.app.R
import com.fasaliq.app.models.HarvestItem

class HarvestAdapter(
    private val harvests: MutableList<HarvestItem> = mutableListOf(),
    private val onEndHarvest: (HarvestItem) -> Unit,
    private val onReportIssue: (HarvestItem) -> Unit
) : RecyclerView.Adapter<HarvestAdapter.HarvestViewHolder>() {

    inner class HarvestViewHolder(view: View) :
        RecyclerView.ViewHolder(view) {
        val tvCropName: TextView = view.findViewById(R.id.tvCropName)
        val tvFieldName: TextView = view.findViewById(R.id.tvFieldName)
        val tvHealthStatus: TextView = view.findViewById(R.id.tvHealthStatus)
        val progressBar: ProgressBar = view.findViewById(R.id.progressHarvest)
        val tvProgress: TextView = view.findViewById(R.id.tvProgress)
        val tvSeason: TextView = view.findViewById(R.id.tvSeason)
        val tvFieldSize: TextView = view.findViewById(R.id.tvFieldSize)
        val tvDaysLeft: TextView = view.findViewById(R.id.tvDaysLeft)
        val tvAnomalies: TextView = view.findViewById(R.id.tvAnomalies)
        val btnEnd: LinearLayout = view.findViewById(R.id.btnEndHarvest)
        val btnIssue: LinearLayout = view.findViewById(R.id.btnReportIssue)
    }

    override fun onCreateViewHolder(
        parent: ViewGroup, viewType: Int
    ) = HarvestViewHolder(
        LayoutInflater.from(parent.context)
            .inflate(R.layout.item_harvest_card, parent, false)
    )

    override fun onBindViewHolder(
        holder: HarvestViewHolder, position: Int
    ) {
        val h = harvests[position]

        holder.tvCropName.text = h.crop_name
        holder.tvFieldName.text = "📍 ${h.field_name}"
        holder.tvSeason.text = h.season.replaceFirstChar { it.uppercase() }
        holder.tvFieldSize.text = "${h.field_size} acres"
        holder.tvDaysLeft.text = "${h.days_remaining ?: "—"} days"
        holder.tvAnomalies.text = "${h.active_anomalies}"

        holder.progressBar.progress = h.progress_percent
        holder.tvProgress.text = "${h.progress_percent}%"

        val healthColor = when (h.health_status) {
            "good" -> 0xFF2E7D32.toInt()
            "warning" -> 0xFFF57F17.toInt()
            "critical" -> 0xFFC62828.toInt()
            else -> 0xFF2E7D32.toInt()
        }
        val healthEmoji = when (h.health_status) {
            "good" -> "● Good"
            "warning" -> "⚠ Warning"
            "critical" -> "🔴 Critical"
            else -> "● Good"
        }
        holder.tvHealthStatus.text = healthEmoji
        holder.tvHealthStatus.setTextColor(healthColor)

        holder.btnEnd.setOnClickListener { onEndHarvest(h) }
        holder.btnIssue.setOnClickListener { onReportIssue(h) }
    }

    override fun getItemCount() = harvests.size

    fun updateHarvests(newList: List<HarvestItem>) {
        harvests.clear()
        harvests.addAll(newList)
        notifyDataSetChanged()
    }
}

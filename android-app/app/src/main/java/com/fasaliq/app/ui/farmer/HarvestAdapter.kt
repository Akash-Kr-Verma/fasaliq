package com.fasaliq.app.ui.farmer

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.LinearLayout
import android.widget.ProgressBar
import android.widget.TextView
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.fasaliq.app.R
import com.fasaliq.app.models.HarvestItem
import com.fasaliq.app.models.MatchedBuyer

class HarvestAdapter(
    private val harvests: MutableList<HarvestItem> = mutableListOf(),
    private val onEndHarvest: (HarvestItem) -> Unit,
    private val onReportIssue: (HarvestItem) -> Unit,
    private val onLoadBuyers: (HarvestItem, ViewHolder) -> Unit
) : RecyclerView.Adapter<HarvestAdapter.ViewHolder>() {

    inner class ViewHolder(view: View) :
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
        val buyerMatchContainer: LinearLayout = view.findViewById(
            R.id.buyerMatchContainer
        )
        val tvBuyerCount: TextView = view.findViewById(R.id.tvBuyerCount)
        val rvBuyers: RecyclerView = view.findViewById(R.id.rvBuyers)
    }

    override fun onCreateViewHolder(
        parent: ViewGroup, viewType: Int
    ) = ViewHolder(
        LayoutInflater.from(parent.context)
            .inflate(R.layout.item_harvest_card, parent, false)
    )

    override fun onBindViewHolder(
        holder: ViewHolder, position: Int
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
        holder.tvHealthStatus.text = when (h.health_status) {
            "good" -> "● Good"
            "warning" -> "⚠ Warning"
            "critical" -> "🔴 Critical"
            else -> "● Good"
        }
        holder.tvHealthStatus.setTextColor(healthColor)

        holder.btnEnd.setOnClickListener { onEndHarvest(h) }
        holder.btnIssue.setOnClickListener { onReportIssue(h) }

        if (h.progress_percent >= 75) {
            holder.buyerMatchContainer.visibility = View.VISIBLE
            holder.rvBuyers.layoutManager = LinearLayoutManager(
                holder.itemView.context
            )
            onLoadBuyers(h, holder)
        } else {
            holder.buyerMatchContainer.visibility = View.GONE
        }
    }

    override fun getItemCount() = harvests.size

    fun updateHarvests(newList: List<HarvestItem>) {
        harvests.clear()
        harvests.addAll(newList)
        notifyDataSetChanged()
    }

    fun updateBuyers(
        holder: ViewHolder,
        buyers: List<MatchedBuyer>,
        total: Int
    ) {
        holder.tvBuyerCount.text = "$total buyers"
        holder.rvBuyers.adapter = BuyerMatchAdapter(buyers)
    }
}

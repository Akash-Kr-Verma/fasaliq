package com.fasaliq.app.ui.farmer

import android.graphics.Color
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.LinearLayout
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.fasaliq.app.R
import com.fasaliq.app.models.CropRecommendation

class RecommendationAdapter(
    private val items: List<CropRecommendation>,
    private val onSelect: (CropRecommendation) -> Unit
) : RecyclerView.Adapter<RecommendationAdapter.ViewHolder>() {

    inner class ViewHolder(view: View) :
        RecyclerView.ViewHolder(view) {
        val tvRank: TextView = view.findViewById(R.id.tvRank)
        val tvCropName: TextView = view.findViewById(R.id.tvCropName)
        val tvSeason: TextView = view.findViewById(R.id.tvSeason)
        val tvScore: TextView = view.findViewById(R.id.tvScore)
        val tvIncome: TextView = view.findViewById(R.id.tvIncome)
        val tvMSP: TextView = view.findViewById(R.id.tvMSP)
        val llReasons: LinearLayout = view.findViewById(R.id.llReasons)
        val btnSelect: LinearLayout = view.findViewById(R.id.btnSelectCrop)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int) =
        ViewHolder(
            LayoutInflater.from(parent.context).inflate(
                R.layout.item_recommendation_card, parent, false
            )
        )

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        val item = items[position]
        val rankColors = listOf("#2D5A27", "#4A7A40", "#6B9B55")

        holder.tvRank.text = "#${position + 1}"
        holder.tvRank.setBackgroundColor(
            Color.parseColor(
                rankColors.getOrElse(position) { "#6B9B55" }
            )
        )
        holder.tvCropName.text = item.crop_name
        holder.tvSeason.text = item.season.replaceFirstChar {
            it.uppercase()
        }
        holder.tvScore.text = String.format("%.2f", item.score)
        holder.tvIncome.text = "₹${
            String.format("%,.0f", item.income_estimate)
        }"
        holder.tvMSP.text = if (item.has_msp)
            "· MSP ₹${item.msp.toInt()}" else ""

        holder.llReasons.removeAllViews()
        item.reasons.forEach { reason ->
            val tv = TextView(holder.itemView.context).apply {
                text = "✓ $reason"
                textSize = 12f
                setTextColor(Color.parseColor("#4A6741"))
                setPadding(0, 3, 0, 3)
                lineSpacingExtra = 2f
            }
            holder.llReasons.addView(tv)
        }

        holder.btnSelect.setOnClickListener { onSelect(item) }
    }

    override fun getItemCount() = items.size
}

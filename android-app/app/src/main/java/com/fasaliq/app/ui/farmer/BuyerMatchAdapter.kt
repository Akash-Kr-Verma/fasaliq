package com.fasaliq.app.ui.farmer

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.LinearLayout
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.fasaliq.app.R
import com.fasaliq.app.models.MatchedBuyer

class BuyerMatchAdapter(
    private val buyers: List<MatchedBuyer>
) : RecyclerView.Adapter<BuyerMatchAdapter.ViewHolder>() {

    inner class ViewHolder(view: View) :
        RecyclerView.ViewHolder(view) {
        val tvName: TextView = view.findViewById(R.id.tvBuyerName)
        val tvDistrict: TextView = view.findViewById(R.id.tvDistrict)
        val tvQuantity: TextView = view.findViewById(R.id.tvQuantity)
        val tvPrice: TextView = view.findViewById(R.id.tvPrice)
        val tvTotal: TextView = view.findViewById(R.id.tvTotalValue)
        val tvNearby: TextView = view.findViewById(R.id.tvSameDistrict)
    }

    override fun onCreateViewHolder(
        parent: ViewGroup, viewType: Int
    ) = ViewHolder(
        LayoutInflater.from(parent.context)
            .inflate(R.layout.item_buyer_match, parent, false)
    )

    override fun onBindViewHolder(
        holder: ViewHolder, position: Int
    ) {
        val b = buyers[position]
        holder.tvName.text = b.buyer_name
        holder.tvDistrict.text = b.buyer_district
        holder.tvQuantity.text = "${b.quantity_kg.toInt()} kg needed"
        holder.tvPrice.text = "₹${b.offered_price_per_kg.toInt()}/kg"
        holder.tvTotal.text = "Total: ₹${
            String.format("%,.0f", b.total_value)
        }"
        holder.tvNearby.visibility =
            if (b.same_district) View.VISIBLE else View.GONE
    }

    override fun getItemCount() = minOf(buyers.size, 3)
}

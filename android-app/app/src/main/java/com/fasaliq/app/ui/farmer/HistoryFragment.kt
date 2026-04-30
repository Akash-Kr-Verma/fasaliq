package com.fasaliq.app.ui.farmer

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.fragment.app.Fragment
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.fasaliq.app.R
import com.github.mikephil.charting.charts.LineChart
import com.github.mikephil.charting.data.Entry
import com.github.mikephil.charting.data.LineData
import com.github.mikephil.charting.data.LineDataSet
import android.graphics.Color

import android.widget.Button
import android.widget.LinearLayout
import android.widget.TextView
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.lifecycleScope
import kotlinx.coroutines.launch

class HistoryFragment : Fragment() {

    private lateinit var viewModel: FarmerViewModel
    private var selectedFieldId: String? = null

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        val view = inflater.inflate(
            R.layout.fragment_history, container, false
        )

        viewModel = ViewModelProvider(requireActivity())[FarmerViewModel::class.java]

        val llEmptyState = view.findViewById<LinearLayout>(R.id.llEmptyState)
        val svContent = view.findViewById<View>(R.id.svContent)
        val rvFields = view.findViewById<RecyclerView>(R.id.rvFields)
        val tvNoCrops = view.findViewById<TextView>(R.id.tvNoCrops)
        val rvCrops = view.findViewById<RecyclerView>(R.id.rvCrops)
        val llChartContainer = view.findViewById<LinearLayout>(R.id.llChartContainer)
        val chart = view.findViewById<LineChart>(R.id.cropTrendChart)

        rvFields.layoutManager = LinearLayoutManager(requireContext(), LinearLayoutManager.HORIZONTAL, false)
        rvCrops.layoutManager = LinearLayoutManager(requireContext())

        lifecycleScope.launch {
            viewModel.state.collect { state ->
                if (state.fields.isEmpty()) {
                    llEmptyState.visibility = View.VISIBLE
                    svContent.visibility = View.GONE
                } else {
                    llEmptyState.visibility = View.GONE
                    svContent.visibility = View.VISIBLE

                    if (selectedFieldId == null) {
                        selectedFieldId = state.fields.first().id
                    }

                    // For now, assume single field selection isn't explicitly implemented via clicks, just pick first or selected
                    val field = state.fields.find { it.id == selectedFieldId } ?: state.fields.first()
                    
                    if (field.crops.isEmpty()) {
                        tvNoCrops.visibility = View.VISIBLE
                        rvCrops.visibility = View.GONE
                        llChartContainer.visibility = View.GONE
                    } else {
                        tvNoCrops.visibility = View.GONE
                        rvCrops.visibility = View.VISIBLE
                        rvCrops.adapter = DynamicCropAdapter(field.crops)

                        // Render chart for the first crop if trend data exists
                        val firstCrop = field.crops.first()
                        if (firstCrop.trend_data.isNotEmpty()) {
                            llChartContainer.visibility = View.VISIBLE
                            setupChart(chart, firstCrop.trend_data)
                        } else {
                            llChartContainer.visibility = View.GONE
                        }
                    }
                }
            }
        }

        return view
    }

    private fun setupChart(chart: LineChart, trendData: List<Float>) {
        val entries = trendData.mapIndexed { index, value ->
            Entry(index.toFloat(), value)
        }

        val dataSet = LineDataSet(entries, "Yield (Quintal)").apply {
            color = Color.parseColor("#2D5A27")
            setCircleColor(Color.parseColor("#76BA1B"))
            lineWidth = 2.5f
            circleRadius = 5f
            setDrawFilled(true)
            fillColor = Color.parseColor("#C8E6C9")
            fillAlpha = 80
            mode = LineDataSet.Mode.CUBIC_BEZIER
            valueTextSize = 10f
            valueTextColor = Color.parseColor("#2D5A27")
        }

        chart.apply {
            data = LineData(dataSet)
            description.isEnabled = false
            legend.isEnabled = false
            xAxis.setDrawGridLines(false)
            axisRight.isEnabled = false
            axisLeft.gridColor = Color.parseColor("#E8F0E5")
            setTouchEnabled(true)
            setPinchZoom(false)
            animateX(800)
            invalidate()
        }
    }

    inner class DynamicCropAdapter(private val crops: List<Crop>) : RecyclerView.Adapter<DynamicCropAdapter.ViewHolder>() {
        inner class ViewHolder(view: View) : RecyclerView.ViewHolder(view) {
            val tvCropName: TextView = view.findViewById(R.id.tvCropName)
            val tvStartDate: TextView = view.findViewById(R.id.tvStartDate)
            val tvStatus: TextView = view.findViewById(R.id.tvStatus)
            val tvSessions: TextView = view.findViewById(R.id.tvSessions)
            val tvResult: TextView = view.findViewById(R.id.tvResult)
        }

        override fun onCreateViewHolder(parent: ViewGroup, viewType: Int) = ViewHolder(
            LayoutInflater.from(parent.context).inflate(R.layout.item_dynamic_crop, parent, false)
        )

        override fun onBindViewHolder(holder: ViewHolder, position: Int) {
            val crop = crops[position]
            holder.tvCropName.text = crop.crop_name
            holder.tvStartDate.text = "Started: ${crop.start_date}"
            holder.tvStatus.text = crop.status
            holder.tvSessions.text = crop.sessions.size.toString()
            holder.tvResult.text = crop.result ?: "-"
        }

        override fun getItemCount() = crops.size
    }
}

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

class HistoryFragment : Fragment() {

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        val view = inflater.inflate(
            R.layout.fragment_history, container, false
        )

        setupChart(view)
        setupFieldCarousel(view)

        return view
    }

    private fun setupChart(view: View) {
        val chart = view.findViewById<LineChart>(R.id.cropTrendChart)

        val entries = listOf(
            Entry(0f, 12f),
            Entry(1f, 15f),
            Entry(2f, 18f),
            Entry(3f, 14f),
            Entry(4f, 20f),
            Entry(5f, 22f)
        )

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

    private fun setupFieldCarousel(view: View) {
        val rv = view.findViewById<RecyclerView>(R.id.rvFields)
        rv.layoutManager = LinearLayoutManager(
            requireContext(),
            LinearLayoutManager.HORIZONTAL,
            false
        )
    }
}

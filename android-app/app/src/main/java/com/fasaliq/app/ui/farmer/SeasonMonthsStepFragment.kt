package com.fasaliq.app.ui.farmer

import android.graphics.Color
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ArrayAdapter
import android.widget.Spinner
import android.widget.TextView
import androidx.fragment.app.Fragment
import com.fasaliq.app.R

class SeasonMonthsStepFragment : Fragment() {

    private val months = listOf(
        "January", "February", "March", "April",
        "May", "June", "July", "August",
        "September", "October", "November", "December"
    )

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        val view = inflater.inflate(
            R.layout.step_season_months, container, false
        )

        val activity = requireActivity() as NewHarvestActivity

        val seasonBtns = mapOf(
            "kharif" to view.findViewById<TextView>(R.id.seasonKharif),
            "rabi" to view.findViewById(R.id.seasonRabi),
            "annual" to view.findViewById(R.id.seasonAnnual)
        )

        fun updateSeason(selected: String) {
            seasonBtns.forEach { (key, tv) ->
                if (key == selected) {
                    tv.setBackgroundColor(Color.parseColor("#2D5A27"))
                    tv.setTextColor(Color.WHITE)
                } else {
                    tv.setBackgroundResource(R.drawable.bg_card_rounded)
                    tv.setTextColor(Color.parseColor("#4A6741"))
                }
            }
        }

        updateSeason("kharif")

        seasonBtns.forEach { (key, tv) ->
            tv.setOnClickListener {
                updateSeason(key)
                activity.season = key
            }
        }

        val adapter = ArrayAdapter(
            requireContext(),
            android.R.layout.simple_spinner_item,
            months
        )
        adapter.setDropDownViewResource(
            android.R.layout.simple_spinner_dropdown_item
        )

        val spinnerStart = view.findViewById<Spinner>(
            R.id.spinnerStartMonth
        )
        spinnerStart.adapter = adapter
        spinnerStart.setSelection(5)
        spinnerStart.onItemSelectedListener =
            object : android.widget.AdapterView.OnItemSelectedListener {
                override fun onItemSelected(
                    p: android.widget.AdapterView<*>?,
                    v: View?, pos: Int, id: Long
                ) {
                    activity.startMonth = pos + 1
                }
                override fun onNothingSelected(
                    p: android.widget.AdapterView<*>?
                ) {}
            }

        val spinnerEnd = view.findViewById<Spinner>(
            R.id.spinnerEndMonth
        )
        spinnerEnd.adapter = adapter
        spinnerEnd.setSelection(9)
        spinnerEnd.onItemSelectedListener =
            object : android.widget.AdapterView.OnItemSelectedListener {
                override fun onItemSelected(
                    p: android.widget.AdapterView<*>?,
                    v: View?, pos: Int, id: Long
                ) {
                    activity.endMonth = pos + 1
                }
                override fun onNothingSelected(
                    p: android.widget.AdapterView<*>?
                ) {}
            }

        return view
    }
}

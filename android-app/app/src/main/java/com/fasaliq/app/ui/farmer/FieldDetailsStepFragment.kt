package com.fasaliq.app.ui.farmer

import android.graphics.Color
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.EditText
import android.widget.TextView
import androidx.fragment.app.Fragment
import com.fasaliq.app.R

class FieldDetailsStepFragment : Fragment() {

    private var selectedSoil = "loamy"
    private var selectedIrrigation = "borewell"
    private var selectedIncome = "middle"

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        val view = inflater.inflate(
            R.layout.step_field_details, container, false
        )

        val activity = requireActivity() as NewHarvestActivity

        val etFieldName = view.findViewById<EditText>(R.id.etFieldName)
        val etFieldSize = view.findViewById<EditText>(R.id.etFieldSize)

        etFieldName.setOnFocusChangeListener { _, _ ->
            activity.fieldName = etFieldName.text.toString().trim()
        }
        etFieldSize.setOnFocusChangeListener { _, _ ->
            activity.fieldSize = etFieldSize.text
                .toString().toDoubleOrNull() ?: 1.0
        }

        val soilBtns = mapOf(
            "loamy" to view.findViewById<TextView>(R.id.soilLoamy),
            "clay" to view.findViewById(R.id.soilClay),
            "sandy" to view.findViewById(R.id.soilSandy),
            "black" to view.findViewById(R.id.soilBlack)
        )
        setupToggleGroup(soilBtns, selectedSoil) { selected ->
            selectedSoil = selected
            activity.soilType = selected
        }

        val irrBtns = mapOf(
            "borewell" to view.findViewById<TextView>(R.id.irrBorewell),
            "canal" to view.findViewById(R.id.irrCanal),
            "rainfed" to view.findViewById(R.id.irrRainfed),
            "drip" to view.findViewById(R.id.irrDrip)
        )
        setupToggleGroup(irrBtns, selectedIrrigation) { selected ->
            selectedIrrigation = selected
            activity.irrigation = selected
        }

        val incomeBtns = mapOf(
            "poor" to view.findViewById<TextView>(R.id.incomePoor),
            "middle" to view.findViewById(R.id.incomeMiddle),
            "rich" to view.findViewById(R.id.incomeRich)
        )
        setupToggleGroup(incomeBtns, selectedIncome) { selected ->
            selectedIncome = selected
            activity.incomeLevel = selected
        }

        return view
    }

    private fun setupToggleGroup(
        buttons: Map<String, TextView>,
        default: String,
        onSelect: (String) -> Unit
    ) {
        fun updateColors(selected: String) {
            buttons.forEach { (key, tv) ->
                if (key == selected) {
                    tv.setBackgroundColor(
                        Color.parseColor("#2D5A27")
                    )
                    tv.setTextColor(Color.WHITE)
                } else {
                    tv.setBackgroundResource(
                        R.drawable.bg_card_rounded
                    )
                    tv.setTextColor(Color.parseColor("#4A6741"))
                }
            }
        }

        updateColors(default)

        buttons.forEach { (key, tv) ->
            tv.setOnClickListener {
                updateColors(key)
                onSelect(key)
            }
        }
    }
}

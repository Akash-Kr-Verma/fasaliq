package com.fasaliq.app.ui.farmer

import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.LinearLayout
import android.widget.TextView
import androidx.fragment.app.Fragment
import com.fasaliq.app.MainActivity
import com.fasaliq.app.R
import com.fasaliq.app.utils.SessionManager

class ProfileFragment : Fragment() {

    private lateinit var session: SessionManager

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        val view = inflater.inflate(
            R.layout.fragment_profile, container, false
        )
        session = SessionManager(requireContext())

        view.findViewById<TextView>(R.id.tvFarmerName).text =
            session.getName() ?: "Farmer"

        view.findViewById<LinearLayout>(R.id.btnEmergency)
            .setOnClickListener {
                val intent = Intent(Intent.ACTION_DIAL).apply {
                    data = Uri.parse("tel:18001801551")
                }
                startActivity(intent)
            }

        view.findViewById<LinearLayout>(R.id.btnLogout)
            .setOnClickListener {
                session.clearSession()
                startActivity(
                    Intent(requireContext(), MainActivity::class.java)
                )
                requireActivity().finish()
            }

        return view
    }
}

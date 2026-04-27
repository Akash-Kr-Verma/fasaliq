package com.fasaliq.app.ui.farmer

import android.content.Intent
import android.os.Bundle
import android.view.animation.Animation
import android.view.animation.ScaleAnimation
import android.widget.FrameLayout
import android.widget.ImageView
import android.widget.LinearLayout
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import androidx.fragment.app.Fragment
import androidx.viewpager2.widget.ViewPager2
import androidx.fragment.app.FragmentActivity
import androidx.viewpager2.adapter.FragmentStateAdapter
import com.fasaliq.app.R
import com.fasaliq.app.utils.SessionManager

class FarmerDashboardActivity : AppCompatActivity() {

    private lateinit var session: SessionManager
    private lateinit var viewPager: ViewPager2

    private val navIds = listOf(
        R.id.navProfile,
        R.id.navHistory,
        R.id.navAI,
        R.id.navDocuments,
        R.id.navNewsletter
    )

    private val labelIds = listOf(
        R.id.labelProfile,
        R.id.labelHistory,
        null,
        R.id.labelDocuments,
        R.id.labelNewsletter
    )

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_farmer_dashboard)

        session = SessionManager(this)
        viewPager = findViewById(R.id.viewPager)
        viewPager.isUserInputEnabled = false

        viewPager.adapter = object : FragmentStateAdapter(this) {
            override fun getItemCount() = 4
            override fun createFragment(position: Int): Fragment =
                when (position) {
                    0 -> ProfileFragment()
                    1 -> HistoryFragment()
                    2 -> DocumentsFragment()
                    3 -> NewsletterFragment()
                    else -> ProfileFragment()
                }
        }

        setupNavigation()
        startAIPulse()
        selectTab(0)
    }

    private fun setupNavigation() {
        findViewById<LinearLayout>(R.id.navProfile).setOnClickListener {
            selectTab(0); viewPager.setCurrentItem(0, false)
        }
        findViewById<LinearLayout>(R.id.navHistory).setOnClickListener {
            selectTab(1); viewPager.setCurrentItem(1, false)
        }
        findViewById<FrameLayout>(R.id.navAI).setOnClickListener {
            startActivity(Intent(this, ChatActivity::class.java))
        }
        findViewById<LinearLayout>(R.id.navDocuments).setOnClickListener {
            selectTab(2); viewPager.setCurrentItem(2, false)
        }
        findViewById<LinearLayout>(R.id.navNewsletter).setOnClickListener {
            selectTab(3); viewPager.setCurrentItem(3, false)
        }
    }

    private fun selectTab(index: Int) {
        val labels = listOf(
            R.id.labelProfile,
            R.id.labelHistory,
            R.id.labelDocuments,
            R.id.labelNewsletter
        )
        val activeColor = getColor(R.color.leaf_green)
        val inactiveColor = getColor(R.color.text_soft)

        labels.forEachIndexed { i, id ->
            findViewById<TextView>(id).setTextColor(
                if (i == index) activeColor else inactiveColor
            )
        }
    }

    private fun startAIPulse() {
        val pulseRing = findViewById<ImageView>(R.id.aiPulseRing)
        val pulse = ScaleAnimation(
            1f, 1.3f, 1f, 1.3f,
            Animation.RELATIVE_TO_SELF, 0.5f,
            Animation.RELATIVE_TO_SELF, 0.5f
        ).apply {
            duration = 1000
            repeatCount = Animation.INFINITE
            repeatMode = Animation.REVERSE
        }
        pulseRing.startAnimation(pulse)
    }
}
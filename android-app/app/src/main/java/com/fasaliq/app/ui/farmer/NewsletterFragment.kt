package com.fasaliq.app.ui.farmer

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.fragment.app.Fragment
import com.fasaliq.app.R

import android.widget.LinearLayout
import android.widget.TextView
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import kotlinx.coroutines.launch

class NewsletterFragment : Fragment() {

    private lateinit var viewModel: FarmerViewModel

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        val view = inflater.inflate(
            R.layout.fragment_newsletter, container, false
        )

        viewModel = ViewModelProvider(requireActivity())[FarmerViewModel::class.java]

        val llEmptyState = view.findViewById<LinearLayout>(R.id.llEmptyState)
        val svContent = view.findViewById<View>(R.id.svContent)

        val llWeatherContainer = view.findViewById<LinearLayout>(R.id.llWeatherContainer)
        val tvWeatherTemp = view.findViewById<TextView>(R.id.tvWeatherTemp)
        val tvWeatherCondition = view.findViewById<TextView>(R.id.tvWeatherCondition)
        val tvLocation = view.findViewById<TextView>(R.id.tvLocation)

        val llMandiContainer = view.findViewById<LinearLayout>(R.id.llMandiContainer)
        val rvMandi = view.findViewById<RecyclerView>(R.id.rvMandi)

        val llNewsContainer = view.findViewById<LinearLayout>(R.id.llNewsContainer)
        val rvNews = view.findViewById<RecyclerView>(R.id.rvNews)

        rvMandi.layoutManager = LinearLayoutManager(requireContext(), LinearLayoutManager.HORIZONTAL, false)
        rvNews.layoutManager = LinearLayoutManager(requireContext())

        lifecycleScope.launch {
            viewModel.state.collect { state ->
                val hasWeather = state.weather != null
                val hasMandi = state.news.any { it.type == "mandi" }
                val hasNews = state.news.any { it.type != "mandi" }

                if (!hasWeather && !hasMandi && !hasNews) {
                    llEmptyState.visibility = View.VISIBLE
                    svContent.visibility = View.GONE
                } else {
                    llEmptyState.visibility = View.GONE
                    svContent.visibility = View.VISIBLE

                    if (hasWeather) {
                        llWeatherContainer.visibility = View.VISIBLE
                        tvWeatherTemp.text = "${state.weather?.temp}°C"
                        tvWeatherCondition.text = state.weather?.condition
                        tvLocation?.text = state.weather?.location
                    } else {
                        llWeatherContainer.visibility = View.GONE
                    }

                    if (hasMandi) {
                        llMandiContainer.visibility = View.VISIBLE
                        rvMandi.adapter = DynamicMandiAdapter(state.news.filter { it.type == "mandi" })
                    } else {
                        llMandiContainer.visibility = View.GONE
                    }

                    if (hasNews) {
                        llNewsContainer.visibility = View.VISIBLE
                        rvNews.adapter = DynamicNewsAdapter(state.news.filter { it.type != "mandi" })
                    } else {
                        llNewsContainer.visibility = View.GONE
                    }
                }
            }
        }

        return view
    }

    inner class DynamicMandiAdapter(private val items: List<NewsItem>) : RecyclerView.Adapter<DynamicMandiAdapter.ViewHolder>() {
        inner class ViewHolder(view: View) : RecyclerView.ViewHolder(view) {
            val tvMandiTitle: TextView = view.findViewById(R.id.tvMandiTitle)
            val tvMandiPrice: TextView = view.findViewById(R.id.tvMandiPrice)
        }

        override fun onCreateViewHolder(parent: ViewGroup, viewType: Int) = ViewHolder(
            LayoutInflater.from(parent.context).inflate(R.layout.item_dynamic_mandi, parent, false)
        )

        override fun onBindViewHolder(holder: ViewHolder, position: Int) {
            val item = items[position]
            holder.tvMandiTitle.text = item.title
            holder.tvMandiPrice.text = item.content
        }

        override fun getItemCount() = items.size
    }

    inner class DynamicNewsAdapter(private val items: List<NewsItem>) : RecyclerView.Adapter<DynamicNewsAdapter.ViewHolder>() {
        inner class ViewHolder(view: View) : RecyclerView.ViewHolder(view) {
            val tvNewsTitle: TextView = view.findViewById(R.id.tvNewsTitle)
            val tvNewsType: TextView = view.findViewById(R.id.tvNewsType)
        }

        override fun onCreateViewHolder(parent: ViewGroup, viewType: Int) = ViewHolder(
            LayoutInflater.from(parent.context).inflate(R.layout.item_dynamic_news, parent, false)
        )

        override fun onBindViewHolder(holder: ViewHolder, position: Int) {
            val item = items[position]
            holder.tvNewsTitle.text = item.title
            holder.tvNewsType.text = item.type.uppercase()
        }

        override fun getItemCount() = items.size
    }
}

package com.fasaliq.app.ui.farmer

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.fragment.app.Fragment
import com.fasaliq.app.R

import android.widget.Button
import android.widget.LinearLayout
import android.widget.TextView
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import kotlinx.coroutines.launch

class DocumentsFragment : Fragment() {

    private lateinit var viewModel: FarmerViewModel

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        val view = inflater.inflate(
            R.layout.fragment_documents, container, false
        )

        viewModel = ViewModelProvider(requireActivity())[FarmerViewModel::class.java]

        val llEmptyState = view.findViewById<LinearLayout>(R.id.llEmptyState)
        val llContentState = view.findViewById<LinearLayout>(R.id.llContentState)
        val tvDocCount = view.findViewById<TextView>(R.id.tvDocCount)
        val rvDocuments = view.findViewById<RecyclerView>(R.id.rvDocuments)
        val btnUpload = view.findViewById<Button>(R.id.btnUpload)

        rvDocuments.layoutManager = LinearLayoutManager(requireContext())

        lifecycleScope.launch {
            viewModel.state.collect { state ->
                if (state.documents.isEmpty()) {
                    llEmptyState.visibility = View.VISIBLE
                    llContentState.visibility = View.GONE
                } else {
                    llEmptyState.visibility = View.GONE
                    llContentState.visibility = View.VISIBLE
                    tvDocCount.text = "${state.documents.size} Documents"
                    rvDocuments.adapter = DynamicDocumentAdapter(state.documents)
                }
            }
        }

        btnUpload.setOnClickListener {
            // Upload dummy interaction
        }

        return view
    }

    inner class DynamicDocumentAdapter(private val documents: List<Document>) : RecyclerView.Adapter<DynamicDocumentAdapter.ViewHolder>() {
        inner class ViewHolder(view: View) : RecyclerView.ViewHolder(view) {
            val tvDocTitle: TextView = view.findViewById(R.id.tvDocTitle)
            val tvDocDate: TextView = view.findViewById(R.id.tvDocDate)
        }

        override fun onCreateViewHolder(parent: ViewGroup, viewType: Int) = ViewHolder(
            LayoutInflater.from(parent.context).inflate(R.layout.item_dynamic_document, parent, false)
        )

        override fun onBindViewHolder(holder: ViewHolder, position: Int) {
            val doc = documents[position]
            holder.tvDocTitle.text = doc.title
            holder.tvDocDate.text = "${doc.type.uppercase()} • ${doc.date}"
        }

        override fun getItemCount() = documents.size
    }
}

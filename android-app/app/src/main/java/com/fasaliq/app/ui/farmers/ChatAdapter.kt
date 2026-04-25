package com.fasaliq.app.ui.farmers

import android.graphics.Color
import android.view.Gravity
import android.view.LayoutInflater
import android.view.ViewGroup
import android.widget.LinearLayout
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.fasaliq.app.R

data class ChatMessage(
    val content: String,
    val isUser: Boolean
)

class ChatAdapter(
    val messages: MutableList<ChatMessage> = mutableListOf()
) : RecyclerView.Adapter<ChatAdapter.MessageViewHolder>() {

    inner class MessageViewHolder(
        val container: LinearLayout,
        val tvMessage: TextView
    ) : RecyclerView.ViewHolder(container)

    override fun onCreateViewHolder(
        parent: ViewGroup, viewType: Int
    ): MessageViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_chat_message, parent, false)
        return MessageViewHolder(
            view as LinearLayout,
            view.findViewById(R.id.tvMessage)
        )
    }

    override fun onBindViewHolder(
        holder: MessageViewHolder, position: Int
    ) {
        val msg = messages[position]
        holder.tvMessage.text = msg.content

        if (msg.isUser) {
            holder.container.gravity = Gravity.END
            holder.tvMessage.setBackgroundColor(Color.parseColor("#534AB7"))
            holder.tvMessage.setTextColor(Color.WHITE)
        } else {
            holder.container.gravity = Gravity.START
            holder.tvMessage.setBackgroundColor(Color.parseColor("#FFFFFF"))
            holder.tvMessage.setTextColor(Color.parseColor("#2C2C2A"))
        }

        holder.tvMessage.background = holder.tvMessage.context
            .getDrawable(R.drawable.input_bg)
    }

    override fun getItemCount() = messages.size

    fun addMessage(msg: ChatMessage) {
        messages.add(msg)
        notifyItemInserted(messages.size - 1)
    }
}

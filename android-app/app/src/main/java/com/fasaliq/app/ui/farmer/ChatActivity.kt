package com.fasaliq.app.ui.farmer

import android.app.Activity
import android.content.Intent
import android.graphics.Bitmap
import android.os.Bundle
import android.provider.MediaStore
import android.speech.RecognizerIntent
import android.util.Base64
import android.view.View
import android.widget.*
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.fasaliq.app.R
import com.fasaliq.app.api.RetrofitClient
import com.fasaliq.app.utils.SessionManager
import kotlinx.coroutines.launch
import org.json.JSONObject
import java.io.ByteArrayOutputStream
import java.util.Locale
import com.fasaliq.app.models.ChatMessageRequest

class ChatActivity : AppCompatActivity() {

    private lateinit var session: SessionManager
    private lateinit var adapter: ChatAdapter
    private var sessionId: String? = null
    private var pendingImageBase64: String? = null

    companion object {
        const val CAMERA_REQUEST = 1001
        const val VOICE_REQUEST = 1002
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_chat)

        session = SessionManager(this)
        adapter = ChatAdapter()

        val rvMessages = findViewById<RecyclerView>(R.id.rvMessages)
        val etMessage = findViewById<EditText>(R.id.etMessage)
        val btnSend = findViewById<Button>(R.id.btnSend)
        val btnVoice = findViewById<ImageButton>(R.id.btnVoice)
        val btnCamera = findViewById<ImageButton>(R.id.btnCamera)
        val tvAnomalyBadge = findViewById<TextView>(R.id.tvAnomalyBadge)

        rvMessages.layoutManager = LinearLayoutManager(this).apply {
            stackFromEnd = true
        }
        rvMessages.adapter = adapter

        startChatSession()

        btnSend.setOnClickListener {
            val text = etMessage.text.toString().trim()
            if (text.isEmpty() && pendingImageBase64 == null) return@setOnClickListener
            sendMessage(text, etMessage, rvMessages, tvAnomalyBadge)
        }

        btnVoice.setOnClickListener {
            val intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply {
                putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL,
                    RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
                putExtra(RecognizerIntent.EXTRA_LANGUAGE, "hi-IN")
                putExtra(RecognizerIntent.EXTRA_PROMPT,
                    "अपनी समस्या बोलें...")
            }
            try {
                startActivityForResult(intent, VOICE_REQUEST)
            } catch (e: Exception) {
                Toast.makeText(this,
                    "Voice not available", Toast.LENGTH_SHORT).show()
            }
        }

        btnCamera.setOnClickListener {
            val intent = Intent(MediaStore.ACTION_IMAGE_CAPTURE)
            startActivityForResult(intent, CAMERA_REQUEST)
        }
    }

    private fun startChatSession() {
        lifecycleScope.launch {
            try {
                val response = RetrofitClient.instance.startChatSession(
                    mapOf("farmer_id" to session.getUserId())
                )
                if (response.isSuccessful) {
                    val body = response.body()!!
                    sessionId = body["session_id"] as? String
                    val welcome = body["welcome_message"] as? String ?: ""
                    adapter.addMessage(ChatMessage(welcome, false))
                }
            } catch (e: Exception) {
                adapter.addMessage(ChatMessage(
                    "Connection error. Please check server.", false
                ))
            }
        }
    }

    private fun sendMessage(
        text: String,
        etMessage: EditText,
        rvMessages: RecyclerView,
        tvAnomalyBadge: TextView
    ) {
        val msgText = if (pendingImageBase64 != null && text.isEmpty())
            "[Photo sent]" else text

        adapter.addMessage(ChatMessage(msgText, true))
        etMessage.setText("")
        rvMessages.scrollToPosition(adapter.itemCount - 1)

        adapter.addMessage(ChatMessage("...", false))
        val loadingPos = adapter.itemCount - 1

        lifecycleScope.launch {
            try {
                val request = ChatMessageRequest(
                    session_id = sessionId ?: "",
                    message = msgText,
                    message_type = if (pendingImageBase64 != null) "image" else "text",
                    image_base64 = pendingImageBase64
                )

                val response = RetrofitClient.instance.sendChatMessage(request)

                if (response.isSuccessful) {
                    val respBody = response.body()!!
                    val aiText = respBody["response"] as? String ?: ""

                    adapter.messages.removeAt(loadingPos)
                    adapter.notifyItemRemoved(loadingPos)
                    adapter.addMessage(ChatMessage(aiText, false))
                    rvMessages.scrollToPosition(adapter.itemCount - 1)

                    val anomaly = respBody["anomaly_detected"]
                    if (anomaly != null) {
                        tvAnomalyBadge.text = "⚠️ Anomaly Detected"
                        tvAnomalyBadge.visibility = View.VISIBLE
                    }
                }
            } catch (e: Exception) {
                adapter.messages.removeAt(loadingPos)
                adapter.notifyItemRemoved(loadingPos)
                adapter.addMessage(ChatMessage(
                    "Error: ${e.message}", false
                ))
            }
            pendingImageBase64 = null
        }
    }

    override fun onActivityResult(
        requestCode: Int, resultCode: Int, data: Intent?
    ) {
        super.onActivityResult(requestCode, resultCode, data)

        if (resultCode != Activity.RESULT_OK) return

        when (requestCode) {
            VOICE_REQUEST -> {
                val results = data?.getStringArrayListExtra(
                    RecognizerIntent.EXTRA_RESULTS
                )
                val text = results?.firstOrNull() ?: return
                findViewById<EditText>(R.id.etMessage).setText(text)
            }
            CAMERA_REQUEST -> {
                val photo = data?.extras?.get("data") as? Bitmap ?: return
                val baos = ByteArrayOutputStream()
                photo.compress(Bitmap.CompressFormat.JPEG, 80, baos)
                pendingImageBase64 = Base64.encodeToString(
                    baos.toByteArray(), Base64.DEFAULT
                )
                Toast.makeText(this,
                    "Photo ready — send a message",
                    Toast.LENGTH_SHORT).show()
            }
        }
    }
}

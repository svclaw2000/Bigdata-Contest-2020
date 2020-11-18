package com.khnsoft.covidchatbot

import android.content.Context
import android.content.Intent
import android.media.AudioAttributes
import android.media.MediaPlayer
import android.os.AsyncTask
import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.speech.RecognitionListener
import android.speech.RecognizerIntent
import android.speech.SpeechRecognizer
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import android.widget.Toast
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.google.gson.JsonParser
import com.gun0912.tedpermission.PermissionListener
import com.gun0912.tedpermission.TedPermission
import com.khnsoft.covidchatbot.Data.Chat
import com.khnsoft.covidchatbot.Utils.MyLogger
import com.khnsoft.covidchatbot.Utils.SDF
import kotlinx.android.synthetic.main.activity_main.*
import kotlinx.coroutines.*
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.io.BufferedReader
import java.io.IOException
import java.io.InputStream
import java.io.InputStreamReader
import java.lang.Exception
import java.net.HttpURLConnection
import java.net.URL
import java.util.ArrayList

class MainActivity : AppCompatActivity() {
    val mCoroutineScope = CoroutineScope(Dispatchers.IO)
    lateinit var recIntent : Intent
    lateinit var recognizer : SpeechRecognizer
    var mediaPlayer : MediaPlayer? = null

    companion object {
        const val URL_CHAT = "http://svclaw.ipdisk.co.kr:7788/chat/%s"
        const val URL_VOICE = "http://svclaw.ipdisk.co.kr:7788/voice/%s"
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        requestPermission()

        recIntent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH)
        recIntent.putExtra(RecognizerIntent.EXTRA_CALLING_PACKAGE, packageName)
        recIntent.putExtra(RecognizerIntent.EXTRA_LANGUAGE, "ko-KR")
        recIntent.putExtra(RecognizerIntent.EXTRA_PARTIAL_RESULTS, true)

        recognizer = SpeechRecognizer.createSpeechRecognizer(this@MainActivity)
        recognizer.setRecognitionListener(listener)

        btn_send.setOnClickListener {
            if (et_chat.text.toString().isEmpty()) {
                return@setOnClickListener
            }

            chat(et_chat.text.toString())
            et_chat.text.clear()
        }

        btn_voice.setOnClickListener {
            mediaPlayer?.stop()
            mediaPlayer = null

            recognizer.startListening(recIntent)
        }

//        btn_settings.setOnClickListener {
//
//        }

        refresh()
    }

    private var listener : RecognitionListener = object : RecognitionListener {
        override fun onReadyForSpeech(p0: Bundle?) {
        }

        override fun onRmsChanged(p0: Float) {
        }

        override fun onBufferReceived(p0: ByteArray?) {
        }

        override fun onPartialResults(partialResults: Bundle?) {
            val key: String = SpeechRecognizer.RESULTS_RECOGNITION
            val mResult = partialResults?.getStringArrayList(key) ?: return
            et_chat.setText(mResult[0])
        }

        override fun onEvent(p0: Int, p1: Bundle?) {
        }

        override fun onBeginningOfSpeech() {
        }

        override fun onEndOfSpeech() {
        }

        override fun onError(error: Int) {
            MyLogger.e("Recognizer", "Error #${error}")
        }

        override fun onResults(results: Bundle?) {
            val key: String = SpeechRecognizer.RESULTS_RECOGNITION
            val mResult = results?.getStringArrayList(key) ?: return
            et_chat.setText(mResult[0])

            chat(et_chat.text.toString())
            et_chat.text.clear()
        }
    }

    fun refresh() {
        val lChat = Chat.getAll(this@MainActivity)
        val adapter = ChatRecyclerAdapter(lChat)
        val lm = LinearLayoutManager(this@MainActivity)
        rv_chat.layoutManager = lm
        rv_chat.adapter = adapter

        rv_chat.scrollToPosition(lChat.size - 1)
    }

    inner class ChatRecyclerAdapter(val lChat : Array<Chat>) :
            RecyclerView.Adapter<ChatRecyclerAdapter.ViewHolder>() {

        inner class ViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
            val time = itemView.findViewById<TextView>(R.id.tv_chat_time)
            val message = itemView.findViewById<TextView>(R.id.tv_chat)
        }

        override fun onBindViewHolder(holder: ViewHolder, position: Int) {
            val chat = lChat[position]
            holder.time.text = SDF.time.format(chat.datetime)
            holder.message.text = chat.message
        }

        override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
            return if (viewType == Chat.BY_BOT) {
                val view = LayoutInflater.from(this@MainActivity).inflate(R.layout.item_chat_bot, parent, false)
                ViewHolder(view)
            } else {
                val view = LayoutInflater.from(this@MainActivity).inflate(R.layout.item_chat_user, parent, false)
                ViewHolder(view)
            }
        }

        override fun getItemViewType(position: Int): Int {
            return lChat[position].by
        }

        override fun getItemCount(): Int {
            return lChat.size
        }
    }

    fun chat(msg: String) {
        GlobalScope.launch(Dispatchers.Main) {
            Chat.add(this@MainActivity, by=Chat.BY_USER, msg=msg)
            val result = JsonParser.parseString(chatRequest(msg)).asJsonObject
            Chat.add(this@MainActivity, by=Chat.BY_BOT, msg=result["resp"].asString)
            refresh()
            talk(if (result.has("voice")) result["voice"].asString else result["resp"].asString)
        }
    }

    fun talk(msg: String) {
        mediaPlayer?.stop()
        mediaPlayer = null

        mediaPlayer = MediaPlayer()
        mediaPlayer?.apply {
            setAudioAttributes(
                AudioAttributes.Builder()
                    .setContentType(AudioAttributes.CONTENT_TYPE_MUSIC)
                    .build()
            )
            setDataSource(String.format(URL_VOICE, msg))
            prepare()
            start()
        }
    }

    private suspend fun chatRequest(msg: String) : String {
        val reuslt = withContext(Dispatchers.IO) {
            var httpConn : HttpURLConnection? = null
            var ret = ""

            try {
                val inputStream : InputStream
                val urlConn = URL(String.format(URL_CHAT, msg))
                httpConn = urlConn.openConnection() as HttpURLConnection

                httpConn.requestMethod = "GET"
                httpConn.doInput = true

                val status = httpConn.responseCode
                try {
                    inputStream = if (status != HttpURLConnection.HTTP_OK) {
                        httpConn.errorStream
                    } else {
                        httpConn.inputStream
                    }

                    if (inputStream != null) {
                        ret = convertInputStreamToString(inputStream)
                    }
                } catch (e: Exception) {
                    e.printStackTrace()
                }
            } catch (e: Exception) {
                e.printStackTrace()
            } finally {
                httpConn?.disconnect()
            }
            ret
        }
        return reuslt
    }

    @Throws(IOException::class)
    fun convertInputStreamToString(inputStream: InputStream): String {
        val bufferedReader = BufferedReader(InputStreamReader(inputStream))
        var ret = ""

        var line = bufferedReader.readLine()
        while (line != null) {
            ret += line
            line = bufferedReader.readLine()
        }
        inputStream.close()
        return ret
    }

    fun requestPermission() {
        TedPermission.with(this@MainActivity)
            .setPermissionListener(permissionListener)
            .setPermissions(
                android.Manifest.permission.INTERNET,
                android.Manifest.permission.RECORD_AUDIO
            )
            .check()
    }

    var permissionListener = object : PermissionListener {
        override fun onPermissionGranted() {
        }

        override fun onPermissionDenied(deniedPermissions: ArrayList<String>?) {
            finish()
        }
    }
}
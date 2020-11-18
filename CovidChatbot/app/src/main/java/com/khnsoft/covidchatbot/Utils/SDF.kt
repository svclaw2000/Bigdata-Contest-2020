package com.khnsoft.covidchatbot.Utils

import java.text.SimpleDateFormat
import java.util.*

class SDF {
    companion object {
        val dateDot = SimpleDateFormat("yyyy.MM.dd", Locale.KOREA)
        val dateBar = SimpleDateFormat("yyyy-MM-dd", Locale.KOREA)
        val dateWeek = SimpleDateFormat("yyyy.MM.dd(E)", Locale.KOREA)
        val time = SimpleDateFormat("a h:mm", Locale.KOREA)
        val dateTimeBar = SimpleDateFormat("yyyy-MM-dd HH:mm:ss", Locale.KOREA)
    }
}
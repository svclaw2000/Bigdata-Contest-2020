package com.khnsoft.covidchatbot.Data

import android.content.Context
import com.google.gson.JsonObject
import com.khnsoft.covidchatbot.Utils.DatabaseHandler
import com.khnsoft.covidchatbot.Utils.MyLogger
import com.khnsoft.covidchatbot.Utils.SDF
import java.lang.Exception
import java.util.*

class Chat(
    val id: Int = -1,
    val datetime: Date = Date(),
    val by: Int = BY_USER,
    val message: String = ""
) {
    companion object {
        const val BY_USER = 0
        const val BY_BOT = 1

        fun getFromJson(jChat: JsonObject): Chat {
            return Chat(
                id = jChat["id"].asInt,
                datetime = SDF.dateTimeBar.parse(jChat["datetime"].asString),
                by = jChat["by"].asInt,
                message = jChat["message"].asString
            )
        }

        fun getAll(context: Context): Array<Chat> {
            val mHandler = DatabaseHandler.open(context)

            try {
                val sql = """
                    SELECT id, datetime, by, message 
                    FROM CHAT_TB 
                    ORDER BY datetime
                """.trimIndent()

                val lResult = mHandler.read(sql)
                val chats = Array(lResult.size()) { Chat() }

                for (i in 0..lResult.size() - 1) {
                    chats[i] = getFromJson(lResult[i].asJsonObject)
                }

                return chats
            } catch (e: Exception) {
                e.printStackTrace()
            } finally {
                mHandler.close()
            }

            return arrayOf()
        }

        fun add(context: Context, by: Int, msg: String) : Boolean {
            return Chat(by = by, message = msg).add(context)
        }
    }

    fun add(context: Context): Boolean {
        val mHandler = DatabaseHandler.open(context)

        try {
            val sql = """
                INSERT INTO CHAT_TB (datetime, by, message)
                VALUES (
                    "${SDF.dateTimeBar.format(datetime)}",
                    ${by},
                    "${message.replace("\"", "\'")}"
                )
            """.trimIndent()

            mHandler.write(sql)

            return true
        } catch (e: Exception) {
            e.printStackTrace()
        } finally {
            mHandler.close()
        }

        return false
    }
}
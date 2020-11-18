package com.khnsoft.covidchatbot.Utils

import android.content.Context
import android.database.sqlite.SQLiteDatabase
import android.database.sqlite.SQLiteOpenHelper
import java.lang.Exception

class DatabaseOpenHelper(val context: Context?, name: String?, factory: SQLiteDatabase.CursorFactory?, version: Int) :
    SQLiteOpenHelper(context, name, factory, version) {

    override fun onCreate(db: SQLiteDatabase) {
        createTableChat(db)
    }

    override fun onOpen(db: SQLiteDatabase) {
        db.setForeignKeyConstraintsEnabled(true)
    }

    override fun onUpgrade(db: SQLiteDatabase?, oldVersion: Int, newVersion: Int) {
    }

    private fun createTableChat(db: SQLiteDatabase) {
        val sql = """
            CREATE TABLE IF NOT EXISTS CHAT_TB (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                datetime TEXT NOT NULL,
                by INTEGER NOT NULL,
                message TEXT NOT NULL
            )
        """.trimIndent()

        MyLogger.d("Initialize CHAT_TB", sql)

        try {
            db.execSQL(sql)
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }
}
package com.fasaliq.app.ui.farmer

import androidx.lifecycle.ViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update

data class FarmerInfo(
    val name: String,
    val phone: String,
    val income_level: String?
)

data class CropSession(
    val id: String,
    val date: String,
    val description: String
)

data class Crop(
    val id: String,
    val crop_name: String,
    val start_date: String,
    val status: String, // ACTIVE | HARVESTED
    val sessions: List<CropSession> = emptyList(),
    val result: String? = null,
    val trend_data: List<Float> = emptyList()
)

data class Field(
    val id: String,
    val name: String,
    val size: Double,
    val crops: List<Crop> = emptyList()
)

data class Document(
    val id: String,
    val title: String,
    val date: String,
    val type: String
)

data class NewsItem(
    val id: String,
    val title: String,
    val content: String,
    val type: String, // "weather", "mandi", "crop_insight"
    val relatedCrop: String? = null
)

data class WeatherInfo(
    val temp: Double,
    val condition: String,
    val location: String
)

data class FarmerState(
    val farmer: FarmerInfo? = null,
    val fields: List<Field> = emptyList(),
    val documents: List<Document> = emptyList(),
    val news: List<NewsItem> = emptyList(),
    val weather: WeatherInfo? = null
)

class FarmerViewModel : ViewModel() {
    private val _state = MutableStateFlow(FarmerState())
    val state: StateFlow<FarmerState> = _state.asStateFlow()

    fun setFarmer(farmer: FarmerInfo?) {
        _state.update { it.copy(farmer = farmer) }
    }

    fun setFields(fields: List<Field>) {
        _state.update { it.copy(fields = fields) }
    }

    fun setDocuments(documents: List<Document>) {
        _state.update { it.copy(documents = documents) }
    }

    fun setNews(news: List<NewsItem>) {
        _state.update { it.copy(news = news) }
    }

    fun setWeather(weather: WeatherInfo?) {
        _state.update { it.copy(weather = weather) }
    }

    fun addDocument(doc: Document) {
        _state.update { it.copy(documents = it.documents + doc) }
    }
}

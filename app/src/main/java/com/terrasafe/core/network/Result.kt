package com.terrasafe.core.network

sealed interface Result<out T> {
    data class Success<T>(val data: T) : Result<T>
    data class Error(val message: String, val throwable: Throwable? = null) : Result<Nothing>
    object Offline : Result<Nothing>
}

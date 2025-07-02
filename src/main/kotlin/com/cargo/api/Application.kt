package com.cargo.api

import io.ktor.server.engine.*
import io.ktor.server.netty.*
import io.ktor.application.*
import io.ktor.http.*
import io.ktor.request.*
import io.ktor.response.*
import io.ktor.routing.*
import io.ktor.server.plugins.contentnegotiation.*
import io.ktor.serialization.kotlinx.json.*
import kotlinx.serialization.Serializable
import java.util.concurrent.ConcurrentHashMap

@Serializable
data class CargoRequest(
    val id: String,
    val sender: String,
    val destination: String,
    val cargoType: String,
    var status: String = "Pending"
)

@Serializable
data class CallbackData(
    val cargoRequestId: String,
    val statusUpdate: String,
    val timestamp: String
)

val cargoRequests = ConcurrentHashMap<String, CargoRequest>()

fun main() {
    embeddedServer(Netty, port = 8080) {
        install(ContentNegotiation) {
            json()
        }
        routing {
            post("/cargo-request") {
                val request = call.receive<CargoRequest>()
                if (cargoRequests.containsKey(request.id)) {
                    call.respond(HttpStatusCode.Conflict, "Cargo request with this ID already exists.")
                } else {
                    cargoRequests[request.id] = request
                    call.respond(HttpStatusCode.Created, request)
                }
            }

            post("/callback") {
                val callback = call.receive<CallbackData>()
                val cargoRequest = cargoRequests[callback.cargoRequestId]
                if (cargoRequest != null) {
                    cargoRequest.status = callback.statusUpdate
                    call.respond(HttpStatusCode.OK, "Status updated")
                } else {
                    call.respond(HttpStatusCode.NotFound, "Cargo request not found")
                }
            }

            get("/cargo-request/{id}") {
                val id = call.parameters["id"]
                if (id == null) {
                    call.respond(HttpStatusCode.BadRequest, "Missing id")
                    return@get
                }
                val request = cargoRequests[id]
                if (request == null) {
                    call.respond(HttpStatusCode.NotFound, "Cargo request not found")
                } else {
                    call.respond(request)
                }
            }
        }
    }.start(wait = true)
}

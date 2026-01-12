package envoy.authz
import input.attributes.request.http as http_request

default allow = false
decision_metadata := {"intent": "action_validation", "version": "v2.0-temporal", "timestamp": time.now_ns()}

allow {
    http_request.method == "GET"
    http_request.path == "/"
}

allow {
    http_request.method == "POST"
    http_request.path == "/delete"
    not action_limit_exceeded
}

action_limit_exceeded {
    input.attributes.context.request_count > 5
}

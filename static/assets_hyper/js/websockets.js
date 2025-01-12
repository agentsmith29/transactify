class WebSocketHandler {
    constructor(socketUrl, pageName) {
        this.socket = new WebSocket(socketUrl);
        this.pageName = pageName;

        this.socket.onopen = this._defaultOnOpen.bind(this);
        this.socket.onclose = this._defaultOnClose.bind(this);
        this.socket.onerror = this._defaultOnError.bind(this);

        // Provide a default onmessage handler
        this.socket.onmessage = this._defaultOnMessage.bind(this);
    }

    // Default handler for onopen
    _defaultOnOpen() {
        console.log("WebSocket connection established for page:", this.pageName);
    }

    // Default handler for onmessage
    _defaultOnMessage(event) {
        console.log("Default message handler:", event.data);
    }

    // Default handler for onclose
    _defaultOnClose() {
        console.log("WebSocket connection closed");
        window.storeManager.toastManager.warning(
            "WebSocket connection closed",
            "WebSocket connection was closed or reset.",
            "",
            false
        );
    }

    // Default handler for onerror
    _defaultOnError(error) {
        console.error("WebSocket error:", error);
    }

    // Allow dynamic reassignment of handlers
    set onmessage(handler) {
        if (typeof handler === "function") {
            this.socket.onmessage = handler;
        } else {
            console.error("onmessage must be a function");
        }
    }

    set onopen(handler) {
        if (typeof handler === "function") {
            this.socket.onopen = handler;
        } else {
            console.error("onopen must be a function");
        }
    }

    set onclose(handler) {
        if (typeof handler === "function") {
            this.socket.onclose = handler;
        } else {
            console.error("onclose must be a function");
        }
    }

    set onerror(handler) {
        if (typeof handler === "function") {
            this.socket.onerror = handler;
        } else {
            console.error("onerror must be a function");
        }
    }
}
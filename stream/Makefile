-include .env
.EXPORT_ALL_VARIABLES:

.PHONY: init-env mediamtx help

init-env: ## Copy .env.example to .env (won't overwrite existing)
	@if [ -f .env ]; then \
		echo ".env already exists, skipping"; \
	else \
		cp .env.example .env; \
		echo ".env created from .env.example"; \
	fi

mediamtx: ## Run the MediaMTX streaming server via Docker
	@if [ "$(MTX_WEBRTCADDITIONALHOSTS)" = "192.168.x.x,192.168.x.x" ]; then \
		echo "Error: MTX_WEBRTCADDITIONALHOSTS is still set to the placeholder value (192.168.x.x,192.168.x.x). Update it in .env before running."; \
		exit 1; \
	fi
	# ---- Port map ----
	# 8554       RTSP (TCP)
	# 1935       RTMP            [not exposed]
	# 8888       HLS             [not exposed]
	# 8889       WebRTC signaling
	# 8890/udp   SRT             [not exposed]
	# 8189/udp   WebRTC ICE/UDP
	# -------------------
	docker run -d --name mediamtx \
		-e MTX_RTSPTRANSPORTS=tcp \
		-e MTX_WEBRTCADDITIONALHOSTS=$(MTX_WEBRTCADDITIONALHOSTS) \
		-p 8554:8554 \
		-p 8889:8889 \
		-p 8189:8189/udp \
		bluenviron/mediamtx:1

help: ## Show this help message with available targets
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(firstword $(MAKEFILE_LIST)) | awk 'BEGIN {FS = ":.*##"}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

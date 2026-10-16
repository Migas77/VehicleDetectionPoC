-include .env
.EXPORT_ALL_VARIABLES:

# IP of the host running MediaMTX: the stream is pushed here and it is advertised as the WebRTC additional host
MEDIAMTX_IP ?= 192.168.93.56
MTX_WEBRTCADDITIONALHOSTS := $(MEDIAMTX_IP)

VIDEO ?= videos/crashes.mp4
STREAM_PATH ?= mystream

# Google Drive folder holding the stream videos (crashes.mp4, ...)
# https://drive.google.com/drive/folders/1jlTpVB6yf7tMdf_Hgwt2fT39tTRdYnyI?usp=sharing
VIDEOS_DRIVE_FOLDER_ID ?= 1jlTpVB6yf7tMdf_Hgwt2fT39tTRdYnyI
VIDEOS_DIR ?= videos

.PHONY: init-env check-ip video-download video-info mediamtx-up mediamtx-down stream-publish stream-play help

init-env: ## Copy .env.example to .env (won't overwrite existing)
	@if [ -f .env ]; then \
		echo ".env already exists, skipping"; \
	else \
		cp .env.example .env; \
		echo ".env created from .env.example"; \
	fi

check-ip:
	@if [ "$(MEDIAMTX_IP)" = "192.168.x.x" ]; then \
		echo "Error: MEDIAMTX_IP is still set to the placeholder value (192.168.x.x). Update it in .env or pass MEDIAMTX_IP=<ip>."; \
		exit 1; \
	fi

video-download: ## Download every file of the videos Google Drive folder into VIDEOS_DIR (wget + sed only)
	@mkdir -p "$(VIDEOS_DIR)"
	@# List the public folder via its embedded view (one "<file id> <file name>" per line), then fetch each file
	@wget -qO- "https://drive.google.com/embeddedfolderview?id=$(VIDEOS_DRIVE_FOLDER_ID)" \
		| sed 's/<div class="flip-entry"/\n&/g' \
		| sed -nE 's|.*file/d/([^/"]+).*flip-entry-title">([^<]+)<.*|\1 \2|p' \
		| while read -r id name || [ -n "$$id" ]; do \
			if [ -f "$(VIDEOS_DIR)/$$name" ]; then \
				echo "$(VIDEOS_DIR)/$$name already exists, skipping"; \
			else \
				echo "Downloading $$name"; \
				wget -q --show-progress -O "$(VIDEOS_DIR)/$$name" \
					"https://drive.usercontent.google.com/download?id=$$id&export=download&confirm=t" \
					|| { rm -f "$(VIDEOS_DIR)/$$name"; exit 1; }; \
			fi; \
		done

video-info: ## Show resolution and frame rate (r_frame_rate,avg_frame_rate) of every video in VIDEOS_DIR
	@printf "%-6s\t%-6s\t%-11s\t%-11s\t%s\n" WIDTH HEIGHT R_FPS AVG_FPS FILE; \
	for f in "$(VIDEOS_DIR)"/*.mkv "$(VIDEOS_DIR)"/*.mp4; do \
		[ -f "$$f" ] || continue; \
		ffprobe -v error -select_streams v:0 -show_entries stream=width,height,r_frame_rate,avg_frame_rate -of csv=p=0 "$$f" \
			| { IFS=, read -r w h r a; printf "%-6s\t%-6s\t%-11s\t%-11s\t%s\n" "$$w" "$$h" "$$r" "$$a" "$$f"; }; \
	done

mediamtx-up: check-ip ## Run the MediaMTX streaming server via Docker
	# ---- Port map ----
	# 8554       RTSP (TCP)
	# 1935       RTMP            [not exposed]
	# 8888       HLS             [not exposed]
	# 8889       WebRTC signaling
	# 8890/udp   SRT             [not exposed]
	# 8189/udp   WebRTC ICE/UDP
	# -------------------
	# If a container named mediamtx already exists, start it instead of creating a new one
	@if sudo docker container inspect mediamtx >/dev/null 2>&1; then \
		echo "Container mediamtx already exists, starting it"; \
		sudo docker start mediamtx; \
	else \
		sudo docker run -d --name mediamtx \
			-e MTX_RTSPTRANSPORTS=tcp \
			-e MTX_WEBRTCADDITIONALHOSTS=$(MTX_WEBRTCADDITIONALHOSTS) \
			-p 8554:8554 \
			-p 8889:8889 \
			-p 8189:8189/udp \
			bluenviron/mediamtx:1; \
	fi

mediamtx-down: ## Stop and remove the MediaMTX container
	sudo docker rm -f mediamtx

stream-publish: check-ip ## [sender] Loop VIDEO as an RTSP stream to rtsp://MEDIAMTX_IP:8554/STREAM_PATH
	@if [ ! -f "$(VIDEO)" ]; then \
		echo "Error: video file '$(VIDEO)' not found. Run 'make video-download', set VIDEO=<path> or place it at videos/crashes.mp4."; \
		exit 1; \
	fi
	ffmpeg -re -stream_loop -1 -i $(VIDEO) \
		-vf fps=30 \
		-c:v libx264 -preset veryfast -tune zerolatency -bf 0 -pix_fmt yuv420p -g 60 \
		-c:a libopus -b:a 128k -ar 48000 \
		-f rtsp -rtsp_transport tcp \
		rtsp://$(MEDIAMTX_IP):8554/$(STREAM_PATH)

stream-play: check-ip ## [receiver] Play the remote RTSP stream rtsp://MEDIAMTX_IP:8554/STREAM_PATH with ffplay (low latency)
	ffplay -rtsp_transport tcp \
		-fflags nobuffer -flags low_delay -framedrop \
		-window_title "$(STREAM_PATH) @ $(MEDIAMTX_IP)" \
		rtsp://$(MEDIAMTX_IP):8554/$(STREAM_PATH)

help: ## Show this help message with available targets and variables
	@echo "Usage: make <target> [VAR=value ...]"
	@echo ""
	@echo "Targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(firstword $(MAKEFILE_LIST)) | awk 'BEGIN {FS = ":.*##"}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "Variables (current value):"
	@printf "  \033[33m%-15s\033[0m %s\n" MEDIAMTX_IP "$(MEDIAMTX_IP)  (stream target + WebRTC additional host)"
	@printf "  \033[33m%-15s\033[0m %s\n" VIDEO "$(VIDEO)"
	@printf "  \033[33m%-15s\033[0m %s\n" STREAM_PATH "$(STREAM_PATH)"
	@printf "  \033[33m%-15s\033[0m %s\n" VIDEOS_DIR "$(VIDEOS_DIR)"
	@printf "  \033[33m%-15s\033[0m %s\n" VIDEOS_DRIVE_FOLDER_ID "$(VIDEOS_DRIVE_FOLDER_ID)"
	@echo ""
	@echo "Example:"
	@echo "  make video-download"
	@echo "  make mediamtx-up MEDIAMTX_IP=$(MEDIAMTX_IP)"
	@echo "  make stream-publish MEDIAMTX_IP=$(MEDIAMTX_IP) VIDEO=$(VIDEO)"
	@echo "  -> rtsp://$(MEDIAMTX_IP):8554/$(STREAM_PATH)"
	@echo "  make stream-play MEDIAMTX_IP=$(MEDIAMTX_IP) STREAM_PATH=$(STREAM_PATH)"

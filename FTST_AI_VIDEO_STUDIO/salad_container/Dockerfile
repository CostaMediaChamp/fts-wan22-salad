FROM ghcr.io/saladtechnologies/comfyui-api:comfy0.3.62-api1.10.0-torch2.8.0-cuda12.8-runtime

USER root

RUN apt-get update && apt-get install -y --no-install-recommends wget ca-certificates && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /opt/ComfyUI/models/diffusion_models \
             /opt/ComfyUI/models/text_encoders \
             /opt/ComfyUI/models/vae && \
    wget -O /opt/ComfyUI/models/diffusion_models/wan2.2_ti2v_5B_fp16.safetensors \
      https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/diffusion_models/wan2.2_ti2v_5B_fp16.safetensors && \
    wget -O /opt/ComfyUI/models/text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors \
      https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged/resolve/main/split_files/text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors && \
    wget -O /opt/ComfyUI/models/vae/wan2.2_vae.safetensors \
      https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/vae/wan2.2_vae.safetensors

WORKDIR /opt
RUN wget https://github.com/SaladTechnologies/salad-cloud-job-queue-worker/releases/download/v0.5.0/salad-http-job-queue-worker_x86_64.tar.gz && \
    tar -xvf salad-http-job-queue-worker_x86_64.tar.gz && \
    rm salad-http-job-queue-worker_x86_64.tar.gz && \
    chmod +x salad-http-job-queue-worker

COPY start-v03b.sh /opt/start-v03b.sh
RUN chmod +x /opt/start-v03b.sh

ENTRYPOINT ["/opt/start-v03b.sh"]

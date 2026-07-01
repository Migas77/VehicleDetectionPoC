import { useCameraInferenceFeed } from '@/features/cameras';

export function CameraFeedPanel() {
    const { camera, frame } = useCameraInferenceFeed();

    const preview = frame?.preview;
    const camLabel = camera ? `CAM-${camera.ue_supi.slice(-3)}` : 'CAM';

    return (
        <div className="relative bg-[#16181B] rounded-[18px] p-3.5 shrink-0">
            <div className="flex items-center justify-between px-1 pb-3">
                <div className="flex items-center gap-2">
                    <span
                        className="w-2 h-2 rounded-full bg-[#E5484D]"
                        style={{ animation: 'vg-blink 1.4s ease-in-out infinite' }}
                    />
                    <span className="font-jetbrains text-[11px] text-[#E4FB52] tracking-[0.06em]">
                        REC · {camLabel}
                    </span>
                </div>
                <span className="font-jetbrains text-[11px] text-[#8A8C86]">expand</span>
            </div>

            <div className="relative aspect-video rounded-xl overflow-hidden bg-black">
                {!camera && (
                    <div className="absolute inset-0 flex items-center justify-center px-4 text-center font-jetbrains text-[11px] text-[#8A8C86]">
                        No inference-enabled camera configured
                    </div>
                )}

                {camera && !preview && (
                    <div className="absolute inset-0 flex items-center justify-center px-4 text-center font-jetbrains text-[11px] text-[#8A8C86]">
                        Connecting to live feed…
                    </div>
                )}

                {preview && (
                    <img
                        src={`data:image/jpeg;base64,${preview.value}`}
                        alt="Live camera feed with detection overlay"
                        className="absolute inset-0 w-full h-full object-cover"
                    />
                )}

                {preview && (
                    <span className="absolute bottom-2 right-2.5 font-jetbrains text-[10px] text-[#E4FB52]">
                        DETECTOR ●
                    </span>
                )}
            </div>
        </div>
    );
}

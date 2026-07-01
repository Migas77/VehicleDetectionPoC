import { useQuery } from '@tanstack/react-query';
import { useEffect, useState } from 'react';

import { fetchCameras, fetchInferenceServerUrl } from '../api/cameras';
import { consumeInferencePipeline, listInferencePipelines } from '../api/inference-pipeline';
import type { CameraInfo, InferenceConsumeOutput } from '../types';

interface CameraInferenceFeed {
    camera: CameraInfo | null;
    frame: InferenceConsumeOutput | null;
    isLoading: boolean;
}

export function useCameraInferenceFeed(): CameraInferenceFeed {
    const { data: cameras, isLoading } = useQuery({
        queryKey: ['cameras'],
        queryFn: fetchCameras,
    });

    const { data: inferenceServerUrl } = useQuery({
        queryKey: ['inference-server-url'],
        queryFn: fetchInferenceServerUrl,
    });

    const camera = cameras?.find((c) => c.inference.inference_enabled) ?? null;

    const { data: pipelineIds } = useQuery({
        queryKey: ['inference-pipelines', inferenceServerUrl],
        queryFn: () => listInferencePipelines(inferenceServerUrl as string),
        enabled: Boolean(inferenceServerUrl) && Boolean(camera),
        refetchInterval: 5_000,
    });

    const pipelineId = pipelineIds?.[0] ?? null;

    const { data: consumeResult } = useQuery({
        queryKey: ['inference-consume', inferenceServerUrl, pipelineId],
        queryFn: () => consumeInferencePipeline(inferenceServerUrl as string, pipelineId as string),
        enabled: Boolean(inferenceServerUrl) && Boolean(pipelineId),
        refetchInterval: 150,
    });

    const [frame, setFrame] = useState<InferenceConsumeOutput | null>(null);

    useEffect(() => {
        const output = consumeResult?.outputs[0];
        if (output?.preview) setFrame(output);
    }, [consumeResult]);

    return { camera, frame, isLoading };
}

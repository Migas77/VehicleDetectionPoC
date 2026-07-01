import type { InferenceConsumeResponse, InferencePipelineListResponse } from '../types';

export async function listInferencePipelines(inferenceServerUrl: string): Promise<string[]> {
    const res = await fetch(`${inferenceServerUrl.replace(/\/$/, '')}/inference_pipelines/list`);
    if (!res.ok) throw new Error(`HTTP ${res.status}: ${res.statusText}`);
    const data = (await res.json()) as InferencePipelineListResponse;
    return data.pipelines;
}

export async function consumeInferencePipeline(
    inferenceServerUrl: string,
    pipelineId: string,
): Promise<InferenceConsumeResponse> {
    const res = await fetch(
        `${inferenceServerUrl.replace(/\/$/, '')}/inference_pipelines/${pipelineId}/consume`,
    );
    if (!res.ok) throw new Error(`HTTP ${res.status}: ${res.statusText}`);
    return res.json() as Promise<InferenceConsumeResponse>;
}

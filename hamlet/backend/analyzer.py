"""
Core music analysis engine using CLAP (Contrastive Language-Audio Pretraining).
"""
from typing import Dict, List, Any
import librosa
import numpy as np
import torch
import torch.nn.functional as F
from transformers import AutoProcessor, ClapModel

class DynamicTemporalMusicAnalyzer:
    """
    Wraps the CLAP model and exposes a single `analyze_track` method that
    scores arbitrary text prompts against successive chunks of an audio file.
    """

    def __init__(
        self,
        model_id: str = "laion/clap-htsat-fused",
        target_sr: int = 48000,
        min_chunk_ratio: float = 0.5,
    ):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"[Analyzer] Loading {model_id} on {self.device} ...")

        self.model = ClapModel.from_pretrained(model_id).to(self.device)
        self.processor = AutoProcessor.from_pretrained(model_id)
        self.target_sr = target_sr
        self.min_chunk_ratio = min_chunk_ratio

    def analyze_track(
        self,
        audio_path: str,
        schemes_dict: Dict[str, List[str]],
        window_sec: float = 4.0,
        temperature: float = 3.0,
    ) -> List[Dict[str, Any]]:
        """
        Analyze an audio file across multiple prompt schemes.
        Returns a list of dicts, one per time-window:
        """
        audio_sample, _ = librosa.load(audio_path, sr=self.target_sr)
        if audio_sample.ndim > 1:
            audio_sample = np.mean(audio_sample, axis=0)

        window_samples = int(window_sec * self.target_sr)
        total_samples = len(audio_sample)
        min_chunk_size = window_samples * self.min_chunk_ratio
        timeline = []

        for start_idx in range(0, total_samples, window_samples):
            chunk = audio_sample[start_idx : start_idx + window_samples]
            if len(chunk) < min_chunk_size:
                continue

            chunk_result = {
                "timestamp_start_sec": round(start_idx / self.target_sr, 2),
                "timestamp_end_sec": round((start_idx + window_samples) / self.target_sr, 2),
                "signatures": {},
            }

            for scheme_name, prompts in schemes_dict.items():
                chunk_result["signatures"][scheme_name] = self._score_chunk(
                    chunk, prompts, temperature
                )

            timeline.append(chunk_result)

        return timeline

    def _score_chunk(
        self, chunk: np.ndarray, prompts: List[str], temperature: float
    ) -> Dict[str, float]:
        """Score one audio chunk against a list of text movement descriptions."""
        inputs = self.processor(
            text=prompts,
            audio=chunk,
            return_tensors="pt",
            sampling_rate=self.target_sr,
            padding=True,
        )
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = self.model(**inputs)

        logits = outputs.logits_per_audio
        probs = F.softmax(logits / temperature, dim=-1).cpu().numpy()[0]

        return {
            (p[:40] + "...") if len(p) > 40 else p: float(prob)
            for p, prob in zip(prompts, probs)
        }

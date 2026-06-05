"""
Gradio web interface for HAMLET.
"""
import asyncio
from typing import Tuple, Dict, Any, Optional
import gradio as gr
import matplotlib.pyplot as plt

from hamlet.backend import (
    DynamicTemporalMusicAnalyzer,
    ConfigLoader,
    generate_timeline_plots,
)

def build_app() -> gr.Blocks:
    """Construct and return the Gradio Blocks interface."""

    #  Load configuration once 
    cfg = ConfigLoader()
    default_schemes = cfg.get_schemes()

    #  Initialise the analyzer once (model weights are heavy) 
    analyzer = DynamicTemporalMusicAnalyzer(
        model_id=cfg.model_id,
        target_sr=cfg.target_sr,
        min_chunk_ratio=cfg.min_chunk_ratio,
    )

    #  Async controller 
    async def process_audio_ui(
        audio_file_path: Optional[str],
        custom_genres: str,
        window_size: float,
        temperature: float,
    ) -> Tuple[Dict[str, Any], Optional[plt.Figure]]:
        if audio_file_path is None:
            return {"error": "Please upload an audio file."}, None

        runtime_schemes = dict(default_schemes)  # shallow copy

        if custom_genres and custom_genres.strip():
            custom_list = [
                line.strip() for line in custom_genres.split("\n") if line.strip()
            ]
            if custom_list:
                runtime_schemes["choreographer_custom"] = custom_list

        try:
            results = await asyncio.to_thread(
                analyzer.analyze_track,
                audio_path=audio_file_path,
                schemes_dict=runtime_schemes,
                window_sec=window_size,
                temperature=temperature,
            )
            fig = generate_timeline_plots(results)
            return results, fig
        except Exception as exc:
            return {"error": str(exc)}, None

    #  Build UI 
    ui_settings = cfg.ui_settings
    with gr.Blocks(title=ui_settings.get("title", "HAMLET")) as demo:
        gr.Markdown("# HAMLET: Music-to-Movement Style Analyzer")
        gr.Markdown(
            "Upload an audio track to analyze its structural intention over time."
        )

        with gr.Row():
            with gr.Column():
                audio_input = gr.Audio(
                    type="filepath", label="Upload Music Track (MP3/WAV)"
                )
                custom_text_input = gr.Textbox(
                    lines=5,
                    label="Choreographer's Custom Elements (Optional)",
                    placeholder="Enter custom descriptive elements. One per line.",
                )

                with gr.Accordion("Advanced Configuration", open=False):
                    window_slider = gr.Slider(
                        minimum=2.0,
                        maximum=10.0,
                        value=cfg.default_window_sec,
                        step=0.5,
                        label="Window Size (seconds)",
                    )
                    temp_slider = gr.Slider(
                        minimum=1.0,
                        maximum=5.0,
                        value=cfg.default_temperature,
                        step=0.1,
                        label="Softmax Temperature",
                    )

                analyze_btn = gr.Button("Analyze Track", variant="primary")

            with gr.Column():
                plot_output = gr.Plot(label="Synchronized Visual Progressions")
                json_output = gr.JSON(label="Raw Output Log Data (JSON)")

        analyze_btn.click(
            fn=process_audio_ui,
            inputs=[audio_input, custom_text_input, window_slider, temp_slider],
            outputs=[json_output, plot_output],
        )

    return demo

def launch():
    """Launch the Gradio app using parameters from settings.yaml."""
    cfg = ConfigLoader()
    ui_cfg = cfg.ui_settings
    demo = build_app()
    demo.launch(
        share=ui_cfg.get("share", False),
        debug=ui_cfg.get("debug", False),
        server_port=ui_cfg.get("server_port", 7860),
    )

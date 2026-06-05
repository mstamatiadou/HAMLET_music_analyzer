"""
Plot generation for HAMLET timeline analysis results.
"""
from typing import List, Dict, Any, Optional
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

def generate_timeline_plots(
    analysis_results: List[Dict[str, Any]],
) -> Optional[plt.Figure]:
    """
    Convert the analyzer's raw output into a multi-panel Matplotlib figure.
    Returns None if there are no results to plot.
    """
    if not analysis_results:
        return None

    all_schemes = list(analysis_results[0]["signatures"].keys())
    if not all_schemes:
        return None

    sns.set_theme(style="whitegrid")
    fig, axes = plt.subplots(
        len(all_schemes), 1, figsize=(12, 4 * len(all_schemes)), sharex=True
    )
    axes = [axes] if len(all_schemes) == 1 else axes.flatten()

    for idx, scheme_key in enumerate(all_schemes):
        rows = []
        for chunk in analysis_results:
            start_t = chunk["timestamp_start_sec"]
            for element, prob in chunk["signatures"].get(scheme_key, {}).items():
                rows.append(
                    {
                        "start_time_seconds": start_t,
                        "element": element,
                        "probability": prob,
                    }
                )

        df = pd.DataFrame(rows)
        if not df.empty:
            sns.lineplot(
                data=df,
                x="start_time_seconds",
                y="probability",
                hue="element",
                marker="o",
                ax=axes[idx],
            )

        clean_title = scheme_key.replace("_", " ").upper()
        axes[idx].set_title(
            f"Timeline Signature: {clean_title}",
            fontsize=11,
            fontweight="bold",
            pad=8,
        )
        axes[idx].set_ylabel("Probability")
        axes[idx].set_ylim(0, 1.05)
        axes[idx].legend(
            bbox_to_anchor=(1.01, 1),
            loc="upper left",
            borderaxespad=0.0,
            fontsize=9,
        )

    axes[-1].set_xlabel(
        "Track Playback Position (Seconds)", fontsize=10, fontweight="bold"
    )
    fig.tight_layout()
    return fig
  

import gradio as gr

from . import config
from .handler import (
    er_fit_md_cange,
    er_max_phase_change,
    er_round_change,
    fit_click,
    fitter_change,
    replot_click,
    sample_num_change,
    sample_percentage_change,
    upload_samples,
)

page = gr.Blocks(title="HyperStarC")

with page:
    gr.Markdown("## HyperStarC")
    with gr.Row():
        with gr.Column(scale=3):
            tab = gr.Tabs()
            with tab:
                with gr.Tab("PDF"):
                    pdf_plot = gr.Plot(label="PDF")
                with gr.Tab("CDF"):
                    cdf_plot = gr.Plot(label="CDF")
                with gr.Tab("Correlation"):
                    corr_plot = gr.Plot(label="Correlation")

        with gr.Column(scale=1):
            gr.Markdown("### Load Samples")
            load_btn = gr.UploadButton("Load Samples")
            replot_btn = gr.Button("Replot")

            gr.Markdown("### Number of Samples")
            with gr.Tabs():
                with gr.Tab("percentage"):
                    sample_percentage = gr.Slider(
                        0,
                        100,
                        value=100,
                        label="percentage of samples",
                        interactive=True,
                    )
                with gr.Tab("total number"):
                    sample_num = gr.Number(
                        value=1000, label="number of samples", interactive=True
                    )

            gr.Markdown("### Fitting Parameters")
            fitter_dropdown = gr.Dropdown(config.FITTER_NAMES, label="Distribution")
            with gr.Row() as exp_block:
                gr.Markdown("no parameters")
            with gr.Row(visible=False) as erlang_block:
                er_fit_md = gr.Dropdown(
                    config.ERMD_NAMES, label="method", interactive=True
                )
                er_round = gr.Dropdown(
                    config.RUNDING_NAMES, label="rounding", interactive=True
                )
                er_max_phase = gr.Number(
                    value=1000, label="max phase", interactive=True
                )
            with gr.Row(visible=False) as hyper_block:
                gr.Markdown("hyper block")
            with gr.Row(visible=False) as map_block:
                branch = gr.Number(value=2, label="branch")
                reassignment = gr.Number(value=10, label="reassignment")
                queue_opt = gr.Number(value=5, label="queue optimize")
                shuffles = gr.Number(value=2, label="shuffles")
            with gr.Row(visible=True) as fitter_block:
                fit_btn = gr.Button("Fit")
                export_btn = gr.Button("Export")

    # set event handlers
    fitter_dropdown.change(
        fn=fitter_change,
        inputs=[fitter_dropdown],
        outputs=[exp_block, erlang_block, hyper_block, map_block],
    )
    load_btn.upload(fn=upload_samples, inputs=load_btn, outputs=pdf_plot)
    replot_btn.click(fn=replot_click, outputs=pdf_plot)
    sample_percentage.change(fn=sample_percentage_change, inputs=sample_percentage)
    sample_num.change(fn=sample_num_change, inputs=sample_num)
    fit_btn.click(fn=fit_click, outputs=pdf_plot)
    er_fit_md.change(fn=er_fit_md_cange, inputs=er_fit_md)
    er_round.change(fn=er_round_change, inputs=er_round)
    er_max_phase.change(fn=er_max_phase_change, inputs=er_max_phase)

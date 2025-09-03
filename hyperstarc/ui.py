import gradio as gr

from . import config
from .config import Parameters
from .erlang_handler import (er_fit_md_change, er_max_phase_change,
                             er_round_change)
from .herlang_handler import (her_fit_md_change, her_max_phase_change, her_peaks_change, her_round_change)
from .fit_handler import fit_click, fitter_change, export_click
from .plot_handler import (bins_num_change, max_x_change, min_x_change,
                           replot_click)
from .sam_handler import sample_num_change, upload_samples

page = gr.Blocks(title="HyperStarC")

with page:
    default_params = Parameters()
    params = gr.State(default_params)
    gr.Markdown("## HyperStarC")
    with gr.Row():
        with gr.Column(scale=3):
            pdf_plot = gr.Plot(label="PDF", visible=True)
            cdf_plot = gr.Plot(label="CDF", visible=True)
            corr_plot = gr.Plot(label="Correlation", visible=False)

        with gr.Column(scale=1):
            load_btn = gr.UploadButton("Load Samples")
            bins_num = gr.Number(
                value = params.value.draw_hist_bins,
                label="number of bins",
                interactive=True,
                maximum=params.value.draw_max_bins,
                minimum=params.value.draw_min_bins,
            )
            max_x = gr.Number(value=params.value.draw_max_x, label="max x for plotting", interactive=True)
            min_x = gr.Number(value=params.value.draw_min_x, label="min x for plotting", interactive=True)
            sample_num = gr.Number(value=1000, label="number of samples for plotting", interactive=True)
            replot_btn = gr.Button("Replot")
            
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
                    value=config.default_param.erlang_max_phase, label="max phase", interactive=True
                )
            with gr.Row(visible=False) as hyper_block:
                her_peaks = gr.Number(
                    value=config.default_param.herlang_peaks, label="peaks", interactive=True
                )
                her_fit_md = gr.Dropdown(
                    config.ERMD_NAMES, label="method", interactive=True
                )
                her_round = gr.Dropdown(
                    config.RUNDING_NAMES, label="rounding", interactive=True
                )
                her_max_phase = gr.Number(
                    value=config.default_param.herlang_max_phase, label="max phase", interactive=True
                )
            with gr.Row(visible=False) as map_block:
                gr.Markdown("## map block")
            with gr.Row(visible=True) as fitter_block:
                dl_file = gr.File(label="Download result")
                fit_btn = gr.Button("Fit")
                export_btn = gr.Button("Export")

    # set event handlers
    fitter_dropdown.change(
        fn=fitter_change,
        inputs=[fitter_dropdown, params],
        outputs=[exp_block, erlang_block, hyper_block, map_block, params],
    )

    sample_num.change(fn=sample_num_change, inputs=[sample_num, params], outputs=params)

    load_btn.upload(fn=upload_samples, inputs=[load_btn, params], outputs=(pdf_plot, cdf_plot, params))
    replot_btn.click(fn=replot_click, inputs=[params], outputs=(pdf_plot, cdf_plot))
    fit_btn.click(fn=fit_click, inputs=[params], outputs=(pdf_plot, cdf_plot, params))


    er_fit_md.change(fn=er_fit_md_change, inputs=[er_fit_md, params], outputs=params)
    er_round.change(fn=er_round_change, inputs=[er_round, params], outputs=params)
    er_max_phase.change(fn=er_max_phase_change, inputs=[er_max_phase, params], outputs=params)

    her_peaks.change(fn=her_peaks_change, inputs=[her_peaks, params], outputs=params)
    her_fit_md.change(fn=her_fit_md_change, inputs=[her_fit_md, params], outputs=params)
    her_round.change(fn=her_round_change, inputs=[her_round, params], outputs=params)
    her_max_phase.change(fn=her_max_phase_change, inputs=[her_max_phase, params], outputs=params)

    bins_num.change(fn=bins_num_change, inputs=[bins_num, params], outputs=params)
    max_x.change(fn=max_x_change, inputs=[max_x, params], outputs=params)
    min_x.change(fn=min_x_change, inputs=[min_x, params], outputs=params)

    export_btn.click(fn=export_click, inputs=[params], outputs=dl_file)
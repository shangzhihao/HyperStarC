import gradio as gr

from .handler import upload_samples

DISTS = ["Exponential", "Erlang", "Hyper-Erlang", "MAP"]


# Function to handle fitting logic (can be adapted based on your needs)
def fit_model(fitter, branch, reassignment, queue_opt, shuffles):
    return f"Fitted with {fitter}, branch={branch}, reassignment={reassignment}, queue_opt={queue_opt}, shuffles={shuffles}"

# Update parameters based on selected fitter
def update_parameters(fitter):
    res = [gr.update(visible=False) for _ in DISTS]
    idx = DISTS.index(fitter)
    res[idx] = gr.update(visible=True)
    return res

# Interface for UI
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

            gr.Markdown("### Limit Data")
            with gr.Tabs():
                with gr.Tab("percentage"):
                    size_slider = gr.Slider(0, 100, value=100, label="percentage of samples", interactive=True)
                with gr.Tab("total number"):
                    num = gr.Number(value=1000, label="number of samples", interactive=True)


            gr.Markdown("### Configuration")
            with gr.Accordion("fitting", open=True):
                fitter = gr.Dropdown(DISTS, label="Fitter")
                with gr.Row() as exp_block:
                    gr.Markdown("exponential block")
                with gr.Row(visible=False) as erlang_block:
                    gr.Markdown("erlang block")
                with gr.Row(visible=False) as hyper_block:
                    gr.Markdown("hyper block")
                with gr.Row(visible=False) as map_block:
                    branch = gr.Number(value=2, label="branch")
                    reassignment = gr.Number(value=10, label="reassignment")
                    queue_opt = gr.Number(value=5, label="queue optimize")
                    shuffles = gr.Number(value=2, label="shuffles")
                    fit_btn = gr.Button("Fit")
                    export_btn = gr.Button("Export")

    
    # Set dropdown for fitter updates and connect to parameters
    fitter.change(fn=update_parameters, inputs=[fitter], outputs=[exp_block, erlang_block, hyper_block, map_block])

    load_btn.upload(fn=upload_samples, inputs=load_btn, outputs=pdf_plot)
    replot_btn.click(fn=upload_samples, outputs=pdf_plot)

    fit_btn.click(fn=fit_model, inputs=[fitter, branch, reassignment, queue_opt, shuffles], outputs=pdf_plot)


etfrom gradio_client import Client, handle_file


def AI_CONVERT(photo1_path, photo2_path):
    client = Client("levihsu/OOTDiffusion", hf_token='secret')
    result = client.predict(
            vton_img=handle_file(photo1_path),
            garm_img=handle_file(photo2_path),
            n_samples=1,
            n_steps=20,
            image_scale=2,
            seed=-1,
            api_name="/process_hd"
    )
    return result











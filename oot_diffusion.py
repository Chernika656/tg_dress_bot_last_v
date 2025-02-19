from gradio_client import Client, handle_file


def AI_CONVERT(photo1_path, photo2_path):
    client = Client("levihsu/OOTDiffusion", hf_token='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')
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









# import replicate
# import os
#
#
#
# def AI_CONVERT(photo1_path, photo2_path):
#     input = {"garment_image": open(photo1_path, "rb"),
#              "model_image": open(photo2_path, "rb")
#              }
#
#     try:
#         output = replicate.run(
#             "viktorfa/oot_diffusion:9f8fa4956970dde99689af7488157a30aa152e23953526a605df1d77598343d7",
#             input=input
#         )
#         #Replicate возвращает список, берем первый элемент (предполагается один результат)
#         image_bytes = output[0]
#
#         # Сохраняем обработанное изображение во временный файл
#         temp_filename = "processed_image.png"
#         with open(temp_filename, "wb") as f:
#             f.write(image_bytes)
#
#         return temp_filename #Возвращаем путь к файлу
#
#     except Exception as e:
#         print(f"Error in AI_CONVERT: {e}")
#         return None

# '5c913dc0a08cf513c6d9854ececdf6143fac72bfb6167b833809ae4b7baba4b9'
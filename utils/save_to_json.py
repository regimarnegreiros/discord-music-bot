import json

async def save_info_to_json(info, filename):
    # Converte a variável info para uma string JSON formatada
    json_data = json.dumps(info, indent=4)

    # Abre o arquivo no modo de escrita e escreve os dados JSON
    with open(filename, 'w') as f:
        f.write(json_data)

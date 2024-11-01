# Bot de Música para Discord

Este é um bot para Discord escrito em Python utilizando as bibliotecas `discord.py` e `yt_dlp`. O bot foi desenvolvido para tocar músicas do YouTube, Spotify e Deezer, gerenciar filas de músicas e lidar com atualizações de estado de voz em canais do Discord. Ele suporta comandos para tocar músicas, pular e mover faixas, visualizar e limpar a fila, e entrar/sair de canais de voz.

## Dependências

### Pacotes Python
- `discord.py`: Um wrapper Python para a API do Discord.
- `yt_dlp`: Uma biblioteca de download do YouTube que fornece capacidades de extração para vídeos e playlists do YouTube.
- `spotipy`: Uma biblioteca para interagir com a API do Spotify.
- `deezer-python`: Uma biblioteca para interagir com a API do Deezer.
- `pynacl`: Uma biblioteca para suporte de voz no `discord.py`.
- `python-dotenv`: Uma biblioteca para carregar variáveis de ambiente a partir de um arquivo `.env`.

### Dependências Externas
- `ffmpeg`: Um framework multimídia necessário para streaming de áudio.

## Instalação

1. **Instalar Pacotes Python:**

   Você pode instalar os pacotes Python necessários usando pip:

   ```sh
   pip install -r requirements.txt
   ```

2. **Instalar FFMPEG:**

   Siga as instruções para baixar e instalar o FFMPEG no site oficial do [FFMPEG](https://ffmpeg.org/download.html). Certifique-se de que o executável `ffmpeg` esteja no PATH do seu sistema.

## Configuração

### Arquivo `.env`

Crie um arquivo chamado `.env` na raiz do seu projeto e adicione as seguintes variáveis de ambiente:

```env
TOKEN=SEU_TOKEN
SPOTIPY_CLIENT_ID=SEU_CLIENT_ID
SPOTIPY_CLIENT_SECRET=SEU_CLIENT_SECRET
```

### Opções FFMPEG

Certifique-se de que o caminho para o executável `ffmpeg` esteja corretamente definido no dicionário `FFMPEG_OPTIONS`:

```python
FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn', 
    'executable': 'C:/ffmpeg/ffmpeg.exe'  # Atualize este caminho para o executável ffmpeg no seu sistema
}
```

## Executando o Bot

Execute o bot usando o seguinte comando:

```sh
python main.py
```
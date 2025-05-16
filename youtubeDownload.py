import streamlit as st
from pytubefix import YouTube, Playlist
from pytubefix.cli import on_progress
from io import BytesIO
import zipfile

st.set_page_config(page_title="YouTube Downloader", layout="centered")

st.title("📥 YouTube Downloader")
st.markdown("Cole o link do vídeo ou playlist abaixo, selecione a ação e baixe o conteúdo.")

modo = st.radio("Escolha uma opção:", ["🎬 Baixar Vídeo", "🎵 Baixar Áudio", "📂 Playlist"])

if modo == "🎬 Baixar Vídeo":
    url_video = st.text_input("🔗 Link do Vídeo - clique em ENTER para cofirmar", key="video")
    if url_video:
        yt = YouTube(url_video, on_progress_callback=on_progress)
        st.markdown(f"**Título:** {yt.title}")
        if st.button("📥 Baixar Vídeo", key="baixar_video"):
            buffer = BytesIO()
            stream = yt.streams.get_highest_resolution()
            stream.stream_to_buffer(buffer)
            buffer.seek(0)
            st.download_button(
                label="📁 Clique para baixar",
                data=buffer,
                file_name=f"{yt.title}.mp4",
                mime="video/mp4"
            )

elif modo == "🎵 Baixar Áudio":
    url_audio = st.text_input("🔗 Link do Vídeo (Áudio) - clique em ENTER para cofirmar", key="audio")
    if url_audio:
        yt = YouTube(url_audio, on_progress_callback=on_progress)
        st.markdown(f"**Título:** {yt.title}")
        if st.button("📥 Baixar Áudio", key="baixar_audio"):
            buffer = BytesIO()
            stream = yt.streams.get_audio_only()
            stream.stream_to_buffer(buffer)
            buffer.seek(0)
            st.download_button(
                label="📁 Clique para baixar",
                data=buffer,
                file_name=f"{yt.title}.mp3",
                mime="audio/mpeg"
            )

elif modo == "📂 Playlist":
    url_playlist = st.text_input("🔗 Link da Playlist - clique em ENTER para cofirmar", key="playlist")

    if 'playlist_videos' not in st.session_state:
        st.session_state['playlist_videos'] = []

    if url_playlist and st.button("🔍 Carregar Playlist"):
        try:
            pl = Playlist(url_playlist)
            videos = pl.videos
            carregando_texto = st.empty()
            playlist_info = []

            for i, video in enumerate(videos, start=1):
                carregando_texto.text(f"⏳ Carregando vídeo {i} de {len(videos)}: {video.title}")
                playlist_info.append({"title": video.title, "url": video.watch_url})

            carregando_texto.text(f"✅ {len(videos)} vídeos carregados com sucesso.")
            st.session_state['playlist_videos'] = playlist_info
        except Exception as e:
            st.error(f"Erro ao carregar a playlist: {e}")

    if st.session_state['playlist_videos']:
        st.markdown("### 🎧 Músicas encontradas:")
        for i, video in enumerate(st.session_state['playlist_videos']):
            st.write(f"{i+1}. {video['title']}")

        if st.button("📥 Baixar Playlist em ZIP", key="baixar_zip"):
            with st.spinner("Baixando e compactando os áudios..."):
                zip_buffer = BytesIO()
                with zipfile.ZipFile(zip_buffer, "w") as zipf:
                    for i, video in enumerate(st.session_state['playlist_videos']):
                        try:
                            yt = YouTube(video['url'])
                            audio_stream = yt.streams.get_audio_only()
                            audio_buffer = BytesIO()
                            audio_stream.stream_to_buffer(audio_buffer)
                            audio_buffer.seek(0)

                            nome_seguro = yt.title.replace(" ", "_").replace("/", "_").replace("\\", "_")
                            zipf.writestr(f"{nome_seguro}.mp3", audio_buffer.read())
                            st.write(f"✔️ {i+1}/{len(st.session_state['playlist_videos'])} - {yt.title}")
                        except Exception as e:
                            st.warning(f"⚠️ Erro com '{video['title']}': {e}")

                zip_buffer.seek(0)
                st.success("✅ Playlist compactada com sucesso!")
                st.download_button(
                    label="📦 Clique aqui para baixar o ZIP",
                    data=zip_buffer,
                    file_name="playlist_musicas.zip",
                    mime="application/zip"
                )

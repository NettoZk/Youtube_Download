import streamlit as st
from pytubefix import YouTube, Playlist
from pytubefix.cli import on_progress
from io import BytesIO

st.set_page_config(page_title="YouTube Downloader", layout="centered")

st.title("📥 YouTube Downloader")
st.markdown("Cole o link do vídeo/playlist abaixo, selecione a ação e baixe o conteúdo.")

modo = st.radio("Escolha uma opção:", ["🎬 Baixar Vídeo", "🎵 Baixar Áudio", "📂 Playlist"])

if modo == "🎬 Baixar Vídeo":
    url_video = st.text_input("🔗 Link do Vídeo", key="video")
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
    url_audio = st.text_input("🔗 Link do Vídeo (Áudio)", key="audio")
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
    url_playlist = st.text_input("🔗 Link da Playlist", key="playlist")

    if 'playlist_videos' not in st.session_state:
        st.session_state['playlist_videos'] = []

    if url_playlist and st.button("🔍 Carregar músicas"):
        try:
            pl = Playlist(url_playlist)
            videos = pl.videos
            carregando_text = st.empty()  # espaço para atualizar texto dinamicamente
            playlist_info = []

            for i, video in enumerate(videos, start=1):
                carregando_text.text(f"⏳ Carregando vídeo {i} de {len(videos)}: {video.title}")
                playlist_info.append({"title": video.title, "url": video.watch_url})

            carregando_text.text(f"✅ Todos os {len(videos)} vídeos carregados com sucesso!")
            st.session_state['playlist_videos'] = playlist_info
        except Exception as e:
            st.error(f"Erro ao carregar a playlist: {e}")

    if st.session_state['playlist_videos']:
        st.markdown("---")
        st.markdown("### 🎧 Lista de músicas")

        for i, video in enumerate(st.session_state['playlist_videos']):
            st.write(f"**{video['title']}**")
            if st.button(f"📥 Baixar '{video['title']}'", key=f"baixar_{i}"):
                with st.spinner(f"Baixando áudio de '{video['title']}'..."):
                    try:
                        yt = YouTube(video['url'], on_progress_callback=on_progress)
                        buffer = BytesIO()
                        yt.streams.get_audio_only().stream_to_buffer(buffer)
                        buffer.seek(0)
                        st.download_button(
                            label=f"🎵 Clique para baixar '{video['title']}'",
                            data=buffer,
                            file_name=f"{video['title']}.mp3",
                            mime="audio/mpeg",
                            key=f"dl_{i}"
                        )
                    except Exception as e:
                        st.error(f"Erro ao baixar '{video['title']}': {e}")
